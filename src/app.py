import streamlit as st
import pandas as pd
from datetime import datetime
import time  # Add this import

# Set the title of the app
st.title("FIDO Review Tool")

# Initialize session state for user authentication and navigation
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'page_history' not in st.session_state:
    st.session_state.page_history = ['login']
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}
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
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])  # Added fourth column for admin upload
    
    with col1:
        if st.button("Non-licensed FIDO Review Projects"):
            navigate_to('nonlicensed')
    with col2:
        if st.button("Licensed FIDO Review Projects"):
            navigate_to('licensed')
    with col3:
        if st.button("CATQ"):
            navigate_to('catq')
    # Add Upload button for admins only
    with col4:
        if st.session_state.current_user['role'] == "Admin":
            if st.button("📤 Upload", type="primary"):
                navigate_to('upload')

def handle_file_upload(uploaded_file, queue_type, project_title):
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            # Add metadata columns
            current_time = datetime.now()
            df['upload_date'] = current_time.strftime("%Y-%m-%d")
            df['status'] = 'Pending Review'
            df['reviewer'] = ''
            df['review_date'] = ''
            df['comments'] = ''
            
            # Create unique file key
            formatted_date = current_time.strftime('%Y%m%d_%H%M%S')
            file_key = f"{queue_type}_{project_title}_{formatted_date}"
            
            # Update session state without clearing existing files
            st.session_state.uploaded_files[file_key] = df
            
            # Force session state to persist
            st.session_state.modified = True
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

def show_reviewer_page(prefix):
    show_back_button(prefix)
    
    queue_type = prefix.split('_')[0]
    queue_files = {k: v for k, v in st.session_state.uploaded_files.items() if k.startswith(queue_type)}
    
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
                        st.success("✅ Review submitted successfully")
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
    show_back_button(queue_type)
    st.header(f"{queue_type.title()} Projects")
    
    # Remove upload tab, only show review projects
    show_reviewer_page(f"{queue_type}_review")

def show_queue_landing_page(queue_type):
    """Show the landing page for a specific queue"""
    show_back_button(f"landing_{queue_type}")
    st.header(f"{queue_type.title()} Projects")
    
    # Filter files for this queue type
    queue_files = {k: v for k, v in st.session_state.uploaded_files.items() 
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
            displayed_files = {k: v for k, v in queue_files.items() 
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
        # Custom CSS for upload form
        st.markdown("""
            <style>
            .upload-container {
                background-color: #1e3d59;
                padding: 2rem;
                border-radius: 0.5rem;
                color: white;
                margin-bottom: 1rem;
            }
            .upload-title, .project-type {
                color: white;
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 1rem;
            }
            .upload-section {
                margin: 1rem 0;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Project details section with dark blue background
        st.markdown("""
            <div class="upload-container">
                <div class="upload-title">Project Details</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Upload CSV File:", 
                type="csv",
                key="admin_upload"
            )
        
        with col2:
            st.markdown('<div class="project-type">Project Type</div>', 
                       unsafe_allow_html=True)
            queue_type = st.radio(
                "Select queue:",
                ["Non-licensed", "Licensed"],
                horizontal=False,
                label_visibility="collapsed"
            )
        
        if uploaded_file:
            # Get file name without extension
            project_title = uploaded_file.name.rsplit('.', 1)[0]
            st.success("✅ File loaded successfully!")
            st.info(f"Project Title: {project_title}")
            
            if st.button("Upload Project", type="primary"):
                # Map radio button selection to queue type
                queue_mapping = {
                    "Non-licensed": "nonlicensed",
                    "Licensed": "licensed"
                }
                
                mapped_queue = queue_mapping[queue_type]
                
                if handle_file_upload(uploaded_file, mapped_queue, project_title):
                    success_message = f"✅ Project '{project_title}' uploaded successfully to {queue_type} queue"
                    st.success(success_message)
                    time.sleep(2)
                    st.rerun()

    with overview_tab:
        st.subheader("Current Projects")
        
        # Group projects by queue type
        for queue_type in ["nonlicensed", "licensed"]:
            queue_files = {k: v for k, v in st.session_state.uploaded_files.items() 
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