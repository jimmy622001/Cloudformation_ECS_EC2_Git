import subprocess
import json
from pathlib import Path

# Templates with known errors
templates_to_check = [
    "templates/database.yaml", 
    "templates/subnet-template.yaml"
]

for template in templates_to_check:
    if not Path(template).exists():
        print(f"Template {template} does not exist")
        continue
        
    print(f"Validating {template}...")
    try:
        # Use AWS CLI to validate CloudFormation templates
        result = subprocess.run(
            ["aws", "cloudformation", "validate-template", "--template-body", f"file://{template}"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {template} is valid")
        else:
            print(f"❌ {template} validation failed:")
            print(result.stderr)
            
    except Exception as e:
        print(f"Error validating {template}: {e}")