# SonarCloud Troubleshooting Guide

This guide will help you resolve common issues with SonarCloud integration for your CloudFormation project.

## Common Errors and Solutions

### Project Not Found Error

If you see an error like: `Project not found. Please check the 'sonar.projectKey' and 'sonar.organization' properties...`

1. **Verify the project exists in SonarCloud**:
   - Go to your SonarCloud organization
   - Check if a project with the key `cloudformation-poc` exists
   - If not, create it by following the setup instructions in `SonarCloud-Setup.md`

2. **Check project key and organization**:
   - Ensure the `sonar.projectKey` and `sonar.organization` in `sonar-project.properties` match exactly what's in SonarCloud
   - Organization names are case-sensitive

3. **Verify SONAR_TOKEN**:
   - Check that your GitHub secret `SONAR_TOKEN` is correctly set
   - Generate a new token if necessary
   - Make sure the token has proper permissions

### Default Branch Not Found Error

If you see an error like: `Could not find a default branch for project with key 'cloudformation-poc'`

1. **Set up the project in SonarCloud first**:
   - Make sure you've created the project in the SonarCloud UI before running analysis
   - During project setup, specify `main` as the default branch

2. **First-time analysis**:
   - For the first scan, you may need to run it on the main branch first
   - Push changes to the main branch and let the workflow run

3. **Branch configuration**:
   - Make sure your `sonar-project.properties` has proper branch configuration:
     ```
     sonar.branch.name=${env.BRANCH_NAME:-main}
     sonar.branch.target=main
     ```
   - Also ensure your GitHub workflow specifies the branch target:
     ```yaml
     -Dsonar.branch.target=main
     ```

## Manual First-Time Setup

If you continue to have issues with GitHub Actions:

1. **Manually create the project**:
   - Go to SonarCloud and create the project manually
   - Configure it with your GitHub repository
   - Set the default branch to `main`

2. **Run analysis locally first**:
   ```bash
   # Install sonar-scanner
   # Generate a token from SonarCloud
   sonar-scanner \
     -Dsonar.projectKey=cloudformation-poc \
     -Dsonar.organization=jimmy622001 \
     -Dsonar.sources=. \
     -Dsonar.host.url=https://sonarcloud.io \
     -Dsonar.login=YOUR_SONAR_TOKEN
   ```

3. **Then retry GitHub Actions**

## Step-by-Step Resolution for Current Error

1. **Check if the project exists in SonarCloud**:
   - Log in to SonarCloud
   - Go to your organization (jimmy622001)
   - Verify if the project `cloudformation-poc` exists
   - If not, create it manually

2. **Generate a new SONAR_TOKEN**:
   - Go to SonarCloud → My Account → Security
   - Generate a new token
   - Update the GitHub repository secret

3. **Force the first analysis on the main branch**:
   - Switch to the main branch
   - Push a minor change to trigger the workflow
   - This will establish the main branch as the default one

## Additional Resources

- [SonarCloud Documentation](https://docs.sonarcloud.io/)
- [GitHub Action Documentation](https://github.com/SonarSource/sonarqube-scan-action)
- [Branch Analysis Documentation](https://docs.sonarcloud.io/branches/overview/)
- [SonarCloud GitHub Integration Guide](https://docs.sonarcloud.io/getting-started/github/)