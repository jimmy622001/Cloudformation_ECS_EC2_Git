#!/bin/bash
# CloudFormation Security Scanning Script

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}======================================================${NC}"
echo -e "${BLUE}${BOLD}     CloudFormation Security Scanning Script        ${NC}"
echo -e "${BLUE}${BOLD}======================================================${NC}\n"

# Keep track of failures
FAILURES=0
TEMPLATE_DIR="templates"

# Function to run a security check and track success/failure
run_check() {
  local check_name=$1
  local command=$2
  
  echo -e "\n${BOLD}${BLUE}Running $check_name...${NC}\n"
  if eval $command; then
    echo -e "\n${GREEN}✓ $check_name completed successfully${NC}\n"
  else
    echo -e "\n${RED}✗ $check_name found issues${NC}\n"
    FAILURES=$((FAILURES + 1))
  fi
  echo -e "${BOLD}${BLUE}======================================================${NC}\n"
}

# Make sure we're in the project root directory
if [ ! -d "$TEMPLATE_DIR" ]; then
  echo -e "${RED}Error: 'templates' directory not found. Please run this script from the project root.${NC}"
  exit 1
fi

# 1. Run Checkov security scan
checkov_scan() {
  checkov -d $TEMPLATE_DIR --framework cloudformation
}
run_check "Checkov security scan" checkov_scan

# 2. Run detect-secrets scan
secrets_scan() {
  python run_secrets_scan.py
}
run_check "Secret scanning with detect-secrets" secrets_scan

# 3. Run CFN-Lint if installed
cfn_lint_scan() {
  if command -v python -m cfnlint &>/dev/null; then
    python -m cfnlint $TEMPLATE_DIR/*.yaml
  elif command -v cfn-lint &>/dev/null; then
    cfn-lint $TEMPLATE_DIR/*.yaml
  else
    echo -e "${YELLOW}cfn-lint not installed. Skipping...${NC}"
    return 0
  fi
}
run_check "CloudFormation linting check" cfn_lint_scan

# 4. Check for CFN-Guard
if command -v cfn-guard &>/dev/null; then
  # Create basic security rules file if it doesn't exist
  if [ ! -f "security-rules.guard" ]; then
    echo -e "${BLUE}Creating basic security rules file...${NC}"
    cat > security-rules.guard << 'EOL'
# Basic Security Rules 
          
# Enforce encryption of S3 buckets
rule s3_encryption when resourceType == "AWS::S3::Bucket" {
  some Properties.BucketEncryption.ServerSideEncryptionConfiguration[*].ServerSideEncryptionByDefault.SSEAlgorithm == "AES256" or
  some Properties.BucketEncryption.ServerSideEncryptionConfiguration[*].ServerSideEncryptionByDefault.SSEAlgorithm == "aws:kms"
}
          
# Ensure S3 buckets block public access
rule s3_public_access_block when resourceType == "AWS::S3::Bucket" {
  Properties.PublicAccessBlockConfiguration.BlockPublicAcls == true
  Properties.PublicAccessBlockConfiguration.BlockPublicPolicy == true
  Properties.PublicAccessBlockConfiguration.IgnorePublicAcls == true
  Properties.PublicAccessBlockConfiguration.RestrictPublicBuckets == true
}
          
# Ensure RDS instances are encrypted
rule rds_encryption when resourceType == "AWS::RDS::DBInstance" {
  Properties.StorageEncrypted == true
}
          
# Ensure security groups don't allow unrestricted access
rule restrict_sg_ingress when resourceType == "AWS::EC2::SecurityGroup" {
  when some Properties.SecurityGroupIngress[*] {
    not (CidrIp == "0.0.0.0/0" and (FromPort == 0 or ToPort == 0 or IpProtocol == "-1"))
  }
}
EOL
  fi

  # Run cfn-guard on each template
  cfn_guard_scan() {
    local exit_code=0
    for template in $TEMPLATE_DIR/*.yaml; do
      echo -e "${BLUE}Scanning $template with cfn-guard...${NC}"
      if ! cfn-guard validate -r security-rules.guard -d $template --show-summary all; then
        exit_code=1
      fi
    done
    return $exit_code
  }
  run_check "CloudFormation Guard security checks" cfn_guard_scan
else
  echo -e "${YELLOW}cfn-guard not installed. Skipping...${NC}"
fi

# Final summary
echo -e "\n${BLUE}${BOLD}======================================================${NC}"
echo -e "${BLUE}${BOLD}                Security Scan Summary                ${NC}"
echo -e "${BLUE}${BOLD}======================================================${NC}\n"

if [ $FAILURES -eq 0 ]; then
  echo -e "${GREEN}${BOLD}All security checks passed!${NC}"
  echo -e "${GREEN}Your CloudFormation templates are ready to be committed.${NC}\n"
else
  echo -e "${RED}${BOLD}$FAILURES security check(s) found issues.${NC}"
  echo -e "${YELLOW}Please address the issues before committing your code.${NC}\n"
  exit 1
fi