#!/bin/bash

# Check if python3 and pip3 are installed
if ! command -v python3 &> /dev/null
then
    echo "python3 is not installed. Please install it first."
    exit 1
fi

if ! command -v pip3 &> /dev/null
then
    echo "pip3 is not installed. Please install it first."
    exit 1
fi

# Check for ttyd (for web terminals)
if ! command -v ttyd &> /dev/null; then
    echo "Warning: ttyd is not installed. Terminal access will not work."
    echo "Install it with:"
    echo "  Linux: sudo apt install ttyd"
    echo "  macOS: brew install ttyd"
    exit 1
fi

VENV_NAME="nlb-venv"

python3 -m venv $VENV_NAME

source $VENV_NAME/bin/activate

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "requirements.txt does not exist in the current directory."
    deactivate
    exit 1
fi

# Install packages from requirements.txt
pip install -r requirements.txt
