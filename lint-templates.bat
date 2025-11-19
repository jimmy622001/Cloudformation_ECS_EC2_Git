@echo off
echo Linting CloudFormation templates...

REM Install cfn-lint if not already installed
pip show cfn-lint >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing cfn-lint...
    pip install cfn-lint
)

REM Lint all templates
echo Linting all templates...
cfn-lint templates/*.yaml

echo Linting complete!