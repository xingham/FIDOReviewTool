# Enterprise Streamlit deployment entry point
# This file serves as the main entry point for enterprise deployments

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from app import main

# Run the application
main()
