#!/usr/bin/env python
"""
CloudFormation Security Issue Fix Script
Automatically fixes common security issues in CloudFormation templates
"""

import os
import re
import sys
import yaml
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

def load_yaml_template(file_path):
    """Load a YAML template with PyYAML"""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"{Colors.FAIL}Error loading YAML from {file_path}: {e}{Colors.END}")
        return None

def save_yaml_template(file_path, template):
    """Save a YAML template with PyYAML"""
    try:
        with open(file_path, 'w') as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False, width=120)
        print(f"{Colors.GREEN}Successfully updated {file_path}{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.FAIL}Error saving YAML to {file_path}: {e}{Colors.END}")
        return False

def fix_kms_key_wildcard_policy(template):
    """Fix KMS key policies that use wildcard actions"""
    fixed = False
    resources = template.get('Resources', {})
    
    for resource_id, resource in resources.items():
        if resource.get('Type') == 'AWS::KMS::Key':
            policy = resource.get('Properties', {}).get('KeyPolicy', {})
            statements = policy.get('Statement', [])
            
            for i, statement in enumerate(statements):
                if isinstance(statement, dict) and '*' in statement.get('Action', ''):
                    print(f"{Colors.BLUE}Fixing wildcard action in KMS policy for {resource_id}{Colors.END}")
                    # Replace wildcard with specific actions
                    if '*' == statement.get('Action'):
                        statements[i]['Action'] = [
                            'kms:Encrypt',
                            'kms:Decrypt',
                            'kms:ReEncrypt*',
                            'kms:GenerateDataKey*',
                            'kms:DescribeKey'
                        ]
                        fixed = True
                    # If it's a list with a wildcard, remove the wildcard
                    elif isinstance(statement.get('Action'), list) and '*' in statement.get('Action'):
                        actions = statement.get('Action', [])
                        if '*' in actions:
                            actions.remove('*')
                            actions.extend([
                                'kms:Encrypt',
                                'kms:Decrypt',
                                'kms:ReEncrypt*',
                                'kms:GenerateDataKey*',
                                'kms:DescribeKey'
                            ])
                            # Remove duplicates while preserving order
                            statements[i]['Action'] = list(dict.fromkeys(actions))
                            fixed = True
    
    return fixed

def fix_wildcard_resources(template):
    """Fix IAM policies that use wildcard resources"""
    fixed = False
    resources = template.get('Resources', {})
    
    for resource_id, resource in resources.items():
        if resource.get('Type') == 'AWS::IAM::Policy' or resource.get('Type') == 'AWS::IAM::Role':
            policies = []
            
            # Get the policy statements based on resource type
            if resource.get('Type') == 'AWS::IAM::Policy':
                policy_doc = resource.get('Properties', {}).get('PolicyDocument', {})
                policies = [(policy_doc, resource_id)]
            elif resource.get('Type') == 'AWS::IAM::Role':
                role_policies = resource.get('Properties', {}).get('Policies', [])
                for policy in role_policies:
                    policy_doc = policy.get('PolicyDocument', {})
                    policy_name = policy.get('PolicyName', 'UnnamedPolicy')
                    policies.append((policy_doc, f"{resource_id}.{policy_name}"))
            
            # Process each policy document
            for policy_doc, policy_id in policies:
                statements = policy_doc.get('Statement', [])
                
                for i, statement in enumerate(statements):
                    # Fix wildcards in Resource field
                    if isinstance(statement, dict):
                        # Handle autoscaling:DescribeAutoScalingGroups specifically
                        if 'autoscaling:DescribeAutoScalingGroups' in str(statement.get('Action', '')) and '*' in str(statement.get('Resource', '')):
                            print(f"{Colors.BLUE}Fixing wildcard resource for autoscaling:DescribeAutoScalingGroups in {policy_id}{Colors.END}")
                            # Replace wildcard with specific ARN pattern for AutoScaling groups
                            if statement.get('Resource') == '*':
                                account_id = {"Ref": "AWS::AccountId"}
                                region = {"Ref": "AWS::Region"}
                                
                                # Create a more specific ARN pattern
                                statements[i]['Resource'] = {
                                    "Fn::Sub": [
                                        "arn:aws:autoscaling:${AWS::Region}:${AWS::AccountId}:autoScalingGroup:*:autoScalingGroupName/*"
                                    ]
                                }
                                fixed = True
                            
                        # Look for other wildcard resources that could be made more specific
                        if isinstance(statement.get('Resource'), list) and '*' in statement.get('Resource'):
                            if len(statement.get('Resource')) == 1 and statement.get('Resource')[0] == '*':
                                # Try to make this more specific based on the actions
                                action_specific_resources = create_specific_resources_for_actions(statement.get('Action', []))
                                if action_specific_resources:
                                    print(f"{Colors.BLUE}Replacing general wildcard with specific resources in {policy_id}{Colors.END}")
                                    statements[i]['Resource'] = action_specific_resources
                                    fixed = True
    
    return fixed

def create_specific_resources_for_actions(actions):
    """Create more specific resource ARNs based on the actions"""
    if not actions:
        return None
    
    # Convert to list if it's a string
    if isinstance(actions, str):
        actions = [actions]
    
    resources = []
    
    # Create service-specific ARN patterns
    for action in actions:
        if isinstance(action, str):
            service = action.split(':')[0] if ':' in action else ''
            
            if service == 's3':
                resources.append({"Fn::Sub": "arn:aws:s3:::${AWS::StackName}-*"})
            elif service == 'dynamodb':
                resources.append({"Fn::Sub": "arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${AWS::StackName}-*"})
            elif service == 'lambda':
                resources.append({"Fn::Sub": "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${AWS::StackName}-*"})
            elif service == 'logs':
                resources.append({"Fn::Sub": "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/lambda/${AWS::StackName}-*"})
                resources.append({"Fn::Sub": "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/lambda/${AWS::StackName}-*:*"})
                
    # If we couldn't create specific resources, return None to keep original
    return resources if resources else None

def fix_rds_password_no_echo(template):
    """Add NoEcho to RDS password parameters"""
    fixed = False
    parameters = template.get('Parameters', {})
    
    # Find DB password parameters
    for param_id, param in parameters.items():
        if 'password' in param_id.lower() or 'pass' in param_id.lower() or 'secret' in param_id.lower():
            if not param.get('NoEcho'):
                print(f"{Colors.BLUE}Adding NoEcho to parameter {param_id}{Colors.END}")
                param['NoEcho'] = True
                fixed = True
    
    # Look for RDS instances without NoEcho on their password parameters
    resources = template.get('Resources', {})
    for resource_id, resource in resources.items():
        if resource.get('Type') == 'AWS::RDS::DBInstance':
            password_prop = resource.get('Properties', {}).get('MasterUserPassword', None)
            
            # If the password is a reference to a parameter, make sure that parameter has NoEcho
            if isinstance(password_prop, dict) and 'Ref' in password_prop:
                param_name = password_prop['Ref']
                param = parameters.get(param_name, {})
                
                if not param.get('NoEcho', False):
                    print(f"{Colors.BLUE}Adding NoEcho to parameter {param_name} referenced by {resource_id}{Colors.END}")
                    parameters[param_name]['NoEcho'] = True
                    fixed = True
    
    return fixed

def fix_security_groups_open_to_world(template):
    """Fix security groups with ingress rules open to the world (0.0.0.0/0)"""
    fixed = False
    resources = template.get('Resources', {})
    
    for resource_id, resource in resources.items():
        if resource.get('Type') == 'AWS::EC2::SecurityGroup':
            ingress_rules = resource.get('Properties', {}).get('SecurityGroupIngress', [])
            
            for i, rule in enumerate(ingress_rules):
                if rule.get('CidrIp') == '0.0.0.0/0' and rule.get('FromPort') != 80 and rule.get('FromPort') != 443:
                    print(f"{Colors.BLUE}Fixing open ingress rule in {resource_id} for port {rule.get('FromPort')}{Colors.END}")
                    # Replace with a more restricted CIDR or use a parameter
                    ingress_rules[i]['CidrIp'] = '10.0.0.0/8'  # Example: restrict to private IPs
                    if 'Description' not in ingress_rules[i]:
                        ingress_rules[i]['Description'] = f"Restricted access to port {rule.get('FromPort')}"
                    else:
                        ingress_rules[i]['Description'] += " (Restricted access)"
                    fixed = True
    
    return fixed

def fix_cfn_lint_errors(template, file_path):
    """Fix common cfn-lint errors"""
    fixed = False
    resources = template.get('Resources', {})
    
    # Fix embedded parameters in Fn::ImportValue
    for resource_id, resource in resources.items():
        fixed |= fix_embedded_parameters_in_resource(resource, resource_id)
    
    # Fix unused parameters
    fixed |= remove_unused_parameters(template, file_path)
    
    return fixed

def fix_embedded_parameters_in_resource(resource, resource_id, path=""):
    """Recursively fix embedded parameters in a resource"""
    fixed = False
    
    if isinstance(resource, dict):
        # Check for Fn::ImportValue with embedded parameters
        if 'Fn::ImportValue' in resource and isinstance(resource['Fn::ImportValue'], str):
            import_value = resource['Fn::ImportValue']
            if '${' in import_value and '}' in import_value:
                print(f"{Colors.BLUE}Fixing embedded parameter in Fn::ImportValue for {path or resource_id}{Colors.END}")
                
                # Convert to Fn::Sub format
                resource.clear()
                resource['Fn::ImportValue'] = {
                    'Fn::Sub': import_value
                }
                fixed = True
        
        # Recursively check nested objects
        for key, value in list(resource.items()):
            if isinstance(value, dict):
                fixed |= fix_embedded_parameters_in_resource(value, resource_id, f"{path}.{key}" if path else key)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        fixed |= fix_embedded_parameters_in_resource(item, resource_id, f"{path}.{key}[{i}]" if path else f"{key}[{i}]")
    
    return fixed

def remove_unused_parameters(template, file_path):
    """Check for and remove unused parameters"""
    fixed = False
    
    # This is risky to automate without a proper CFN parser
    # For now, we'll just print warnings and not remove anything
    parameters = template.get('Parameters', {})
    used_parameters = find_used_parameters(template)
    
    for param_name in parameters:
        if param_name not in used_parameters:
            print(f"{Colors.WARNING}Parameter {param_name} in {file_path} appears to be unused{Colors.END}")
    
    return fixed

def find_used_parameters(template):
    """Find all used parameters in a template"""
    used_params = set()
    
    def scan_for_refs(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == 'Ref' and isinstance(value, str) and value in template.get('Parameters', {}):
                    used_params.add(value)
                else:
                    scan_for_refs(value)
        elif isinstance(obj, list):
            for item in obj:
                scan_for_refs(item)
    
    # Scan all resources, outputs, conditions, etc.
    for section in ['Resources', 'Outputs', 'Conditions', 'Mappings']:
        scan_for_refs(template.get(section, {}))
    
    return used_params

def main():
    """Main function to fix security issues in CloudFormation templates"""
    parser = argparse.ArgumentParser(description='Fix common security issues in CloudFormation templates')
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
    for template_path in templates:
        print_header(f"PROCESSING {os.path.basename(template_path)}")
        
        # Load the template
        template = load_yaml_template(template_path)
        if not template:
            continue
        
        # Fix security issues
        fixed_kms = fix_kms_key_wildcard_policy(template)
        fixed_wildcard = fix_wildcard_resources(template)
        fixed_password = fix_rds_password_no_echo(template)
        fixed_sg = fix_security_groups_open_to_world(template)
        fixed_lint = fix_cfn_lint_errors(template, template_path)
        
        # Save the updated template if not in dry run mode
        if fixed_kms or fixed_wildcard or fixed_password or fixed_sg or fixed_lint:
            if not args.dry_run:
                save_yaml_template(template_path, template)
            else:
                print(f"{Colors.BLUE}Would update {template_path} (dry run){Colors.END}")
        else:
            print(f"{Colors.GREEN}No issues to fix in {template_path}{Colors.END}")
    
    print_header("SECURITY FIXES COMPLETE")
    print(f"{Colors.GREEN}Successfully processed all templates{Colors.END}")
    
    if args.dry_run:
        print(f"\n{Colors.BLUE}This was a dry run. No files were modified.{Colors.END}")
        print(f"{Colors.BLUE}Run without --dry-run to apply the changes.{Colors.END}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())