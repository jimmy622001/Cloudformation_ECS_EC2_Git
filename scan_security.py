#!/usr/bin/env python
import os
import subprocess
import json
import sys
import glob
import platform
from pathlib import Path

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
                return False
            else:
                print_success("No secrets detected in CloudFormation templates")
                return True
        else:
            print_success("No secrets detected in repository")
            return True
            
    except json.JSONDecodeError as e:
        print_error(f"Error parsing detect-secrets output: {e}")
        return False

def run_checkov():
    """Run Checkov security scan on CloudFormation templates"""
    print_section("Running Checkov Security Scan")
    
    checkov_cmd = "checkov"
    
    # Check if checkov is installed
    return_code, stdout, stderr = run_command([checkov_cmd, "--version"], shell=True)
    if return_code != 0:
        print_warning("Checkov is not installed. Install with: pip install checkov")
        return False
    
    # Run Checkov on templates directory
    return_code, stdout, stderr = run_command([checkov_cmd, "-d", "templates", "--framework", "cloudformation"], shell=True)
    
    print(stdout)
    
    if return_code != 0:
        print_error("Checkov found security issues")
        return False
    else:
        print_success("Checkov scan completed with no issues")
        return True

def check_wildcard_permissions():
    """Check for wildcard permissions in IAM policies"""
    print_section("Checking for wildcard permissions in IAM policies")
    
    template_files = glob.glob("templates/*.yaml")
    issues_found = False
    
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
                for line_num, line, context in resource_lines:
                    print(f"  Line {line_num}: {line}")
                issues_found = True
                
        except Exception as e:
            print_error(f"Error analyzing {template_file}: {str(e)}")
    
    if not issues_found:
        print_success("No wildcard permissions found in IAM policies")
        return True
    else:
        print_warning("Recommendation: Replace wildcard permissions with specific resource ARNs")
        return False

def check_security_group_rules():
    """Check for overly permissive security group rules"""
    print_section("Checking for overly permissive security group rules")
    
    template_files = glob.glob("templates/*.yaml")
    issues_found = False
    
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
                for line_num, line, ports in security_group_issues:
                    print(f"  Line {line_num}: {line}")
                    print(f"    Opens {', '.join(ports)} to the world (0.0.0.0/0)")
                issues_found = True
                
        except Exception as e:
            print_error(f"Error analyzing {template_file}: {str(e)}")
    
    if not issues_found:
        print_success("No overly permissive security group rules found")
        return True
    else:
        print_warning("Recommendation: Restrict security group rules to specific IP ranges")
        return False

def check_encryption_settings():
    """Check for missing encryption in resources"""
    print_section("Checking for missing encryption settings")
    
    template_files = glob.glob("templates/*.yaml")
    issues_found = False
    
    encryption_keywords = {
        "AWS::S3::Bucket": ["BucketEncryption", "ServerSideEncryptionConfiguration"],
        "AWS::RDS::DBInstance": ["StorageEncrypted", "true"],
        "AWS::SNS::Topic": ["KmsMasterKeyId"],
        "AWS::SQS::Queue": ["KmsMasterKeyId"],
        "AWS::Lambda::Function": ["KmsKeyArn"],
        "AWS::Logs::LogGroup": ["KmsKeyId"]
    }
    
    for template_file in template_files:
        try:
            with open(template_file, 'r') as f:
                content = ''.join(f.readlines())
                
            for resource_type, keywords in encryption_keywords.items():
                if resource_type in content:
                    missing_encryption = True
                    for keyword in keywords:
                        if keyword in content:
                            missing_encryption = False
                            break
                    
                    if missing_encryption:
                        print_error(f"Missing encryption settings for {resource_type} in {template_file}")
                        issues_found = True
                
        except Exception as e:
            print_error(f"Error analyzing {template_file}: {str(e)}")
    
    if not issues_found:
        print_success("All resources have proper encryption settings")
        return True
    else:
        print_warning("Recommendation: Enable encryption for all sensitive resources")
        return False

def main():
    print_header("CloudFormation Security Scanner")
    
    results = {}
    failures = 0
    
    # Run secret detection
    results["Secret Detection"] = run_detect_secrets()
    if not results["Secret Detection"]:
        failures += 1
    
    # Run custom policy checks
    results["Wildcard IAM Permissions Check"] = check_wildcard_permissions()
    if not results["Wildcard IAM Permissions Check"]:
        failures += 1
    
    # Run security group checks
    results["Security Group Rules Check"] = check_security_group_rules()
    if not results["Security Group Rules Check"]:
        failures += 1
    
    # Run encryption checks
    results["Resource Encryption Check"] = check_encryption_settings()
    if not results["Resource Encryption Check"]:
        failures += 1
    
    # Run Checkov if available
    try:
        results["Checkov Security Scan"] = run_checkov()
        if not results["Checkov Security Scan"]:
            failures += 1
    except:
        print_warning("Checkov scan failed to run")
    
    # Print summary
    print_header("Security Scan Summary")
    
    for check, passed in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.NC}" if passed else f"{Colors.RED}✗ FAIL{Colors.NC}"
        print(f"{check.ljust(30)}: {status}")
    
    # Final summary
    if failures == 0:
        print_success("\nAll security checks passed! Your CloudFormation templates are secure.")
        return 0
    else:
        print_error(f"\n{failures} security check(s) failed. Please address the issues before pushing to GitHub.")
        return 1

if __name__ == "__main__":
    sys.exit(main())