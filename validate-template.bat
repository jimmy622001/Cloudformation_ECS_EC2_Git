@echo off
echo Validating CloudFormation template...
aws cloudformation validate-template --template-body file://templates/master.yaml

echo Validation complete!