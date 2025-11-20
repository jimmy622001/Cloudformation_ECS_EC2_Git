@echo off
echo Setting up IAM Role for GitHub Actions OIDC authentication

REM Set variables
set PROJECT_NAME=ecs-jenkins-github
set GITHUB_ORG=jimmy622001
set GITHUB_REPO=CloudFormation_ECS_EC2_Jenkins_Git

echo Deploying GitHub Actions OIDC Role...
aws cloudformation deploy --template-file templates/github-actions-oidc.yaml --stack-name %PROJECT_NAME%-github-actions-role --parameter-overrides ProjectName=%PROJECT_NAME% GitHubOrg=%GITHUB_ORG% GitHubRepo=%GITHUB_REPO% --capabilities CAPABILITY_NAMED_IAM

echo.
echo Getting Role ARN...
aws cloudformation describe-stacks --stack-name %PROJECT_NAME%-github-actions-role --query "Stacks[0].Outputs[?OutputKey=='GitHubActionsRoleArn'].OutputValue" --output text > github-actions-role-arn.txt

echo.
echo Role ARN saved to github-actions-role-arn.txt
echo IMPORTANT: Add this ARN as a GitHub secret named AWS_ROLE_TO_ASSUME in your repository settings