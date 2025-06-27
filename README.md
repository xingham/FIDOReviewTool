# FIDO Review Tool

## Overview
The FIDO Review Tool is a Streamlit application designed to facilitate the review process for FIDO projects. It provides a user-friendly interface for reviewers and administrators to manage project submissions, view project details, and submit flags for issues encountered during the review process.

## Project Structure
```
fido-review-tool
├── src
│   ├── app.py                # Main entry point for the Streamlit application
│   ├── static
│   │   ├── css
│   │   │   └── styles.css     # CSS styles for the application
│   │   └── templates
│   │       └── index.html     # HTML structure for the application
│   └── utils
│       └── helpers.py         # Utility functions for the application
├── requirements.txt           # List of dependencies
└── README.md                  # Project documentation
```

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd fido-review-tool
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run src/app.py
   ```

## Usage
- Upon launching the application, users will be presented with a login panel.
- Users can log in as either a reviewer or an admin.
- Reviewers can view and manage non-licensed and licensed FIDO review projects.
- Admins have additional capabilities, including uploading new projects and managing submissions.
- Users can submit flags for issues encountered during the review process.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.