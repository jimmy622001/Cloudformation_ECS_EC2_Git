# Git Security Guidelines for CloudFormation Projects

This document outlines best practices for storing CloudFormation templates and related files in GitHub or other version control systems.

## Security Considerations

### 1. Parameter Management

- **DO NOT** commit any files containing actual parameter values to GitHub, especially:
  - Database credentials
  - API keys
  - SSH keys
  - Domain certificates
  - Personal access tokens
  - IP addresses/CIDRs for restricted access

- **DO** use AWS Systems Manager Parameter Store and AWS Secrets Manager for parameter storage
  - Reference these parameters in templates using secure references
  - Use IAM roles to control access to parameters

### 2. Configuration Files

- Store environment-specific configuration files separately from the code repository
- Use placeholder values in templates and documentation

### 3. Private vs. Public Repositories

- Consider using a private repository if your infrastructure code contains:
  - Internal network architecture
  - Security group rules
  - IAM policy details
  - Any other information that could aid attackers

### 4. CI/CD Integration

- When integrating with CI/CD systems:
  - Use environment variables for sensitive values
  - Configure secrets in your CI/CD platform (e.g., GitHub Secrets, Jenkins Credentials)
  - Never expose secrets in build logs or error messages

## Recommended Workflow

1. **Parameter Setup**:
   - Run the `setup-ssm-parameters.sh` script locally to create parameters
   - Never commit the script with actual values filled in

2. **Template Development**:
   - Develop CloudFormation templates with parameter references
   - Use `{{resolve:ssm:parameter-name}}` or `{{resolve:ssm-secure:parameter-name}}` syntax

3. **Deployment**:
   - Deploy using AWS CLI, AWS Console, or CI/CD pipeline
   - Configure IAM roles for deployment to have access to required parameters

## Security Checks Before Committing

- Run `git diff --staged` before committing to check for accidentally staged secrets
- Consider using pre-commit hooks or tools like git-secrets to catch secrets
- Review all changes carefully before pushing to the repository

## Additional Security Tools

- [git-secrets](https://github.com/awslabs/git-secrets): Prevents committing secrets and sensitive information
- [trufflehog](https://github.com/trufflesecurity/trufflehog): Searches for secrets in git repositories
- [detect-secrets](https://github.com/Yelp/detect-secrets): An enterprise friendly way of detecting and preventing secrets in code

Remember: The goal is to maintain version control of infrastructure code while ensuring no sensitive information is exposed in the repository.