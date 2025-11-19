#!/usr/bin/env python
"""
CloudFormation Security Issue Fixer
Uses regex patterns to fix common security issues in CloudFormation templates
"""

import os
import re
import sys
import argparse
from pathlib import Path

# Define templates to fix
TEMPLATES = [
    "templates/dr-lambda.yaml",
    "templates/dr-pilot-light.yaml", 
    "templates/database.yaml",
    "templates/monitoring.yaml", 
    "templates/subnet-template.yaml"
]

# Define colors for output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.END}\n")

def read_file(file_path):
    """Read a file and return its contents as string"""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"{Colors.FAIL}Error reading file {file_path}: {e}{Colors.END}")
        return None

def write_file(file_path, content):
    """Write content to a file"""
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"{Colors.GREEN}Successfully updated {file_path}{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.FAIL}Error writing to file {file_path}: {e}{Colors.END}")
        return False

def fix_kms_key_wildcard_policy(content):
    """Fix KMS key policies with wildcard actions"""
    # Find KMS key resources with wildcard actions
    original_content = content
    
    # Pattern to find KMS key policies with "*" action
    pattern = r'(Type:\s*AWS::KMS::Key[^}]*?KeyPolicy:[^}]*?Action:\s*)(["\'])?\*(["\'])?'
    
    if re.search(pattern, content, re.DOTALL):
        print(f"{Colors.BLUE}Found and fixing wildcard KMS key policies{Colors.END}")
        
        # Replace with specific actions
        replacement = r'\1[\2kms:Encrypt\3, \2kms:Decrypt\3, \2kms:ReEncrypt*\3, \2kms:GenerateDataKey*\3, \2kms:DescribeKey\3]'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Pattern for list format with "*" in it
    list_pattern = r'(Type:\s*AWS::KMS::Key[^}]*?KeyPolicy:[^}]*?Action:\s*\[[^\]]*?)(["\'])?\*(["\'])?([^\]]*?\])'
    
    if re.search(list_pattern, content, re.DOTALL):
        print(f"{Colors.BLUE}Found and fixing wildcard KMS key policies in list format{Colors.END}")
        
        # Replace "*" with specific actions in list
        list_replacement = r'\1\2kms:Encrypt\3, \2kms:Decrypt\3, \2kms:ReEncrypt*\3, \2kms:GenerateDataKey*\3, \2kms:DescribeKey\3\4'
        content = re.sub(list_pattern, list_replacement, content, flags=re.DOTALL)
    
    return content != original_content, content

def fix_wildcard_resources_in_roles(content):
    """Fix IAM policies with wildcard resources for specific services"""
    original_content = content
    
    # Pattern to find autoscaling:DescribeAutoScalingGroups with "*" resources
    pattern = r'(Action:.*?["\']autoscaling:DescribeAutoScalingGroups["\'].*?Resource:)(\s*["\'])?\*(["\'])?'
    
    if re.search(pattern, content, re.DOTALL):
        print(f"{Colors.BLUE}Found and fixing wildcard resources for autoscaling:DescribeAutoScalingGroups{Colors.END}")
        
        # Replace with specific ARN pattern
        replacement = r'\1 !Sub "arn:aws:autoscaling:${AWS::Region}:${AWS::AccountId}:autoScalingGroup:*:autoScalingGroupName/*"'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Add more patterns for other services as needed
    
    return content != original_content, content

def fix_rds_password_no_echo(content):
    """Add NoEcho to password parameters"""
    original_content = content
    
    # Pattern to find password parameters without NoEcho
    patterns = [
        r'(Parameters:[^}]*?)(\s+)(Password|DBPassword|MasterUserPassword):(.*?)Type:(.*?)(?!.*?NoEcho)',
        r'(Parameters:[^}]*?)(\s+)(DBMasterPassword|MasterPassword|AdminPassword):(.*?)Type:(.*?)(?!.*?NoEcho)'
    ]
    
    for pattern in patterns:
        if re.search(pattern, content, re.DOTALL):
            print(f"{Colors.BLUE}Found and adding NoEcho to password parameters{Colors.END}")
            
            # Add NoEcho: true to the parameter definition
            replacement = r'\1\2\3:\4Type:\5\2  NoEcho: true'
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    return content != original_content, content

def fix_security_groups_open_to_world(content):
    """Fix security groups with ingress rules open to 0.0.0.0/0"""
    original_content = content
    
    # Pattern to find security group ingress rules with 0.0.0.0/0 for non-HTTP/HTTPS ports
    pattern = r'(Type:\s*AWS::EC2::SecurityGroup[^}]*?SecurityGroupIngress:[^}]*?CidrIp:\s*)(["\'])?0\.0\.0\.0/0(["\'])?([^}]*?)(FromPort:\s*)(\d+)([^}]*?)(ToPort:\s*)(\d+)'
    
    def replace_non_web_ports(match):
        full_match = match.group(0)
        from_port = int(match.group(6))
        to_port = int(match.group(9))
        prefix = match.group(1)
        quote = match.group(2) or ""
        
        # Leave HTTP/HTTPS ports open but restrict others
        if (from_port == 80 and to_port == 80) or (from_port == 443 and to_port == 443):
            return full_match
        else:
            print(f"{Colors.BLUE}Found and restricting security group rule for port {from_port}-{to_port}{Colors.END}")
            return f"{prefix}{quote}10.0.0.0/8{quote}{match.group(4)}{match.group(5)}{match.group(6)}{match.group(7)}{match.group(8)}{match.group(9)}"
    
    # Apply the replacement with a callback function
    content = re.sub(pattern, replace_non_web_ports, content, flags=re.DOTALL)
    
    return content != original_content, content

def fix_embedded_parameters_in_importvalue(content):
    """Fix embedded parameters in Fn::ImportValue"""
    original_content = content
    
    # Pattern to find Fn::ImportValue with ${...} embedded parameters
    pattern = r'(Fn::ImportValue:\s*)(["\'])([^"\']*?\${[^}]+?}[^"\']*?)(["\'])'
    
    if re.search(pattern, content, re.DOTALL):
        print(f"{Colors.BLUE}Found and fixing embedded parameters in Fn::ImportValue{Colors.END}")
        
        # Replace with properly formatted !Sub or Fn::Sub
        replacement = r'\1\n      Fn::Sub: \2\3\4'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    return content != original_content, content

def process_template(file_path, dry_run=False):
    """Process a single template file"""
    print_header(f"PROCESSING {os.path.basename(file_path)}")
    
    # Read the template
    content = read_file(file_path)
    if not content:
        return False
    
    # Apply fixes
    fixed = False
    
    # Fix KMS key wildcard policies
    kms_fixed, content = fix_kms_key_wildcard_policy(content)
    fixed = fixed or kms_fixed
    
    # Fix wildcard resources in IAM roles
    wildcard_fixed, content = fix_wildcard_resources_in_roles(content)
    fixed = fixed or wildcard_fixed
    
    # Fix password parameters without NoEcho
    password_fixed, content = fix_rds_password_no_echo(content)
    fixed = fixed or password_fixed
    
    # Fix security groups open to the world
    sg_fixed, content = fix_security_groups_open_to_world(content)
    fixed = fixed or sg_fixed
    
    # Fix embedded parameters in Fn::ImportValue
    import_fixed, content = fix_embedded_parameters_in_importvalue(content)
    fixed = fixed or import_fixed
    
    # Save the changes
    if fixed:
        if not dry_run:
            write_file(file_path, content)
        else:
            print(f"{Colors.BLUE}Changes would be made to {file_path} (dry run){Colors.END}")
    else:
        print(f"{Colors.GREEN}No matching issues found in {file_path}{Colors.END}")
    
    return fixed

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Fix security issues in CloudFormation templates')
    parser.add_argument('--templates', nargs='+', default=TEMPLATES,
                        help='CloudFormation template files to fix')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be changed without modifying files')
    args = parser.parse_args()
    
    # Validate templates exist
    templates = []
    for template_path in args.templates:
        if not os.path.exists(template_path):
            print(f"{Colors.FAIL}Template not found: {template_path}{Colors.END}")
            continue
        templates.append(template_path)
    
    if not templates:
        print(f"{Colors.FAIL}No valid templates found to process{Colors.END}")
        return 1
    
    print_header("CLOUDFORMATION SECURITY AUTO-FIX TOOL")
    print(f"Processing the following templates:")
    for template_path in templates:
        print(f"  - {template_path}")
    
    if args.dry_run:
        print(f"\n{Colors.BLUE}DRY RUN MODE - No files will be modified{Colors.END}")
    
    # Process each template
    fixed_count = 0
    for template_path in templates:
        if process_template(template_path, args.dry_run):
            fixed_count += 1
    
    print_header("SECURITY FIXES COMPLETE")
    print(f"{Colors.GREEN}Found issues in {fixed_count} out of {len(templates)} templates{Colors.END}")
    
    if args.dry_run:
        print(f"\n{Colors.BLUE}This was a dry run. No files were modified.{Colors.END}")
        print(f"{Colors.BLUE}Run without --dry-run to apply the changes.{Colors.END}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())