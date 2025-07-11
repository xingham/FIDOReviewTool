import streamlit as st

# Set the title of the app
st.title("FIDO Review Tool")

# Initialize session state for user authentication and navigation
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'page_history' not in st.session_state:
    st.session_state.page_history = ['login']

def navigate_to(page):
    if page not in st.session_state.page_history:
        st.session_state.page_history.append(page)
    st.rerun()  # Updated from experimental_rerun()

def show_back_button():
    if len(st.session_state.page_history) > 1:
        if st.button('← Back'):
            st.session_state.page_history.pop()  # Remove current page
            st.rerun()  # Updated from experimental_rerun()

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
        st.session_state.page_history.append('main')
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

# Function to display the admin page
def show_admin_page():
    if st.session_state.current_user and st.session_state.current_user['role'] == "Admin":
        show_back_button()
        st.header("Admin Page")
        st.selectbox("Select Queue:", ["Non-licensed", "Licensed", "CATQ"])
        uploaded_file = st.file_uploader("Upload CSV File:", type="csv")
        if st.button("Upload Project"):
            if uploaded_file is not None:
                st.success("Project uploaded successfully.")
            else:
                st.error("Please select a file to upload.")
    else:
        st.error("Access denied. Admins only.")

# Main page routing logic
current_page = get_current_page()

if st.session_state.current_user:
    if current_page == 'admin':
        show_admin_page()
    elif current_page == 'main':
        show_main_page()
    elif current_page in ['nonlicensed', 'licensed', 'catq']:
        show_back_button()
        st.header(f"{current_page.title()} Projects")
else:
    show_login_panel()