@echo off
echo Installiere benoetigte Programmteile (einmalig) ...
where python >nul 2>nul
if %errorlevel%==0 (python -m pip install openpyxl reportlab pillow) else (py -m pip install openpyxl reportlab pillow)
echo.
echo Fertig. Jetzt Etiketten_starten.bat doppelklicken.
pause
