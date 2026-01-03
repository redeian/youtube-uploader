@echo off
REM #############################################################################
REM YouTube Video Uploader - Startup Script (Windows)
REM This script automatically handles virtual environment creation,
REM dependency installation, and application startup.
REM #############################################################################

setlocal enabledelayedexpansion

echo [INFO] YouTube Video Uploader Startup Script
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] uv is not installed. Installing uv...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    REM Refresh PATH
    call refreshenv 2>nul || (
        echo [WARNING] uv has been installed but may not be in PATH
        echo [WARNING] Please restart your terminal or add uv to your PATH
    )
) else (
    echo [SUCCESS] uv is already installed
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo [INFO] Creating virtual environment...
    uv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [SUCCESS] Virtual environment already exists
)

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install or update dependencies
echo [INFO] Installing/updating dependencies...
uv pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "data\tokens" mkdir data\tokens
if not exist "logs" mkdir logs
echo [SUCCESS] Directories created

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

echo [INFO] Python version: %PYTHON_VERSION%

if %MAJOR% LSS 3 (
    echo [WARNING] Python version %PYTHON_VERSION% detected
    echo [WARNING] Python 3.10 or higher is recommended
    echo [WARNING] The application may not work correctly with this version
    set /p CONTINUE="Do you want to continue? (y/N): "
    if /i not "!CONTINUE!"=="y" (
        echo [INFO] Exiting...
        pause
        exit /b 1
    )
) else if %MAJOR% EQU 3 (
    if %MINOR% LSS 10 (
        echo [WARNING] Python version %PYTHON_VERSION% detected
        echo [WARNING] Python 3.10 or higher is recommended
        echo [WARNING] The application may not work correctly with this version
        set /p CONTINUE="Do you want to continue? (y/N): "
        if /i not "!CONTINUE!"=="y" (
            echo [INFO] Exiting...
            pause
            exit /b 1
        )
    )
)

REM Start the application
echo.
echo [INFO] Starting YouTube Video Uploader...
echo [SUCCESS] Application will open in your default browser
echo.

REM Run Streamlit
streamlit run app.py

REM Cleanup on exit
echo.
echo [INFO] Cleaning up temporary files...
del /q temp_* 2>nul
echo [SUCCESS] Cleanup complete

pause
