import streamlit as st

# Set the title of the app
st.title("FIDO Review Tool")

# Initialize session state for user authentication
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Function to display the login panel
def show_login_panel():
    st.subheader("Welcome to the FIDO Review Tool")
    name = st.text_input("Name:")
    role = st.radio("Select your role:", ["Reviewer", "Admin"])
    
    if st.button("Login"):
        if name and role:
            st.session_state.current_user = {"name": name, "role": role}
            st.success(f"Welcome, {name} ({role})")
            show_main_page()
        else:
            st.error("Please enter your name and select a role.")

# Function to display the main page
def show_main_page():
    st.header("Main Page")
    st.button("Non-licensed FIDO Review Projects")
    st.button("Licensed FIDO Review Projects")
    st.button("CATQ")

# Function to display the admin page
def show_admin_page():
    if st.session_state.current_user and st.session_state.current_user['role'] == "Admin":
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

# Function to toggle between pages based on user authentication
if st.session_state.current_user:
    if st.session_state.current_user['role'] == "Admin":
        show_admin_page()
    else:
        show_main_page()
else:
    show_login_panel()