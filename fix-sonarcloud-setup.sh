#!/bin/bash

# Script to fix SonarCloud project setup and default branch issues
# Usage: ./fix-sonarcloud-setup.sh <SONAR_TOKEN>

if [ -z "$1" ]; then
    echo "Error: SONAR_TOKEN is required"
    echo "Usage: ./fix-sonarcloud-setup.sh <SONAR_TOKEN>"
    exit 1
fi

SONAR_TOKEN=$1
PROJECT_KEY="cloudformation-poc"
ORGANIZATION="jimmy622001"
DEFAULT_BRANCH="main"

echo "🔍 Diagnosing SonarCloud setup issues..."

# Step 1: Check SonarCloud connectivity
echo "Checking SonarCloud connectivity..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${SONAR_TOKEN}" "https://sonarcloud.io/api/system/status")

if [ "$STATUS" != "200" ]; then
    echo "❌ Failed to connect to SonarCloud (HTTP Status: $STATUS)"
    echo "Please verify your SONAR_TOKEN is correct"
    exit 1
fi
echo "✅ Connected to SonarCloud successfully"

# Step 2: Check if project exists
echo "Checking if project exists..."
PROJECT_RESPONSE=$(curl -s -H "Authorization: Bearer ${SONAR_TOKEN}" "https://sonarcloud.io/api/projects/search?projects=${PROJECT_KEY}")
PROJECT_COUNT=$(echo $PROJECT_RESPONSE | grep -o '"paging":{"pageIndex":1,"pageSize":100,"total":[0-9]*}' | grep -o '"total":[0-9]*' | cut -d':' -f2)

if [ "$PROJECT_COUNT" = "0" ]; then
    echo "❌ Project ${PROJECT_KEY} does not exist in SonarCloud"
    echo
    echo "Creating project in SonarCloud..."
    CREATE_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer ${SONAR_TOKEN}" \
        "https://sonarcloud.io/api/projects/create" \
        -d "name=${PROJECT_KEY}&project=${PROJECT_KEY}&organization=${ORGANIZATION}")
    
    if echo $CREATE_RESPONSE | grep -q "error"; then
        echo "❌ Failed to create project"
        echo "Error: $(echo $CREATE_RESPONSE | grep -o '"msg":"[^"]*"' | cut -d':' -f2 | tr -d '"')"
        echo
        echo "Manual steps to fix:"
        echo "1. Go to https://sonarcloud.io/organizations/${ORGANIZATION}/projects/create"
        echo "2. Create a project with key: ${PROJECT_KEY}"
        echo "3. In the project settings, set '${DEFAULT_BRANCH}' as the main branch"
        exit 1
    else
        echo "✅ Project created successfully"
    fi
else
    echo "✅ Project ${PROJECT_KEY} exists in SonarCloud"
fi

# Step 3: Check and set default branch
echo "Checking default branch configuration..."
BRANCH_RESPONSE=$(curl -s -H "Authorization: Bearer ${SONAR_TOKEN}" \
    "https://sonarcloud.io/api/project_branches/list?project=${PROJECT_KEY}")

if echo $BRANCH_RESPONSE | grep -q "error"; then
    echo "❌ Failed to get branch information"
    echo "Error: $(echo $BRANCH_RESPONSE | grep -o '"msg":"[^"]*"' | cut -d':' -f2 | tr -d '"')"
    echo
    echo "This usually means the project exists but has never had a successful analysis."
    echo
    echo "Running a minimal initial analysis to establish the main branch..."
    
    # Create a temporary sonar-scanner properties file
    echo "sonar.projectKey=${PROJECT_KEY}" > sonar-scanner.properties
    echo "sonar.organization=${ORGANIZATION}" >> sonar-scanner.properties
    echo "sonar.host.url=https://sonarcloud.io" >> sonar-scanner.properties
    echo "sonar.login=${SONAR_TOKEN}" >> sonar-scanner.properties
    echo "sonar.sources=." >> sonar-scanner.properties
    echo "sonar.exclusions=**/*.bat,**/*.sh,.github/**/*,**/*.properties" >> sonar-scanner.properties
    
    # Run initial analysis using sonar-scanner CLI if available, otherwise suggest manual steps
    if command -v sonar-scanner &> /dev/null; then
        sonar-scanner -Dsonar.projectKey=${PROJECT_KEY} \
            -Dsonar.organization=${ORGANIZATION} \
            -Dsonar.host.url=https://sonarcloud.io \
            -Dsonar.login=${SONAR_TOKEN} \
            -Dsonar.sources=. \
            -Dsonar.branch.name=${DEFAULT_BRANCH}
        
        echo "✅ Initial analysis completed. Default branch should now be established."
    else
        echo "❌ sonar-scanner CLI not found"
        echo
        echo "Manual steps to fix:"
        echo "1. Install sonar-scanner CLI: https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/"
        echo "2. Run the following command:"
        echo "   sonar-scanner -Dsonar.projectKey=${PROJECT_KEY} \\"
        echo "     -Dsonar.organization=${ORGANIZATION} \\"
        echo "     -Dsonar.host.url=https://sonarcloud.io \\"
        echo "     -Dsonar.login=YOUR_SONAR_TOKEN \\"
        echo "     -Dsonar.sources=. \\"
        echo "     -Dsonar.branch.name=${DEFAULT_BRANCH}"
        exit 1
    fi
else
    # Check if there's a main branch and if it's set as default
    MAIN_BRANCH_EXISTS=$(echo $BRANCH_RESPONSE | grep -c '"name":"'${DEFAULT_BRANCH}'"')
    DEFAULT_BRANCH_SET=$(echo $BRANCH_RESPONSE | grep -c '"name":"'${DEFAULT_BRANCH}'","isMain":true')
    
    if [ "$MAIN_BRANCH_EXISTS" = "0" ]; then
        echo "❌ The ${DEFAULT_BRANCH} branch does not exist in SonarCloud"
        echo
        echo "Running a minimal initial analysis to establish the main branch..."
        
        # Run initial analysis for the main branch
        if command -v sonar-scanner &> /dev/null; then
            sonar-scanner -Dsonar.projectKey=${PROJECT_KEY} \
                -Dsonar.organization=${ORGANIZATION} \
                -Dsonar.host.url=https://sonarcloud.io \
                -Dsonar.login=${SONAR_TOKEN} \
                -Dsonar.sources=. \
                -Dsonar.branch.name=${DEFAULT_BRANCH}
            
            echo "✅ Initial analysis completed. Default branch should now be established."
        else
            echo "❌ sonar-scanner CLI not found"
            echo "Please install sonar-scanner and run an initial analysis on the ${DEFAULT_BRANCH} branch"
            exit 1
        fi
    elif [ "$DEFAULT_BRANCH_SET" = "0" ]; then
        echo "❌ The ${DEFAULT_BRANCH} branch exists but is not set as the main branch"
        echo
        echo "Setting ${DEFAULT_BRANCH} as the main branch..."
        
        # Set the main branch
        SET_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer ${SONAR_TOKEN}" \
            "https://sonarcloud.io/api/project_branches/set_main_branch" \
            -d "project=${PROJECT_KEY}&branch=${DEFAULT_BRANCH}")
        
        if echo $SET_RESPONSE | grep -q "error"; then
            echo "❌ Failed to set main branch"
            echo "Error: $(echo $SET_RESPONSE | grep -o '"msg":"[^"]*"' | cut -d':' -f2 | tr -d '"')"
            echo
            echo "Manual steps to fix:"
            echo "1. Go to https://sonarcloud.io/project/branches?id=${PROJECT_KEY}"
            echo "2. Set ${DEFAULT_BRANCH} as the main branch"
            exit 1
        else
            echo "✅ Successfully set ${DEFAULT_BRANCH} as the main branch"
        fi
    else
        echo "✅ ${DEFAULT_BRANCH} is correctly configured as the main branch"
    fi
fi

echo
echo "🎉 SonarCloud configuration is now fixed!"
echo "You can now run your SonarCloud analysis workflow"