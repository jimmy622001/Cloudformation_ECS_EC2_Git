#!/usr/bin/env python
import os
import sys
import subprocess
import glob
import json
import platform
from pathlib import Path

# ANSI Colors for terminals that support it
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{message.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.END}\n")

def print_section(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{message}{Colors.END}\n")

def print_success(message):
    print(f"{Colors.GREEN}{message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}{message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}{message}{Colors.END}")

def run_command(command, shell=False):
    """Run a command and return its exit code, stdout and stderr"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=False,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def is_command_available(command):
    """Check if a command is available in PATH"""
    if platform.system() == 'Windows':
        # Windows requires .exe extension and "where" command
        try:
            result = subprocess.run(
                ['where', command],
                check=False,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    else:
        # Unix-like systems use "which" command
        try:
            result = subprocess.run(
                ['which', command],
                check=False,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False

def is_python_module_available(module_name):
    """Check if a Python module is available"""
    try:
        subprocess.run(
            [sys.executable, '-c', f"import {module_name}"],
            check=False,
            capture_output=True
        )
        return True
    except:
        return False

def run_checkov():
    """Run Checkov security scanner"""
    print_section("Running Checkov CloudFormation Security Scanner")
    
    if not is_command_available('checkov'):
        print_warning("Checkov is not installed. Install with: pip install checkov")
        return False
    
    # Get all CloudFormation template files
    template_files = glob.glob("templates/*.yaml")
    if not template_files:
        print_warning("No CloudFormation templates found in templates/ directory")
        return False
    
    # Run checkov
    cmd = ['checkov', '-d', 'templates', '--framework', 'cloudformation']
    return_code, stdout, stderr = run_command(cmd)
    
    print(stdout)
    if stderr:
        print_warning(stderr)
    
    if return_code != 0:
        print_error("Checkov found security issues")
        return False
    else:
        print_success("Checkov scan completed - No issues found")
        return True

def run_detect_secrets():
    """Run detect-secrets to find hardcoded secrets"""
    print_section("Running Secret Detection")
    
    if not is_command_available('detect-secrets'):
        print_warning("detect-secrets is not installed. Install with: pip install detect-secrets")
        return False
    
    # Run detect-secrets
    cmd = ['detect-secrets', 'scan']
    return_code, stdout, stderr = run_command(cmd)
    
    if stderr:
        print_warning(stderr)
    
    try:
        # Parse the results
        results = json.loads(stdout)
        
        if results.get("results") and len(results["results"]) > 0:
            print_error("Potential secrets found in repository!")
            print("-" * 70)
            
            # Count the secrets by file
            secrets_by_file = {}
            for filepath, secrets in results["results"].items():
                if filepath.startswith('templates/'):
                    secrets_by_file[filepath] = len(secrets)
            
            if secrets_by_file:
                # Print a summary of files with secrets
                print("Summary of CloudFormation template files with potential secrets:")
                for filepath, count in secrets_by_file.items():
                    print(f"  - {filepath}: {count} potential secrets")
                
                print("\nRecommendation: Review these files for hardcoded secrets and use AWS Secrets Manager instead")
                return False
            else:
                print_success("No secrets detected in CloudFormation templates")
                return True
        else:
            print_success("No secrets detected in CloudFormation templates")
            return True
            
    except json.JSONDecodeError as e:
        print_error(f"Error parsing detect-secrets output: {e}")
        return False

def run_cfnlint():
    """Run cfn-lint on CloudFormation templates"""
    print_section("Running CloudFormation Linter (cfn-lint)")
    
    has_cfnlint = False
    
    # Try different ways to run cfn-lint
    if is_command_available('cfn-lint'):
        has_cfnlint = True
        cmd = ['cfn-lint', 'templates/*.yaml']
    elif is_python_module_available('cfnlint'):
        has_cfnlint = True
        cmd = [sys.executable, '-m', 'cfnlint', 'templates/*.yaml']
    
    if not has_cfnlint:
        print_warning("cfn-lint is not installed. Install with: pip install cfn-lint")
        return False
    
    # Run cfn-lint
    return_code, stdout, stderr = run_command(cmd, shell=True)
    
    if stdout:
        print(stdout)
    if stderr:
        print_warning(stderr)
    
    if return_code != 0:
        print_error("cfn-lint found issues with the CloudFormation templates")
        return False
    else:
        print_success("cfn-lint validation passed - No issues found")
        return True

def create_cfnguard_rules():
    """Create CloudFormation Guard rules file"""
    rules_content = """# Basic Security Rules 
          
# Enforce encryption of S3 buckets
rule s3_encryption when resourceType == "AWS::S3::Bucket" {
  some Properties.BucketEncryption.ServerSideEncryptionConfiguration[*].ServerSideEncryptionByDefault.SSEAlgorithm == "AES256" or
  some Properties.BucketEncryption.ServerSideEncryptionConfiguration[*].ServerSideEncryptionByDefault.SSEAlgorithm == "aws:kms"
}
          
# Ensure S3 buckets block public access
rule s3_public_access_block when resourceType == "AWS::S3::Bucket" {
  Properties.PublicAccessBlockConfiguration.BlockPublicAcls == true
  Properties.PublicAccessBlockConfiguration.BlockPublicPolicy == true
  Properties.PublicAccessBlockConfiguration.IgnorePublicAcls == true
  Properties.PublicAccessBlockConfiguration.RestrictPublicBuckets == true
}
          
# Ensure RDS instances are encrypted
rule rds_encryption when resourceType == "AWS::RDS::DBInstance" {
  Properties.StorageEncrypted == true
}
          
# Ensure security groups don't allow unrestricted access
rule restrict_sg_ingress when resourceType == "AWS::EC2::SecurityGroup" {
  when some Properties.SecurityGroupIngress[*] {
    not (CidrIp == "0.0.0.0/0" and (FromPort == 0 or ToPort == 0 or IpProtocol == "-1"))
  }
}

# Ensure IAM roles don't have wild card permissions
rule iam_no_wildcards when resourceType == "AWS::IAM::Role" {
  when some Properties.Policies[*] {
    when some Properties.Policies[*].PolicyDocument.Statement[*] {
      when Properties.Policies[*].PolicyDocument.Statement[*].Effect == "Allow" {
        Properties.Policies[*].PolicyDocument.Statement[*].Resource != "*"
      }
    }
  }
}

# Ensure Lambda functions have environment variables encrypted
rule lambda_env_encryption when resourceType == "AWS::Lambda::Function" {
  when Properties.Environment exists {
    Properties.KmsKeyArn exists
  }
}

# Ensure Lambda functions have dead letter queues
rule lambda_dlq when resourceType == "AWS::Lambda::Function" {
  Properties.DeadLetterConfig exists
  Properties.DeadLetterConfig.TargetArn exists
}

# Ensure CloudWatch Log Groups are encrypted
rule cloudwatch_encrypted when resourceType == "AWS::Logs::LogGroup" {
  Properties.KmsKeyId exists
}

# Ensure no security groups allow ingress from 0.0.0.0/0 to port 22 (SSH)
rule no_public_ssh when resourceType == "AWS::EC2::SecurityGroup" {
  when some Properties.SecurityGroupIngress[*] {
    not (CidrIp == "0.0.0.0/0" and FromPort == 22 and ToPort == 22)
  }
}

# Ensure SNS topics are encrypted
rule sns_encryption when resourceType == "AWS::SNS::Topic" {
  Properties.KmsMasterKeyId exists
}
"""
    
    with open("security-rules.guard", "w") as f:
        f.write(rules_content)
    
    print_success("Created CloudFormation Guard rules file: security-rules.guard")

def run_cfnguard():
    """Run CloudFormation Guard on templates"""
    print_section("Running CloudFormation Guard Security Checks")
    
    if not is_command_available('cfn-guard'):
        print_warning("CloudFormation Guard is not installed.")
        print_warning("  Install instructions: https://github.com/aws-cloudformation/cloudformation-guard")
        return False
    
    # Create rules file if it doesn't exist
    if not os.path.exists("security-rules.guard"):
        create_cfnguard_rules()
    
    # Get all template files
    template_files = glob.glob("templates/*.yaml")
    if not template_files:
        print_warning("No CloudFormation templates found in templates/ directory")
        return False
    
    all_passed = True
    for template in template_files:
        print(f"Scanning {template} with cfn-guard...")
        cmd = ['cfn-guard', 'validate', '-r', 'security-rules.guard', '-d', template, '--show-summary', 'all']
        return_code, stdout, stderr = run_command(cmd)
        
        print(stdout)
        if stderr:
            print_warning(stderr)
        
        if return_code != 0:
            print_error(f"CloudFormation Guard found issues in {template}")
            all_passed = False
    
    if all_passed:
        print_success("CloudFormation Guard security checks passed - No issues found")
    else:
        print_error("CloudFormation Guard found security issues")
    
    return all_passed

def main():
    print_header("CloudFormation Security Scanner")
    
    # Dictionary to track results
    results = {}
    failures = 0
    
    # Run Checkov
    results['Checkov Security Scan'] = run_checkov()
    if not results['Checkov Security Scan']:
        failures += 1
    
    # Run detect-secrets
    results['Secret Detection'] = run_detect_secrets()
    if not results['Secret Detection']:
        failures += 1
    
    # Run cfn-lint
    results['CloudFormation Linter'] = run_cfnlint()
    if not results['CloudFormation Linter']:
        failures += 1
    
    # Run CloudFormation Guard if available
    if is_command_available('cfn-guard'):
        results['CloudFormation Guard'] = run_cfnguard()
        if not results['CloudFormation Guard']:
            failures += 1
    
    # Print summary
    print_header("Security Scan Summary")
    
    for check, passed in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{check.ljust(30)}: {status}")
    
    # Final assessment
    if failures == 0:
        print_success("\nAll security checks passed! Your CloudFormation templates are ready to commit.")
        return 0
    else:
        print_error(f"\n{failures} security checks failed. Please fix the issues before committing your code.")
        return 1

if __name__ == "__main__":
    sys.exit(main())