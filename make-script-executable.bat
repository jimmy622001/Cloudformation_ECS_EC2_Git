@echo off
REM This script is used for Linux/Mac users to make the shell script executable
echo Making the shell script executable for Linux/Mac users...

REM Windows can't directly make a file executable, but this note reminds users what to do when they transfer the file
echo If you are using Linux or Mac, please run the following command after transferring the file:
echo chmod +x scripts/remove-aws-organization.sh
echo.

echo For Windows users, you can use the PowerShell script directly.
echo.

pause