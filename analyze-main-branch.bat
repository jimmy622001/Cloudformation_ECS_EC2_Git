@echo off
setlocal EnableDelayedExpansion

echo ===== SonarCloud Main Branch Analysis =====

if "%~1"=="" (
  echo Error: SONAR_TOKEN is required
  echo Usage: %0 YOUR_SONARCLOUD_TOKEN
  exit /b 1
)

set SONAR_TOKEN=%~1
set PROJECT_KEY=cloudformation-poc
set ORGANIZATION=jimmy622001

echo Checking if sonar-scanner is installed...

where sonar-scanner >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo SonarScanner not found in PATH. Trying to use the locally installed one...
  
  if exist "sonar-scanner-temp\sonar-scanner-7.0.2.4839-windows\bin\sonar-scanner.bat" (
    echo Using locally installed SonarScanner...
    set SONAR_SCANNER=sonar-scanner-temp\sonar-scanner-7.0.2.4839-windows\bin\sonar-scanner.bat
  ) else (
    echo SonarScanner not found. Installing it now...
    call install-sonar-scanner.sh
    
    if %ERRORLEVEL% NEQ 0 (
      echo Failed to install SonarScanner. Please install it manually.
      echo Refer to SONARCLOUD_DEFAULT_BRANCH_FIX.md for instructions.
      exit /b 1
    )
    
    echo Installation successful.
    set SONAR_SCANNER=run-sonar-analysis.bat
  )
) else (
  set SONAR_SCANNER=sonar-scanner
)

echo Running SonarCloud analysis on main branch...

call %SONAR_SCANNER% ^
  -Dsonar.projectKey=%PROJECT_KEY% ^
  -Dsonar.organization=%ORGANIZATION% ^
  -Dsonar.host.url=https://sonarcloud.io ^
  -Dsonar.token=%SONAR_TOKEN% ^
  -Dsonar.sources=. ^
  -Dsonar.exclusions=**/*.bat,**/*.sh,.github/**/*,sonar-scanner-temp/**/* ^
  -Dsonar.cfn.file.suffixes=.yaml,.yml,templates/**/*.yaml,templates/**/*.yml ^
  -Dsonar.branch.name=main

if %ERRORLEVEL% NEQ 0 (
  echo Analysis failed! Please check the output above for errors.
  exit /b 1
) else (
  echo Analysis completed successfully!
  echo Your main branch should now be established in SonarCloud.
  echo You can now run analyses on other branches.
)