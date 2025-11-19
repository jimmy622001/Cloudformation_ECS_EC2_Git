# Git Security Guidelines

This document provides essential guidelines for working with Git repositories while maintaining security best practices, particularly regarding sensitive information.

## Never Commit Sensitive Information

Never commit the following sensitive information to Git repositories:

- Passwords
- API keys or tokens
- Private keys (SSH, PGP, etc.)
- Connection strings
- AWS credentials
- Personally identifiable information (PII)
- Customer data
- Infrastructure secrets or certificates

## Use .gitignore Properly

Add patterns to your `.gitignore` file to prevent accidental commits of sensitive files:

```
# Sensitive files
*.pem
*.key
*.pfx
*.p12
*.cer
*.crt
*.env
.env*
*secrets*
*credentials*
*password*
*token*

# Developer environments
.vscode/
.idea/
*.swp
*.swo
```

## Configure Git According to Security Best Practices

```bash
# Enable signed commits if possible
git config --global commit.gpgsign true

# Configure Git to detect renames more effectively
git config --global diff.renamelimit 5000

# Make sure autocrlf is set correctly to avoid unnecessary changes
git config --global core.autocrlf input  # For Unix/Mac
# git config --global core.autocrlf true  # For Windows

# Use default branch name for consistency
git config --global init.defaultBranch main
```

## Use Pre-Commit Hooks

Configure pre-commit hooks to prevent committing sensitive information:

1. Install pre-commit: `pip install pre-commit`
2. Create a `.pre-commit-config.yaml` file
3. Add secret detection hooks
4. Run `pre-commit install` to set up the hooks

## What to Do If Secrets Are Committed

If sensitive information is committed to a repository:

### 1. Revoke and Rotate the Secret

Immediately revoke and rotate any committed secrets. A leaked secret is compromised, even if removed from Git history.

### 2. Remove the Secret from Git History

Use `git filter-repo` to remove the secret from Git history:

```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove files containing sensitive data
git filter-repo --path path/to/sensitive-file --invert-paths

# Replace secrets in specific files
git filter-repo --replace-text <<EOF
password123==>REMOVED-SECRET
api_key_123456==>REMOVED-API-KEY
EOF
```

### 3. Force Push the Changes

After cleaning the repository:

```bash
# Force push to rewrite history on remote (USE WITH CAUTION!)
git push --force origin main
```

### 4. Notify Relevant Parties

Inform your security team and other collaborators about the leak and remediation.

## Best Practices for Managing Secrets

1. **Use Environment Variables**
   - Store secrets in environment variables that are loaded at runtime
   - Keep these variables out of version control

2. **Use Secret Management Tools**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault
   - Google Secret Manager

3. **Reference Secrets in CloudFormation Templates**

   Instead of hardcoding:
   ```yaml
   Password: "insecure-password-123"
   ```

   Use:
   ```yaml
   Password: '{{resolve:secretsmanager:mySecretName:SecretString:password}}'
   ```

4. **Generate Secrets in CloudFormation**

   ```yaml
   Resources:
     MySecret:
       Type: AWS::SecretsManager::Secret
       Properties:
         GenerateSecretString:
           SecretStringTemplate: '{"username": "admin"}'
           GenerateStringKey: "password"
           PasswordLength: 16
   ```

## Using Git Safely in CI/CD Pipelines

1. Store secrets in the CI/CD system's secure storage (e.g., GitHub Secrets)
2. Use separate deployment credentials with minimal permissions
3. Avoid checking out the entire Git history in CI/CD pipelines when possible
4. Implement branch protection rules to prevent force-pushing to main branches

## Additional Security Measures

1. **Implement Branch Protection Rules**
   - Require pull request reviews
   - Require status checks to pass before merging
   - Restrict who can push to matching branches

2. **Regular Security Audits**
   - Scan repositories for secrets regularly
   - Audit access permissions
   - Review webhook configurations

3. **Monitor for Unusual Activity**
   - Watch for unusual commit patterns
   - Monitor repository access
   - Review Git activity logs

## Resources

- [GitGuardian Documentation](https://docs.gitguardian.com/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Git Filter-Repo Documentation](https://github.com/newren/git-filter-repo/blob/main/Documentation/git-filter-repo.txt)
- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)