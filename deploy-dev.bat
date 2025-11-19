@echo off
echo Deploying Development Environment...
aws cloudformation deploy ^
  --template-file templates\master.yaml ^
  --stack-name dev-ecs-jenkins-infrastructure ^
  --parameter-overrides file://dev-parameters.json ^
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND

echo Deployment complete!