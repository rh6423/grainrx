@echo off
REM GrainRX UI - Quick start script (Windows)
REM Usage: grainui.bat

setlocal
set "SCRIPT_DIR=%~dp0"

echo GrainRX UI - Starting server...

REM Activate virtual environment if present
if exist "%SCRIPT_DIR%venv\Scripts\activate.bat" (
    call "%SCRIPT_DIR%venv\Scripts\activate.bat"
) else if exist "%SCRIPT_DIR%.venv\Scripts\activate.bat" (
    call "%SCRIPT_DIR%.venv\Scripts\activate.bat"
) else (
    echo No virtual environment found, using system Python...
)

REM Install dependencies if FastAPI isn't present
python -c "import fastapi" 2>NUL
if errorlevel 1 (
    echo Installing dependencies from requirements.txt...
    pip install -r "%SCRIPT_DIR%requirements.txt"
    pip install fastapi uvicorn
)

if "%PORT%"=="" set "PORT=8000"

cd /d "%SCRIPT_DIR%gui"

echo Opening http://127.0.0.1:%PORT% in your browser...
start "" "http://127.0.0.1:%PORT%"
echo.

uvicorn app:app --host 127.0.0.1 --port %PORT% --reload

endlocal
