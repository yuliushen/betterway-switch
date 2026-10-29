@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
    python -m betterway ui
) else (
    py -3 -m betterway ui
)
if errorlevel 1 pause
