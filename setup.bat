@echo off
REM Setup script for Avatar Generation Application
REM This script creates virtual environments and installs dependencies for all modules

setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo === Avatar Generation Application Setup ===
echo.

REM Initialize and update submodules
echo [1/4] Initializing git submodules...
git submodule update --init --recursive
if errorlevel 1 (
    echo ERROR: Failed to initialize submodules
    exit /b 1
)
echo Submodules initialized.
echo.

REM Setup measurements_extraction_module
echo [2/4] Setting up measurements_extraction_module...
cd /d "%SCRIPT_DIR%measurements_extraction_module"
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install measurements_extraction_module dependencies
    call deactivate
    exit /b 1
)
call deactivate
echo measurements_extraction_module setup complete.
echo.

REM Setup mesh_generation_module
echo [3/4] Setting up mesh_generation_module...
cd /d "%SCRIPT_DIR%mesh_generation_module"
if not exist "myenv" (
    python -m venv myenv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
call myenv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install mesh_generation_module dependencies
    call deactivate
    exit /b 1
)
call deactivate
echo mesh_generation_module setup complete.
echo.

REM Setup main application
echo [4/4] Setting up main application...
cd /d "%SCRIPT_DIR%"
if not exist ".venv" (
    python -m venv .venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install main application dependencies
    call deactivate
    exit /b 1
)
call deactivate
echo Main application setup complete.
echo.

echo === Setup Complete ===
echo.
echo Virtual environments created:
echo   - .venv (main application)
echo   - measurements_extraction_module\venv
echo   - mesh_generation_module\myenv

endlocal
