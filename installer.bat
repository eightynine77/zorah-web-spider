@echo off
SETLOCAL EnableDelayedExpansion

title Web Spider Installer
color 0A
cls

ECHO =========================================================
ECHO  WEB SPIDER - DEVELOPER SOURCE INSTALLER
ECHO =========================================================
ECHO.
ECHO This script will install all required Python
ECHO packages globally.
ECHO.
ECHO Changing directory to /src...
cd src

:: 1. Check if requirements.txt exists
IF NOT EXIST "requirements.txt" (
ECHO.
ECHO !--- ERROR: requirements.txt not found ---!
ECHO This installer must be in the parent folder of "src".
ECHO Your "src" folder must contain "requirements.txt".
ECHO.
pause
exit /b 1
)

:: 2. Check if the main TUI script exists
IF NOT EXIST "zorah.py" (
ECHO.
ECHO !--- ERROR: zorah.py not found ---!
ECHO Your "src" folder must contain "zorah.py".
ECHO.
pause
exit /b 1
)

:: 3. Check if the backend engine script exists
IF NOT EXIST "engine.py" (
ECHO.
ECHO !--- ERROR: engine.py not found ---!
ECHO Your "src" folder must contain "engine.py".
ECHO.
pause
exit /b 1
)

:: 4. Install packages
ECHO Installing required Python packages globally...
python -m pip install -r requirements.txt
IF !ERRORLEVEL! NEQ 0 (
ECHO.
ECHO !--- FAILED TO INSTALL PACKAGES ---!
ECHO Please check your internet connection or pip setup.
pause
exit /b !ERRORLEVEL!
)

:: 5. Show success message
ECHO.
ECHO All packages installed successfully!
ECHO.
ECHO You can now run the program by navigating to the 'src'
ECHO folder in your terminal and running:
ECHO.
ECHO python zorah.py
ECHO.
ECHO.
ECHO ==========================================================
ECHO you can support me by subscribing to my youtube channel:
ECHO https://youtube.com/c/jebbidan
ECHO and subscribe to my website's newsletter:
ECHO https://jebbidan.wixstudio.com/youtube/subscribe
ECHO.
ECHO.
ECHO all my sites and social media links:
ECHO https://jebbidan.great-site.net/
ECHO.
ECHO press any key to close this script...
pause >nul
ENDLOCAL
goto :EOL
:EOL