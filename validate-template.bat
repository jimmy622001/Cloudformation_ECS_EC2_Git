@echo off
echo Validating CloudFormation templates...

REM Validate master template
echo Validating master.yaml
aws cloudformation validate-template --template-body file://templates/master.yaml
if %ERRORLEVEL% neq 0 goto :error

echo All templates validated successfully!
goto :end

:error
echo ERROR: Template validation failed.
exit /b %ERRORLEVEL%

:end