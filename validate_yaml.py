import yaml
import sys
from pathlib import Path

def validate_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            yaml.safe_load(file)
        print(f"✅ {file_path} is valid YAML")
        return True
    except yaml.YAMLError as e:
        print(f"❌ {file_path} has YAML errors:")
        print(e)
        return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

if __name__ == "__main__":
    template_dir = Path("templates")
    if not template_dir.exists():
        print(f"Directory {template_dir} does not exist")
        sys.exit(1)
        
    yaml_files = list(template_dir.glob("*.yaml"))
    if not yaml_files:
        print(f"No YAML files found in {template_dir}")
        sys.exit(1)
        
    success = True
    for file_path in yaml_files:
        if not validate_yaml(file_path):
            success = False
            
    if not success:
        sys.exit(1)