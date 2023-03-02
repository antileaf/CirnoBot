#!/bin/bash

# Check if python3-venv package is installed
if ! dpkg -s python3-venv >/dev/null 2>&1; then
    echo >&2 "python3-venv is not installed. Aborting."
    exit 1
fi

# Define the name of the virtual environment
CIRNOBOT_VENV_NAME=.venv

# Check if the virtual environment already exists
if [ -d "$CIRNOBOT_VENV_NAME" ]; then
    echo "Virtual environment already exists."
	source "$CIRNOBOT_VENV_NAME/bin/activate"
	
else
    # Create a new virtual environment
    echo "Creating new virtual environment..."
    python3 -m venv "$CIRNOBOT_VENV_NAME"

	source "$CIRNOBOT_VENV_NAME/bin/activate"
	# Install any required packages
	pip install -r requirements.txt
	
fi
