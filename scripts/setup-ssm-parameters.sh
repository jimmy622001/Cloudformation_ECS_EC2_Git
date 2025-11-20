#!/bin/bash

# This script creates or updates parameters in AWS Systems Manager Parameter Store
# These parameters are referenced in the CloudFormation templates

# Default values (DO NOT put sensitive actual values here)
AWS_REGION="us-east-1"  # Change to your preferred region
DB_USERNAME="dbadmin"
GRAFANA_PASSWORD="changeme"
ALLOWED_SSH_CIDR="10.0.0.0/16"
DOMAIN_NAME="dev.example.com"
GITHUB_REPO="your-org/your-repo"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --region)
      AWS_REGION="$2"
      shift 2
      ;;
    --db-username)
      DB_USERNAME="$2"
      shift 2
      ;;
    --grafana-password)
      GRAFANA_PASSWORD="$2"
      shift 2
      ;;
    --allowed-ssh-cidr)
      ALLOWED_SSH_CIDR="$2"
      shift 2
      ;;
    --domain-name)
      DOMAIN_NAME="$2"
      shift 2
      ;;
    --github-repo)
      GITHUB_REPO="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --region VALUE           AWS region to store parameters (default: us-east-1)"
      echo "  --db-username VALUE      Database username"
      echo "  --grafana-password VALUE Grafana admin password (stored as SecureString)"
      echo "  --allowed-ssh-cidr VALUE CIDR range for SSH access"
      echo "  --domain-name VALUE      Domain name for application"
      echo "  --github-repo VALUE      GitHub repository name (org/repo format)"
      echo "  --help                   Display this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Prompt for confirmation before proceeding
echo "The following parameters will be set in AWS SSM Parameter Store:"
echo "Region: $AWS_REGION"
echo "Database Username: $DB_USERNAME"
echo "Grafana Password: [SECURE]"
echo "Allowed SSH CIDR: $ALLOWED_SSH_CIDR"
echo "Domain Name: $DOMAIN_NAME"
echo "GitHub Repository: $GITHUB_REPO"
echo ""
read -p "Do you want to continue? (y/n): " CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
  echo "Operation cancelled"
  exit 0
fi

# Database parameters
aws ssm put-parameter \
  --name "/cloudformation/database/username" \
  --value "$DB_USERNAME" \
  --type "String" \
  --overwrite \
  --region "$AWS_REGION"

# Monitoring parameters
aws ssm put-parameter \
  --name "/cloudformation/monitoring/grafana-password" \
  --value "$GRAFANA_PASSWORD" \
  --type "SecureString" \
  --overwrite \
  --region "$AWS_REGION"

# Network parameters
aws ssm put-parameter \
  --name "/cloudformation/network/allowed-ssh-cidr" \
  --value "$ALLOWED_SSH_CIDR" \
  --type "String" \
  --overwrite \
  --region "$AWS_REGION"

# Domain parameters
aws ssm put-parameter \
  --name "/cloudformation/domain/name" \
  --value "$DOMAIN_NAME" \
  --type "String" \
  --overwrite \
  --region "$AWS_REGION"

# CI/CD parameters
aws ssm put-parameter \
  --name "/cloudformation/cicd/github-repository" \
  --value "$GITHUB_REPO" \
  --type "String" \
  --overwrite \
  --region "$AWS_REGION"

echo "Parameters successfully created or updated in AWS Systems Manager Parameter Store"