# SonarCloud Setup Guide for Your CloudFormation Project

This guide will help you resolve the "Project not found" and "Default branch not found" errors in your SonarCloud integration.

## Step 1: Verify SonarCloud Organization

1. Log in to SonarCloud at https://sonarcloud.io using your account:
   - Username: `jimmy622001-BJIbF@githubGitHub`
   - Email: `jimmy622001@outlook.com`

2. Confirm you have an organization named `jimmy622001`:
   - If it exists, proceed to Step 2
   - If not, create it by clicking "+" next to Organizations and following the prompts

## Step 2: Create the Project in SonarCloud

1. Navigate to your organization dashboard at https://sonarcloud.io/organizations/jimmy622001/projects
2. Click "+ Create project" or "Analyze new project" button
3. Select "GitHub" as your provider
4. Find and select your repository "Cloudformation_ECS_EC2_Git"
   - If you don't see it, click "Install our GitHub App" and grant access to this repository
5. In the project setup:
   - Set the project key to exactly `cloudformation-poc`
   - Set the display name (e.g., "CloudFormation POC")
   - Choose "main" as the main branch
6. Complete the project setup by clicking "Set Up"

## Step 3: Generate a New SonarCloud Token

1. Click your account avatar in the top-right corner
2. Select "My Account"
3. Go to the "Security" tab
4. Generate a new token:
   - Name: "GitHub Actions CloudFormation"
   - Expiration: (Choose appropriate duration)
   - Click "Generate"
5. Copy the generated token immediately (you won't see it again)

## Step 4: Add Token to GitHub Secrets

1. Go to your GitHub repository "Cloudformation_ECS_EC2_Git"
2. Navigate to "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Set Name as `SONAR_TOKEN`
5. Paste the token you copied in Step 3
6. Click "Add secret"

## Step 5: Initial Analysis on Main Branch

For the first analysis, it's important to run it on your main branch:

1. Make a small commit to your main branch (even just updating a comment)
2. Push the commit to trigger the workflow:
   ```bash
   git checkout main
   # Make a small change to any file
   git add .
   git commit -m "Trigger initial SonarCloud analysis"
   git push
   ```
3. Go to the "Actions" tab in your GitHub repository to monitor the workflow
4. After the workflow completes, check SonarCloud to verify the project was analyzed

## Step 6: Subsequent Analysis on Dev Branch

Once the main branch analysis completes successfully:

1. Switch to the dev branch:
   ```bash
   git checkout dev
   ```
2. Make a small commit if needed
3. Push the changes:
   ```bash
   git push
   ```
4. The SonarCloud analysis should now work on the dev branch too

## Troubleshooting

If you continue to experience issues:

1. **Double-check the project key**: Make sure it's exactly `cloudformation-poc` in both SonarCloud and your configuration files.

2. **Verify token permissions**: Ensure your token has the right permissions for the organization and project.

3. **Check the GitHub workflow execution**: Look at the detailed logs in the GitHub Actions tab for more specific error information.

4. **Manually confirm project existence**: In SonarCloud, try to navigate directly to your project: https://sonarcloud.io/project/overview?id=cloudformation-poc

5. **Contact SonarCloud support**: If all else fails, reach out to SonarCloud support with the specific error messages.

## Technical Checks

Your configuration files look good:

- `.github/workflows/sonarcloud.yml`: Properly configured with dynamic branch name and host URL
- `sonar-project.properties`: Contains all necessary configuration parameters

The GitHub workflow is already set up correctly to:
1. Generate a cfn-lint analysis
2. Run SonarCloud scan
3. Check quality gate status