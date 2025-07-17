@echo off
echo ========================================
echo Django to Windows .exe Packaging Script
echo ========================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Step 3: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

pip install pyinstaller
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo Step 4: Packaging application with PyInstaller...
pyinstaller app.spec

if %errorlevel% neq 0 (
    echo ERROR: PyInstaller packaging failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS: Application packaged successfully!
echo ========================================
echo.
echo The executable is located at: dist\run_production\run_production.exe
echo.
echo To test the application:
echo 1. Copy the dist\run_production folder to a machine without Python
echo 2. Run run_production.exe
echo 3. The browser should open automatically to http://localhost:8080
echo.
pause