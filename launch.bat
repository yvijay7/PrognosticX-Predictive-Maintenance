@echo off
echo ====================================================================
echo        Starting PrognosticX Industrial Predictive Maintenance
echo ====================================================================
echo Opening Web Application in your default browser...
start index.html
echo.
echo Dashboard launched successfully!
echo To test Python backend, run: python -m uvicorn backend.main:app --reload
pause
