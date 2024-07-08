@echo off

rem Set your project directory path
set PROJECT_DIR=D:\Project\Project\echeck_system\echeck_system\echeck

rem Set your virtual environment path
set VENV_DIR=D:\Project\Project\echeck_system\echeck_system

rem Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    rem Activate virtual environment if not already activated
    call "%VENV_DIR%\Scripts\activate.bat"
)

rem Change directory to your Django project directory
cd /d "%PROJECT_DIR%"

rem Run Django server
echo Running Django application...
python manage.py runserver
