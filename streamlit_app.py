# Streamlit app entry point for enterprise deployment
# This file serves as the main entry point located in the root directory

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from app import main

if __name__ == "__main__":
    main()
