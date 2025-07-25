# Enterprise Streamlit deployment entry point
# This file serves as the main entry point and runs the application from src/

import subprocess
import sys
import os

# Run the main application from the src directory
if __name__ == "__main__":
    # Change to src directory and run main.py
    src_main = os.path.join(os.path.dirname(__file__), 'src', 'main.py')
    subprocess.run([sys.executable, src_main])