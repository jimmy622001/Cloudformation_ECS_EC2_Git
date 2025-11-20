import re
import sys
from pathlib import Path

def fix_database_yaml():
    file_path = Path("templates/database.yaml")
    if not file_path.exists():
        print(f"File {file_path} does not exist")
        return False
    
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Print lines around the error area
        lines = content.split('\n')
        
        print("Lines around error (385-395):")
        for i in range(385, 396):
            if i < len(lines):
                print(f"{i}: {lines[i]}")
        
        # Check around line 390-392 for indentation or other issues
        # For now, we'll just print the content
        return True
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def fix_subnet_template_yaml():
    file_path = Path("templates/subnet-template.yaml")
    if not file_path.exists():
        print(f"File {file_path} does not exist")
        return False
    
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Print lines around the error area
        lines = content.split('\n')
        
        print("Lines around error (120-130):")
        for i in range(120, 131):
            if i < len(lines):
                print(f"{i}: {lines[i]}")
        
        # Check around line 125-127 for collection issues
        return True
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

if __name__ == "__main__":
    fix_database_yaml()
    print("\n----------\n")
    fix_subnet_template_yaml()