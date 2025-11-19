#!/usr/bin/env python
import os
import subprocess
import sys
import json
import time
import platform
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_section(message):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{message}{Colors.ENDC}\n")

def print_success(message):
    print(f"{Colors.GREEN}{message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}{message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}{message}{Colors.ENDC}")

def run_command(command, shell=False):
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

def check_tool_installed(tool_name, check_command):
    print_section(f"Checking if {tool_name} is installed...")
    try:
        return_code, stdout, stderr = run_command(check_command, shell=True)
        if return_code != 0:
            print_warning(f"{tool_name} is not installed or not in PATH.")
            return False
        print_success(f"{tool_name} is installed: {stdout.strip()}")
        return True
    except Exception as e:
        print_warning(f"Error checking {tool_name}: {str(e)}")
        return False

def install_tool(tool_name, install_command):
    print_section(f"Installing {tool_name}...")
    return_code, stdout, stderr = run_command(install_command, shell=True)
    if return_code != 0:
        print_error(f"Failed to install {tool_name}:\n{stderr}")
        return False
    print_success(f"{tool_name} installed successfully")
    return True

def create_basic_guard_rules():
    print_section("Creating CloudFormation Guard rules file...")
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
"""
    
    with open("security-rules.guard", "w") as f:
        f.write(rules_content)
    print_success("Created security-rules.guard")
    return True

def run_cfn_lint():
    print_section("Running CloudFormation Linter (cfn-lint)...")
    # Fix: Don't use shell=True when passing a list, and change command format
    if platform.system() == "Windows":
        return_code, stdout, stderr = run_command("cfn-lint templates\\*.yaml", shell=True)
    else:
        return_code, stdout, stderr = run_command("cfn-lint templates/*.yaml", shell=True)
    if return_code != 0:
        print_error(f"CloudFormation Linter found issues:\n{stdout}\n{stderr}")
        return False
    print_success("CloudFormation Linter completed successfully")
    return True

def run_checkov():
    print_section("Running Checkov Security Scanner...")
    if platform.system() == "Windows":
        return_code, stdout, stderr = run_command("checkov -d templates\ --framework cloudformation", shell=True)
    else:
        return_code, stdout, stderr = run_command("checkov -d templates/ --framework cloudformation", shell=True)
    
    print(stdout)
    if stderr:
        print_warning(f"Checkov warnings:\n{stderr}")
    
    if return_code != 0:
        print_warning("Checkov found potential security issues.")
        return False
    
    print_success("Checkov scan completed successfully")
    return True

def run_cfn_guard():
    print_section("Running CloudFormation Guard...")

    # First check if we have rules file
    if not os.path.exists("security-rules.guard"):
        create_basic_guard_rules()

    # Get all template files
    template_files = list(Path("templates").glob("*.yaml"))

    all_pass = True
    for template in template_files:
        print(f"Scanning {template}...")
        if platform.system() == "Windows":
            command = f"cfn-guard validate -r security-rules.guard -d {template} --show-summary all"
        else:
            command = f"cfn-guard validate -r security-rules.guard -d {template} --show-summary all"
        return_code, stdout, stderr = run_command(command, shell=True)
        
        print(stdout)
        if stderr:
            print_warning(stderr)
        
        if return_code != 0:
            print_warning(f"CloudFormation Guard found issues in {template}")
            all_pass = False
    
    if all_pass:
        print_success("CloudFormation Guard completed successfully")
    else:
        print_warning("CloudFormation Guard found issues in some templates")
    
    return all_pass

def run_detect_secrets():
    print_section("Running detect-secrets for secret scanning...")
    if platform.system() == "Windows":
        return_code, stdout, stderr = run_command("detect-secrets scan > secrets-scan-results.json", shell=True)
    else:
        return_code, stdout, stderr = run_command("detect-secrets scan > secrets-scan-results.json", shell=True)
    
    try:
        with open("secrets-scan-results.json", "r") as f:
            results = json.load(f)
            
        if results.get("results") and len(results["results"]) > 0:
            print_error("Potential secrets found in repository:")
            print(json.dumps(results["results"], indent=2))
            return False
        else:
            print_success("No secrets detected in codebase")
            return True
            
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print_error(f"Error reading detect-secrets results: {str(e)}")
        return False

def run_owasp_dependency_check():
    print_section("Running OWASP Dependency Check...")

    if platform.system() == "Windows":
        command = "dependency-check --project CloudFormation-Project --scan templates\ --enableExperimental --out reports --format HTML"
    else:
        command = "dependency-check --project CloudFormation-Project --scan templates/ --enableExperimental --out reports --format HTML"

    return_code, stdout, stderr = run_command(command, shell=True)
    
    print(stdout)
    if stderr:
        print_warning(stderr)
    
    if return_code != 0:
        print_warning("OWASP Dependency Check found issues")
        return False
    
    print_success("OWASP Dependency Check completed successfully")
    return True

def run_cloudsploit():
    print_section("Running CloudSploit...")
    print_warning("CloudSploit requires AWS credentials and cannot be run without them.")
    print_warning("This scan is skipped in local testing.")
    return True


def check_install_prerequisites():
    installed_tools = {}
    
    # Check for pip
    installed_tools["pip"] = check_tool_installed("pip", "pip --version")
    
    # Check for Python tools
    installed_tools["cfn-lint"] = check_tool_installed("cfn-lint", "cfn-lint --version")
    installed_tools["checkov"] = check_tool_installed("checkov", "checkov --version")
    installed_tools["detect-secrets"] = check_tool_installed("detect-secrets", "detect-secrets --version")
    
    # Check for Rust/Cargo tools
    installed_tools["cargo"] = check_tool_installed("cargo", "cargo --version")
    installed_tools["cfn-guard"] = check_tool_installed("cfn-guard", "cfn-guard --version")
    
    # Check for Java tools
    installed_tools["dependency-check"] = check_tool_installed("OWASP Dependency Check", "dependency-check --version")
    
    # Install missing tools
    missing_tools = {k: v for k, v in installed_tools.items() if not v}
    
    if missing_tools:
        print_section("Installing missing tools...")
        
        if not installed_tools["pip"]:
            print_error("pip is not installed. Please install pip first.")
            return False
            
        # Install Python tools
        if not installed_tools["cfn-lint"]:
            install_tool("cfn-lint", "pip install cfnlint")
            
        if not installed_tools["checkov"]:
            install_tool("checkov", "pip install checkov")
            
        if not installed_tools["detect-secrets"]:
            install_tool("detect-secrets", "pip install detect-secrets==1.4.0")
        
        # Install Rust tools if Cargo is available
        if installed_tools["cargo"] and not installed_tools["cfn-guard"]:
            install_tool("cfn-guard", "cargo install cfn-guard")
            
        # OWASP Dependency Check needs special handling - it's a Java tool
        if not installed_tools["dependency-check"]:
            print_warning("OWASP Dependency Check not found.")
            print_warning("This tool requires Java and is more complex to install locally.")
            print_warning("You can skip this check or install it manually from: https://owasp.org/www-project-dependency-check/")
        
    return True

def main():
    print_header("CloudFormation Security Scanner")
    
    # Check and install prerequisites
    if not check_install_prerequisites():
        print_error("Failed to set up prerequisites. Exiting.")
        return 1
        
    results = {}
    
    # Run all security scans
    results["cfn-lint"] = run_cfn_lint()
    results["checkov"] = run_checkov()
    
    # Only run if installed
    try:
        result = run_command(["cfn-guard", "--version"], shell=True)
        if result[0] == 0:
            results["cfn-guard"] = run_cfn_guard()
    except:
        print_warning("Skipping cfn-guard (not installed)")
        
    try:
        result = run_command(["detect-secrets", "--version"], shell=True)
        if result[0] == 0:
            results["detect-secrets"] = run_detect_secrets()
    except:
        print_warning("Skipping detect-secrets (not installed)")
        
    try:
        result = run_command(["dependency-check", "--version"], shell=True)
        if result[0] == 0:
            results["owasp"] = run_owasp_dependency_check()
    except:
        print_warning("Skipping OWASP Dependency Check (not installed)")
    
    # Print summary
    print_header("Security Scan Summary")
    for tool, passed in results.items():
        status = f"{Colors.GREEN}PASS{Colors.ENDC}" if passed else f"{Colors.RED}FAIL{Colors.ENDC}"
        print(f"{tool:<20}: {status}")
        
    # Final result - did all scans pass?
    if all(results.values()):
        print_success("\nAll security checks passed! Safe to commit and push.")
        return 0
    else:
        print_error("\nSome security checks failed. Please fix the issues before committing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())