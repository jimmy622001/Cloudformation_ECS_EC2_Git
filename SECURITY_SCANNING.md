# CloudFormation Security Scanning

This document describes the security scanning tools available in this project to check CloudFormation templates for security issues before pushing to GitHub.

## Available Security Scan Scripts

### 1. Quick Security Scan (Recommended for daily use)

Run the quick security scan for faster feedback during development:

```
quick-security-scan.bat
```

This performs the most essential checks:
- CloudFormation Linting (cfn-lint)
- Security scanning with Checkov

### 2. Template Validation

Validate your CloudFormation templates with AWS:

```
validate-template.bat
```

### 3. CloudFormation Linting Only

Use this for a quick check of template syntax and best practices:

```
cfn-lint-check.bat
```

### 4. Full Security Scan (Comprehensive) 

Run the full security scan to check for all possible security issues:

```
python run_all_security_scans.py
```

This comprehensive scan includes:
- CloudFormation Linting (cfn-lint)
- Security scanning with Checkov
- Rule-based validation with CloudFormation Guard
- Secret detection with detect-secrets
- Dependency checking with OWASP Dependency Check

**Note:** The full scan may take several minutes to complete and requires multiple tools to be installed.

## Prerequisites

The security scanning scripts will attempt to install the required tools if they're missing. The following tools are used:

- Python 3.7+
- cfn-lint - For template syntax and best practice validation
- checkov - For security scanning
- detect-secrets - For detecting secrets (full scan only)
- cfn-guard - For rule-based validation (full scan only)
- OWASP Dependency Check - For vulnerability scanning (full scan only)

## Recommended Workflow

1. During development, use `cfn-lint-check.bat` or `quick-security-scan.bat` for fast feedback
2. Before committing, run `validate-template.bat` to ensure templates are valid
3. Before pushing to the repository, run the full security scan with `python run_all_security_scans.py`

## Resolving Security Issues

When security issues are found:

1. Review the scan output to understand the specific issues
2. Make the necessary changes to your CloudFormation templates
3. Run the scan again to confirm the issues are resolved
4. Push your changes to GitHub only after all security checks pass

## Common Security Issues

- Unrestricted security group rules (0.0.0.0/0)
- Unencrypted resources (S3, RDS, etc.)
- Overly permissive IAM policies (using wildcards *)
- Hard-coded secrets or credentials
- Missing logging configurations

## Maintaining Security Scripts

The security scanning scripts in this repository are:

- `run_all_security_scans.py` - The main comprehensive security scan
- `cfn-lint-check.bat` - Quick syntax and best practice checks
- `quick-security-scan.bat` - Basic security checks for daily use
- `validate-template.bat` - AWS CloudFormation validation

If you need to add additional security checks, consider extending these scripts rather than creating new ones to avoid confusion.