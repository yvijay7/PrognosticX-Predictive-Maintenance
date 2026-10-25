@echo off
setlocal enabledelayedexpansion
title PrognosticX GitHub Push
set "PATH=%LOCALAPPDATA%\Programs\gh;%LOCALAPPDATA%\Programs\Git\cmd;%PATH%"

echo ====================================================================
echo      PrognosticX: One-Click GitHub Setup & Push for yvijay7
echo ====================================================================
echo.

:: Check GitHub Login Status
gh auth status >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [!] You are not logged into GitHub yet.
    echo.
    echo --------------------------------------------------------------------
    echo [ACTION REQUIRED] A browser window will open shortly.
    echo 1. A one-time code will appear below (it is already copied).
    echo 2. Press Enter to open the browser, paste the code, and click 'Authorize'.
    echo --------------------------------------------------------------------
    echo.
    gh auth login --web -h github.com -p https
    if %ERRORLEVEL% neq 0 (
        echo.
        echo [X] GitHub login was cancelled or failed. Please try again.
        pause
        exit /b 1
    )
)

echo.
echo [OK] Authenticated with GitHub successfully!
echo.
echo [*] Creating repository 'PrognosticX-Predictive-Maintenance' and pushing...
echo.

gh repo create PrognosticX-Predictive-Maintenance --public --source=. --remote=origin --push --description "PrognosticX: Industrial Predictive Maintenance Using Multi-Agent Small Language Models (SLMs)"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ====================================================================
    echo [SUCCESS] Your project has been pushed successfully!
    echo URL: https://github.com/yvijay7/PrognosticX-Predictive-Maintenance
    echo ====================================================================
    start https://github.com/yvijay7/PrognosticX-Predictive-Maintenance
) else (
    echo.
    echo [*] Checking if repository already exists...
    git remote add origin https://github.com/yvijay7/PrognosticX-Predictive-Maintenance.git 2>nul
    git push -u origin main
    if %ERRORLEVEL% equ 0 (
        echo.
        echo ====================================================================
        echo [SUCCESS] Your project has been pushed successfully!
        echo URL: https://github.com/yvijay7/PrognosticX-Predictive-Maintenance
        echo ====================================================================
        start https://github.com/yvijay7/PrognosticX-Predictive-Maintenance
    ) else (
        echo.
        echo [!] Push encountered an issue. Please review the message above.
    )
)

pause
