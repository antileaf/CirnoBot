@echo off

REM Check if python3 is installed
where python3 >nul 2>&1
if %errorlevel% neq 0 (
    echo python3 is not installed. Aborting.
    exit /b 1
)

REM Check if python3-venv package is installed
@REM python -m pip show python3-venv >nul 2>&1
@REM if %errorlevel% neq 0 (
@REM     echo python3-venv is not installed. Aborting.
@REM     echo To install python3-venv, you can run 'pip install venv'.
@REM     exit /b 1
@REM )

REM Get the Python3 version number
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set cirnobot_python3_version=%%v

echo Creating virtual environment with Python %cirnobot_python3_version%...

REM Check if the version is 3.10
for /f "tokens=2 delims=." %%m in ("%cirnobot_python3_version%") do set major_version=%%m
if %major_version% lss 10 (
  echo Warning: Your Python3 version is %cirnobot_python3_version%, which is lower than 3.10. This may cause some unexpected errors.
)

REM Define the name of the virtual environment
set cirnobot_venv_name=.venv

REM Check if the virtual environment already exists
if exist "%cirnobot_venv_name%" (
    echo Virtual environment already exists.
) else (
    REM Create a new virtual environment
    echo Virtual environment not found, creating new virtual environment...
    python -m venv "%cirnobot_venv_name%" --prompt "CirnoBot"

    call "%cirnobot_venv_name%\Scripts\activate.bat"

    echo Installing required packages...
    REM Install any required packages
    python -m pip install -r requirements.txt > nul

    echo Installing adapters, drivers and required plugins for NoneBot2...
    REM Install drivers and adapters for NoneBot2
    nb adapter install nonebot-adapter-onebot > nul
    nb driver install fastapi > nul
    nb plugin install nonebot-plugin-apscheduler > nul

    echo Done.
)

echo To activate the virtual environment, type '%cirnobot_venv_name%\Scripts\activate.bat'. 
