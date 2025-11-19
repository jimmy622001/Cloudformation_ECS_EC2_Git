@echo off
echo Running CloudFormation linter to validate templates...

REM Check if cfn-lint is installed
cfn-lint --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo cfn-lint is not installed. Installing it now...
    pip install cfnlint
    if %ERRORLEVEL% neq 0 (
        echo Failed to install cfn-lint. Please install it manually with: pip install cfnlint
        exit /b %ERRORLEVEL%
    )
)

echo Running linting on templates...
cfn-lint templates\*.yaml

if %ERRORLEVEL% neq 0 (
    echo Linting found issues with templates that need to be fixed.
    exit /b %ERRORLEVEL%
) else (
    echo All templates passed linting checks!
)