@echo off
echo Running quick security scan on CloudFormation templates...

REM Check for cfn-lint
cfn-lint --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing cfn-lint...
    pip install cfnlint
)

REM Check for checkov
checkov --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing checkov...
    pip install checkov
)

echo Running CloudFormation linter...
cfn-lint templates\*.yaml

echo.
echo Running Checkov security scanner...
checkov -d templates\ --framework cloudformation

echo.
echo Quick security scan complete!