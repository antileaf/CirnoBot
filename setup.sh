#!/bin/bash

# Check if python3 is installed
if ! dpkg -s python3 >/dev/null 2>&1; then
    echo >&2 "python3 is not installed. Aborting."
    exit 1
fi

# Check if python3-venv package is installed
if ! dpkg -s python3-venv >/dev/null 2>&1; then
    echo >&2 "python3-venv is not installed. Aborting."
    echo "To install python3-venv, you can run 'sudo apt install python3-venv'."
    exit 1
fi

# Get the Python3 version number
cirnobot_python3_version=$(python3 -c "import platform; print(platform.python_version())")

# Check if the version is 3.10
if [[ $version != "3.10"* && $version < "3.10" ]]; then
  echo >&2 "Warning: Python3 version is lower than 3.10. This may cause some unexpected errors."
fi

# Define the name of the virtual environment
cirnobot_venv_name=.venv

# Check if the virtual environment already exists
if [ -d "$cirnobot_venv_name" ]; then
    echo "Virtual environment already exists."
	
else
    # Create a new virtual environment
    echo "Virtual environment not found, creating new virtual environment..."
    python -m venv "$cirnobot_venv_name" --prompt "CirnoBot"

	source "$cirnobot_venv_name/bin/activate"

    echo "Installing required packages..."
	# Install any required packages
	pip install -r requirements.txt > /dev/null
	
    echo "Installing adapters, drivers and required plugins for NoneBot2..."
    # Install drivers and adapters for NoneBot2
    nb adapter install nonebot-adapter-onebot > /dev/null
    nb driver install fastapi > /dev/null
    nb plugin install nonebot-plugin-apscheduler > /dev/null

    echo "Done."
fi

echo "To activate the virtual environment, type 'source $cirnobot_venv_name/bin/activate'."
