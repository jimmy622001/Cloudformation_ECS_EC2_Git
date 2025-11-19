#!/usr/bin/env python
import os
import sys
import subprocess
import json
import glob
import re
import argparse
import shutil
from datetime import datetime

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

def print_header(message):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 70}{Colors.NC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{message.center(70)}{Colors.NC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 70}{Colors.NC}\n")

def print_section(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{message}{Colors.NC}\n")

def print_success(message):
    print(f"{Colors.GREEN}{message}{Colors.NC}")

def print_warning(message):
    print(f"{Colors.YELLOW}{message}{Colors.NC}")

def print_error(message):
    print(f"{Colors.RED}{message}{Colors.NC}")

def run_command(cmd, shell=False):
    """Run a command and return its exit code, stdout and stderr"""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            check=False,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def backup_file(file_path):
    """Create a backup of a file before modifying it"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.bak_{timestamp}"
    shutil.copy2(file_path, backup_path)
    return backup_path

def run_detect_secrets():
    """Run detect-secrets to find hardcoded secrets in CloudFormation templates"""
    print_section("Running Secret Detection with detect-secrets")
    
    # Run detect-secrets
    return_code, stdout, stderr = run_command(['detect-secrets', 'scan'])
    
    if stderr:
        print_warning(stderr)
    
    try:
        # Parse the results
        results = json.loads(stdout)
        
        if results.get("results") and len(results["results"]) > 0:
            # Find secrets only in CloudFormation templates
            template_secrets = {}
            for filepath, secrets in results["results"].items():
                if filepath.startswith('templates/') and filepath.endswith('.yaml'):
                    template_secrets[filepath] = secrets
            
            if template_secrets:
                print_error("Potential secrets found in CloudFormation templates!")
                print("-" * 70)
                
                # Print summary of files with secrets
                for filepath, secrets in template_secrets.items():
                    print(f"  File: {filepath}")
                    for secret in secrets:
                        print(f"    - Line {secret.get('line_number')}: {secret.get('type')}")
                
                print("\nRecommendation: Replace hardcoded secrets with parameter references or use AWS Secrets Manager")
                return False, template_secrets
            else:
                print_success("No secrets detected in CloudFormation templates")
                return True, {}
        else:
            print_success("No secrets detected in repository")
            return True, {}
            
    except json.JSONDecodeError as e:
        print_error(f"Error parsing detect-secrets output: {e}")
        return False, {}

def check_wildcard_permissions():
    """Check for wildcard permissions in IAM policies"""
    print_section("Checking for wildcard permissions in IAM policies")
    
    template_files = glob.glob("templates/*.yaml")
    issues = {}
    
    for template_file in template_files:
        try:
            with open(template_file, 'r') as f:
                content = f.readlines()
                
            resource_lines = []
            for i, line in enumerate(content):
                if "Resource" in line and '"*"' in line:
                    # Look for context (5 lines before and after)
                    start = max(0, i-5)
                    end = min(len(content), i+5)
                    context = ''.join(content[start:end])
                    resource_lines.append((i+1, line.strip(), context))
            
            if resource_lines:
                print_error(f"Wildcard permissions found in {template_file}:")
                issues[template_file] = resource_lines
                for line_num, line, context in resource_lines:
                    print(f"  Line {line_num}: {line}")
                
        except Exception as e:
            print_error(f"Error analyzing {template_file}: {str(e)}")
    
    if not issues:
        print_success("No wildcard permissions found in IAM policies")
        return True, {}
    else:
        print_warning("Recommendation: Replace wildcard permissions with specific resource ARNs")
        return False, issues

def check_security_group_rules():
    """Check for overly permissive security group rules"""
    print_section("Checking for overly permissive security group rules")
    
    template_files = glob.glob("templates/*.yaml")
    issues = {}
    
    for template_file in template_files:
        try:
            with open(template_file, 'r') as f:
                content = f.readlines()
                
            security_group_issues = []
            for i, line in enumerate(content):
                if "CidrIp" in line and "0.0.0.0/0" in line:
                    # Look for port 22 (SSH), 3389 (RDP), or other sensitive ports nearby
                    start = max(0, i-10)
                    end = min(len(content), i+10)
                    context = ''.join(content[start:end])
                    
                    port_issues = []
                    if "Port" in context and ("22" in context or "3389" in context or "3306" in context):
                        if "22" in context:
                            port_issues.append("SSH (22)")
                        if "3389" in context:
                            port_issues.append("RDP (3389)")
                        if "3306" in context:
                            port_issues.append("MySQL (3306)")
                    
                    if port_issues:
                        security_group_issues.append((i+1, line.strip(), port_issues))
            
            if security_group_issues:
                print_error(f"Overly permissive security group rules found in {template_file}:")
                issues[template_file] = security_group_issues
                for line_num, line, ports in security_group_issues:
                    print(f"  Line {line_num}: {line}")
                    print(f"    Opens {', '.join(ports)} to the world (0.0.0.0/0)")
                
        except Exception as e:
            print_error(f"Error analyzing {template_file}: {str(e)}")
    
    if not issues:
        print_success("No overly permissive security group rules found")
        return True, {}
    else:
        print_warning("Recommendation: Restrict security group rules to specific IP ranges")
        return False, issues

def check_encryption_settings():
    """Check for missing encryption in resources"""
    print_section("Checking for missing encryption settings")
    
    template_files = glob.glob("templates/*.yaml")
    issues = {}
    
    encryption_keywords = {
        "AWS::S3::Bucket": ["BucketEncryption", "ServerSideEncryptionConfiguration"],
        "AWS::RDS::DBInstance": ["StorageEncrypted", "true"],
        "AWS::SNS::Topic": ["KmsMasterKeyId"],
        "AWS::SQS::Queue": ["KmsMasterKeyId"],
        "AWS::Lambda::Function": ["KmsKeyArn"],
        "AWS::Logs::LogGroup": ["KmsKeyId"]
    }
    
    for template_file in template_files:
        file_issues = []
        try:
            with open(template_file, 'r') as f:
                content = f.readlines()
                full_content = ''.join(content)
                
            for resource_type, keywords in encryption_keywords.items():
                if resource_type in full_content:
                    # Find all resource definitions of this type
                    pattern = rf'(\s+\w+:\s*\n\s+Type:\s*{resource_type.replace(":", ":")}\s*\n)'
                    resource_matches = list(re.finditer(pattern, full_content))
                    
                    for match in resource_matches:
                        resource_start = match.start()
                        missing_encryption = True
                        
                        # Check if any encryption keyword exists in the resource definition
                        for keyword in keywords:
                            if keyword in full_content[resource_start:resource_start+1000]:  # Check next 1000 chars
                                missing_encryption = False
                                break
                        
                        if missing_encryption:
                            # Find the resource name
                            resource_lines = full_content[resource_start:resource_start+100].split('\n')
                            resource_name = resource_lines[0].strip().rstrip(':')
                            
                            # Find line number
                            line_num = 1
                            for i, line in enumerate(content):
                                if resource_name in line and i > 0:
                                    line_num = i + 1
                                    break
                            
                            print_error(f"Missing encryption settings for {resource_type} ({resource_name}) in {template_file}")
                            file_issues.append((line_num, resource_type, resource_name))
                
            if file_issues:
                issues[template_file] = file_issues
                
        except Exception as e:
            print_error(f"Error analyzing {template_file}: {str(e)}")
    
    if not issues:
        print_success("All resources have proper encryption settings")
        return True, {}
    else:
        print_warning("Recommendation: Enable encryption for all sensitive resources")
        return False, issues

def fix_wildcard_permissions(issues, dry_run=True):
    """Fix wildcard permissions in IAM policies"""
    print_section("Fixing wildcard permissions in IAM policies")
    
    for file_path, lines in issues.items():
        if dry_run:
            print_warning(f"[DRY RUN] Would fix wildcard permissions in {file_path}:")
        else:
            backup_path = backup_file(file_path)
            print(f"Created backup at {backup_path}")
            print(f"Fixing wildcard permissions in {file_path}:")
        
        with open(file_path, 'r') as f:
            content = f.readlines()
        
        modified = False
        
        for line_num, line, context in lines:
            if "Resource" in line and '"*"' in line:
                # Fixed version with specific resource ARNs
                indent = len(line) - len(line.lstrip())
                fixed_line = ' ' * indent + 'Resource: !Sub "arn:aws:service:${AWS::Region}:${AWS::AccountId}:resource/*"\n'
                
                if dry_run:
                    print(f"  Line {line_num}: {line.strip()} -> {fixed_line.strip()}")
                else:
                    content[line_num-1] = fixed_line
                    modified = True
                    print(f"  Fixed line {line_num}")
        
        if modified and not dry_run:
            with open(file_path, 'w') as f:
                f.writelines(content)
            print_success(f"Fixed wildcard permissions in {file_path}")

def fix_security_group_rules(issues, dry_run=True):
    """Fix overly permissive security group rules"""
    print_section("Fixing overly permissive security group rules")
    
    for file_path, lines in issues.items():
        if dry_run:
            print_warning(f"[DRY RUN] Would fix security group rules in {file_path}:")
        else:
            backup_path = backup_file(file_path)
            print(f"Created backup at {backup_path}")
            print(f"Fixing security group rules in {file_path}:")
        
        with open(file_path, 'r') as f:
            content = f.readlines()
        
        modified = False
        
        for line_num, line, ports in lines:
            if "CidrIp" in line and "0.0.0.0/0" in line:
                # Fixed version with more restrictive CIDR
                indent = len(line) - len(line.lstrip())
                fixed_line = ' ' * indent + 'CidrIp: 10.0.0.0/8  # Restrict to private network\n'
                
                if dry_run:
                    print(f"  Line {line_num}: {line.strip()} -> {fixed_line.strip()}")
                else:
                    content[line_num-1] = fixed_line
                    modified = True
                    print(f"  Fixed line {line_num}")
        
        if modified and not dry_run:
            with open(file_path, 'w') as f:
                f.writelines(content)
            print_success(f"Fixed security group rules in {file_path}")

def fix_encryption_settings(issues, dry_run=True):
    """Fix missing encryption settings"""
    print_section("Fixing missing encryption settings")
    
    for file_path, resources in issues.items():
        if dry_run:
            print_warning(f"[DRY RUN] Would fix encryption settings in {file_path}:")
        else:
            backup_path = backup_file(file_path)
            print(f"Created backup at {backup_path}")
            print(f"Fixing encryption settings in {file_path}:")
        
        with open(file_path, 'r') as f:
            content = f.readlines()
        
        with open(file_path, 'r') as f:
            full_content = f.read()
        
        modified = False
        
        for line_num, resource_type, resource_name in resources:
            if resource_type == "AWS::S3::Bucket":
                # Add encryption to S3 bucket
                if dry_run:
                    print(f"  Would add BucketEncryption to {resource_name}")
                else:
                    # Find the position to insert the encryption config
                    pattern = f"{resource_name}:\\s*\\n\\s*Type: AWS::S3::Bucket\\s*\\n\\s*Properties:"
                    match = re.search(pattern, full_content)
                    if match:
                        # Find where to insert the encryption config
                        props_pos = match.end()
                        indent_match = re.search(r'(\s+)Properties:', full_content[match.start():props_pos])
                        if indent_match:
                            indent = indent_match.group(1)
                            encryption_config = f"\n{indent}  BucketEncryption:\n{indent}    ServerSideEncryptionConfiguration:\n{indent}      - ServerSideEncryptionByDefault:\n{indent}          SSEAlgorithm: AES256\n"
                            
                            # Find the line number
                            props_line_num = full_content[:props_pos].count('\n')
                            
                            # Insert encryption config after Properties line
                            content.insert(props_line_num + 1, encryption_config)
                            modified = True
                            print(f"  Added encryption to {resource_name}")
            
            elif resource_type == "AWS::SNS::Topic":
                # Add KMS encryption to SNS topic
                if dry_run:
                    print(f"  Would add KmsMasterKeyId to {resource_name}")
                else:
                    # Find the position to insert the encryption config
                    pattern = f"{resource_name}:\\s*\\n\\s*Type: AWS::SNS::Topic\\s*\\n\\s*Properties:"
                    match = re.search(pattern, full_content)
                    if match:
                        # Find where to insert the encryption config
                        props_pos = match.end()
                        indent_match = re.search(r'(\s+)Properties:', full_content[match.start():props_pos])
                        if indent_match:
                            indent = indent_match.group(1)
                            encryption_config = f"\n{indent}  KmsMasterKeyId: !GetAtt KMSKey.Arn\n"
                            
                            # Find the line number
                            props_line_num = full_content[:props_pos].count('\n')
                            
                            # Insert encryption config after Properties line
                            content.insert(props_line_num + 1, encryption_config)
                            
                            # Check if we need to add KMS key resource
                            if "AWS::KMS::Key" not in full_content:
                                kms_key_resource = f"""
  KMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: KMS key for encryption
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'
      EnableKeyRotation: true
"""
                                # Add KMS key at the end of the Resources section
                                resources_end_match = re.search(r'Resources:\s*\n', full_content)
                                if resources_end_match:
                                    resources_end_line = full_content[:resources_end_match.end()].count('\n')
                                    content.insert(resources_end_line + 1, kms_key_resource)
                            
                            modified = True
                            print(f"  Added KMS encryption to {resource_name}")
            
            elif resource_type == "AWS::Logs::LogGroup":
                # Add KMS encryption to CloudWatch Log Group
                if dry_run:
                    print(f"  Would add KmsKeyId to {resource_name}")
                else:
                    # Find the position to insert the encryption config
                    pattern = f"{resource_name}:\\s*\\n\\s*Type: AWS::Logs::LogGroup\\s*\\n\\s*Properties:"
                    match = re.search(pattern, full_content)
                    if match:
                        # Find where to insert the encryption config
                        props_pos = match.end()
                        indent_match = re.search(r'(\s+)Properties:', full_content[match.start():props_pos])
                        if indent_match:
                            indent = indent_match.group(1)
                            encryption_config = f"\n{indent}  KmsKeyId: !GetAtt LogsKMSKey.Arn\n"
                            
                            # Find the line number
                            props_line_num = full_content[:props_pos].count('\n')
                            
                            # Insert encryption config after Properties line
                            content.insert(props_line_num + 1, encryption_config)
                            
                            # Check if we need to add KMS key resource
                            if "AWS::KMS::Key" not in full_content:
                                kms_key_resource = f"""
  LogsKMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: KMS key for CloudWatch Logs encryption
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'
          - Sid: Allow CloudWatch Logs
            Effect: Allow
            Principal:
              Service: !Sub 'logs.${AWS::Region}.amazonaws.com'
            Action:
              - 'kms:Encrypt*'
              - 'kms:Decrypt*'
              - 'kms:ReEncrypt*'
              - 'kms:GenerateDataKey*'
              - 'kms:Describe*'
            Resource: '*'
      EnableKeyRotation: true
"""
                                # Add KMS key at the end of the Resources section
                                resources_end_match = re.search(r'Resources:\s*\n', full_content)
                                if resources_end_match:
                                    resources_end_line = full_content[:resources_end_match.end()].count('\n')
                                    content.insert(resources_end_line + 1, kms_key_resource)
                            
                            modified = True
                            print(f"  Added KMS encryption to {resource_name}")
            
            elif resource_type == "AWS::Lambda::Function":
                # Add KMS encryption for Lambda environment variables
                if dry_run:
                    print(f"  Would add KmsKeyArn to {resource_name}")
                else:
                    # Find the position to insert the encryption config
                    env_pattern = f"{resource_name}:[\\s\\S]*?Environment:"
                    env_match = re.search(env_pattern, full_content)
                    if env_match:
                        # Add KMS key to existing environment section
                        pattern = f"(\\s+Environment:[\\s\\S]*?)(\\s+[a-zA-Z]+:)"
                        replacement = f"\\1    KmsKeyArn: !GetAtt LambdaKMSKey.Arn\n\\2"
                        updated_content = re.sub(pattern, replacement, full_content)
                        
                        # Write updated content
                        if updated_content != full_content:
                            # Check if we need to add KMS key resource
                            if "AWS::KMS::Key" not in full_content:
                                kms_key_resource = f"""
  LambdaKMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: KMS key for Lambda environment variables
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'
          - Sid: Allow Lambda Service
            Effect: Allow
            Principal:
              Service: 'lambda.amazonaws.com'
            Action:
              - 'kms:Encrypt*'
              - 'kms:Decrypt*'
              - 'kms:ReEncrypt*'
              - 'kms:GenerateDataKey*'
              - 'kms:Describe*'
            Resource: '*'
      EnableKeyRotation: true
"""
                                # Add KMS key resource
                                with open(file_path, 'w') as f:
                                    f.write(updated_content.replace("Resources:", f"Resources:\n{kms_key_resource}"))
                            else:
                                with open(file_path, 'w') as f:
                                    f.write(updated_content)
                            
                            modified = True
                            print(f"  Added KMS encryption to Lambda environment variables for {resource_name}")
                            
                            # Skip further processing since we already wrote the file
                            continue
        
        if modified and not dry_run:
            with open(file_path, 'w') as f:
                f.writelines(content)
            print_success(f"Fixed encryption settings in {file_path}")

def main():
    parser = argparse.ArgumentParser(description="CloudFormation Security Scanner and Fixer")
    parser.add_argument('--fix', action='store_true', help='Fix security issues automatically')
    parser.add_argument('--scan-only', action='store_true', help='Only scan, do not fix issues (default)')
    parser.add_argument('--check-secrets', action='store_true', help='Check for hardcoded secrets')
    parser.add_argument('--check-iam', action='store_true', help='Check for wildcard IAM permissions')
    parser.add_argument('--check-sg', action='store_true', help='Check for overly permissive security groups')
    parser.add_argument('--check-encryption', action='store_true', help='Check for missing encryption')
    args = parser.parse_args()
    
    # If no specific checks are selected, run all checks
    run_all = not (args.check_secrets or args.check_iam or args.check_sg or args.check_encryption)
    fix_mode = args.fix
    
    print_header("CloudFormation Security Scanner")
    
    # Dictionary to track results and issues
    results = {}
    issues = {}
    failures = 0
    
    # Run secret detection
    if run_all or args.check_secrets:
        secrets_passed, secrets_issues = run_detect_secrets()
        results["Secret Detection"] = secrets_passed
        if not secrets_passed:
            failures += 1
            issues["secrets"] = secrets_issues
    
    # Check for wildcard IAM permissions
    if run_all or args.check_iam:
        iam_passed, iam_issues = check_wildcard_permissions()
        results["Wildcard IAM Permissions Check"] = iam_passed
        if not iam_passed:
            failures += 1
            issues["iam"] = iam_issues
    
    # Check security group rules
    if run_all or args.check_sg:
        sg_passed, sg_issues = check_security_group_rules()
        results["Security Group Rules Check"] = sg_passed
        if not sg_passed:
            failures += 1
            issues["sg"] = sg_issues
    
    # Check encryption settings
    if run_all or args.check_encryption:
        encryption_passed, encryption_issues = check_encryption_settings()
        results["Resource Encryption Check"] = encryption_passed
        if not encryption_passed:
            failures += 1
            issues["encryption"] = encryption_issues
    
    # Print summary
    print_header("Security Scan Summary")
    
    for check, passed in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.NC}" if passed else f"{Colors.RED}✗ FAIL{Colors.NC}"
        print(f"{check.ljust(30)}: {status}")
    
    # Fix security issues if requested
    if fix_mode and failures > 0:
        print_header("Fixing Security Issues")
        
        # Fix IAM wildcard permissions
        if "iam" in issues and issues["iam"]:
            fix_wildcard_permissions(issues["iam"], dry_run=False)
        
        # Fix security group rules
        if "sg" in issues and issues["sg"]:
            fix_security_group_rules(issues["sg"], dry_run=False)
        
        # Fix encryption settings
        if "encryption" in issues and issues["encryption"]:
            fix_encryption_settings(issues["encryption"], dry_run=False)
        
        # We can't automatically fix secrets - just provide guidance
        if "secrets" in issues and issues["secrets"]:
            print_section("Manual Fixes Required for Secrets")
            print_warning("Hardcoded secrets must be manually replaced with AWS Secrets Manager or parameter references")
        
        print_success("\nSecurity fixes applied. Run scan again to verify fixes.")
    elif failures > 0 and not fix_mode:
        print_header("Fix Recommendations")
        
        # Show IAM wildcard permission fixes
        if "iam" in issues and issues["iam"]:
            fix_wildcard_permissions(issues["iam"], dry_run=True)
        
        # Show security group rule fixes
        if "sg" in issues and issues["sg"]:
            fix_security_group_rules(issues["sg"], dry_run=True)
        
        # Show encryption setting fixes
        if "encryption" in issues and issues["encryption"]:
            fix_encryption_settings(issues["encryption"], dry_run=True)
        
        print_warning("\nRun with --fix to automatically apply these fixes")
    
    # Final summary
    if failures == 0:
        print_success("\nAll security checks passed! Your CloudFormation templates are secure.")
        return 0
    else:
        print_error(f"\n{failures} security check(s) failed. Please address the issues before pushing to GitHub.")
        return 1

if __name__ == "__main__":
    sys.exit(main())