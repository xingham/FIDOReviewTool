import streamlit as st
import pandas as pd
from datetime import datetime
import time
import pickle
import os

# Configure page
st.set_page_config(
    page_title="FIDO Review Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for modern styling
st.markdown("""
    <style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        min-height: 100vh;
        transition: all 0.3s ease;
    }
    
    /* CSS Variables for theming */
    :root {
        --bg-primary: #667eea;
        --bg-secondary: #764ba2;
        --card-bg: rgba(255, 255, 255, 0.1);
        --card-hover-bg: rgba(255, 255, 255, 0.15);
        --text-primary: #ffffff;
        --text-secondary: #ffffff;
        --text-muted: #e2e8f0;
        --border-color: rgba(255, 255, 255, 0.2);
        --input-bg: rgba(255, 255, 255, 0.7);
        --input-focus-bg: rgba(255, 255, 255, 0.9);
    }
    
    [data-theme="light"] {
        --bg-primary: #f8fafc;
        --bg-secondary: #e2e8f0;
        --card-bg: rgba(255, 255, 255, 0.9);
        --card-hover-bg: rgba(255, 255, 255, 1);
        --text-primary: #1a202c;
        --text-secondary: #2d3748;
        --text-muted: #4a5568;
        --border-color: rgba(0, 0, 0, 0.1);
        --input-bg: rgba(255, 255, 255, 0.9);
        --input-focus-bg: rgba(255, 255, 255, 1);
    }
    
    /* Theme toggle button */
    .theme-toggle {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--border-color);
        border-radius: 50px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        color: var(--text-secondary);
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .theme-toggle:hover {
        background: var(--card-hover-bg);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Base text sizing */
    .stMarkdown p {
        font-size: 1rem;
        line-height: 1.5;
    }
    
    /* Metric styling */
    .metric-container [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Main container */
    .main > div {
        padding: 2rem;
        background: transparent;
        border-radius: 0px;
        backdrop-filter: none;
        box-shadow: none;
        margin: 1rem;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--text-primary);
        font-weight: 600;
        text-align: center;
    }
    
    h1 {
        color: var(--text-primary);
        text-align: center;
        font-size: 2.2rem;
        margin-bottom: 1.5rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    h2 {
        font-size: 1.8rem;
        margin-bottom: 1.2rem;
    }
    
    h3 {
        font-size: 1.4rem;
        margin-bottom: 1rem;
    }
    
    /* Modern cards */
    .modern-card {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        margin-bottom: 1.5rem;
    }
    
    .modern-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        background: var(--card-hover-bg);
    }
    
    .project-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 2rem;
        color: white;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .project-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    }
    
    .project-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    
    .project-info {
        font-size: 1rem;
        opacity: 0.9;
        margin-bottom: 0.4rem;
    }
    
    /* Stats cards */
    .stats-card {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
        border: 1px solid var(--border-color);
    }
    
    .stats-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .stats-label {
        color: var(--text-muted);
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton > button {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #667eea !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .stButton > button:hover {
        background: rgba(255, 255, 255, 1) !important;
        color: #667eea !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        border-color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Primary buttons (Login, Upload, etc.) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.4);
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid rgba(102, 126, 234, 0.3);
        background: var(--input-bg);
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
        color: #1a202c !important;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        background: var(--input-focus-bg);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        color: #1a202c !important;
    }
    
    /* Placeholder text */
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #6b7280 !important;
        opacity: 0.7;
    }
    
    /* Radio button options */
    .stRadio > div > div > div > label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
    }
    
    /* Select box options */
    .stSelectbox > div > div > select option {
        background: white !important;
        color: #1a202c !important;
    }
    
    /* Input labels */
    .stTextInput > label,
    .stSelectbox > label,
    .stTextArea > label,
    .stRadio > label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Navigation */
    .nav-pill {
        background: rgba(102, 126, 234, 0.1);
        color: #667eea;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        text-decoration: none;
        font-weight: 500;
        margin: 0.25rem;
        display: inline-block;
        transition: all 0.3s ease;
    }
    
    .nav-pill:hover {
        background: #667eea;
        color: white;
        transform: translateY(-2px);
    }
    
    /* Animations */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-slide-in {
        animation: slideIn 0.5s ease-out;
    }
    
    /* Modern tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 12px;
        padding: 12px 24px;
        border: none;
        color: #667eea;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* File uploader */
    .stFileUploader > div {
        border: 2px dashed #667eea;
        border-radius: 12px;
        background: rgba(102, 126, 234, 0.05);
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #764ba2;
        background: rgba(102, 126, 234, 0.1);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border-radius: 12px;
        color: white;
    }
    
    .stError {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        border-radius: 12px;
        color: white;
    }
    
    /* FIDO Card Styles */
    .fido-card {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .fido-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
        background: var(--card-hover-bg);
    }
    
    .fido-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .fido-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }
    
    .fido-status {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-pending {
        background: #fef3c7;
        color: #92400e;
    }
    
    .status-reviewed {
        background: #d1fae5;
        color: #065f46;
    }
    
    .fido-content {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .fido-field {
        margin-bottom: 0.5rem;
    }
    
    .fido-field strong {
        color: var(--text-primary);
        font-weight: 600;
    }
    
    .fido-field span {
        color: var(--text-secondary);
        margin-left: 0.5rem;
    }
    
    .share-link {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 0.25rem 0.5rem;
        font-size: 0.75rem;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .share-link:hover {
        background: var(--card-hover-bg);
        color: var(--text-primary);
    }
    
    .review-actions {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border-color);
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main > div {
            margin: 0.5rem;
            padding: 1rem;
        }
        
        h1 {
            font-size: 2rem;
        }
        
        .project-card {
            padding: 1.5rem;
        }
    }
    </style>
    
    <!-- Theme Toggle Script -->
    <div class="theme-toggle" onclick="toggleTheme()">
        <span id="theme-icon">🌙</span>
        <span id="theme-text">Dark</span>
    </div>
    
    <script>
    function toggleTheme() {
        const body = document.body;
        const currentTheme = body.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        const icon = document.getElementById('theme-icon');
        const text = document.getElementById('theme-text');
        
        body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        if (newTheme === 'light') {
            icon.textContent = '🌞';
            text.textContent = 'Light';
        } else {
            icon.textContent = '🌙';
            text.textContent = 'Dark';
        }
    }
    
    // Handle navigation from clickable cards
    window.addEventListener('message', function(event) {
        if (event.data.type === 'navigate') {
            // Map page names to button keys
            const buttonMap = {
                'nonlicensed': 'nav_nonlicensed',
                'licensed': 'nav_licensed', 
                'catq': 'nav_catq'
            };
            
            const targetButton = buttonMap[event.data.page];
            if (targetButton) {
                // Find button by data-testid or key
                const buttons = document.querySelectorAll('button');
                buttons.forEach(button => {
                    const testId = button.getAttribute('data-testid');
                    if (testId && testId.includes(targetButton)) {
                        button.click();
                        return;
                    }
                });
            }
        }
    });
    
    // Alternative: direct navigation using Streamlit's JavaScript API
    function navigateToPage(page) {
        const buttonMap = {
            'nonlicensed': 'nav_nonlicensed',
            'licensed': 'nav_licensed', 
            'catq': 'nav_catq'
        };
        
        const targetButton = buttonMap[page];
        if (targetButton) {
            // Try to find and click the button
            setTimeout(() => {
                const buttons = document.querySelectorAll('button');
                buttons.forEach(button => {
                    const testId = button.getAttribute('data-testid');
                    if (testId && testId.includes(targetButton)) {
                        button.click();
                    }
                });
            }, 100);
        }
    }
    
    // Auto-scroll to FIDO if URL parameter is present
    function autoScrollToFido() {
        const urlParams = new URLSearchParams(window.location.search);
        const fidoId = urlParams.get('fido');
        if (fidoId) {
            setTimeout(() => {
                const fidoElement = document.getElementById(`fido-${fidoId}`);
                if (fidoElement) {
                    fidoElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    fidoElement.style.border = '3px solid #667eea';
                    fidoElement.style.borderRadius = '12px';
                    fidoElement.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
                }
            }, 1000);
        }
    }
    
    // Initialize theme on page load
    document.addEventListener('DOMContentLoaded', function() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        const icon = document.getElementById('theme-icon');
        const text = document.getElementById('theme-text');
        
        document.body.setAttribute('data-theme', savedTheme);
        
        if (savedTheme === 'light') {
            icon.textContent = '🌞';
            text.textContent = 'Light';
        } else {
            icon.textContent = '🌙';
            text.textContent = 'Dark';
        }
        
        // Auto-scroll to FIDO
        autoScrollToFido();
    });
    
    // Apply theme immediately to prevent flash
    (function() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.body.setAttribute('data-theme', savedTheme);
    })();
    </script>
""", unsafe_allow_html=True)

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
        try:
            with open(STORAGE_FILE, 'rb') as f:
                data = pickle.load(f)
                if isinstance(data, dict):
                    return data
                else:
                    return {}
        except Exception:
            return {}
    return {}

# Function to refresh session state from disk (for real-time updates)
def refresh_session_state():
    """Refresh uploaded files from disk to get latest updates"""
    latest_data = load_session_state()
    st.session_state.uploaded_files = latest_data if isinstance(latest_data, dict) else {}

# Function to find GMV column in a dataframe
def find_gmv_column(df):
    """Find the first column that contains 'GMV' in its name (case insensitive)"""
    if df is None or df.empty:
        return None
    
    for col in df.columns:
        if 'gmv' in str(col).lower():
            return col
    return None

# Function to get GMV sum from a dataframe
def get_gmv_sum(df):
    """Get the sum of GMV values from any GMV-related column"""
    gmv_col = find_gmv_column(df)
    if gmv_col:
        try:
            # Convert to numeric, replacing non-numeric values with 0
            return pd.to_numeric(df[gmv_col], errors='coerce').fillna(0).sum()
        except:
            return 0
    return 0

# Function to get GMV value from a row
def get_gmv_value(row, df_columns=None):
    """Get GMV value from a row, checking for any GMV-related column"""
    if df_columns:
        gmv_col = None
        for col in df_columns:
            if 'gmv' in str(col).lower():
                gmv_col = col
                break
        if gmv_col:
            try:
                return pd.to_numeric(row.get(gmv_col, 0), errors='coerce') or 0
            except:
                return 0
    
    # Fallback: check the row itself for GMV-related keys
    for key in row.index if hasattr(row, 'index') else []:
        if 'gmv' in str(key).lower():
            try:
                return pd.to_numeric(row.get(key, 0), errors='coerce') or 0
            except:
                return 0
    return 0

# Initialize session state
if 'uploaded_files' not in st.session_state or not isinstance(st.session_state.uploaded_files, dict):
    st.session_state.uploaded_files = load_session_state()
    if not isinstance(st.session_state.uploaded_files, dict):
        st.session_state.uploaded_files = {}
else:
    # Refresh data from disk to ensure real-time updates across users
    refresh_session_state()

# Set the title of the app
st.title("🚀 Welcome to FIDO Review Tool")

# Initialize session state for user authentication and navigation
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'page_history' not in st.session_state:
    st.session_state.page_history = ['login']
if 'selected_project' not in st.session_state:
    st.session_state.selected_project = None
if 'current_queue' not in st.session_state:
    st.session_state.current_queue = None

# Handle URL parameters for navigation and deep linking
query_params = st.query_params
if 'fido' in query_params:
    st.session_state.highlighted_fido = query_params['fido']
elif 'highlighted_fido' not in st.session_state:
    st.session_state.highlighted_fido = None

def navigate_to(page):
    """Handle navigation between pages"""
    if page not in st.session_state.page_history:
        st.session_state.page_history.append(page)
    st.rerun()

def show_back_button(prefix=""):
    if len(st.session_state.page_history) > 1:
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
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div style="text-align: center; margin-top: 3rem;">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: white; font-size: 2rem; margin-bottom: 1rem; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3); text-align: center;">🔐 Please Login to Continue</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin-bottom: 2rem; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2); text-align: center;">Enter your credentials to access the FIDO Review Tool</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        name = st.text_input("👤 Full Name:", placeholder="Enter your full name")
        role = st.radio("🔒 Select your role:", ["Reviewer", "Admin"], horizontal=True)
        
        col_a, col_b = st.columns(2)
        with col_b:
            login_button = st.button("🔑 Login", type="primary", use_container_width=True)
        
        if login_button and name and role:
            st.session_state.current_user = {"name": name, "role": role}
            st.success(f"Welcome, {name}! 👋")
            time.sleep(1)
            navigate_to('main')
        elif login_button:
            st.error("Please fill in all fields")

# Function to display the main page
def show_main_page():
    show_back_button()
    
    # Welcome message with user info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 👋 Welcome back, {st.session_state.current_user['name']}")
        st.markdown(f"**Role:** {st.session_state.current_user['role']}")
    
    with col2:
        if st.button("📊 Overview", type="secondary"):
            navigate_to('overview')
    
    st.markdown("---")
    
    # Modern dashboard cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="project-card" onclick="navigateToPage('nonlicensed')">
                <div class="project-title">📋 Non-Licensed</div>
                <div class="project-info">Review non-licensed FIDO items</div>
                <div class="project-info">Click to start reviewing</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="project-card" onclick="navigateToPage('licensed')">
                <div class="project-title">📜 Licensed</div>
                <div class="project-info">Review licensed FIDO items</div>
                <div class="project-info">Click to start reviewing</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="project-card" onclick="navigateToPage('catq')">
                <div class="project-title">🔍 CATQ</div>
                <div class="project-info">Category Quality Review</div>
                <div class="project-info">Click to start reviewing</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Hidden navigation buttons that can be triggered by JavaScript
    col_hidden1, col_hidden2, col_hidden3 = st.columns(3)
    with col_hidden1:
        if st.button("Navigate to Non-Licensed", key="nav_nonlicensed", type="primary"):
            navigate_to('nonlicensed')
    with col_hidden2:
        if st.button("Navigate to Licensed", key="nav_licensed", type="primary"):
            navigate_to('licensed')
    with col_hidden3:
        if st.button("Navigate to CATQ", key="nav_catq", type="primary"):
            navigate_to('catq')
    
    # Hide the navigation buttons with CSS
    st.markdown("""
        <style>
        button[data-testid*="nav_nonlicensed"],
        button[data-testid*="nav_licensed"],
        button[data-testid*="nav_catq"] {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Admin section
    if st.session_state.current_user['role'] == "Admin":
        st.markdown("### 🛠️ Admin Tools")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📤 Upload Project", type="primary", use_container_width=True):
                navigate_to('upload')
        
        with col2:
            if st.button("👥 Admin Panel", type="secondary", use_container_width=True):
                navigate_to('admin')
        
        with col3:
            if st.button("📈 Analytics", type="secondary", use_container_width=True):
                navigate_to('analytics')

def show_overview_page():
    show_back_button('overview')
    st.header("📊 Project Overview Dashboard")

    # Refresh data to ensure we see latest changes from all users
    refresh_session_state()
    
    # Add refresh button
    if st.button("🔄 Refresh Data", help="Refresh to see latest changes from all users"):
        refresh_session_state()
        st.rerun()

    # Gather all projects - visible to ALL users
    all_projects = []
    for file_key, df in st.session_state.uploaded_files.items():
        parts = file_key.split('_')
        if len(parts) < 2:  # Skip malformed keys
            continue
            
        queue_type = parts[0]
        project_name = parts[1]
        date_str = parts[-1][:8] if len(parts[-1]) >= 8 else "00000000"
        try:
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        except (ValueError, IndexError):
            formatted_date = "Unknown"
            
        uploader = df['uploader'].iloc[0] if 'uploader' in df.columns else "Unknown"
        priority = df['priority'].iloc[0] if 'priority' in df.columns else "medium"
        total_records = len(df)
        reviewed = len(df[df['status'] == 'Reviewed'])
        gmv = get_gmv_sum(df)

        all_projects.append({
            "queue_type": queue_type,
            "project_name": project_name,
            "date": formatted_date,
            "uploader": uploader,
            "priority": priority,
            "total": total_records,
            "reviewed": reviewed,
            "progress": (reviewed / total_records * 100) if total_records > 0 else 0,
            "gmv": gmv,
            "file_key": file_key
        })

    if not all_projects:
        st.info("🚀 No projects uploaded yet. Start by uploading your first project!")
        if st.session_state.current_user['role'] == "Admin":
            if st.button("📤 Upload First Project", type="primary"):
                navigate_to('upload')
        return

    # Summary statistics
    total_gmv = sum(p['gmv'] for p in all_projects)
    total_projects = len(all_projects)
    total_records = sum(p['total'] for p in all_projects)
    total_reviewed = sum(p['reviewed'] for p in all_projects)
    avg_progress = (total_reviewed / total_records * 100) if total_records > 0 else 0

    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{total_projects}</div>
                <div class="stats-label">Total Projects</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">${total_gmv:,.0f}</div>
                <div class="stats-label">Total GMV</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{total_records:,}</div>
                <div class="stats-label">Total Records</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{avg_progress:.1f}%</div>
                <div class="stats-label">Avg Progress</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Project grid
    st.subheader("📋 All Projects")
    
    # Add info about project visibility and permissions
    if st.session_state.current_user['role'] == "Admin":
        st.info("👑 **Admin View**: You can see all projects and delete them. Regular reviewers can see all projects but cannot delete them.")
    else:
        st.info("👀 **Reviewer View**: You can see and review all projects uploaded by any user. Only admins can delete projects.")
    
    priority_colors = {
        'high': '#ef4444',
        'medium': '#f59e0b', 
        'low': '#10b981'
    }
    
    priority_map = {
        'high': 'High Priority',
        'medium': 'Medium Priority',
        'low': 'Low Priority'
    }
    
    cols = st.columns(2)
    for idx, proj in enumerate(all_projects):
        priority_color = priority_colors.get(str(proj['priority']).lower(), '#6b7280')
        
        with cols[idx % 2]:
            st.markdown(f"""
                <div class="modern-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h4 style="margin: 0; color: var(--text-primary); font-weight: 600;">{proj['project_name']}</h4>
                        <span style="background: {priority_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem; font-weight: 500;">
                            {priority_map.get(str(proj['priority']).lower(), proj['priority'])}
                        </span>
                    </div>
                    <div style="color: var(--text-secondary); margin-bottom: 1rem; font-weight: 500;">
                        <p style="margin: 0.25rem 0;"><strong>Queue:</strong> {proj['queue_type'].title()}</p>
                        <p style="margin: 0.25rem 0;"><strong>Upload Date:</strong> {proj['date']}</p>
                        <p style="margin: 0.25rem 0;"><strong>Uploader:</strong> {proj['uploader']}</p>
                        <p style="margin: 0.25rem 0;"><strong>GMV:</strong> ${proj['gmv']:,.2f}</p>
                        <p style="margin: 0.25rem 0;"><strong>Progress:</strong> {proj['reviewed']}/{proj['total']} ({proj['progress']:.1f}%)</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Progress bar
            st.progress(proj['progress'] / 100)
            
            # Action buttons
            col_action1, col_action2 = st.columns(2)
            with col_action1:
                if st.button(f"🔍 Review Project", key=f"review_btn_{proj['file_key']}", use_container_width=True):
                    st.session_state.selected_project = proj['file_key']
                    navigate_to(f"{proj['queue_type']}_review")
            
            # Admin delete functionality from overview
            if st.session_state.current_user['role'] == "Admin":
                with col_action2:
                    if st.button(f"🗑️ Delete", key=f"overview_delete_{proj['file_key']}", type="secondary", use_container_width=True):
                        # Show confirmation
                        if f"overview_confirm_delete_{proj['file_key']}" not in st.session_state:
                            st.session_state[f"overview_confirm_delete_{proj['file_key']}"] = True
                            st.warning(f"⚠️ Delete '{proj['project_name']}'?")
                            st.rerun()
                
                # Handle confirmation for overview delete
                if st.session_state.get(f"overview_confirm_delete_{proj['file_key']}", False):
                    col_confirm1, col_confirm2 = st.columns([1, 1])
                    with col_confirm1:
                        if st.button("❌ Cancel", key=f"overview_cancel_{proj['file_key']}", use_container_width=True):
                            del st.session_state[f"overview_confirm_delete_{proj['file_key']}"]
                            st.rerun()
                    with col_confirm2:
                        if st.button("✅ Delete", key=f"overview_confirm_btn_{proj['file_key']}", type="primary", use_container_width=True):
                            # Delete the file
                            if proj['file_key'] in st.session_state.uploaded_files:
                                del st.session_state.uploaded_files[proj['file_key']]
                            
                            # Save the updated state
                            save_session_state()
                            
                            # Refresh to ensure immediate visibility across users
                            refresh_session_state()
                            
                            # Clean up confirmation state
                            if f"overview_confirm_delete_{proj['file_key']}" in st.session_state:
                                del st.session_state[f"overview_confirm_delete_{proj['file_key']}"]
                            
                            st.success(f"✅ Project '{proj['project_name']}' deleted!")
                            time.sleep(1)
                            st.rerun()

def handle_file_upload(uploaded_file, queue_type, project_title, priority="medium"):
    if uploaded_file is not None:
        try:
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            
            # Read the file content to check if it's empty
            content = uploaded_file.read()
            if not content or len(content.strip()) == 0:
                st.error("❌ The uploaded file is empty. Please upload a file with data.")
                return False
            
            # Reset file pointer again for pandas to read
            uploaded_file.seek(0)
            
            # Try to read with different parameters to handle various CSV formats
            try:
                df = pd.read_csv(uploaded_file)
            except pd.errors.EmptyDataError:
                st.error("❌ The CSV file contains no data or has no columns.")
                return False
            except pd.errors.ParserError as pe:
                st.error(f"❌ Error parsing CSV file: {str(pe)}")
                return False
            
            # Check if dataframe is empty
            if df.empty:
                st.error("❌ The CSV file contains no data rows.")
                return False
            
            # Check if dataframe has no columns
            if len(df.columns) == 0:
                st.error("❌ The CSV file has no columns. Please ensure the file has proper headers.")
                return False
            
            current_time = datetime.now()
            
            # Add metadata columns
            df['upload_date'] = current_time.strftime("%Y-%m-%d")
            df['status'] = 'Pending Review'
            df['uploader'] = st.session_state.current_user['name']
            df['reviewer'] = ''
            df['review_date'] = ''
            df['comments'] = ''
            df['priority'] = priority
            
            # Handle GMV - ensure we have a standardized GMV column
            gmv_col = find_gmv_column(df)
            if gmv_col and gmv_col != 'GMV':
                # Copy the GMV column to standardized name and keep original
                df['GMV'] = pd.to_numeric(df[gmv_col], errors='coerce').fillna(0)
            elif not gmv_col:
                # No GMV column found, create one with zeros
                df['GMV'] = 0

            formatted_date = current_time.strftime('%Y%m%d_%H%M%S')
            file_key = f"{queue_type}_{project_title}_{priority}_{formatted_date}"
            
            # Debug: Show what queue this project will be assigned to
            st.info(f"📌 Project will be saved to '{queue_type}' queue with key: {file_key}")
            
            st.session_state.uploaded_files[file_key] = df
            save_session_state()
            
            # Refresh to ensure immediate visibility across users  
            refresh_session_state()
            
            return True
        except Exception as e:
            st.error(f"❌ Error uploading file: {str(e)}")
            st.error("Please ensure your file is a valid CSV with proper headers and data.")
            return False
    return False

def show_upload_page():
    if st.session_state.current_user['role'] != "Admin":
        st.error("🚫 Access denied. Admins only.")
        return
    
    show_back_button('upload')
    st.header("📤 Upload New Project")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.subheader("📁 Project Details")
        
        project_title = st.text_input(
            "📝 Project Title:",
            placeholder="Enter a descriptive project title"
        )
        
        uploaded_file = st.file_uploader(
            "📄 Upload CSV File:",
            type="csv",
            help="Select a CSV file containing FIDO data"
        )
        
        if uploaded_file:
            st.success("✅ File loaded successfully!")
            # Show file preview
            try:
                # Reset file pointer for preview
                uploaded_file.seek(0)
                
                # Check if file has content
                content = uploaded_file.read()
                if not content or len(content.strip()) == 0:
                    st.warning("⚠️ The uploaded file appears to be empty.")
                else:
                    # Reset file pointer for pandas
                    uploaded_file.seek(0)
                    
                    # Try to preview the file
                    try:
                        preview_df = pd.read_csv(uploaded_file)
                        if preview_df.empty:
                            st.warning("⚠️ The CSV file contains no data rows.")
                        elif len(preview_df.columns) == 0:
                            st.warning("⚠️ The CSV file has no columns.")
                        else:
                            st.markdown("**File Preview:**")
                            st.dataframe(preview_df.head(), use_container_width=True)
                            st.info(f"📊 File contains {len(preview_df)} rows and {len(preview_df.columns)} columns")
                    except pd.errors.EmptyDataError:
                        st.warning("⚠️ The CSV file contains no data or has no columns.")
                    except pd.errors.ParserError as pe:
                        st.warning(f"⚠️ Error parsing CSV file: {str(pe)}")
                        
                # Reset file pointer for final upload
                uploaded_file.seek(0)
            except Exception as e:
                st.warning(f"⚠️ Could not preview file: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.subheader("⚙️ Settings")
        
        queue_type = st.selectbox(
            "📋 Queue Type:",
            ["Non-licensed", "Licensed", "CATQ"],
            help="Select the appropriate queue for this project"
        )
        
        priority = st.select_slider(
            "🎯 Priority Level:",
            options=["low", "medium", "high"],
            value="medium",
            format_func=lambda x: f"{'🟢' if x=='low' else '🟡' if x=='medium' else '🔴'} {x.title()} Priority"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Upload button
        if st.button("🚀 Upload Project", type="primary", use_container_width=True):
            if uploaded_file and project_title:
                queue_mapping = {
                    "Non-licensed": "nonlicensed",
                    "Licensed": "licensed", 
                    "CATQ": "catq"
                }
                
                mapped_queue_type = queue_mapping[queue_type]
                if handle_file_upload(uploaded_file, mapped_queue_type, project_title, priority):
                    st.success(f"🎉 Project '{project_title}' uploaded successfully to {queue_type} queue!")
                    time.sleep(2)
                    st.rerun()
            else:
                st.error("❌ Please provide both project title and file")

def show_project_selection_page(queue_type):
    show_back_button(f"selection_{queue_type}")
    st.header(f"📂 {queue_type.title()} Projects")
    
    # Refresh data to ensure we see latest changes from all users
    refresh_session_state()
    
    # Add refresh button for manual updates
    col_refresh, col_info = st.columns([1, 4])
    with col_refresh:
        if st.button("🔄 Refresh", help="Refresh to see latest changes from all users"):
            refresh_session_state()
            st.rerun()
    
    # Add info about project visibility and category filtering
    with col_info:
        if st.session_state.current_user['role'] == "Admin":
            st.info(f"👑 **Admin View**: Only {queue_type} projects are shown here. Projects appear only in their designated category.")
        else:
            st.info(f"👀 **Reviewer View**: Only {queue_type} projects are shown here. All users can see projects regardless of uploader.")
    
    # Filter files for this queue type - show ALL projects to ALL users
    # Fixed: Only show projects that exactly match the queue type (category)
    queue_files = {}
    for k, v in st.session_state.uploaded_files.items():
        parts = k.split('_')
        if len(parts) > 0 and parts[0] == queue_type:
            queue_files[k] = v
    
    # Debug: Show all available file keys for troubleshooting
    if st.session_state.current_user['role'] == "Admin":
        with st.expander("🔧 Debug Info (Admin Only)"):
            st.write("**All uploaded files:**")
            for key in st.session_state.uploaded_files.keys():
                st.write(f"- {key}")
            st.write(f"**Looking for files starting with:** '{queue_type}'")
            st.write(f"**Found {len(queue_files)} matching files**")
    
    if not queue_files:
        st.info(f"📭 No projects available in {queue_type} queue")
        if st.session_state.current_user['role'] == "Admin":
            if st.button("📤 Upload First Project", type="primary"):
                navigate_to('upload')
        return
    
    # Group by project
    projects = {}
    for k, df in queue_files.items():
        parts = k.split('_')
        project_name = parts[1]
        priority = parts[2] if len(parts) > 3 else 'medium'
        
        if project_name not in projects:
            projects[project_name] = {
                'files': [],
                'priority': priority,
                'total': 0,
                'reviewed': 0,
                'gmv': 0,
                'uploader': df['uploader'].iloc[0] if 'uploader' in df.columns else "Unknown"
            }
        
        projects[project_name]['files'].append((k, df))
        projects[project_name]['total'] += len(df)
        projects[project_name]['reviewed'] += len(df[df['status'] == 'Reviewed'])
        projects[project_name]['gmv'] += get_gmv_sum(df)

    # Display projects in modern cards
    cols = st.columns(2)
    priority_colors = {'high': '#ef4444', 'medium': '#f59e0b', 'low': '#10b981'}
    
    for idx, (project_name, data) in enumerate(projects.items()):
        progress = (data['reviewed'] / data['total'] * 100) if data['total'] > 0 else 0
        priority_color = priority_colors.get(data['priority'], '#6b7280')
        
        with cols[idx % 2]:
            st.markdown(f"""
                <div class="modern-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h4 style="margin: 0; color: var(--text-primary); font-weight: 600;">{project_name}</h4>
                        <span style="background: {priority_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem;">
                            {data['priority'].title()}
                        </span>
                    </div>
                    <div style="color: var(--text-secondary); margin-bottom: 1rem; font-weight: 500;">
                        <p style="margin: 0.25rem 0;">👤 <strong>Uploader:</strong> {data['uploader']}</p>
                        <p style="margin: 0.25rem 0;">💰 <strong>GMV:</strong> ${data['gmv']:,.2f}</p>
                        <p style="margin: 0.25rem 0;">📊 <strong>Progress:</strong> {data['reviewed']}/{data['total']} ({progress:.1f}%)</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.progress(progress / 100)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔍 Review", key=f"review_{project_name}", use_container_width=True):
                    st.session_state.selected_project = data['files'][0][0]  # First file key
                    navigate_to(f"{queue_type}_review")
            
            with col_b:
                # Download option
                first_file = data['files'][0][1]
                csv = first_file.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download",
                    data=csv,
                    file_name=f"{project_name}.csv",
                    mime="text/csv",
                    key=f"download_{project_name}",
                    use_container_width=True
                )
            
            # Admin-only delete functionality
            if st.session_state.current_user['role'] == "Admin":
                st.markdown("---")
                col_del1, col_del2 = st.columns([1, 1])
                with col_del2:
                    if st.button("🗑️ Delete Project", key=f"delete_{project_name}", type="secondary", use_container_width=True):
                        # Show confirmation
                        if f"confirm_delete_{project_name}" not in st.session_state:
                            st.session_state[f"confirm_delete_{project_name}"] = True
                            st.warning(f"⚠️ Are you sure you want to delete '{project_name}'? This action cannot be undone!")
                            st.rerun()
                
                # Handle confirmation
                if st.session_state.get(f"confirm_delete_{project_name}", False):
                    col_confirm1, col_confirm2 = st.columns([1, 1])
                    with col_confirm1:
                        if st.button("❌ Cancel", key=f"cancel_delete_{project_name}", use_container_width=True):
                            del st.session_state[f"confirm_delete_{project_name}"]
                            st.rerun()
                    with col_confirm2:
                        if st.button("✅ Confirm Delete", key=f"confirm_delete_btn_{project_name}", type="primary", use_container_width=True):
                            # Delete all files for this project
                            files_to_delete = [file_key for file_key, _ in data['files']]
                            for file_key in files_to_delete:
                                if file_key in st.session_state.uploaded_files:
                                    del st.session_state.uploaded_files[file_key]
                            
                            # Save the updated state
                            save_session_state()
                            
                            # Refresh to ensure immediate visibility across users
                            refresh_session_state()
                            
                            # Clean up confirmation state
                            if f"confirm_delete_{project_name}" in st.session_state:
                                del st.session_state[f"confirm_delete_{project_name}"]
                            
                            st.success(f"✅ Project '{project_name}' has been deleted successfully!")
                            time.sleep(1)
                            st.rerun()

# Enhanced reviewer interface showing all FIDOs
def show_reviewer_page(queue_type):
    if not st.session_state.selected_project:
        show_project_selection_page(queue_type)
        return
    
    show_back_button('reviewer')
    
    # Refresh data to ensure we see latest changes from all users
    refresh_session_state()
    
    # Get project data
    file_key = st.session_state.selected_project
    if file_key not in st.session_state.uploaded_files:
        st.error("❌ Project not found. It may have been deleted.")
        if st.button("← Back to Projects"):
            navigate_to(queue_type)
        return
        
    df = st.session_state.uploaded_files[file_key]
    project_name = file_key.split('_')[1]
    
    st.header(f"🔍 Reviewing: {project_name}")
    
    # Progress indicator
    pending = df[df['status'] == 'Pending Review']
    reviewed = len(df[df['status'] == 'Reviewed'])
    total = len(df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", total)
    with col2:
        st.metric("Reviewed", reviewed)
    with col3:
        st.metric("Remaining", len(pending))
    with col4:
        st.metric("Progress", f"{(reviewed / total * 100):.1f}%" if total > 0 else "0%")
    
    st.progress(reviewed / total if total > 0 else 0)
    
    # Filter options
    col1, col2 = st.columns([1, 1])
    with col1:
        filter_status = st.selectbox(
            "Filter by Status:",
            ["All", "Pending Review", "Reviewed"],
            key="status_filter"
        )
    with col2:
        search_term = st.text_input(
            "Search FIDOs:",
            placeholder="Search by FIDO, UPC, Brand, Category, or Description",
            key="search_filter"
        )
    
    # Apply filters
    filtered_df = df.copy()
    if filter_status != "All":
        filtered_df = filtered_df[filtered_df['status'] == filter_status]
    
    if search_term:
        search_columns = ['FIDO', 'BARCODE', 'BRAND', 'CATEGORY', 'DESCRIPTION']
        mask = pd.Series([False] * len(filtered_df))
        for col in search_columns:
            if col in filtered_df.columns:
                mask |= filtered_df[col].astype(str).str.contains(search_term, case=False, na=False)
        filtered_df = filtered_df[mask]
    
    st.markdown(f"**Showing {len(filtered_df)} of {total} records**")
    
    if filtered_df.empty:
        st.info("No records match your current filters.")
        return
    
    # Show all FIDOs
    for idx, (_, row) in enumerate(filtered_df.iterrows()):
        fido_id = row.get('FIDO', f'record_{idx}')
        status_class = 'status-reviewed' if row['status'] == 'Reviewed' else 'status-pending'
        
        # Create shareable link
        share_url = f"?fido={fido_id}"
        
        st.markdown(f"""
            <div class="fido-card" id="fido-{fido_id}">
                <div class="fido-header">
                    <h4 class="fido-title">📝 FIDO: {fido_id}</h4>
                    <div class="share-link" onclick="navigator.clipboard.writeText(window.location.origin + window.location.pathname + '{share_url}'); alert('Link copied to clipboard!')">
                        🔗 Share
                    </div>
                </div>
                <div class="fido-content">
                    <div>
                        <div class="fido-field"><strong>UPC:</strong><span>{row.get('BARCODE', 'N/A')}</span></div>
                        <div class="fido-field"><strong>Brand ID:</strong><span>{row.get('BRAND_ID', 'N/A')}</span></div>
                        <div class="fido-field"><strong>Original Brand:</strong><span>{row.get('BRAND', 'N/A')}</span></div>
                        <div class="fido-field"><strong>GMV:</strong><span>${get_gmv_value(row, filtered_df.columns):,.2f}</span></div>
                    </div>
                    <div>
                        <div class="fido-field"><strong>Category:</strong><span>{row.get('CATEGORY', 'N/A')}</span></div>
                        <div class="fido-field"><strong>Description:</strong><span>{row.get('DESCRIPTION', 'N/A')}</span></div>
                        <div class="fido-field"><strong>Status:</strong><span class="fido-status {status_class}">{row['status']}</span></div>
                        {f'<div class="fido-field"><strong>Reviewer:</strong><span>{row.get("reviewer", "")}</span></div>' if row.get('reviewer') else ''}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Review form for pending items
        if row['status'] == 'Pending Review':
            with st.container():
                st.markdown('<div class="review-actions">', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    updated_desc = st.text_area(
                        "📝 Updated Description",
                        value=row.get('DESCRIPTION', ''),
                        key=f"desc_{idx}_{fido_id}",
                        height=100
                    )
                    
                    updated_cat = st.text_input(
                        "📦 Updated Category",
                        value=row.get('CATEGORY', ''),
                        key=f"cat_{idx}_{fido_id}"
                    )
                
                with col2:
                    updated_brand = st.text_input(
                        "🏷️ Updated Brand",
                        value=row.get('BRAND', ''),
                        key=f"brand_{idx}_{fido_id}"
                    )
                    
                    comments = st.text_input(
                        "💬 Comments",
                        key=f"comment_{idx}_{fido_id}"
                    )
                
                col_check, col_submit = st.columns([1, 1])
                with col_check:
                    no_change = st.checkbox(
                        "✅ No Change Required", 
                        key=f"nochange_{idx}_{fido_id}"
                    )
                
                with col_submit:
                    if st.button(
                        "✅ Submit Review", 
                        type="primary", 
                        key=f"submit_{idx}_{fido_id}",
                        use_container_width=True
                    ):
                        # Update the dataframe
                        row_index = df.index[df.get('FIDO', df.index) == fido_id].tolist()
                        if not row_index:
                            row_index = [df.index[idx]]
                        
                        actual_idx = row_index[0]
                        df.at[actual_idx, 'updated_description'] = updated_desc
                        df.at[actual_idx, 'updated_category'] = updated_cat
                        df.at[actual_idx, 'updated_brand'] = updated_brand
                        df.at[actual_idx, 'no_change'] = no_change
                        df.at[actual_idx, 'comments'] = comments
                        df.at[actual_idx, 'status'] = 'Reviewed'
                        df.at[actual_idx, 'reviewer'] = st.session_state.current_user['name']
                        df.at[actual_idx, 'review_date'] = datetime.now().strftime("%Y-%m-%d")
                        
                        st.session_state.uploaded_files[file_key] = df
                        save_session_state()
                        
                        # Refresh to ensure immediate visibility across users
                        refresh_session_state()
                        
                        st.success(f"✅ Review submitted for FIDO {fido_id}!")
                        time.sleep(1)
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Show review details for completed items
        elif row['status'] == 'Reviewed':
            with st.expander(f"📋 Review Details for FIDO {fido_id}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Updated Description:** {row.get('updated_description', 'N/A')}")
                    st.markdown(f"**Updated Category:** {row.get('updated_category', 'N/A')}")
                with col2:
                    st.markdown(f"**Updated Brand:** {row.get('updated_brand', 'N/A')}")
                    st.markdown(f"**Comments:** {row.get('comments', 'N/A')}")
                st.markdown(f"**No Change Required:** {'Yes' if row.get('no_change') else 'No'}")
                st.markdown(f"**Reviewed by:** {row.get('reviewer', 'N/A')} on {row.get('review_date', 'N/A')}")
    
    # Download section
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Download All Results", type="primary", use_container_width=True):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Complete Dataset",
                data=csv,
                file_name=f"Complete_{project_name}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if reviewed > 0:
            reviewed_df = df[df['status'] == 'Reviewed']
            csv_reviewed = reviewed_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Reviewed Only",
                data=csv_reviewed,
                file_name=f"Reviewed_{project_name}.csv",
                mime="text/csv",
                use_container_width=True
            )

# Main routing
current_page = get_current_page()

if st.session_state.current_user:
    if current_page == 'main':
        show_main_page()
    elif current_page == 'overview':
        show_overview_page()
    elif current_page == 'upload':
        show_upload_page()
    elif current_page in ['nonlicensed', 'licensed', 'catq']:
        show_project_selection_page(current_page)
    elif current_page.endswith('_review'):
        show_reviewer_page(current_page.split('_')[0])
else:
    show_login_panel()