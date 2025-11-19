@echo off
echo Creating CloudFormation change set...

REM Create a change set
aws cloudformation create-change-set ^
  --stack-name dev-ecs-jenkins-infrastructure ^
  --change-set-name dev-changes-preview ^
  --template-body file://templates/master.yaml ^
  --parameters file://dev-parameters.json ^
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND ^
  --change-set-type UPDATE

REM Wait for change set creation to complete
aws cloudformation wait change-set-create-complete ^
  --stack-name dev-ecs-jenkins-infrastructure ^
  --change-set-name dev-changes-preview

REM Describe the change set to see what would change
aws cloudformation describe-change-set ^
  --stack-name dev-ecs-jenkins-infrastructure ^
  --change-set-name dev-changes-preview

echo "To delete this change set without applying it, run:"
echo "aws cloudformation delete-change-set --stack-name dev-ecs-jenkins-infrastructure --change-set-name dev-changes-preview"