# Streamlit app entrypoint
# This file serves as the main entry point for enterprise Streamlit deployments

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Always import and run the main application regardless of how it's called
from app import main

# Run the application
main()