#!/bin/bash
# IMPORTANT: DO NOT COMMIT THIS FILE WITH ACTUAL VALUES
# Make a copy of this file, rename it to something like "my-parameter-values.sh" (which is gitignored)
# Then update with your actual values and use that for parameter setup

# Database parameters
DB_USERNAME="your-db-username"

# Monitoring parameters  
GRAFANA_PASSWORD="your-complex-grafana-password"

# Network parameters
ALLOWED_SSH_CIDR="your-allowed-ip-range/32"

# Domain parameters
DOMAIN_NAME="your-actual-domain.com"

# CI/CD parameters
GITHUB_REPO="your-org/your-actual-repo"

# Run the setup script with these values
./setup-ssm-parameters.sh \
  --db-username "$DB_USERNAME" \
  --grafana-password "$GRAFANA_PASSWORD" \
  --allowed-ssh-cidr "$ALLOWED_SSH_CIDR" \
  --domain-name "$DOMAIN_NAME" \
  --github-repo "$GITHUB_REPO"