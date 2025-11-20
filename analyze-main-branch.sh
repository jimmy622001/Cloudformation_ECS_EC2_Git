#!/bin/bash

# Script to run SonarCloud analysis on main branch
# Usage: ./analyze-main-branch.sh <SONAR_TOKEN>

if [ -z "$1" ]; then
    echo "Error: SONAR_TOKEN is required"
    echo "Usage: ./analyze-main-branch.sh <SONAR_TOKEN>"
    exit 1
fi

SONAR_TOKEN=$1
PROJECT_KEY="cloudformation-poc"
ORGANIZATION="jimmy622001"

echo "Checking if sonar-scanner is installed..."

if ! command -v sonar-scanner &> /dev/null; then
    echo "sonar-scanner not found in PATH. Checking for local installation..."
    
    # Check if we have already installed it locally
    if [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "win"* ]]; then
        SCANNER_PATH="./sonar-scanner-temp/sonar-scanner-7.0.2.4839-windows/bin/sonar-scanner.bat"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        SCANNER_PATH="./sonar-scanner-temp/sonar-scanner-7.0.2.4839-macosx/bin/sonar-scanner"
    else
        SCANNER_PATH="./sonar-scanner-temp/sonar-scanner-7.0.2.4839-linux-x64/bin/sonar-scanner"
    fi
    
    if [ -f "$SCANNER_PATH" ]; then
        echo "Using locally installed SonarScanner at $SCANNER_PATH"
        SONAR_SCANNER="$SCANNER_PATH"
        chmod +x "$SONAR_SCANNER" 2>/dev/null
    else
        echo "SonarScanner not found. Installing it now..."
        ./install-sonar-scanner.sh
        
        if [ $? -ne 0 ]; then
            echo "Failed to install SonarScanner. Please install it manually."
            echo "Refer to SONARCLOUD_DEFAULT_BRANCH_FIX.md for instructions."
            exit 1
        fi
        
        echo "Installation successful."
        SONAR_SCANNER="./run-sonar-analysis.sh"
    fi
else
    SONAR_SCANNER="sonar-scanner"
fi

echo "Running SonarCloud analysis on main branch..."

"$SONAR_SCANNER" \
  -Dsonar.projectKey=$PROJECT_KEY \
  -Dsonar.organization=$ORGANIZATION \
  -Dsonar.host.url=https://sonarcloud.io \
  -Dsonar.token=$SONAR_TOKEN \
  -Dsonar.sources=. \
  -Dsonar.exclusions='**/*.bat,**/*.sh,.github/**/*,sonar-scanner-temp/**/*' \
  -Dsonar.cfn.file.suffixes='.yaml,.yml,templates/**/*.yaml,templates/**/*.yml' \
  -Dsonar.branch.name=main

if [ $? -ne 0 ]; then
    echo "Analysis failed! Please check the output above for errors."
    exit 1
else
    echo "Analysis completed successfully!"
    echo "Your main branch should now be established in SonarCloud."
    echo "You can now run analyses on other branches."
fi