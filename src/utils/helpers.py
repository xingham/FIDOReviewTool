def authenticate_user(username, role):
    """Authenticate the user based on their username and role."""
    if username and role in ['reviewer', 'admin']:
        return True
    return False

def upload_project(file, queue):
    """Handle the project upload and store it in local storage."""
    if not file:
        raise ValueError("No file provided for upload.")
    
    # Simulate reading the file and storing the project
    content = file.read().decode('utf-8')
    lines = content.splitlines()
    project = {
        'name': file.name,
        'type': queue,
        'data': lines
    }
    return project

def toggle_theme(current_theme):
    """Toggle between light and dark themes."""
    return 'dark' if current_theme == 'light' else 'light'