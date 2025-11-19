@echo off
echo Fixing CloudFormation Security Issues...
python secure_cloudformation.py --fix %*

if %errorlevel% neq 0 (
    echo.
    echo Some issues may need manual intervention. Review the output above.
) else (
    echo All issues have been fixed!
)

pause