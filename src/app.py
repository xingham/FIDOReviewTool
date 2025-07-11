import streamlit as st
import pandas as pd
from datetime import datetime

# Set the title of the app
st.title("FIDO Review Tool")

# Initialize session state for user authentication and navigation
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'page_history' not in st.session_state:
    st.session_state.page_history = ['login']
# Add new session state for uploaded files
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}

def navigate_to(page):
    if page not in st.session_state.page_history:
        st.session_state.page_history.append(page)
    st.rerun()  # Updated from experimental_rerun()

def show_back_button():
    if len(st.session_state.page_history) > 1:
        if st.button('← Back'):
            previous_page = st.session_state.page_history[-2]  # Get previous page
            if previous_page == 'login':
                # Clear user session and go back to login
                st.session_state.current_user = None
                st.session_state.page_history = ['login']
            else:
                # Normal back navigation
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
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Non-licensed FIDO Review Projects"):
            navigate_to('nonlicensed')
    with col2:
        if st.button("Licensed FIDO Review Projects"):
            navigate_to('licensed')
    with col3:
        if st.button("CATQ"):
            navigate_to('catq')

def handle_file_upload(uploaded_file, queue_type):
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            # Add metadata columns
            df['upload_date'] = datetime.now().strftime("%Y-%m-%d")
            df['status'] = 'Pending Review'
            df['reviewer'] = ''
            df['review_date'] = ''
            df['comments'] = ''
            
            # Store in session state with unique key
            file_key = f"{queue_type}_{uploaded_file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.uploaded_files[file_key] = df
            return True
        except Exception as e:
            st.error(f"Error uploading file: {str(e)}")
            return False
    return False

# Function to display the admin page
def show_admin_page():
    if st.session_state.current_user and st.session_state.current_user['role'] == "Admin":
        show_back_button()
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

def show_reviewer_page(queue_type):
    show_back_button()
    st.header(f"{queue_type.title()} Projects Review")
    
    # Filter files for this queue
    queue_files = {k: v for k, v in st.session_state.uploaded_files.items() if k.startswith(queue_type)}
    
    if not queue_files:
        st.info(f"No files available for review in {queue_type} queue")
        return
    
    # File selection
    selected_file = st.selectbox(
        "Select file to review:",
        options=list(queue_files.keys()),
        format_func=lambda x: x.split('_')[1]
    )
    
    if selected_file:
        df = queue_files[selected_file]
        pending_reviews = df[df['status'] == 'Pending Review']
        
        # Add save all button in sidebar
        with st.sidebar:
            st.markdown("### 🛠️ Controls")
            if st.button("💾 Save All Reviews"):
                st.session_state.uploaded_files[selected_file] = df
                st.success("✅ All changes saved")
                st.rerun()
        
        if not pending_reviews.empty:
            st.subheader("Records Pending Review")
            for idx, row in pending_reviews.iterrows():
                with st.expander(f"FIDO: {row.get('FIDO', f'Record {idx + 1}')}"):
                    # Display original values
                    st.text(f"UPC: {row.get('BARCODE', 'N/A')}")
                    st.text(f"Brand ID: {row.get('BRAND_ID', 'N/A')}")
                    st.text(f"Original Brand: {row.get('BRAND', 'N/A')}")
                    st.text(f"Category: {row.get('CATEGORY', 'N/A')}")
                    st.text(f"Description: {row.get('DESCRIPTION', 'N/A')}")
                    
                    # Edit fields
                    df.at[idx, 'updated_description'] = st.text_area(
                        "📝 Updated Description", 
                        value=row.get('updated_description', row.get('DESCRIPTION', '')),
                        key=f"desc_{idx}"
                    )
                    df.at[idx, 'updated_category'] = st.text_input(
                        "📦 Updated Category",
                        value=row.get('updated_category', row.get('CATEGORY', '')),
                        key=f"cat_{idx}"
                    )
                    df.at[idx, 'updated_brand'] = st.text_input(
                        "🏷️ Updated Brand",
                        value=row.get('updated_brand', row.get('BRAND', '')),
                        key=f"brand_{idx}"
                    )
                    df.at[idx, 'no_change'] = st.checkbox(
                        "✅ No Change Required",
                        value=row.get('no_change', False),
                        key=f"nochange_{idx}"
                    )
                    df.at[idx, 'comments'] = st.text_input(
                        "🗒️ Comments",
                        value=row.get('comments', ''),
                        key=f"comment_{idx}"
                    )
                    
                    if st.button("Submit Review", key=f"submit_{idx}"):
                        df.at[idx, 'status'] = 'Reviewed'
                        df.at[idx, 'reviewer'] = st.session_state.current_user['name']
                        df.at[idx, 'review_date'] = datetime.now().strftime("%Y-%m-%d")
                        st.session_state.uploaded_files[selected_file] = df
                        st.success("✅ Review submitted successfully")
                        st.rerun()
        else:
            st.success("All records in this file have been reviewed!")

def show_queue_page(queue_type):
    show_back_button()
    st.header(f"{queue_type.title()} Projects")
    
    # Add tabs for different views
    tab1, tab2 = st.tabs(["Review Projects", "Upload New Project"])
    
    with tab1:
        show_reviewer_page(queue_type)
    
    with tab2:
        if st.session_state.current_user['role'] == "Admin":
            st.subheader("Upload New Project")
            uploaded_file = st.file_uploader(
                "Upload CSV File:", 
                type="csv",
                key=f"upload_{queue_type}"  # Unique key for each queue
            )
            
            if st.button("Upload Project", key=f"upload_button_{queue_type}"):
                if uploaded_file is not None:
                    if handle_file_upload(uploaded_file, queue_type):
                        st.success(f"File uploaded successfully to {queue_type} queue")
                else:
                    st.error("Please select a file to upload")
        else:
            st.warning("Only administrators can upload new projects")

# Main page routing logic
current_page = get_current_page()

if st.session_state.current_user:
    if current_page == 'admin':
        show_admin_page()
    elif current_page == 'main':
        show_main_page()
    elif current_page in ['nonlicensed', 'licensed', 'catq']:
        show_queue_page(current_page)
else:
    show_login_panel()