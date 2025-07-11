import streamlit as st

# Set the title of the app
st.title("FIDO Review Tool")

# Initialize session state for user authentication and navigation
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'previous_page' not in st.session_state:
    st.session_state.previous_page = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'

def navigate_to(page):
    st.session_state.previous_page = st.session_state.current_page
    st.session_state.current_page = page
    st.experimental_rerun()

def show_back_button():
    if st.session_state.previous_page:
        col1, col2 = st.columns([1, 9])
        with col1:
            if st.button('← Back'):
                temp = st.session_state.current_page
                st.session_state.current_page = st.session_state.previous_page
                st.session_state.previous_page = temp
                st.experimental_rerun()

# Function to display the login panel
def show_login_panel():
    st.subheader("Welcome to the FIDO Review Tool")
    name = st.text_input("Name:")
    role = st.radio("Select your role:", ["Reviewer", "Admin"])
    
    if st.button("Login"):
        if name and role:
            st.session_state.current_user = {"name": name, "role": role}
            st.success(f"Welcome, {name} ({role})")
            navigate_to('main')
        else:
            st.error("Please enter your name and select a role.")

# Function to display the main page
def show_main_page():
    show_back_button()
    st.header("Main Page")
    if st.button("Non-licensed FIDO Review Projects"):
        navigate_to('nonlicensed')
    if st.button("Licensed FIDO Review Projects"):
        navigate_to('licensed')
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
if st.session_state.current_user:
    if st.session_state.current_page == 'admin':
        show_admin_page()
    elif st.session_state.current_page == 'main':
        show_main_page()
    elif st.session_state.current_page in ['nonlicensed', 'licensed', 'catq']:
        show_back_button()
        st.header(f"{st.session_state.current_page.title()} Projects")
else:
    show_login_panel()