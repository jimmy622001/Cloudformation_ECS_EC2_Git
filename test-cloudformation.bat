@echo off
echo CloudFormation Template Validation and Testing
echo ===========================================

REM Set variables
set ENV=%1
if "%ENV%"=="" set ENV=dev

echo Testing CloudFormation templates for %ENV% environment...
echo.

echo 1. Validating CloudFormation template syntax...
for %%f in (templates\*.yaml) do (
    echo   Validating %%f
    aws cloudformation validate-template --template-body file://%%f
    if %errorlevel% neq 0 (
        echo Error validating %%f
        exit /b %errorlevel%
    )
)
echo All templates validated successfully.
echo.

echo 2. Creating a change set to simulate deployment (without actually deploying)...
aws cloudformation create-change-set ^
    --stack-name ecs-jenkins-github-%ENV% ^
    --change-set-name test-change-set-%RANDOM% ^
    --template-body file://templates/master.yaml ^
    --parameters file://%ENV%-parameters.json ^
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND ^
    --change-set-type UPDATE ^
    --no-execute-change-set

echo.
echo 3. Describing the change set to see what would be deployed...
aws cloudformation describe-change-set ^
    --stack-name ecs-jenkins-github-%ENV% ^
    --change-set-name test-change-set-%RANDOM%

echo.
echo 4. Deleting the change set (no changes were applied)...
aws cloudformation delete-change-set ^
    --stack-name ecs-jenkins-github-%ENV% ^
    --change-set-name test-change-set-%RANDOM%

echo.
echo Testing complete! No changes were made to your infrastructure.
echo Usage: test-cloudformation.bat [environment]
echo Example: test-cloudformation.bat dev