import re
from pathlib import Path

def fix_database_yaml():
    file_path = Path("templates/database.yaml")
    if not file_path.exists():
        print(f"File {file_path} does not exist")
        return False
    
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Find the exact location around line 390
        # Look for specific patterns that might cause YAML parsing issues
        problem_area = ''.join(lines[385:395])
        print(f"Problem area in database.yaml:\n{problem_area}")
        
        # Fix for database.yaml line 390 issue
        # Looking at the error message, it's likely an indentation issue
        # Checking for a block mapping issue where a tag was found when a block end was expected
        fixed_content = []
        in_secret_string = False
        join_indent = None
        
        for i, line in enumerate(lines):
            if "SecretString: !Join" in line:
                in_secret_string = True
                join_indent = len(line) - len(line.lstrip())
                fixed_content.append(line)
            elif in_secret_string and line.strip().startswith('- ') and not line.strip().startswith('- -'):
                # Ensure proper indentation for list items in !Join
                # The line should be indented consistently with the !Join level + 2 spaces
                fixed_line = ' ' * (join_indent + 2) + line.strip() + '\n'
                fixed_content.append(fixed_line)
            else:
                fixed_content.append(line)
                if in_secret_string and not line.strip().startswith('-'):
                    in_secret_string = False
                    join_indent = None
        
        # Write fixed content back to file
        with open(file_path, 'w') as file:
            file.writelines(fixed_content)
            
        print(f"Fixed {file_path}")
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def fix_subnet_template_yaml():
    file_path = Path("templates/subnet-template.yaml")
    if not file_path.exists():
        print(f"File {file_path} does not exist")
        return False
    
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Find the exact location around line 125
        problem_area = ''.join(lines[120:130])
        print(f"Problem area in subnet-template.yaml:\n{problem_area}")
        
        # Fix for subnet-template.yaml line 125 issue
        # The error indicates a block collection issue with missing '-' indicator
        fixed_content = []
        
        for i, line in enumerate(lines):
            if i == 126 and "!ImportValue" in line and len(line.strip()) == len("!ImportValue"):
                # If this is just "!ImportValue" without any continuation, fix indentation
                indent = len(line) - len(line.lstrip())
                next_line = lines[i+1] if i+1 < len(lines) else ""
                if "!Sub" in next_line:
                    # Ensure proper indentation for !Sub after !ImportValue
                    fixed_content.append(line)
                    fixed_content.append(' ' * indent + '  ' + next_line.strip() + '\n')
                    # Skip the next line as we've already handled it
                    i += 1
                    continue
            else:
                fixed_content.append(line)
        
        # Write fixed content back to file
        with open(file_path, 'w') as file:
            file.writelines(fixed_content)
            
        print(f"Fixed {file_path}")
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

if __name__ == "__main__":
    fix_database_yaml()
    print("\n----------\n")
    fix_subnet_template_yaml()