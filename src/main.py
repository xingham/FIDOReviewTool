# Streamlit app entrypoint
# This file serves as the main entry point for enterprise Streamlit deployments

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import and run the main application
if __name__ == "__main__":
    from app import main
    main()
else:
    # For imports
    from app import *