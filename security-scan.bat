@echo off
echo ##########################################
echo # CloudFormation Security Scanning Suite #
echo ##########################################
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python first.
    goto :EOF
)

echo Installing required tools...
pip install cfn-lint checkov

echo.
echo Running cfn-lint...
cfn-lint templates/*.yaml

echo.
echo Running Checkov...
checkov -d templates/ --framework cloudformation

echo.
echo If you want to run additional security checks:
echo - CloudFormation Guard (requires Rust): cargo install cfn-guard
echo - CloudSploit (requires Node.js): npm install -g @cloudsploit/scanner
echo.
echo For SonarQube and OWASP integration, please refer to the GitHub workflows in .github/workflows/
echo.
echo Scan complete!