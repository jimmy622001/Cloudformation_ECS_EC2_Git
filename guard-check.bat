@echo off
echo Checking CloudFormation templates with cfn-guard...

REM Install cfn-guard if not already installed
where cfn-guard >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo CloudFormation Guard not found. Installing...
    echo Please install cfn-guard from https://github.com/aws-cloudformation/cloudformation-guard
    echo After installation, run this script again.
    exit /b 1
)

REM Example rule file - create if it doesn't exist
if not exist rules\basic_rules.guard (
    mkdir rules 2>nul
    echo # Sample rule to ensure all S3 buckets have encryption enabled > rules\basic_rules.guard
    echo AWS::S3::Bucket >> rules\basic_rules.guard
    echo   Properties >> rules\basic_rules.guard
    echo     BucketEncryption exists >> rules\basic_rules.guard
)

REM Run guard check on templates
echo Checking templates against policy rules...
cfn-guard validate -r rules\basic_rules.guard -d templates\*.yaml

echo Guard check complete!