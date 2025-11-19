@echo off
echo Previewing CloudFormation deployment (no changes will be applied)...
aws cloudformation deploy ^
  --template-file templates\master.yaml ^
  --stack-name dev-ecs-jenkins-infrastructure ^
  --parameter-overrides file://dev-parameters.json ^
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND ^
  --no-execute-changeset

echo Preview complete! Review the changeset above.