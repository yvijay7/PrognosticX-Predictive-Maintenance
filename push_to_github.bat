@echo off
setlocal
title PrognosticX GitHub Push
set "PATH=%LOCALAPPDATA%\Programs\gh;%LOCALAPPDATA%\Programs\Git\cmd;%PATH%"

echo ====================================================================
echo      PrognosticX: One-Click GitHub Setup and Push for yvijay7
echo ====================================================================
echo.

:: Check GitHub Login
call gh auth status >nul 2>&1
if %ERRORLEVEL% equ 0 goto LOGGED_IN

echo [!] You need to login to GitHub first.
echo.
echo --------------------------------------------------------------------
echo A browser window will open.
echo If an 8-character code appears on screen, paste it in the browser.
echo --------------------------------------------------------------------
echo.
call gh auth login --web -h github.com -p https
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] GitHub login was not completed.
    goto END
)

:LOGGED_IN
echo.
echo [OK] Logged in to GitHub successfully!
echo.
echo [*] Creating GitHub repository 'PrognosticX-Predictive-Maintenance'...
echo.

call gh repo create PrognosticX-Predictive-Maintenance --public --source=. --remote=origin --push --description "PrognosticX: Industrial Predictive Maintenance Using Multi-Agent Small Language Models (SLMs)"

if %ERRORLEVEL% equ 0 goto SUCCESS

echo.
echo [*] Trying direct push to repository...
git remote add origin https://github.com/yvijay7/PrognosticX-Predictive-Maintenance.git >nul 2>&1
git push -u origin main
if %ERRORLEVEL% equ 0 goto SUCCESS

echo.
echo [!] Push failed. Please check the error above.
goto END

:SUCCESS
echo.
echo ====================================================================
echo [SUCCESS] Your project is now LIVE on GitHub!
echo URL: https://github.com/yvijay7/PrognosticX-Predictive-Maintenance
echo ====================================================================
start https://github.com/yvijay7/PrognosticX-Predictive-Maintenance

:END
echo.
pause
