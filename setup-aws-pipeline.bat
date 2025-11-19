@echo off
echo Setting up AWS CodePipeline for CloudFormation deployments

REM Set variables
set PROJECT_NAME=ecs-jenkins-github
set ENVIRONMENT=dev
set GITHUB_OWNER=your-github-username-or-org
set GITHUB_REPO=CloudFormation_ECS_EC2_Jenkins_Git
set GITHUB_BRANCH=main
set PARAMETER_FILE=dev-parameters.json

REM Create CodeStar Connection
echo Creating CodeStar Connection to GitHub...
aws codestar-connections create-connection --provider-type GitHub --connection-name %PROJECT_NAME%-%ENVIRONMENT%-github-connection > connection.json

echo.
echo IMPORTANT: You need to complete the GitHub connection by visiting the URL in the AWS console.
echo After creating the connection, get the ARN from the console and update the CONNECTION_ARN variable below.
echo Then uncomment and run the remaining commands.
echo.

REM Set the ARN of the connection after you've completed the authorization in AWS Console
REM set CONNECTION_ARN=arn:aws:codestar-connections:REGION:ACCOUNT_ID:connection/CONNECTION_ID

REM Uncomment these lines after setting up the CONNECTION_ARN
REM echo Deploying AWS CodePipeline CloudFormation stack...
REM aws cloudformation deploy --template-file templates/aws-pipeline.yaml --stack-name %PROJECT_NAME%-%ENVIRONMENT%-pipeline --parameter-overrides ProjectName=%PROJECT_NAME% Environment=%ENVIRONMENT% GitHubOwner=%GITHUB_OWNER% GitHubRepo=%GITHUB_REPO% GitHubBranch=%GITHUB_BRANCH% ConnectionArn=%CONNECTION_ARN% TemplateFilePath=templates/master.yaml ParameterFilePath=%PARAMETER_FILE% --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM

REM echo.
REM echo Pipeline setup complete. You can view the pipeline in the AWS console.
REM echo Stack Name: %PROJECT_NAME%-%ENVIRONMENT%-pipeline