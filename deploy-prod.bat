@echo off
echo Deploying Production Environment...
aws cloudformation deploy ^
  --template-file templates\master.yaml ^
  --stack-name prod-ecs-jenkins-infrastructure ^
  --parameter-overrides file://prod-parameters.json ^
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND

echo Deployment complete!