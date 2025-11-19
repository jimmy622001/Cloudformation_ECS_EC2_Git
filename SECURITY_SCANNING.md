# Security Scanning for CloudFormation Templates

This document explains the security scanning tools set up for this CloudFormation project and how to use them.

## Available Security Tools

### 1. Local Scanning Tools

#### Using the Integrated Script
Run the `security-scan.bat` script for quick local scanning:

```bash
./security-scan.bat
```

This script installs and runs:
- cfn-lint: Validates CloudFormation template syntax and best practices
- Checkov: Scans for security and compliance issues

#### Manual Tool Installation

If you prefer to install and run tools individually:

```bash
# Install cfn-lint
pip install cfn-lint

# Install Checkov
pip install checkov

# Install CloudFormation Guard (requires Rust)
cargo install cfn-guard

# Install trufflehog for secret detection
pip install trufflehog
```

### 2. GitHub Actions Workflows

The following automated workflows run when code is pushed or on a schedule:

- **cfn-lint**: Validates CloudFormation template syntax
- **Checkov**: Performs security and compliance checks
- **CloudFormation Guard**: Validates templates against security policies
- **SonarCloud**: Provides code quality and security analysis
- **OWASP Dependency-Check**: Scans for vulnerable dependencies
- **CloudSploit**: Scans AWS environment for security issues

## Setup Requirements

### For GitHub Actions

1. **SonarCloud Integration**:
   - Create a SonarCloud account and project at https://sonarcloud.io
   - Add your SonarCloud token as a GitHub Secret named `SONAR_TOKEN`
   - Update the organization and project key in `.github/workflows/sonarcloud.yml`

2. **CloudSploit/AWS Integration**:
   - Add AWS credentials as GitHub Secrets:
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`
   - Ensure the AWS user has read-only permissions

## Understanding Results

### Security Issue Severity

Issues are typically categorized as:

- **Critical**: Must be fixed immediately
- **High**: Should be fixed as soon as possible
- **Medium**: Should be planned for remediation
- **Low**: Consider fixing in future updates
- **Info**: Informational findings

### Common CloudFormation Security Issues

1. **Unencrypted Resources**: Storage, databases, or snapshots without encryption
2. **Overly Permissive IAM Policies**: Using wildcards (`"*"`) in IAM policies
3. **Open Security Groups**: Unrestricted ingress/egress rules (0.0.0.0/0)
4. **Unprotected S3 Buckets**: Missing encryption or public access blocks
5. **Insecure Communication**: Services configured without TLS/SSL

## Integration with CI/CD

These security tools can be integrated with Jenkins or other CI/CD systems:

- **SonarQube**: Will scan on push to GitHub if configured correctly
- **OWASP Dependency-Check**: Will scan on push to GitHub if configured correctly

## Best Practices

1. **Pre-commit Scanning**: Run local scans before pushing changes
2. **Regular Scheduled Scans**: Use scheduled GitHub Actions
3. **Fix Critical Issues**: Immediately address critical security findings
4. **Review False Positives**: Document deliberate exceptions
5. **Update Scanners**: Keep security tools up to date

## Additional Resources

- [AWS CloudFormation Best Practices](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html)
- [OWASP Cloud Security](https://owasp.org/www-project-cloud-security/)
- [CIS AWS Benchmarks](https://www.cisecurity.org/benchmark/amazon_web_services/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)