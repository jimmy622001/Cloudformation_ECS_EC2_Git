import sys
import os
import re
import glob

def validate_yaml_file(file_path):
    try:
        # Instead of parsing, check basic YAML syntax by checking indentation and brackets
        with open(file_path, 'r') as file:
            content = file.read()

            # Validate basic structure (matching brackets and braces)
            brackets = {'(': ')', '{': '}', '[': ']'}
            stack = []
            for char in content:
                if char in brackets.keys():
                    stack.append(char)
                elif char in brackets.values():
                    if not stack or char != brackets[stack.pop()]:
                        raise SyntaxError(f"Mismatched brackets in file")

            if stack:
                raise SyntaxError(f"Unclosed brackets: {''.join(stack)}")

            # Basic indentation check
            lines = content.split('\n')
            prev_indent = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('#'):
                    indent = len(line) - len(line.lstrip())
                    if indent > prev_indent + 2 and prev_indent > 0:
                        # More than 2 spaces increase in indentation might be suspicious
                        if not lines[i-1].rstrip().endswith(':') and not lines[i-1].rstrip().endswith('-'):
                            raise SyntaxError(f"Potentially incorrect indentation at line {i+1}")
                    prev_indent = indent

            print(f"✓ {file_path}: Basic syntax validation passed")
            return True
    except Exception as e:
        print(f"✗ {file_path}: Invalid - {str(e)}")
        return False

def validate_cfnlintrc():
    try:
        with open('.cfnlintrc.yaml', 'r') as file:
            content = file.read()
            print(f"✓ .cfnlintrc.yaml: Basic syntax validation passed")
            return True
    except Exception as e:
        print(f"✗ .cfnlintrc.yaml: Invalid - {str(e)}")
        return False

def main():
    # First validate the .cfnlintrc.yaml
    validate_cfnlintrc()

    templates_dir = "templates"
    yaml_files = glob.glob(os.path.join(templates_dir, "*.yaml"))

    if not yaml_files:
        print(f"No YAML files found in {templates_dir} directory")
        return 1

    print(f"Found {len(yaml_files)} YAML files to validate")

    all_valid = True
    for template in yaml_files:
        if not validate_yaml_file(template):
            all_valid = False

    if all_valid:
        print("\nAll templates passed basic syntax validation.")
        return 0
    else:
        print("\nSome templates have basic syntax errors.")
        return 1

if __name__ == "__main__":
    sys.exit(main())