import streamlit as st
import pandas as pd
from datetime import datetime
import time
import pickle
import os

# Add file storage constants
STORAGE_DIR = "data"
STORAGE_FILE = os.path.join(STORAGE_DIR, "uploaded_files.pkl")

# Create storage directory if it doesn't exist
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

# Function to save session state
def save_session_state():
    """Save uploaded files to disk"""
    with open(STORAGE_FILE, 'wb') as f:
        pickle.dump(st.session_state.uploaded_files, f)

# Function to load session state
def load_session_state():
    """Load uploaded files from disk"""
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

# Initialize session state
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = load_session_state()

# Set the title of the app
st.title("FIDO Review Tool")

# Initialize session state for user authentication and navigation
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'page_history' not in st.session_state:
    st.session_state.page_history = ['login']
if 'selected_project' not in st.session_state:
    st.session_state.selected_project = None
if 'current_queue' not in st.session_state:
    st.session_state.current_queue = None

def navigate_to(page):
    """Handle navigation between pages"""
    if page not in st.session_state.page_history:
        st.session_state.page_history.append(page)
    st.rerun()

def show_back_button(prefix=""):
    if len(st.session_state.page_history) > 1:
        # Add prefix to make button ID unique
        if st.button('← Back', key=f"back_button_{prefix}"):
            previous_page = st.session_state.page_history[-2]
            if previous_page == 'login':
                st.session_state.current_user = None
                st.session_state.page_history = ['login']
            else:
                st.session_state.page_history.pop()
            st.rerun()

def get_current_page():
    return st.session_state.page_history[-1] if st.session_state.page_history else 'login'

# Function to display the login panel
def show_login_panel():
    st.subheader("Welcome to the FIDO Review Tool")
    name = st.text_input("Name:")
    role = st.radio("Select your role:", ["Reviewer", "Admin"])
    
    login_button = st.button("Login")
    if login_button and name and role:
        st.session_state.current_user = {"name": name, "role": role}
        st.success(f"Welcome, {name} ({role})")
        navigate_to('main')  # Use navigate_to instead of directly appending
    elif login_button:
        st.error("Please enter your name and select a role.")

# Function to display the main page
def show_main_page():
    show_back_button()
    st.header("Main Page")
    
    # Add custom CSS for modern cards
    st.markdown("""
        <style>
        .main-card {
            background-color: #1e3d59;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        .main-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            background-color: #2a527a;
        }
        .card-title {
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .card-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create layout with modern cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        container = st.container()
        button = st.button("##", key="nonlicensed", label_visibility="collapsed")
        container.markdown("""
            <div class='main-card'>
                <div class='card-icon'>📋</div>
                <div class='card-title'>Non-Licensed<br>FIDO Review</div>
            </div>
        """, unsafe_allow_html=True)
        if button:
            navigate_to('nonlicensed')
    
    with col2:
        container = st.container()
        button = st.button("##", key="licensed", label_visibility="collapsed")
        container.markdown("""
            <div class='main-card'>
                <div class='card-icon'>📜</div>
                <div class='card-title'>Licensed<br>FIDO Review</div>
            </div>
        """, unsafe_allow_html=True)
        if button:
            navigate_to('licensed')
    
    with col3:
        container = st.container()
        button = st.button("##", key="catq", label_visibility="collapsed")
        container.markdown("""
            <div class='main-card'>
                <div class='card-icon'>🔍</div>
                <div class='card-title'>CATQ</div>
            </div>
        """, unsafe_allow_html=True)
        if button:
            navigate_to('catq')
    
    # Add Upload button for admins
    if st.session_state.current_user['role'] == "Admin":
        st.markdown("""
            <style>
            .upload-button {
                background-color: #4CAF50;
                color: white;
                padding: 15px 30px;
                border-radius: 5px;
                text-align: center;
                margin-top: 20px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            .upload-button:hover {
                background-color: #45a049;
            }
            </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📤 Upload New Project", type="primary", key="upload"):
                navigate_to('upload')

def handle_file_upload(uploaded_file, queue_type, project_title):
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            current_time = datetime.now()
            
            # Add metadata columns including uploader
            df['upload_date'] = current_time.strftime("%Y-%m-%d")
            df['status'] = 'Pending Review'
            df['uploader'] = st.session_state.current_user['name']  # Add uploader
            df['reviewer'] = ''
            df['review_date'] = ''
            df['comments'] = ''
            
            formatted_date = current_time.strftime('%Y%m%d_%H%M%S')
            file_key = f"{queue_type}_{project_title}_{formatted_date}"
            
            # Update session state without clearing existing files
            st.session_state.uploaded_files[file_key] = df
            save_session_state()  # Save after upload
            return True
            
        except Exception as e:
            st.error(f"Error uploading file: {str(e)}")
            return False
    return False

# Function to display the admin page
def show_admin_page():
    if st.session_state.current_user and st.session_state.current_user['role'] == "Admin":
        show_back_button('admin')  # Add admin prefix
        st.header("Admin Page")
        
        tab1, tab2 = st.tabs(["Upload Files", "Review Status"])
        
        with tab1:
            st.subheader("Upload New Files")
            queue_type = st.selectbox("Select Queue:", ["Non-licensed", "Licensed", "CATQ"])
            uploaded_file = st.file_uploader("Upload CSV File:", type="csv")
            
            if st.button("Upload Project"):
                if uploaded_file is not None:
                    if handle_file_upload(uploaded_file, queue_type.lower()):
                        st.success(f"File uploaded successfully to {queue_type} queue")
                else:
                    st.error("Please select a file to upload")
        
        with tab2:
            st.subheader("Review Status")
            for file_key, df in st.session_state.uploaded_files.items():
                queue, filename, _ = file_key.split('_', 2)
                with st.expander(f"{filename} ({queue})"):
                    st.dataframe(df)
                    reviewed = len(df[df['status'] == 'Reviewed'])
                    total = len(df)
                    st.progress(reviewed / total)
                    st.text(f"Progress: {reviewed}/{total} records reviewed")
                    
                    # Download button for reviewed data
                    if reviewed > 0:
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="⬇️ Download Reviewed Data",
                            data=csv,
                            file_name=f"Reviewed_{filename}",
                            mime="text/csv"
                        )
    else:
        st.error("Access denied. Admins only.")

def show_reviewer_page(prefix, show_back=True):
    """Show the reviewer interface"""
    queue_type = prefix.split('_')[0]
    queue_files = {k: v for k in st.session_state.uploaded_files.keys() 
                  if k.startswith(queue_type)}
    
    if not queue_files:
        st.info(f"No files available for review in {queue_type} queue")
        return
    
    # Add tabs for reviewing and downloading
    tab1, tab2 = st.tabs(["Review FIDOs", "Download Reviewed"])
    
    with tab1:
        selected_file = st.selectbox(
            "Select file to review:",
            options=list(queue_files.keys()),
            format_func=lambda x: x.split('_')[1],
            key=f"select_{prefix}"
        )
        
        if selected_file:
            df = queue_files[selected_file]
            pending_reviews = df[df['status'] == 'Pending Review']
            
            # Add save all button in sidebar
            with st.sidebar:
                st.markdown("### 🛠️ Controls")
                if st.button("💾 Save All Reviews", key=f"save_all_{prefix}"):
                    st.session_state.uploaded_files[selected_file] = df
                    st.success("✅ All changes saved")
                    st.rerun()
            
            if not pending_reviews.empty:
                st.subheader("Records Pending Review")
                for idx, row in pending_reviews.iterrows():
                    st.markdown(f"### FIDO: {row.get('FIDO', f'Record {idx + 1}')}")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.text(f"UPC: {row.get('BARCODE', 'N/A')}")
                        st.text(f"Brand ID: {row.get('BRAND_ID', 'N/A')}")
                        st.text(f"Original Brand: {row.get('BRAND', 'N/A')}")
                    with col2:
                        st.text(f"Category: {row.get('CATEGORY', 'N/A')}")
                        st.text(f"Description: {row.get('DESCRIPTION', 'N/A')}")
                    
                    # Edit fields with unique keys
                    df.at[idx, 'updated_description'] = st.text_area(
                        "📝 Updated Description", 
                        value=row.get('updated_description', row.get('DESCRIPTION', '')),
                        key=f"desc_{prefix}_{idx}"
                    )
                    df.at[idx, 'updated_category'] = st.text_input(
                        "📦 Updated Category",
                        value=row.get('updated_category', row.get('CATEGORY', '')),
                        key=f"cat_{prefix}_{idx}"
                    )
                    df.at[idx, 'updated_brand'] = st.text_input(
                        "🏷️ Updated Brand",
                        value=row.get('updated_brand', row.get('BRAND', '')),
                        key=f"brand_{prefix}_{idx}"
                    )
                    df.at[idx, 'no_change'] = st.checkbox(
                        "✅ No Change Required",
                        value=row.get('no_change', False),
                        key=f"nochange_{prefix}_{idx}"
                    )
                    df.at[idx, 'comments'] = st.text_input(
                        "🗒️ Comments",
                        value=row.get('comments', ''),
                        key=f"comment_{prefix}_{idx}"
                    )
                    
                    if st.button("Submit Review", key=f"submit_{prefix}_{idx}"):
                        df.at[idx, 'status'] = 'Reviewed'
                        df.at[idx, 'reviewer'] = st.session_state.current_user['name']
                        df.at[idx, 'review_date'] = datetime.now().strftime("%Y-%m-%d")
                        st.session_state.uploaded_files[selected_file] = df
                        save_session_state()
                        st.success(f"✅ Review submitted by {st.session_state.current_user['name']}")
                        st.rerun()
                    
                    st.markdown("---")  # Add separator between records
            else:
                st.success("All records in this file have been reviewed!")
    
    with tab2:
        st.subheader("Download Reviewed FIDOs")
        for file_key, df in queue_files.items():
            reviewed_df = df[df['status'] == 'Reviewed'].copy()
            if not reviewed_df.empty:
                filename = file_key.split('_')[1]
                st.markdown(f"#### {filename}")
                
                # Prepare download data in original format
                download_df = reviewed_df[['FIDO', 'BARCODE', 'BRAND_ID', 'updated_brand', 
                                         'updated_category', 'updated_description', 
                                         'comments', 'reviewer', 'review_date']]
                download_df.columns = ['FIDO', 'BARCODE', 'BRAND_ID', 'BRAND', 
                                     'CATEGORY', 'DESCRIPTION', 
                                     'REVIEW_COMMENTS', 'REVIEWER', 'REVIEW_DATE']
                
                csv = download_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"⬇️ Download {filename} Reviews",
                    data=csv,
                    file_name=f"Reviewed_{filename}",
                    mime="text/csv",
                    key=f"download_{file_key}"
                )
                
                # Show preview
                st.dataframe(download_df)

def show_queue_page(queue_type):
    """Show the review interface for selected project"""
    if not st.session_state.selected_project:
        show_project_selection_page(queue_type)
        return
    
    # Add back button here
    show_back_button(queue_type)
    st.header(f"Reviewing: {st.session_state.selected_project}")
    
    # Show reviewer page without its own back button
    show_reviewer_page(f"{queue_type}_review", show_back=False)

def show_queue_landing_page(queue_type):
    """Show the landing page for a specific queue"""
    show_back_button(f"landing_{queue_type}")
    st.header(f"{queue_type.title()} Projects")
    
    # Filter files for this queue type
    queue_files = {k: v for k in st.session_state.uploaded_files.keys() 
                  if k.startswith(queue_type)}
    
    if queue_type == "nonlicensed":
        # Get unique project names
        project_files = [k.split('_')[1] for k in queue_files.keys()]
        unique_projects = sorted(set(project_files)) if project_files else ["No projects available"]
        
        # Project selection dropdown
        project_category = st.selectbox(
            "Select Project:",
            options=unique_projects,
            key=f"project_select_{queue_type}"
        )
        
        if project_category != "No projects available":
            # Filter files for selected project
            displayed_files = {k: v for k in queue_files.keys() 
                            if k.split('_')[1] == project_category}
            st.subheader(f"📋 {project_category} Files")
            
            # Add admin controls
            if st.session_state.current_user['role'] == "Admin":
                with st.expander("🛠️ Admin Controls"):
                    if st.button("🗑️ Remove Project", key=f"remove_{project_category}"):
                        if st.session_state.current_user['role'] == "Admin":
                            # Remove all files for this project
                            keys_to_remove = [k for k in st.session_state.uploaded_files.keys() 
                                            if k.split('_')[1] == project_category]
                            for key in keys_to_remove:
                                del st.session_state.uploaded_files[key]
                            st.success(f"Project '{project_category}' removed successfully")
                            st.rerun()
                        else:
                            st.error("Only admins can remove projects")
        else:
            displayed_files = {}
    else:
        displayed_files = queue_files
        st.subheader("📋 Available Projects")
    
    if not displayed_files:
        st.info(f"No files available in selected category")
        return

    # Display project cards
    cols = st.columns(2)
    for idx, (file_key, df) in enumerate(displayed_files.items()):
        parts = file_key.split('_')
        project_name = parts[1]
        date_str = parts[-1][:8]
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        
        total_records = len(df)
        reviewed = len(df[df['status'] == 'Reviewed'])
        
        with cols[idx % 2]:
            st.markdown(f"""
                <div class="project-card">
                    <div class="project-title">{project_name}</div>
                    <div class="project-info">Upload Date: {formatted_date}</div>
                    <div class="project-info">Progress: {reviewed}/{total_records} records reviewed</div>
                </div>
            """, unsafe_allow_html=True)
            
            progress = reviewed/total_records if total_records > 0 else 0
            st.progress(progress)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📄 Review", key=f"review_{file_key}"):
                    st.session_state.selected_project = file_key
                    navigate_to(f"{queue_type}_review")
            with col2:
                # Add download button for each file
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download",
                    data=csv,
                    file_name=f"{project_name}_{formatted_date}.csv",
                    mime="text/csv",
                    key=f"download_{file_key}"
                )

def show_upload_section(queue_type):
    st.subheader("📤 Upload New Project")
    
    # Get project title
    project_title = st.text_input(
        "Project Title:",
        key=f"title_{queue_type}_queue",
        placeholder="Enter a descriptive title for this project"
    )
    
    uploaded_file = st.file_uploader(
        "Upload CSV File:", 
        type="csv",
        key=f"upload_{queue_type}_queue"
    )
    
    if st.button("Upload Project", key=f"upload_button_{queue_type}_queue"):
        if uploaded_file is not None and project_title:
            # Use project title instead of filename
            if handle_file_upload(uploaded_file, queue_type, project_title):
                st.success(f"File uploaded successfully to {queue_type} queue")
                st.rerun()
        else:
            st.error("Please provide both a project title and select a file")

def show_upload_page():
    """Dedicated upload page for admins"""
    if st.session_state.current_user['role'] != "Admin":
        st.error("Access denied. Admins only.")
        return
    
    show_back_button('upload')
    st.header("📤 Upload New Project")
    
    # Create tabs for upload and overview
    upload_tab, overview_tab = st.tabs(["Upload New Project", "Project Overview"])
    
    with upload_tab:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Upload CSV File:", 
                type="csv",
                key="admin_upload"
            )
        
        with col2:
            st.markdown('<div style="color: white;">Project Type</div>', 
                       unsafe_allow_html=True)
            queue_type = st.radio(
                "Select queue:",
                ["Non-licensed", "Licensed"],
                horizontal=False,
                label_visibility="collapsed"
            )
            
            st.markdown('<div style="color: white;">Priority Level</div>', 
                       unsafe_allow_html=True)
            priority = st.select_slider(
                "Select priority:",
                options=["Low Priority", "Medium Priority", "High Priority"],
                value="Medium Priority",
                label_visibility="collapsed"
            )
        
        if uploaded_file:
            project_title = uploaded_file.name.rsplit('.', 1)[0]
            st.success("✅ File loaded successfully!")
            st.info(f"Project Title: {project_title}")
            
            if st.button("Upload Project", type="primary"):
                queue_mapping = {
                    "Non-licensed": "nonlicensed",
                    "Licensed": "licensed"
                }
                mapped_queue = queue_mapping[queue_type]
                # Add priority to project title
                project_title = f"{project_title}_{priority.split()[0].lower()}"
                
                if handle_file_upload(uploaded_file, mapped_queue, project_title):
                    st.success(f"✅ Project '{project_title}' uploaded successfully to {queue_type} queue")
                    time.sleep(2)
                    st.rerun()
    
    # Rest of the overview tab code remains the same...
    with overview_tab:
        st.subheader("Current Projects")
        
        # Group projects by queue type
        for queue_type in ["nonlicensed", "licensed"]:
            # Fix the dictionary comprehension
            queue_files = {k: st.session_state.uploaded_files[k] for k in st.session_state.uploaded_files.keys() 
                         if k.startswith(queue_type)}
            
            if queue_files:
                st.markdown(f"### {queue_type.title()} Projects")
                
                for file_key, df in queue_files.items():
                    parts = file_key.split('_')
                    project_name = parts[1]
                    date_str = parts[-1][:8]
                    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    
                    total_records = len(df)
                    reviewed = len(df[df['status'] == 'Reviewed'])
                    
                    # Create expandable section for each project
                    with st.expander(f"📁 {project_name}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.text(f"Upload Date: {formatted_date}")
                            st.text(f"Progress: {reviewed}/{total_records} records reviewed")
                            st.progress(reviewed/total_records if total_records > 0 else 0)
                        
                        with col2:
                            # Add remove button
                            if st.button("🗑️ Remove", key=f"remove_{file_key}"):
                                del st.session_state.uploaded_files[file_key]
                                st.success(f"Removed {project_name}")
                                st.rerun()
                            
                            # Add download button
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="⬇️ Download",
                                data=csv,
                                file_name=f"{project_name}_{formatted_date}.csv",
                                mime="text/csv",
                                key=f"download_{file_key}"
                            )
            else:
                st.info(f"No {queue_type.title()} projects uploaded yet")

def show_project_selection_page(queue_type):
    """Show project selection menu page"""
    show_back_button(f"selection_{queue_type}")
    st.header(f"{queue_type.title()} Projects")
    
    # Filter files for this queue type
    queue_files = {k: v for k, v in st.session_state.uploaded_files.items() 
                  if k.startswith(queue_type)}
    
    if not queue_files:
        st.info(f"No projects available in {queue_type} queue")
        return
    
    # Get unique project names and their statistics
    project_stats = {}
    unique_projects = sorted(set(k.split('_')[1] for k in queue_files.keys()))
    
    # Priority mapping
    priority_map = {
        'high': 'High Priority',
        'medium': 'Medium Priority',
        'low': 'Low Priority'
    }
    
    for project_name in unique_projects:
        project_files = {k: v for k, v in queue_files.items() 
                        if k.split('_')[1] == project_name}
        total_records = sum(len(df) for df in project_files.values())
        reviewed = sum(len(df[df['status'] == 'Reviewed']) for df in project_files.values())
        
        # Extract priority from project name and map to display value
        priority_key = project_name.split('_')[-1].lower()
        priority = priority_map.get(priority_key, 'Unknown Priority')
        
        project_stats[project_name] = {
            'total': total_records,
            'reviewed': reviewed,
            'priority': priority,
            'progress': (reviewed/total_records * 100) if total_records > 0 else 0
        }
    # Create two columns for selection and statistics
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Select Project")
        selected_project = st.selectbox(
            "Choose a project:",
            options=list(project_stats.keys()),
            format_func=lambda x: x.rsplit('_', 1)[0]  # Remove priority from display name
        )
    
    with col2:
        if selected_project:
            st.subheader("Project Statistics")
            stats = project_stats[selected_project]
            
            # Get uploader name from the first file of the project
            project_files = {k: v for k, v in queue_files.items() 
                           if k.split('_')[1] == selected_project}
            first_file = next(iter(project_files.values()))
            uploader = first_file['uploader'].iloc[0]
            
            # Display statistics with uploader info
            st.markdown(f"""
                <div style='padding: 1rem; background-color: #1e3d59; border-radius: 0.5rem; color: white;'>
                    <h3>{selected_project.rsplit('_', 1)[0]}</h3>
                    <p>Uploaded by: {uploader}</p>
                    <p>Priority Level: {stats['priority']}</p>
                    <p>Total Records: {stats['total']}</p>
                    <p>Reviewed: {stats['reviewed']}</p>
                    <p>Progress: {stats['progress']:.1f}%</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.progress(stats['progress']/100)
            
            if st.button("Begin Review", type="primary"):
                st.session_state.selected_project = selected_project
                navigate_to(f"{queue_type}_review")

    # Add admin controls if user is admin
    if st.session_state.current_user['role'] == "Admin":
        st.markdown("---")
        with st.expander("🛠️ Admin Controls"):
            for project_name in unique_projects:  # Now unique_projects is defined
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{project_name}**")
                with col2:
                    if st.button("🗑️ Remove", key=f"remove_{project_name}"):
                        keys_to_remove = [k for k in st.session_state.uploaded_files.keys() 
                                        if k.split('_')[1] == project_name]
                        for key in keys_to_remove:
                            del st.session_state.uploaded_files[key]
                        st.success(f"Removed project: {project_name}")
                        st.rerun()

# Main page routing logic
current_page = get_current_page()

if st.session_state.current_user:
    if current_page == 'admin':
        show_admin_page()
    elif current_page == 'upload':
        show_upload_page()
    elif current_page == 'main':
        show_main_page()
    elif current_page in ['nonlicensed', 'licensed', 'catq']:
        show_project_selection_page(current_page)
    elif current_page.endswith('_review'):
        show_queue_page(current_page.split('_')[0])
else:
    show_login_panel()