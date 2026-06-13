@echo off
set PORT=5000

echo ===================================================
echo   Smart Path Suggestor - Easy Startup
echo ===================================================
echo.
echo [*] Starting Flask Server on port %PORT%...
echo [!] Once started, SCAN the QR CODE in the new window with your phone.
echo.

:: Start the Flask Server in a new window
start "Smart Path Server" cmd /k ".\venv\Scripts\python.exe server.py"

echo ===================================================
echo   Server window opened. Please keep it visible
echo   to scan the QR code for mobile connection.
echo ===================================================
pause
