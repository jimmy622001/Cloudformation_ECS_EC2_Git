#!/usr/bin/env python
"""
CloudFormation Security Scanner
Run multiple security scanning tools against CloudFormation templates
"""

import os
import subprocess
import sys
import argparse
import json
from pathlib import Path

# Configure the templates to scan
DEFAULT_TEMPLATES = [
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

def run_command(command, description):
    """Run a shell command and return the output"""
    print_header(description)
    print(f"{Colors.BLUE}Running: {' '.join(command)}{Colors.END}\n")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"{Colors.WARNING}{result.stderr}{Colors.END}")
        
        print(f"{Colors.GREEN}Exit code: {result.returncode}{Colors.END}")
        return result.returncode
    except Exception as e:
        print(f"{Colors.FAIL}Error running command: {e}{Colors.END}")
        return 1

def run_checkov(templates):
    """Run Checkov on the templates"""
    # Try multiple possible locations for checkov
    possible_paths = [
        os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python314', 'Scripts', 'checkov.exe'),
        os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python312', 'Scripts', 'checkov.exe'),
        os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python310', 'Scripts', 'checkov.exe'),
        'checkov.exe',
        'checkov'
    ]

    # Find the first valid path
    checkov_path = None
    for path in possible_paths:
        if os.path.exists(path):
            checkov_path = path
            break

        # Use Python to run checkov directly
        try:
            print(f"{Colors.BLUE}Using Python to run Checkov directly{Colors.END}")
            cmd = [sys.executable, '-c', f'''
    try:
        from checkov.main import run
        import sys
        sys.argv = ['checkov', '--quiet', '--framework', 'cloudformation']
        for template in {templates}:
            sys.argv.extend(['-f', template])
        exit_code = run()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error running Checkov: {{e}}")
        sys.exit(1)
    ''']
            return run_command(cmd, "RUNNING CHECKOV SCAN")
        except Exception as e:
            print(f"{Colors.FAIL}Failed to run Checkov: {e}{Colors.END}")
            return 1
    
    cmd = [checkov_path, '--quiet', '--framework', 'cloudformation']
    for template in templates:
        cmd.extend(['-f', template])
    
    return run_command(cmd, "RUNNING CHECKOV SCAN")

def run_cfripper(templates):
    """Run CFRipper on the templates"""
    # Try multiple possible locations for cfripper
    possible_paths = [
        os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python314', 'Scripts', 'cfripper.exe'),
        os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python312', 'Scripts', 'cfripper.exe'),
        os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python310', 'Scripts', 'cfripper.exe'),
        'cfripper.exe',
        'cfripper'
    ]

    # Find the first valid path
    cfripper_path = None
    for path in possible_paths:
        if os.path.exists(path):
            cfripper_path = path
            break

    # If not found, use pip to install it directly
    if not cfripper_path:
        print(f"{Colors.WARNING}CFRipper not found. Trying to install it...{Colors.END}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--user", "cfripper"], check=True)
            # Try again to find it
            for path in possible_paths:
                if os.path.exists(path):
                    cfripper_path = path
                    break
        except Exception as e:
            print(f"{Colors.FAIL}Failed to install CFRipper: {e}{Colors.END}")
            return 1

    if not cfripper_path:
        print(f"{Colors.FAIL}Could not find or install CFRipper{Colors.END}")
        return 1

    print(f"{Colors.BLUE}Using CFRipper at: {cfripper_path}{Colors.END}")
    
    return run_command([cfripper_path] + templates, "RUNNING CFRIPPER SCAN")

def run_cfn_lint(templates):
    """Run CFN-Lint on the templates"""
    # Try multiple possible locations for cfn-lint
    possible_paths = [
        os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python314', 'Scripts', 'cfn-lint.exe'),
        os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python312', 'Scripts', 'cfn-lint.exe'),
        os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python310', 'Scripts', 'cfn-lint.exe'),
        'cfn-lint.exe',
        'cfn-lint'
    ]

    # Find the first valid path
    cfn_lint_path = None
    for path in possible_paths:
        if os.path.exists(path):
            cfn_lint_path = path
            break

    # If not found, try the Python module approach
    if not cfn_lint_path:
        print(f"{Colors.WARNING}CFN-Lint executable not found. Trying Python module...{Colors.END}")
        return run_command([sys.executable, '-m', 'cfnlint'] + templates, "RUNNING CFN-LINT SCAN (PYTHON MODULE)")

    print(f"{Colors.BLUE}Using CFN-Lint at: {cfn_lint_path}{Colors.END}")
    
    try:
        return run_command([cfn_lint_path] + templates, "RUNNING CFN-LINT SCAN")
    except Exception:
        print(f"{Colors.WARNING}CFN-Lint executable not found. Trying Python module...{Colors.END}")
        return run_command(['python', '-m', 'cfnlint'] + templates, "RUNNING CFN-LINT SCAN (PYTHON MODULE)")

def create_summary(results):
    """Create and print a summary of the scan results"""
    print_header("SECURITY SCAN SUMMARY")
    
    all_passed = all(code == 0 for code in results.values())
    
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}All security scans passed!{Colors.END}")
    else:
        print(f"{Colors.WARNING}{Colors.BOLD}Some security scans failed:{Colors.END}")
        for tool, code in results.items():
            status = f"{Colors.GREEN}PASSED" if code == 0 else f"{Colors.FAIL}FAILED"
            print(f"  - {tool}: {status} (Exit Code: {code}){Colors.END}")
    
    print("\nRecommended actions:")
    if all_passed:
        print(f"{Colors.GREEN}✅ No issues found. Templates are secure!{Colors.END}")
    else:
        print(f"{Colors.WARNING}⚠️  Review the output above for each failed tool and address the issues.{Colors.END}")
        print(f"{Colors.WARNING}⚠️  Run this script again after making changes to verify fixes.{Colors.END}")
    
    return 0 if all_passed else 1

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run security scans on CloudFormation templates')
    parser.add_argument('--templates', nargs='+', default=DEFAULT_TEMPLATES,
                        help='CloudFormation template files to scan')
    args = parser.parse_args()
    
    # validate templates exist
    templates = []
    for template in args.templates:
        if os.path.exists(template):
            templates.append(template)
        else:
            print(f"{Colors.WARNING}Warning: Template file not found: {template}{Colors.END}")
    
    if not templates:
        print(f"{Colors.FAIL}Error: No valid template files found to scan{Colors.END}")
        return 1
    
    print_header("CLOUDFORMATION SECURITY SCANNER")
    print(f"Scanning the following templates:")
    for template in templates:
        print(f"  - {template}")
    
    # Run the tools
    results = {}
    
    # Run Checkov
    try:
        results["Checkov"] = run_checkov(templates)
    except Exception as e:
        print(f"{Colors.FAIL}Error running Checkov: {e}{Colors.END}")
        results["Checkov"] = 1
    
    # Run CFRipper
    try:
        results["CFRipper"] = run_cfripper(templates)
    except Exception as e:
        print(f"{Colors.FAIL}Error running CFRipper: {e}{Colors.END}")
        results["CFRipper"] = 1
    
    # Run CFN-Lint
    try:
        results["CFN-Lint"] = run_cfn_lint(templates)
    except Exception as e:
        print(f"{Colors.FAIL}Error running CFN-Lint: {e}{Colors.END}")
        results["CFN-Lint"] = 1
    
    # Create and print summary
    return create_summary(results)

if __name__ == "__main__":
    sys.exit(main())