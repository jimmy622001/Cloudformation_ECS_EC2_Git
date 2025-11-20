import yaml
import sys
from pathlib import Path

def validate_yaml_structure(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            yaml.safe_load(content)
            print(f"✅ {file_path} has valid YAML structure")
            return True
    except yaml.YAMLError as e:
        print(f"❌ {file_path} has YAML structure errors:")
        print(str(e))
        return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

if __name__ == "__main__":
    templates_to_check = [
        "templates/database.yaml",
        "templates/subnet-template.yaml"
    ]
    
    for template in templates_to_check:
        template_path = Path(template)
        if not template_path.exists():
            print(f"Template {template} does not exist")
            continue
            
        validate_yaml_structure(template_path)