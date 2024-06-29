@echo off

rem Set your project directory path
set PROJECT_DIR=D:\Projects\echeck_system\echeck

rem Set your virtual environment path
set VENV_DIR=D:\Projects\echeck_system\echeck\env

rem Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    rem Activate virtual environment if not already activated
    call "%VENV_DIR%\Scripts\activate.bat"
)

rem Change directory to your Django project directory
cd /d "%PROJECT_DIR%"

rem Run Django server
python manage.py runserver
