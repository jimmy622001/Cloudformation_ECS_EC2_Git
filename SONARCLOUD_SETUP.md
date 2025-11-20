# SonarCloud Setup Guide

## Step 1: Create a SonarCloud Account and Organization

1. Go to [SonarCloud](https://sonarcloud.io/) and sign up/sign in (preferably with your GitHub account)
2. Verify that you have an organization called `jimmy622001`
   - If not, create it by clicking on "Create an organization" and following the prompts

## Step 2: Create the Project in SonarCloud

1. In your SonarCloud organization, click "Analyze new project"
2. Select the GitHub repository containing your CloudFormation code
3. **Important**: When creating the project, make sure to use **exactly** `cloudformation-poc` as the project key
4. Select "main" as your default branch when prompted

## Step 3: Generate a SonarCloud Token

1. In SonarCloud, go to your account (icon in top right) → My Account → Security
2. Generate a new token with a descriptive name (e.g., "GH Actions Integration")
3. Copy the token (you won't be able to see it again after closing this screen)

## Step 4: Configure GitHub Repository Secrets

1. Go to your GitHub repository
2. Go to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Create a secret named `SONAR_TOKEN` and paste the token value you copied from SonarCloud

## Step 5: Verify the Configuration Files

Make sure your `.github/workflows/sonarcloud.yml` and `sonar-project.properties` files contain the correct settings:

### GitHub Workflow File (.github/workflows/sonarcloud.yml)

The GitHub workflow file should include:

```yaml
- name: SonarCloud Scan
  uses: SonarSource/sonarqube-scan-action@v5.0.0
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_HOST_URL: https://sonarcloud.io
  with:
    args: >
      -Dsonar.projectKey=cloudformation-poc
      -Dsonar.organization=jimmy622001
      -Dsonar.sources=.
      -Dsonar.cfn.file.suffixes=.yaml,.yml,templates/**/*.yaml,templates/**/*.yml
      -Dsonar.branch.name=${{ github.ref_name }}
      -Dsonar.branch.target=main
```

### sonar-project.properties

The sonar-project.properties file should include:

```properties
sonar.projectKey=cloudformation-poc
sonar.organization=jimmy622001
sonar.branch.name=${env.BRANCH_NAME:-main}
sonar.branch.target=main
```

## Step 6: First Analysis on Main Branch

1. Make sure to run the first analysis on the main branch to establish it as the default branch
2. You can do this by making a commit to the main branch, which will trigger the GitHub Action

## Troubleshooting

### Project Not Found Error

If you're seeing a "Project not found" error when running SonarCloud analysis:

1. Verify that you created the project with **exactly** the name `cloudformation-poc` in SonarCloud
2. Check that the organization name is correct (`jimmy622001`)
3. Ensure that the `SONAR_TOKEN` environment variable is correctly set with a valid token

### Default Branch Not Found Error

If you're seeing a "Could not find a default branch" error:

1. Make sure the project exists in SonarCloud
2. Ensure the main branch is established as the default branch
3. Confirm the `sonar.branch.target` property is correctly set to `main`

### Manual First Analysis

To manually establish the main branch, you can run SonarScanner locally:

```bash
sonar-scanner \
  -Dsonar.projectKey=cloudformation-poc \
  -Dsonar.organization=jimmy622001 \
  -Dsonar.sources=. \
  -Dsonar.host.url=https://sonarcloud.io \
  -Dsonar.login=YOUR_SONAR_TOKEN
```