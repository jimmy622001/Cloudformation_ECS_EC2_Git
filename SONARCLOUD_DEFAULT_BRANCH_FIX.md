# Fix for SonarCloud "Default Branch Not Found" Error

If you're encountering the following error when running SonarCloud analysis:

```
Could not find a default branch for project with key 'cloudformation-poc'. Make sure project exists.
```

This document provides steps to fix the issue.

## Understanding the Issue

This error typically occurs due to one of the following reasons:

1. The project doesn't exist in SonarCloud yet
2. The project exists but has never had a successful analysis on the main branch
3. The project has an incorrect default branch configuration

## Automated Solution

We've created a script to automatically diagnose and fix these issues:

```bash
# Make the script executable
chmod +x fix-sonarcloud-setup.sh

# Run the script with your SonarCloud token
./fix-sonarcloud-setup.sh YOUR_SONAR_TOKEN
```

The script will:
- Check if the project exists and create it if needed
- Verify the default branch configuration
- Run a minimal analysis to establish the main branch if needed

## Manual Solution Steps

If you prefer to fix the issue manually, follow these steps:

### 1. Verify the Project Exists

1. Go to [SonarCloud](https://sonarcloud.io/) and sign in
2. Navigate to your organization (jimmy622001)
3. Check if a project with key `cloudformation-poc` exists
4. If not, create it by clicking "Analyze new project"

### 2. Run an Initial Analysis on the Main Branch

The most critical step is to run an analysis on your main branch first:

```bash
# Install sonar-scanner if needed
# https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/

# Run a minimal analysis on the main branch
sonar-scanner \
  -Dsonar.projectKey=cloudformation-poc \
  -Dsonar.organization=jimmy622001 \
  -Dsonar.host.url=https://sonarcloud.io \
  -Dsonar.login=YOUR_SONAR_TOKEN \
  -Dsonar.sources=. \
  -Dsonar.branch.name=main
```

### 3. Verify Branch Configuration

1. Go to the project in SonarCloud
2. Navigate to Administration > Branches
3. Check that "main" is set as the default branch
4. If not, click the "..." menu next to the main branch and select "Set as main branch"

### 4. Update Your GitHub Actions Workflow

Make sure your workflow is correctly configured:

1. In `.github/workflows/sonarcloud.yml`, verify the proper branch parameters:
   ```yaml
   -Dsonar.branch.name=${{ github.ref_name }}
   -Dsonar.branch.target=main
   ```

2. In `sonar-project.properties`, ensure you have:
   ```properties
   sonar.branch.name=${env.BRANCH_NAME:-main}
   sonar.branch.target=main
   ```

## After Fixing

After applying these fixes, your SonarCloud analysis should run successfully. You'll be able to:

1. See analysis results in the SonarCloud dashboard
2. Compare branches and pull requests
3. Track code quality metrics over time

## Need More Help?

If you're still experiencing issues, check out:

- [SonarCloud Documentation on Branches](https://docs.sonarcloud.io/advanced-setup/branches/)
- [SonarCloud GitHub Integration Guide](https://docs.sonarcloud.io/getting-started/github/)
- [SonarCloud Troubleshooting](https://docs.sonarcloud.io/troubleshooting/)