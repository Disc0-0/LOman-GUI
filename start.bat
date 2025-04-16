@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title LastOasisManager Launcher
color 0B

REM =============================================================================================
echo.
echo   ██╗      █████╗ ███████╗████████╗     ██████╗  █████╗ ███████╗██╗███████╗
echo   ██║     ██╔══██╗██╔════╝╚══██╔══╝    ██╔═══██╗██╔══██╗██╔════╝██║██╔════╝
echo   ██║     ███████║███████╗   ██║       ██║   ██║███████║███████╗██║███████╗
echo   ██║     ██╔══██║╚════██║   ██║       ██║   ██║██╔══██║╚════██║██║╚════██║
echo   ███████╗██║  ██║███████║   ██║       ╚██████╔╝██║  ██║███████║██║███████║
echo   ╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝        ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝╚══════╝
echo.
echo   ███╗   ███╗ █████╗ ███╗   ██╗ █████╗  ██████╗ ███████╗██████╗ 
echo   ████╗ ████║██╔══██╗████╗  ██║██╔══██╗██╔════╝ ██╔════╝██╔══██╗
echo   ██╔████╔██║███████║██╔██╗ ██║███████║██║  ███╗█████╗  ██████╔╝
echo   ██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║   ██║██╔══╝  ██╔══██╗
echo   ██║ ╚═╝ ██║██║  ██║██║╚═╝ ██║██║  ██║╚██████╗███████╗██████╔╝
echo   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝╚═════╝
echo.
echo =============================================================================================
echo  This script launches the LastOasisManager application with proper environment setup
echo =============================================================================================
echo.

REM Define colors for console output
set "INFO_COLOR=color 0B"
set "SUCCESS_COLOR=color 0A"
set "WARNING_COLOR=color 0E"
set "ERROR_COLOR=color 0C"
set "RESET_COLOR=color 0B"

REM Store the script's directory path for absolute path references
set "SCRIPT_DIR=%~dp0"
set "VENV_PATH=%SCRIPT_DIR%.venv"
set "VENV_ACTIVATE=%VENV_PATH%\Scripts\activate.bat"
set "APP_SCRIPT=%SCRIPT_DIR%LastOasisManager.py"
set "EXIT_CODE=0"

echo [%time%] ▶ LastOasisManager launcher initializing...
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                     ENVIRONMENT VALIDATION                      ║
echo ╚════════════════════════════════════════════════════════════════════╝

REM Check if virtual environment exists
if not exist "%VENV_PATH%" (
    %ERROR_COLOR%
    echo [%time%] ✖ [ERROR] Virtual environment not found at: %VENV_PATH%
    echo         Please run setup script or create virtual environment before running this script.
    pause
    exit /b 1
)

REM Check if activation script exists
if not exist "%VENV_ACTIVATE%" (
    %ERROR_COLOR%
    echo [%time%] ✖ [ERROR] Virtual environment activation script not found at: %VENV_ACTIVATE%
    echo         The virtual environment may be corrupted. Please recreate it.
    pause
    exit /b 1
)

REM Check if Python script exists
if not exist "%APP_SCRIPT%" (
    %ERROR_COLOR%
    echo [%time%] ✖ [ERROR] Application script not found at: %APP_SCRIPT%
    echo         Please ensure the application files are installed correctly.
    pause
    exit /b 1
)

%INFO_COLOR%
echo [%time%] ✓ Environment validation complete
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                        LAUNCHING APP                            ║
echo ╚════════════════════════════════════════════════════════════════════╝

REM Activate virtual environment
echo [%time%] ⚡ Activating Python virtual environment...
call "%VENV_ACTIVATE%"
if errorlevel 1 (
    %ERROR_COLOR%
    echo [%time%] ✖ [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

%INFO_COLOR%
echo [%time%] ✓ Virtual environment activated successfully

REM Optional: Export requirements (commented out by default)
REM echo [%time%] Exporting requirements list...
REM pip freeze > "%SCRIPT_DIR%requirements.txt"

REM Run the Python script
echo [%time%] ⚡ Starting LastOasisManager application...
echo.
python "%APP_SCRIPT%"
set EXIT_CODE=%errorlevel%
echo.

REM Deactivate virtual environment
echo [%time%] ⚡ Deactivating Python virtual environment...
call deactivate

REM Check Python script exit code
if %EXIT_CODE% neq 0 (
    %WARNING_COLOR%
    echo [%time%] ⚠ [WARNING] LastOasisManager exited with code: %EXIT_CODE%
) else (
    %SUCCESS_COLOR%
    echo [%time%] ✓ LastOasisManager completed successfully.
)

%INFO_COLOR%
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                      LAUNCHER COMPLETED                         ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo [%time%] ■ LastOasisManager launcher finished.
pause
%RESET_COLOR%
exit /b %EXIT_CODE%
