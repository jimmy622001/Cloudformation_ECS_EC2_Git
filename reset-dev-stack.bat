@echo off
echo Resetting dev-stack that is in ROLLBACK_COMPLETE state...
powershell -ExecutionPolicy Bypass -File "%~dp0\scripts\Reset-FailedStack.ps1" -StackName dev-stack

echo.
echo After the stack has been deleted, you can either:
echo 1. Push your changes to the dev branch to trigger GitHub Actions workflow
echo 2. Or manually deploy using AWS CLI with the following command:
echo.
echo aws cloudformation deploy --template-file packaged-template.yaml --stack-name dev-stack --parameter-overrides Environment=dev --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
echo.
pause