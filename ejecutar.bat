@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Primero crea .venv e instala requirements.txt siguiendo el README.
    exit /b 1
)
".venv\Scripts\python.exe" modelo_ipap.py
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" comprobar.py
