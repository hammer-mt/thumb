@echo off
SETLOCAL

:: Check for existence of virtual environment
IF NOT EXIST thumb_env (
    echo Creating virtual environment...
    python -m venv thumb_env
)

:: Activate the virtual environment
CALL thumb_env\Scripts\activate

:: Check for the existence of requirements.txt
IF EXIST requirements.txt (
    echo requirements.txt found. Installing necessary libraries...
    pip install -r requirements.txt
) ELSE (
    echo requirements.txt not found. Installing default libraries...
    pip install gradio langchain python-dotenv
    echo Exporting installed libraries to requirements.txt...
    pip freeze > requirements.txt
)

:: Run the Gradio app
echo Launching thumb...
python gradio.py

:: Deactivate the virtual environment
CALL deactivate

echo Server closed.

ENDLOCAL
