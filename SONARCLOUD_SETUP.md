# SonarCloud Integration Setup

This document explains how to properly set up SonarCloud integration for CloudFormation project quality analysis.

## Prerequisites

1. A SonarCloud account (https://sonarcloud.io/)
2. GitHub repository access with admin permissions
3. GitHub Actions enabled on your repository

## Setup Steps

### 1. Create SonarCloud Organization and Project

1. Log in to [SonarCloud](https://sonarcloud.io/)
2. Create a new organization or use an existing one
   - Current organization name in configuration: `jimmy622001`
3. Create a new project with key: `cloudformation-poc`
   - Make sure to use the exact same project key as specified in the workflow
   - Select GitHub as the provider and follow the integration steps

### 2. Generate SonarCloud Token

1. In SonarCloud, go to your user profile (click your avatar)
2. Select "Security" or "My Account" > "Security"
3. Generate a new token with a meaningful name like "GitHub Actions"
4. Copy the token value - you'll need it in the next step

### 3. Add SONAR_TOKEN to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Name: `SONAR_TOKEN`
5. Value: paste the token you generated in SonarCloud
6. Click "Add secret"

### 4. Setup the Default Branch

1. For this project, ensure the default branch in SonarCloud matches your GitHub default branch (main)
2. Branch configuration is already set properly in `sonar-project.properties`

### 5. SonarCloud Analysis Configuration

The project is configured with:

- Project key: `cloudformation-poc`
- Organization: `jimmy622001`
- CloudFormation specific settings
- Automated linting for CloudFormation templates

## Workflow Execution

The SonarCloud analysis will run automatically on:
- Push to `main` or `dev` branches
- Pull requests targeting `main` or `dev`
- Manual triggering via workflow_dispatch
- Weekly on Mondays at 8:00 AM UTC

## Troubleshooting

### Common Issues:

1. **Project Not Found Error**:
   - Ensure project exists in SonarCloud with the exact projectKey
   - Check organization name in both workflow file and SonarCloud

2. **Authentication Errors**:
   - Verify SONAR_TOKEN is correctly set in GitHub Secrets
   - Generate a new token if issues persist

3. **Branch Not Found**:
   - Ensure at least one analysis has been completed on the main branch
   - Check that branch configuration in sonar-project.properties matches actual branch names