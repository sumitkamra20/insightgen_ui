#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Run the streamlit application
./venv/bin/streamlit run run_ui.py

# Deactivate the virtual environment when the application is closed
deactivate
