@echo off
echo Running CloudFormation Security Scanner...
python run_all_security_scans.py
if %ERRORLEVEL% NEQ 0 (
  echo Security scan failed with issues. Please fix before pushing to GitHub.
  exit /b %ERRORLEVEL%
) else (
  echo Security scan completed successfully. Safe to push to GitHub.
)