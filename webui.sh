#!/bin/bash

# Ensure the virtual environment is present, or create one
if [ ! -d "thumb_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv thumb_env
fi

# Activate the virtual environment
source thumb_env/bin/activate

# Check for the existence of requirements.txt
if [ -f "requirements.txt" ]; then
    echo "requirements.txt found. Installing necessary libraries..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Installing default libraries..."
    pip install gradio langchain ipython ipywidgets
    echo "Exporting installed libraries to requirements.txt..."
    pip freeze > requirements.txt
fi

# Run the Gradio app
echo "Launching thumb..."
python gradio.py

# Deactivate the virtual environment
deactivate

echo "Server closed."
