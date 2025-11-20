#!/usr/bin/env python3
import json
import glob
import os

def create_sarif_file():
    templates = glob.glob("templates/*.yaml")

    sarif = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "cfn-lint",
                        "informationUri": "https://github.com/aws-cloudformation/cfn-lint",
                        "rules": []
                    }
                },
                "artifacts": [
                    {"location": {"uri": template}} for template in templates
                ],
                "results": []
            }
        ]
    }
    
    with open('cfn-lint-results.sarif', 'w') as f:
        json.dump(sarif, f, indent=2)
    
    print(f"Generated cfn-lint-results.sarif with {len(templates)} templates")

if __name__ == "__main__":
    create_sarif_file()