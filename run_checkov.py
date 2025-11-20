import yaml
import sys
from pathlib import Path

def check_well_formed_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            yaml.safe_load_all(file)
        print(f"✓ {file_path} - Well-formed YAML")
        return True
    except yaml.YAMLError as e:
        print(f"✗ {file_path} - YAML Error: {e}")
        return False

def check_database_file():
    file_path = "templates/database.yaml"
    if not Path(file_path).exists():
        print(f"File {file_path} does not exist")
        return
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Check for specific structural errors
    lines = content.split('\n')
    line_390 = lines[389] if len(lines) > 389 else "LINE NOT FOUND"
    line_391 = lines[390] if len(lines) > 390 else "LINE NOT FOUND"
    line_392 = lines[391] if len(lines) > 391 else "LINE NOT FOUND"
    
    print(f"Line 390: {line_390}")
    print(f"Line 391: {line_391}")
    print(f"Line 392: {line_392}")
    
    # Check for proper indentation in !ImportValue !Sub expressions
    import_value_sub_pattern = r'!ImportValue\s*\n\s*!Sub'
    if re.search(import_value_sub_pattern, content):
        print("Found potentially problematic !ImportValue !Sub pattern")
        
    # Display all !ImportValue occurrences
    lines_with_import = [(i+1, line) for i, line in enumerate(lines) if '!ImportValue' in line]
    if lines_with_import:
        print("Lines containing !ImportValue:")
        for line_num, line in lines_with_import:
            print(f"{line_num}: {line}")
            # Check next line for !Sub
            if line_num < len(lines) and '!Sub' in lines[line_num]:
                print(f"{line_num+1}: {lines[line_num]}")

def check_subnet_template_file():
    file_path = "templates/subnet-template.yaml"
    if not Path(file_path).exists():
        print(f"File {file_path} does not exist")
        return
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Check for specific structural errors
    lines = content.split('\n')
    line_125 = lines[124] if len(lines) > 124 else "LINE NOT FOUND"
    line_126 = lines[125] if len(lines) > 125 else "LINE NOT FOUND"
    line_127 = lines[126] if len(lines) > 126 else "LINE NOT FOUND"
    
    print(f"Line 125: {line_125}")
    print(f"Line 126: {line_126}")
    print(f"Line 127: {line_127}")
    
    # Look for potential block collection issues
    for i, line in enumerate(lines):
        if i >= 124 and i <= 128 and line.strip().startswith('!'):
            indent = len(line) - len(line.lstrip())
            print(f"Line {i+1} indent: {indent} - {line.rstrip()}")

if __name__ == "__main__":
    import re
    
    # Check if the templates are well-formed YAML
    print("Checking YAML structure...")
    check_well_formed_yaml("templates/database.yaml")
    check_well_formed_yaml("templates/subnet-template.yaml")
    
    print("\nChecking specific error locations...")
    check_database_file()
    print("\n---\n")
    check_subnet_template_file()