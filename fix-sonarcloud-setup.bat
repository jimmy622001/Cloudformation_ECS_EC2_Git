@echo off
echo SonarCloud Default Branch Fix Utility

if "%1" == "" (
    echo Error: SONAR_TOKEN is required
    echo Usage: fix-sonarcloud-setup.bat YOUR_SONAR_TOKEN
    exit /b 1
)

echo Running the fix script...

:: Check if WSL is available
where wsl >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo Using WSL to run the bash script...
    wsl bash ./fix-sonarcloud-setup.sh %1
    goto end
)

:: Check if Git Bash is available
where bash >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo Using Git Bash to run the script...
    bash ./fix-sonarcloud-setup.sh %1
    goto end
)

:: If neither is available, show manual instructions
echo Neither WSL nor Git Bash was found.
echo.
echo To fix the SonarCloud default branch issue:
echo.
echo 1. Install Git Bash from https://git-scm.com/download/win
echo    OR
echo    Enable Windows Subsystem for Linux (WSL)
echo.
echo 2. Then run: fix-sonarcloud-setup.bat YOUR_SONAR_TOKEN
echo.
echo Alternatively, follow the manual instructions in SONARCLOUD_DEFAULT_BRANCH_FIX.md

:end
echo.
echo Please check SONARCLOUD_DEFAULT_BRANCH_FIX.md for more information.