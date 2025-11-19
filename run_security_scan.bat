@echo off
echo Running CloudFormation Security Scan...
python secure_cloudformation.py --scan-only %*

if %errorlevel% neq 0 (
    echo.
    echo Security issues found! To fix, run: python secure_cloudformation.py --fix
)

pause