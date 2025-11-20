import os
import json
import subprocess
import sys

# Run cfn-lint and get the output in json format
command = 'cfn-lint templates/*.yaml -i W --format json'
print(f"Running command: {command}")
try:
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stderr:
        print(f"Error occurred: {result.stderr}")
        sys.exit(1)
    
    # Parse the JSON output
    try:
        lint_results = json.loads(result.stdout)
        
        # Create a basic SARIF structure (simplified)
        sarif_output = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "cfn-lint",
                            "rules": []
                        }
                    },
                    "results": []
                }
            ]
        }
        
        # Convert cfn-lint results to SARIF format
        rules_dict = {}
        for item in lint_results:
            rule_id = item.get('Rule', {}).get('Id', 'unknown')
            
            # Add rule to rules array if not already there
            if rule_id not in rules_dict:
                rules_dict[rule_id] = {
                    "id": rule_id,
                    "shortDescription": {
                        "text": item.get('Rule', {}).get('ShortDescription', 'No description')
                    },
                    "helpUri": item.get('Rule', {}).get('Source', '')
                }
            
            # Add result
            sarif_result = {
                "ruleId": rule_id,
                "level": "error" if item.get('Level', '') == 'Error' else "warning",
                "message": {
                    "text": item.get('Message', 'No message')
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": item.get('Filename', 'unknown')
                            },
                            "region": {
                                "startLine": item.get('Location', {}).get('Start', {}).get('LineNumber', 1),
                                "startColumn": item.get('Location', {}).get('Start', {}).get('ColumnNumber', 1)
                            }
                        }
                    }
                ]
            }
            sarif_output['runs'][0]['results'].append(sarif_result)
        
        # Add the rules to the SARIF output
        sarif_output['runs'][0]['tool']['driver']['rules'] = list(rules_dict.values())
        
        # Write SARIF output to file
        with open('cfn-lint-results.sarif', 'w') as f:
            json.dump(sarif_output, f, indent=2)
        
        print("SARIF output successfully written to cfn-lint-results.sarif")
        
    except json.JSONDecodeError:
        print("Failed to parse JSON output from cfn-lint")
        print(f"Raw output: {result.stdout}")
        sys.exit(1)
    
except Exception as e:
    print(f"Error running command: {e}")
    sys.exit(1)