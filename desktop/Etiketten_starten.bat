@echo off
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel%==0 (python etiketten_fenster.py) else (py etiketten_fenster.py)
echo.
echo Das Programm wurde beendet.
pause
