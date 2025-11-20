#!/bin/bash

# AWS Organization Removal Script
# This script helps remove an AWS organization from your account

set -e

# Set default region
DEFAULT_REGION="us-east-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check AWS CLI is installed and credentials are configured
check_aws_cli() {
  echo "Checking AWS CLI installation..."
  if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed.${NC}"
    echo "Please install AWS CLI and run 'aws configure' to set up credentials."
    exit 1
  fi
  
  echo "AWS CLI is installed: $(aws --version)"
  
  # Check credentials
  echo "Verifying AWS credentials..."
  if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials are not properly configured.${NC}"
    echo "Please run 'aws configure' to set up your credentials."
    exit 1
  fi
  
  IDENTITY=$(aws sts get-caller-identity)
  ACCOUNT_ID=$(echo $IDENTITY | jq -r '.Account')
  USER_ARN=$(echo $IDENTITY | jq -r '.Arn')
  
  echo -e "${GREEN}Authenticated as: ${USER_ARN}${NC}"
}

# Function to check if account is management account of organization
check_management_account() {
  echo "Checking if current account is the organization's management account..."
  
  ORG_INFO=$(aws organizations describe-organization 2>/dev/null || true)
  
  if [ -z "$ORG_INFO" ]; then
    echo -e "${RED}Error: Could not retrieve organization information.${NC}"
    echo "Make sure you have permissions to access organization information or the organization may not exist."
    exit 1
  fi
  
  MANAGEMENT_ACCOUNT_ID=$(echo $ORG_INFO | jq -r '.Organization.MasterAccountId')
  
  if [ "$ACCOUNT_ID" != "$MANAGEMENT_ACCOUNT_ID" ]; then
    echo -e "${RED}Error: Current account ($ACCOUNT_ID) is not the management account ($MANAGEMENT_ACCOUNT_ID).${NC}"
    echo "You must be logged into the management account to remove an organization."
    exit 1
  fi
  
  echo -e "${GREEN}Confirmed: Current account is the management account for the organization.${NC}"
}

# Function to remove member accounts
remove_member_accounts() {
  echo "Listing member accounts..."
  
  ACCOUNTS=$(aws organizations list-accounts)
  SELF_ID=$(aws sts get-caller-identity | jq -r '.Account')
  
  # Filter out the management account
  MEMBER_ACCOUNTS=$(echo $ACCOUNTS | jq -r ".Accounts[] | select(.Id != \"$SELF_ID\") | .Id")
  MEMBER_COUNT=$(echo $MEMBER_ACCOUNTS | wc -w)
  
  if [ "$MEMBER_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}Found $MEMBER_COUNT member accounts that need to be removed first.${NC}"
    
    if [ "$FORCE" != "true" ]; then
      echo -e "${RED}WARNING: All member accounts will be removed from the organization.${NC}"
      read -p "Are you sure you want to remove all member accounts? This cannot be undone. (y/N) " CONFIRM
      if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        echo "Operation cancelled by user."
        return 1
      fi
    fi
    
    for ACCOUNT_ID in $MEMBER_ACCOUNTS; do
      ACCOUNT_NAME=$(echo $ACCOUNTS | jq -r ".Accounts[] | select(.Id == \"$ACCOUNT_ID\") | .Name")
      ACCOUNT_STATUS=$(echo $ACCOUNTS | jq -r ".Accounts[] | select(.Id == \"$ACCOUNT_ID\") | .Status")
      
      echo "Removing account $ACCOUNT_NAME ($ACCOUNT_ID) from organization..."
      
      if [ "$ACCOUNT_STATUS" == "SUSPENDED" ]; then
        echo -e "${YELLOW}Account $ACCOUNT_ID is suspended and cannot be removed normally.${NC}"
        continue
      fi
      
      if aws organizations remove-account-from-organization --account-id $ACCOUNT_ID; then
        echo -e "${GREEN}Successfully removed account $ACCOUNT_NAME ($ACCOUNT_ID).${NC}"
      else
        echo -e "${RED}Error removing account $ACCOUNT_ID.${NC}"
        echo "You may need to ensure the account has necessary IAM roles and payment methods set up."
        return 1
      fi
    done
    
    # Verify all accounts were removed
    REMAINING=$(aws organizations list-accounts | jq -r ".Accounts[] | select(.Id != \"$SELF_ID\") | .Id" | wc -w)
    if [ "$REMAINING" -gt 0 ]; then
      echo -e "${RED}Warning: Some member accounts could not be removed. Cannot delete organization.${NC}"
      return 1
    fi
  else
    echo -e "${GREEN}No member accounts found in the organization.${NC}"
  fi
  
  return 0
}

# Function to remove organization policies
remove_policies() {
  POLICY_TYPES=("SERVICE_CONTROL_POLICY" "TAG_POLICY" "BACKUP_POLICY" "AISERVICES_OPT_OUT_POLICY")
  
  for POLICY_TYPE in "${POLICY_TYPES[@]}"; do
    echo "Checking for $POLICY_TYPE policies..."
    
    # Check if policy type is enabled
    POLICIES=$(aws organizations list-policies --filter $POLICY_TYPE 2>/dev/null || echo '{"Policies":[]}')
    
    # Process each policy
    for POLICY_ID in $(echo $POLICIES | jq -r '.Policies[] | select(.AwsManaged == false) | .Id'); do
      POLICY_NAME=$(echo $POLICIES | jq -r ".Policies[] | select(.Id == \"$POLICY_ID\") | .Name")
      
      # First detach policy from all targets
      echo "Detaching policy $POLICY_NAME from all targets..."
      TARGETS=$(aws organizations list-targets-for-policy --policy-id $POLICY_ID)
      
      for TARGET_ID in $(echo $TARGETS | jq -r '.Targets[] | .TargetId'); do
        echo "Detaching policy from target $TARGET_ID..."
        aws organizations detach-policy --policy-id $POLICY_ID --target-id $TARGET_ID
      done
      
      # Then delete the policy
      echo "Deleting policy $POLICY_NAME ($POLICY_ID)..."
      aws organizations delete-policy --policy-id $POLICY_ID
      echo -e "${GREEN}Deleted policy $POLICY_NAME${NC}"
    done
  done
  
  return 0
}

# Function to remove organizational units recursively
remove_organizational_units() {
  echo "Listing organizational units..."
  
  ROOT_ID=$(aws organizations list-roots | jq -r '.Roots[0].Id')
  
  function remove_ou_recursively() {
    local PARENT_ID=$1
    
    # Get all OUs in this parent
    local OUS=$(aws organizations list-organizational-units-for-parent --parent-id $PARENT_ID)
    
    for OU_ID in $(echo $OUS | jq -r '.OrganizationalUnits[].Id'); do
      local OU_NAME=$(echo $OUS | jq -r ".OrganizationalUnits[] | select(.Id == \"$OU_ID\") | .Name")
      
      # Recursively remove child OUs
      remove_ou_recursively $OU_ID
      
      # Move any accounts to the root
      local ACCOUNTS=$(aws organizations list-accounts-for-parent --parent-id $OU_ID)
      
      for ACCOUNT_ID in $(echo $ACCOUNTS | jq -r '.Accounts[].Id'); do
        echo "Moving account $ACCOUNT_ID from OU $OU_NAME to root..."
        aws organizations move-account --account-id $ACCOUNT_ID --source-parent-id $OU_ID --destination-parent-id $ROOT_ID
      done
      
      # Delete the OU
      echo "Deleting organizational unit $OU_NAME ($OU_ID)..."
      aws organizations delete-organizational-unit --organizational-unit-id $OU_ID
      echo -e "${GREEN}Deleted organizational unit $OU_NAME${NC}"
    done
  }
  
  remove_ou_recursively $ROOT_ID
  return 0
}

# Function to delete the organization
delete_organization() {
  echo -e "${YELLOW}Deleting AWS organization...${NC}"
  
  if aws organizations delete-organization; then
    echo -e "${GREEN}AWS organization has been successfully deleted!${NC}"
  else
    echo -e "${RED}Error deleting organization.${NC}"
    echo "Please ensure all prerequisites for deletion have been met."
    return 1
  fi
  
  return 0
}

# Main execution
echo "========================================"
echo "AWS Organization Removal Tool"
echo "========================================"
echo

# Parse command line arguments
FORCE=false
REGION="$DEFAULT_REGION"

while [[ $# -gt 0 ]]; do
  case $1 in
    --force)
      FORCE=true
      shift
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    *)
      echo "Unknown parameter: $1"
      exit 1
      ;;
  esac
done

# Set AWS region
export AWS_DEFAULT_REGION=$REGION
echo "Using AWS region: $REGION"

# Check prerequisites
check_aws_cli
check_management_account

# Confirm user wants to proceed
if [ "$FORCE" != "true" ]; then
  echo
  echo -e "${RED}WARNING: Removing an AWS organization is a destructive action that cannot be undone.${NC}"
  echo "Before proceeding, please ensure you understand the consequences:"
  echo "- All member accounts will be removed from the organization"
  echo "- All organization policies will be deleted"
  echo "- All organizational units will be deleted"
  echo "- The organization itself will be deleted"
  echo "- You will lose benefits of consolidated billing, organizational policies, etc."
  echo
  
  read -p "Are you absolutely sure you want to remove your AWS organization? Type 'DELETE ORGANIZATION' to confirm: " CONFIRMATION
  
  if [ "$CONFIRMATION" != "DELETE ORGANIZATION" ]; then
    echo "Operation cancelled by user."
    exit 0
  fi
fi

STEPS_COMPLETED=true

# Step 1: Remove member accounts
echo
echo "=== STEP 1: Removing Member Accounts ==="
echo
if ! remove_member_accounts; then
  STEPS_COMPLETED=false
fi

# Step 2: Remove organization policies
echo
echo "=== STEP 2: Removing Organization Policies ==="
echo
if ! remove_policies; then
  STEPS_COMPLETED=false
fi

# Step 3: Remove organizational units
echo
echo "=== STEP 3: Removing Organizational Units ==="
echo
if ! remove_organizational_units; then
  STEPS_COMPLETED=false
fi

# Step 4: Delete the organization
if [ "$STEPS_COMPLETED" = true ]; then
  echo
  echo "=== STEP 4: Deleting the Organization ==="
  echo
  delete_organization
else
  echo
  echo -e "${RED}Not all prerequisite steps completed successfully. Organization was not deleted.${NC}"
  echo "Please resolve the issues above and try again."
  exit 1
fi