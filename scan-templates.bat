@echo off
echo CloudFormation Security Scanner
echo ==============================

REM Check for Python installation
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python first.
    exit /b 1
)

REM Install required tools if not already installed
echo Installing/Updating security scanning tools...
pip install cfn-lint checkov > nul 2>&1

echo Running security scans on CloudFormation templates...
echo.
echo 1. Running cfn-lint for CloudFormation best practices...
echo ------------------------------------------------------
cfn-lint templates/*.yaml -i W
echo.

echo 2. Running Checkov for security checks...
echo ---------------------------------------
checkov -d templates/ --framework cloudformation
echo.

echo 3. Checking AWS CloudFormation Guard rules (if installed)...
echo ----------------------------------------------------------
where cfn-guard > nul 2>&1
if %errorlevel% equ 0 (
    echo Checking with CloudFormation Guard (add your rules to cfn-guard-rules.json)
    if exist cfn-guard-rules.json (
        for %%f in (templates\*.yaml) do (
            cfn-guard validate -r cfn-guard-rules.json -t %%f
        )
    ) else (
        echo cfn-guard-rules.json not found. Skipping Guard checks.
    )
) else (
    echo cfn-guard not installed. Skipping Guard checks.
    echo To install: pip install cloudformation-guard
)
echo.

echo Scan complete! Review the output for any security issues.
echo ------------------------------------------------------------