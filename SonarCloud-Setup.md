# SonarCloud Integration Setup

This document describes how to set up SonarCloud analysis for your CloudFormation templates.

## Prerequisites

1. A [SonarCloud](https://sonarcloud.io/) account
2. GitHub repository access with admin rights
3. GitHub Actions enabled on your repository

## Setup Instructions

### 1. Create a SonarCloud Project

1. Go to [SonarCloud](https://sonarcloud.io/) and log in
2. Create a new organization or use an existing one (jimmy622001)
3. Set up a new project with the key `cloudformation-poc`
4. Choose "GitHub Actions" as the analysis method

### 2. Generate a SONAR_TOKEN

1. In SonarCloud, go to your account → My Account → Security
2. Generate a new token and give it a descriptive name (e.g., "GitHub Actions")
3. Copy the generated token

### 3. Add the SONAR_TOKEN to GitHub Secrets

1. In your GitHub repository, go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `SONAR_TOKEN`
4. Value: Paste the token you copied from SonarCloud
5. Click "Add secret"

### 4. Run the Analysis

The analysis will automatically run on:
- Every push to the `main` or `dev` branches
- Every pull request targeting the `main` or `dev` branches

## Understanding Results

After the analysis completes:

1. Go to your project on SonarCloud
2. Review the identified issues, code smells, and security vulnerabilities
3. The Quality Gate will show whether your code passes the quality thresholds

## CloudFormation Specific Rules

The analysis includes specific checks for CloudFormation templates:

- Syntax validation
- Best practices enforcement
- Security checks
- Resource configuration validation

## Troubleshooting

If you encounter any issues:

1. Check the GitHub Actions logs for detailed error messages
2. Ensure your SONAR_TOKEN is correctly set up
3. Verify that your sonar-project.properties file is properly configured
4. Make sure the cfn-lint-results.sarif file is correctly generated

For more help, refer to the [SonarCloud documentation](https://docs.sonarcloud.io/) or the [GitHub Action documentation](https://github.com/SonarSource/sonarcloud-github-action).