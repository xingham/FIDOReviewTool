# Streamlit app entrypoint
# This file serves as the main entry point for enterprise Streamlit deployments

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Always import and run the main application regardless of how it's called
from app import main

# Run the application
main()