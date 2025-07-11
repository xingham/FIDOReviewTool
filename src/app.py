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

def show_back_button():
    if st.session_state.previous_page:
        if st.button('← Back'):
            # Swap current and previous page
            temp = st.session_state.current_page
            st.session_state.current_page = st.session_state.previous_page
            st.session_state.previous_page = temp

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
            show_main_page()
        else:
            st.error("Please enter your name and select a role.")

# Function to display the main page
def show_main_page():
    st.header("Main Page")
    show_back_button()
    st.button("Non-licensed FIDO Review Projects")
    st.button("Licensed FIDO Review Projects")
    st.button("CATQ")

# Function to display the admin page
def show_admin_page():
    if st.session_state.current_user and st.session_state.current_user['role'] == "Admin":
        st.header("Admin Page")
        show_back_button()
        st.selectbox("Select Queue:", ["Non-licensed", "Licensed", "CATQ"])
        uploaded_file = st.file_uploader("Upload CSV File:", type="csv")
        if st.button("Upload Project"):
            if uploaded_file is not None:
                st.success("Project uploaded successfully.")
            else:
                st.error("Please select a file to upload.")
    else:
        st.error("Access denied. Admins only.")

# Function to toggle between pages based on user authentication and current page
if st.session_state.current_user:
    if st.session_state.current_page == 'admin':
        show_admin_page()
    else:
        show_main_page()
else:
    show_login_panel()