#!/bin/bash
# Script to verify SonarCloud setup

# Colors for output
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

if [ -z "$1" ]; then
  echo -e "${RED}Error: SONAR_TOKEN not provided${NC}"
  echo "Usage: $0 <SONAR_TOKEN>"
  exit 1
fi

SONAR_TOKEN=$1
PROJECT_KEY="cloudformation-poc"
ORGANIZATION="jimmy622001"

echo -e "${YELLOW}Verifying SonarCloud setup...${NC}"

# Check connection to SonarCloud
echo -e "\n${YELLOW}Checking connection to SonarCloud...${NC}"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -u "$SONAR_TOKEN:" "https://sonarcloud.io/api/system/status")

if [ "$RESPONSE" = "200" ]; then
  echo -e "${GREEN}✓ Successfully connected to SonarCloud${NC}"
else
  echo -e "${RED}✗ Failed to connect to SonarCloud. HTTP response: $RESPONSE${NC}"
  echo "Please check your SONAR_TOKEN and internet connection."
  exit 1
fi

# Check if organization exists
echo -e "\n${YELLOW}Checking if organization '$ORGANIZATION' exists...${NC}"
ORG_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -u "$SONAR_TOKEN:" "https://sonarcloud.io/api/organizations/search?organizations=$ORGANIZATION")

if [ "$ORG_RESPONSE" = "200" ]; then
  echo -e "${GREEN}✓ Organization '$ORGANIZATION' exists${NC}"
else
  echo -e "${RED}✗ Organization '$ORGANIZATION' not found or not accessible${NC}"
  echo "Please create the organization or check its name."
fi

# Check if project exists
echo -e "\n${YELLOW}Checking if project '$PROJECT_KEY' exists...${NC}"
PROJ_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -u "$SONAR_TOKEN:" "https://sonarcloud.io/api/components/show?component=$PROJECT_KEY")

if [ "$PROJ_RESPONSE" = "200" ]; then
  echo -e "${GREEN}✓ Project '$PROJECT_KEY' exists${NC}"
else
  echo -e "${RED}✗ Project '$PROJECT_KEY' not found or not accessible${NC}"
  echo "Please create the project with key '$PROJECT_KEY' in organization '$ORGANIZATION'."
fi

# Check if token has proper permissions
echo -e "\n${YELLOW}Checking token permissions...${NC}"
PERM_RESPONSE=$(curl -s -u "$SONAR_TOKEN:" "https://sonarcloud.io/api/permissions/users")

if echo "$PERM_RESPONSE" | grep -q "errors"; then
  echo -e "${RED}✗ Token does not have sufficient permissions${NC}"
  echo "Please generate a new token with appropriate permissions."
else
  echo -e "${GREEN}✓ Token has necessary permissions${NC}"
fi

# Verify workflow file
echo -e "\n${YELLOW}Verifying workflow file...${NC}"
if [ -f ".github/workflows/sonarcloud.yml" ]; then
  echo -e "${GREEN}✓ SonarCloud workflow file exists${NC}"
else
  echo -e "${RED}✗ SonarCloud workflow file not found${NC}"
  echo "Please create the workflow file at '.github/workflows/sonarcloud.yml'."
fi

# Summary
echo -e "\n${YELLOW}Summary:${NC}"
echo -e "1. Create the project '$PROJECT_KEY' in organization '$ORGANIZATION' if not already done"
echo -e "2. Ensure the token has proper permissions"
echo -e "3. Run an initial analysis on the 'main' branch"
echo -e "4. Then try running analysis on the 'dev' branch"
echo -e "\nFor detailed instructions, see SONARCLOUD_SETUP_GUIDE.md"