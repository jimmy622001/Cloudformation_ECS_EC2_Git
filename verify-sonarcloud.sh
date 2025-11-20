#!/bin/bash

# Script to verify SonarCloud connectivity and project setup
# Usage: ./verify-sonarcloud.sh <SONAR_TOKEN>

if [ -z "$1" ]; then
    echo "Error: SONAR_TOKEN is required"
    echo "Usage: ./verify-sonarcloud.sh <SONAR_TOKEN>"
    exit 1
fi

SONAR_TOKEN=$1
PROJECT_KEY="cloudformation-poc"
ORGANIZATION="jimmy622001"

echo "Checking SonarCloud connectivity..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${SONAR_TOKEN}" "https://sonarcloud.io/api/system/status")

if [ "$STATUS" == "200" ]; then
    echo "✅ Successfully connected to SonarCloud"
else
    echo "❌ Failed to connect to SonarCloud (HTTP Status: $STATUS)"
    echo "Please verify your SONAR_TOKEN is correct"
    exit 1
fi

echo "Checking project existence..."
PROJECT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${SONAR_TOKEN}" "https://sonarcloud.io/api/projects/search?projects=${PROJECT_KEY}")

if [ "$PROJECT_STATUS" == "200" ]; then
    echo "✅ Project ${PROJECT_KEY} exists"
else
    echo "❌ Project ${PROJECT_KEY} does not exist or is not accessible"
    echo "Please create the project in SonarCloud with the exact key: ${PROJECT_KEY}"
    echo "See SONARCLOUD_SETUP.md for detailed instructions"
    exit 1
fi

echo "Checking organization..."
ORG_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${SONAR_TOKEN}" "https://sonarcloud.io/api/organizations/search?organizations=${ORGANIZATION}")

if [ "$ORG_STATUS" == "200" ]; then
    echo "✅ Organization ${ORGANIZATION} exists"
else
    echo "❌ Organization ${ORGANIZATION} does not exist or is not accessible"
    echo "Please create the organization in SonarCloud with the exact key: ${ORGANIZATION}"
    echo "See SONARCLOUD_SETUP.md for detailed instructions"
    exit 1
fi

echo "All checks passed! SonarCloud is properly configured."
echo "You can now run the workflow to analyze your code."