# CloudFormation Security Scanning

This project includes security scanning capabilities to help identify and fix security issues in CloudFormation templates before pushing to GitHub.

## Essential Security Files

The project has been cleaned up to retain only the essential security scanning files:

1. **`run_all_security_scans.py`** - The primary security scanning script that performs comprehensive checks including:
   - CloudFormation Linting (cfn-lint)
   - Security scanning with Checkov
   - Secret detection with detect-secrets
   - Policy checking with CloudFormation Guard
   - And more

2. **`security-rules.guard`** - Rules file for CloudFormation Guard policy checks

3. **`run_security_scan.bat`** - Convenient batch file to run the security scanning script

## How to Use

Before pushing changes to GitHub, run the security scans:

```bash
run_security_scan.bat
```

This will check your CloudFormation templates for:
- Syntax errors and best practices (cfn-lint)
- Security issues and compliance (Checkov)
- Hardcoded secrets (detect-secrets)
- Policy violations (CloudFormation Guard)

Fix any issues reported before pushing to avoid GitHub workflow failures.

## Cleanup Notes

All redundant security scanning files have been removed to keep the project clean.
Only the essential files needed for security scanning are retained.

## Dependencies

The security scanner will attempt to install missing dependencies, but you may need:
- Python 3.7+
- pip
- cfn-lint
- Checkov
- detect-secrets
- CloudFormation Guard (optional)