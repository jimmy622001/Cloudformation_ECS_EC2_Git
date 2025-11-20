@echo off
setlocal enabledelayedexpansion

echo CloudFormation StackSet Deletion Tool
echo ===================================

if "%~1"=="" (
    set /p STACKSET_NAME="Enter the StackSet name to delete: "
) else (
    set STACKSET_NAME=%~1
)

if "%~2"=="" (
    set /p AWS_REGION="Enter AWS region (default: eu-west-1): " 
    if "!AWS_REGION!"=="" set AWS_REGION=eu-west-1
) else (
    set AWS_REGION=%~2
)

set /p FORCE_DELETE="Force delete all stack instances at once? (y/N): "
if /i "%FORCE_DELETE%"=="y" (
    powershell -ExecutionPolicy Bypass -File scripts\Delete-CloudFormationStackSet.ps1 -StackSetName %STACKSET_NAME% -Region %AWS_REGION% -Force
) else (
    powershell -ExecutionPolicy Bypass -File scripts\Delete-CloudFormationStackSet.ps1 -StackSetName %STACKSET_NAME% -Region %AWS_REGION%
)

pause