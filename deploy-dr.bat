@echo off
echo Deploying DR Pilot Light Infrastructure...

aws cloudformation deploy ^
  --template-file templates/dr-pilot-light.yaml ^
  --stack-name dr-ecs-jenkins-infrastructure ^
  --parameter-overrides file://dr-parameters.json ^
  --capabilities CAPABILITY_NAMED_IAM

if %ERRORLEVEL% EQU 0 (
    echo DR Pilot Light Infrastructure deployment completed successfully!
) else (
    echo DR Pilot Light Infrastructure deployment failed with error code %ERRORLEVEL%
)