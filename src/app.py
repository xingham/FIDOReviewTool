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
        color: #704968;
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
    .stProgress > div > div {
        background-color: #e5e7eb !important;
        border-radius: 10px !important;
        height: 12px !important;
        margin: 0.5rem 0 !important;
        border: 1px solid #d1d5db !important;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
        height: 12px !important;
        box-shadow: none !important;
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
        background: #ff6b35 !important;
        color: #ffffff !important;
        border: 2px solid #e55a2b !important;
        font-weight: 700 !important;
        box-shadow: 0 3px 8px rgba(255, 107, 53, 0.4) !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
        padding: 0.4rem 0.8rem !important;
        border-radius: 25px !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.5px !important;
    }
    
    .status-reviewed {
        background: #22c55e !important;
        color: #ffffff !important;
        border: 2px solid #16a34a !important;
        font-weight: 700 !important;
        box-shadow: 0 3px 8px rgba(34, 197, 94, 0.4) !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
        padding: 0.4rem 0.8rem !important;
        border-radius: 25px !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.5px !important;
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
    
    // Copy to clipboard function with fallback
    function copyToClipboard(path, description) {
        const fullUrl = window.location.origin + window.location.pathname + path;
        
        // Try modern clipboard API first
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(fullUrl).then(() => {
                alert(`✅ Link copied to clipboard for ${description}!`);
            }).catch(err => {
                console.error('Failed to copy: ', err);
                fallbackCopyTextToClipboard(fullUrl, description);
            });
        } else {
            // Fallback for older browsers or non-secure contexts
            fallbackCopyTextToClipboard(fullUrl, description);
        }
    }
    
    // Fallback copy function
    function fallbackCopyTextToClipboard(text, description) {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        
        // Avoid scrolling to bottom
        textArea.style.top = "0";
        textArea.style.left = "0";
        textArea.style.position = "fixed";
        textArea.style.opacity = "0";
        
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                alert(`✅ Link copied to clipboard for ${description}!`);
            } else {
                alert(`❌ Failed to copy link. Please copy manually: ${text}`);
            }
        } catch (err) {
            console.error('Fallback copy failed: ', err);
            alert(`❌ Copy failed. Please copy manually: ${text}`);
        }
        
        document.body.removeChild(textArea);
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
    try:
        # Ensure directory exists
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)
        
        # Create a backup before saving
        if os.path.exists(STORAGE_FILE):
            backup_file = STORAGE_FILE + ".backup"
            import shutil
            shutil.copy2(STORAGE_FILE, backup_file)
        
        with open(STORAGE_FILE, 'wb') as f:
            pickle.dump(st.session_state.uploaded_files, f)
        
        # Verify the save was successful
        if os.path.exists(STORAGE_FILE):
            # Try to load it back to verify integrity
            with open(STORAGE_FILE, 'rb') as f:
                test_data = pickle.load(f)
                if not isinstance(test_data, dict):
                    raise ValueError("Saved data is not a dictionary")
        
    except Exception as e:
        st.error(f"❌ Error saving session state: {e}")
        # Try to restore from backup if available
        backup_file = STORAGE_FILE + ".backup"
        if os.path.exists(backup_file):
            import shutil
            shutil.copy2(backup_file, STORAGE_FILE)
            st.warning("⚠️ Restored from backup due to save error")

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
                    st.warning("⚠️ Invalid data format in storage file")
                    return {}
        except Exception as e:
            st.error(f"❌ Error loading session state: {e}")
            # Try to load from backup
            backup_file = STORAGE_FILE + ".backup"
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, 'rb') as f:
                        data = pickle.load(f)
                        if isinstance(data, dict):
                            st.warning("⚠️ Loaded from backup due to corrupted main file")
                            return data
                except Exception:
                    pass
            return {}
    return {}

# Function to refresh session state from disk (for real-time updates)
def refresh_session_state():
    """Refresh uploaded files from disk to get latest updates"""
    try:
        latest_data = load_session_state()
        if isinstance(latest_data, dict):
            st.session_state.uploaded_files = latest_data
        else:
            st.warning("⚠️ Could not refresh session state - invalid data format")
    except Exception as e:
        st.error(f"❌ Error refreshing session state: {e}")

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
            numeric_series = pd.to_numeric(df[gmv_col], errors='coerce').fillna(0)
            total = float(numeric_series.sum())
            return total
        except Exception as e:
            st.error(f"❌ Error calculating GMV sum: {e}")
            return 0.0
    return 0.0

# Function to get GMV value from a row
def get_gmv_value(row, df_columns=None):
    """Get GMV value from a row, checking for any GMV-related column"""
    if df_columns is not None and len(df_columns) > 0:
        gmv_col = None
        for col in df_columns:
            if 'gmv' in str(col).lower():
                gmv_col = col
                break
        if gmv_col:
            try:
                value = pd.to_numeric(row.get(gmv_col, 0), errors='coerce')
                return float(value) if pd.notna(value) else 0.0
            except Exception as e:
                # Use st.write instead of print for Streamlit visibility
                st.error(f"❌ Error getting GMV value from '{gmv_col}': {e}")
                return 0.0
    
    # Fallback: check the row itself for GMV-related keys
    if hasattr(row, 'index'):
        for key in row.index:
            if 'gmv' in str(key).lower():
                try:
                    value = pd.to_numeric(row.get(key, 0), errors='coerce')
                    return float(value) if pd.notna(value) else 0.0
                except Exception as e:
                    st.error(f"❌ Error getting GMV value from key '{key}': {e}")
                    return 0.0
    return 0.0

# Function to extract relevant category (part after last ">")
def get_relevant_category(category_hierarchy):
    """Extract the relevant category from a hierarchical category string"""
    if not category_hierarchy or pd.isna(category_hierarchy):
        return ''
    
    category_str = str(category_hierarchy).strip()
    if '>' in category_str:
        # Split by ">" and get the last part, stripping whitespace
        return category_str.split('>')[-1].strip()
    else:
        # If no ">" found, return the original category
        return category_str

# Initialize session state
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = load_session_state()
    if not isinstance(st.session_state.uploaded_files, dict):
        st.session_state.uploaded_files = {}
else:
    # Don't automatically refresh on every page load - only when explicitly requested
    # This prevents losing data during normal navigation
    pass

# Ensure all existing projects have claim columns (but don't save immediately)
needs_update = False
for file_key, df in st.session_state.uploaded_files.items():
    if 'claimed_by' not in df.columns:
        df['claimed_by'] = ''
        needs_update = True
    if 'claimed_date' not in df.columns:
        df['claimed_date'] = ''
        needs_update = True
    if 'project_status' not in df.columns:
        df['project_status'] = 'Available'
        needs_update = True
    st.session_state.uploaded_files[file_key] = df

# Only save if we actually made changes
if needs_update:
    save_session_state()

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
    st.session_state.highlighted_fido = query_params.get('fido')
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
    # Sign out button instead of back button for main page
    col_signout, col_spacer = st.columns([1, 5])
    with col_signout:
        if st.button('🚪 Sign Out', key="signout_button"):
            st.session_state.current_user = None
            st.session_state.page_history = ['login']
            st.success("👋 Signed out successfully!")
            time.sleep(1)
            st.rerun()
    
    # Welcome message with user info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 👋 Welcome back, {st.session_state.current_user['name']}")
        st.markdown(f"**Role:** {st.session_state.current_user['role']}")
    
    with col2:
        if st.button("📊 Overview", type="secondary"):
            navigate_to('overview')
    
    st.markdown("---")
    
    # Modern dashboard cards as buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Non-Licensed", 
                     key="card_nonlicensed", 
                     use_container_width=True,
                     help="Navigate to Non-Licensed projects"):
            navigate_to('nonlicensed')
    
    with col2:
        if st.button("📜 Licensed", 
                     key="card_licensed", 
                     use_container_width=True,
                     help="Navigate to Licensed projects"):
            navigate_to('licensed')
    
    with col3:
        if st.button("🔍 CATQ", 
                     key="card_catq", 
                     use_container_width=True,
                     help="Navigate to CATQ projects"):
            navigate_to('catq')
    
    # Custom CSS to style the card buttons with glassmorphism effects
    st.markdown("""
        <style>
        /* Enhanced glassmorphism styling for card buttons */
        button[data-testid*="card_nonlicensed"],
        button[data-testid*="card_licensed"], 
        button[data-testid*="card_catq"] {
            background: rgba(255, 255, 255, 0.15) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            color: white !important;
            margin-bottom: 1.5rem !important;
            transition: all 0.3s ease !important;
            cursor: pointer !important;
            min-height: 180px !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            line-height: 1.5 !important;
            text-align: center !important;
            white-space: pre-line !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        /* Add gradient overlay for better visual appeal */
        button[data-testid*="card_nonlicensed"]:before,
        button[data-testid*="card_licensed"]:before,
        button[data-testid*="card_catq"]:before {
            content: '' !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%) !important;
            border-radius: 16px !important;
            z-index: -1 !important;
        }
        
        button[data-testid*="card_nonlicensed"]:hover,
        button[data-testid*="card_licensed"]:hover,
        button[data-testid*="card_catq"]:hover {
            transform: translateY(-8px) scale(1.02) !important;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3) !important;
            background: rgba(255, 255, 255, 0.25) !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            color: white !important;
        }
        
        button[data-testid*="card_nonlicensed"]:hover:before,
        button[data-testid*="card_licensed"]:hover:before,
        button[data-testid*="card_catq"]:hover:before {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.4) 0%, rgba(118, 75, 162, 0.4) 100%) !important;
        }
        
        button[data-testid*="card_nonlicensed"]:focus,
        button[data-testid*="card_licensed"]:focus,
        button[data-testid*="card_catq"]:focus {
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3), 0 15px 35px rgba(0, 0, 0, 0.25) !important;
            transform: translateY(-5px) !important;
            outline: none !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
            background: rgba(255, 255, 255, 0.2) !important;
            color: white !important;
        }
        
        /* Override any conflicting Streamlit button styles */
        div[data-testid="column"] button[data-testid*="card_"] {
            background: rgba(255, 255, 255, 0.15) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
        }
        
        div[data-testid="column"] button[data-testid*="card_"]:hover {
            background: rgba(255, 255, 255, 0.25) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            transform: translateY(-8px) scale(1.02) !important;
        }
        
        div[data-testid="column"] button[data-testid*="card_"]:focus {
            background: rgba(255, 255, 255, 0.2) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
        }
        
        /* Ensure no dark backgrounds override our styling */
        button[data-testid*="card_"].stButton > button,
        .stButton button[data-testid*="card_"] {
            background: rgba(255, 255, 255, 0.15) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
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
    
    # Sort projects by priority (high -> medium -> low)
    priority_order = {'high': 3, 'medium': 2, 'low': 1}
    sorted_projects = sorted(all_projects, key=lambda x: priority_order.get(str(x['priority']).lower(), 0), reverse=True)
    
    cols = st.columns(2)
    for idx, proj in enumerate(sorted_projects):
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
                    <div style="margin-top: 1rem; margin-bottom: 1rem;">
                        <div style="background-color: #e5e7eb; border-radius: 10px; height: 12px; border: 1px solid #d1d5db; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; width: {proj['progress']}%; border-radius: 10px; transition: width 0.3s ease;"></div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Action buttons inside the card area (but outside the HTML since Streamlit buttons need to be separate)
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
            st.subheader("🔍 GMV Column Detection")
            gmv_col = find_gmv_column(df)
            if gmv_col and gmv_col != 'GMV':
                # Copy the GMV column to standardized name and keep original
                try:
                    df['GMV'] = pd.to_numeric(df[gmv_col], errors='coerce').fillna(0)
                    st.success(f"✅ Copied '{gmv_col}' to standardized 'GMV' column")
                except Exception as e:
                    st.error(f"❌ Error processing GMV column {gmv_col}: {e}")
                    df['GMV'] = 0.0
            elif not gmv_col:
                # No GMV column found, create one with zeros
                df['GMV'] = 0.0
                st.warning("⚠️ No GMV column found - created 'GMV' column with zeros")
            else:
                # GMV column exists, ensure it's numeric
                try:
                    df['GMV'] = pd.to_numeric(df['GMV'], errors='coerce').fillna(0)
                    st.success("✅ Existing 'GMV' column processed and validated")
                except Exception as e:
                    st.error(f"❌ Error processing existing GMV column: {e}")
                    df['GMV'] = 0.0

            formatted_date = current_time.strftime('%Y%m%d_%H%M%S')
            file_key = f"{queue_type}_{project_title}_{priority}_{formatted_date}"
            
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
    
    # Add refresh button and search bar for manual updates
    col_refresh, col_search, col_info = st.columns([1, 2, 2])
    with col_refresh:
        if st.button("🔄 Refresh", help="Refresh to see latest changes from all users"):
            refresh_session_state()
            st.rerun()
    
    with col_search:
        search_query = st.text_input(
            "🔍 Search Projects",
            placeholder="Search by project name...",
            key=f"project_search_{queue_type}",
            help="Filter projects by name"
        )
    
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
        
        # Extract date from file key as fallback
        date_str = parts[-1].split('_')[0] if '_' in parts[-1] and len(parts[-1].split('_')[0]) == 8 else "00000000"
        try:
            if len(date_str) == 8 and date_str.isdigit():
                fallback_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            else:
                fallback_date = "Unknown"
        except (ValueError, IndexError):
            fallback_date = "Unknown"
        
        # Use actual upload_date from dataframe if available, otherwise use fallback
        if 'upload_date' in df.columns and not df['upload_date'].empty:
            formatted_date = df['upload_date'].iloc[0]
        else:
            formatted_date = fallback_date
        
        # Ensure claim columns exist
        if 'claimed_by' not in df.columns:
            df['claimed_by'] = ''
        if 'claimed_date' not in df.columns:
            df['claimed_date'] = ''
        if 'project_status' not in df.columns:
            df['project_status'] = 'Available'
        
        if project_name not in projects:
            projects[project_name] = {
                'files': [],
                'priority': priority,
                'total': 0,
                'reviewed': 0,
                'gmv': 0,
                'uploader': df['uploader'].iloc[0] if 'uploader' in df.columns else "Unknown",
                'date': formatted_date,
                'claimed_by': df['claimed_by'].iloc[0] if 'claimed_by' in df.columns and not df['claimed_by'].iloc[0] == '' else None,
                'claimed_date': df['claimed_date'].iloc[0] if 'claimed_date' in df.columns and not df['claimed_date'].iloc[0] == '' else None,
                'project_status': df['project_status'].iloc[0] if 'project_status' in df.columns else 'Available'
            }
        
        projects[project_name]['files'].append((k, df))
        projects[project_name]['total'] += len(df)
        projects[project_name]['reviewed'] += len(df[df['status'] == 'Reviewed'])
        projects[project_name]['gmv'] += get_gmv_sum(df)

    # Display projects in modern cards
    cols = st.columns(2)
    priority_colors = {'high': '#ef4444', 'medium': '#f59e0b', 'low': '#10b981'}
    
    # Sort projects by priority (high -> medium -> low)
    priority_order = {'high': 3, 'medium': 2, 'low': 1}
    sorted_projects = sorted(projects.items(), key=lambda x: priority_order.get(x[1]['priority'], 0), reverse=True)
    
    # Apply search filter if search query is provided
    if search_query:
        filtered_projects = []
        for project_name, data in sorted_projects:
            if search_query.lower() in project_name.lower():
                filtered_projects.append((project_name, data))
        sorted_projects = filtered_projects
    
    # Show search results info
    if search_query:
        if sorted_projects:
            st.success(f"🔍 Found {len(sorted_projects)} project(s) matching '{search_query}'")
        else:
            st.warning(f"❌ No projects found matching '{search_query}'. Try a different search term.")
            return
    
    for idx, (project_name, data) in enumerate(sorted_projects):
        progress = (data['reviewed'] / data['total'] * 100) if data['total'] > 0 else 0
        priority_color = priority_colors.get(data['priority'], '#6b7280')
        
        # Determine project status display
        status_info = ""
        if data.get('claimed_by'):
            claimed_date = data.get('claimed_date', 'Unknown')
            status_info = f"<p style='margin: 0.25rem 0;'><strong>🎯 Reviewing:</strong> {data['claimed_by']} (claimed {claimed_date})</p>"
        else:
            status_info = "<p style='margin: 0.25rem 0;'><strong>📌 Status:</strong> Available for review</p>"
        
        with cols[idx % 2]:
            st.markdown(f"""
                <div class="modern-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h4 style="margin: 0; color: var(--text-primary); font-weight: 600;">{project_name}</h4>
                        <span style="background: {priority_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem; font-weight: 500;">
                            {data['priority'].title()}
                        </span>
                    </div>
                    <div style="color: var(--text-secondary); margin-bottom: 1rem; font-weight: 500;">
                        <p style="margin: 0.25rem 0;"><strong>Queue:</strong> {queue_type.title()}</p>
                        <p style="margin: 0.25rem 0;"><strong>Upload Date:</strong> {data['date']}</p>
                        <p style="margin: 0.25rem 0;"><strong>Uploader:</strong> {data['uploader']}</p>
                        {status_info}
                        <p style="margin: 0.25rem 0;"><strong>GMV:</strong> ${data['gmv']:,.2f}</p>
                        <p style="margin: 0.25rem 0;"><strong>Progress:</strong> {data['reviewed']}/{data['total']} ({progress:.1f}%)</p>
                    </div>
                    <div style="margin-top: 1rem; margin-bottom: 1rem;">
                        <div style="background-color: #e5e7eb; border-radius: 10px; height: 12px; border: 1px solid #d1d5db; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; width: {progress}%; border-radius: 10px; transition: width 0.3s ease;"></div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Action buttons inside the card area (but outside the HTML since Streamlit buttons need to be separate)
            col_action1, col_action2 = st.columns(2)
            
            with col_action1:
                if st.button("� Review", key=f"review_{project_name}", use_container_width=True):
                    # Automatically claim the project when reviewing
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    for file_key, df in data['files']:
                        df['claimed_by'] = st.session_state.current_user['name']
                        df['claimed_date'] = current_date
                        df['project_status'] = 'Claimed'
                        st.session_state.uploaded_files[file_key] = df
                    save_session_state()
                    refresh_session_state()
                    
                    st.session_state.selected_project = data['files'][0][0]  # First file key
                    navigate_to(f"{queue_type}_review")
            
            with col_action2:
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
            
            # Admin delete button (also inside the card)
            if st.session_state.current_user['role'] == "Admin":
                if st.button("🗑️ Delete Project", key=f"delete_{project_name}", type="secondary", use_container_width=True):
                    # Show confirmation
                    if f"confirm_delete_{project_name}" not in st.session_state:
                        st.session_state[f"confirm_delete_{project_name}"] = True
                        st.warning(f"⚠️ Are you sure you want to delete '{project_name}'? This action cannot be undone!")
                        st.rerun()
            
            # Handle confirmation for project delete
            if st.session_state.get(f"confirm_delete_{project_name}", False):
                col_confirm1, col_confirm2 = st.columns([1, 1])
                with col_confirm1:
                    if st.button("❌ Cancel", key=f"cancel_{project_name}", use_container_width=True):
                        del st.session_state[f"confirm_delete_{project_name}"]
                        st.rerun()
                with col_confirm2:
                    if st.button("✅ Delete", key=f"confirm_btn_{project_name}", type="primary", use_container_width=True):
                        # Delete all files for this project
                        for file_key, _ in data['files']:
                            if file_key in st.session_state.uploaded_files:
                                del st.session_state.uploaded_files[file_key]
                        
                        # Save the updated state
                        save_session_state()
                        
                        # Refresh to ensure immediate visibility across users
                        refresh_session_state()
                        
                        # Clean up confirmation state
                        if f"confirm_delete_{project_name}" in st.session_state:
                            del st.session_state[f"confirm_delete_{project_name}"]
                        
                        st.success(f"✅ Project '{project_name}' deleted!")
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
            st.subheader("🔍 GMV Column Detection")
            gmv_col = find_gmv_column(df)
            if gmv_col and gmv_col != 'GMV':
                # Copy the GMV column to standardized name and keep original
                try:
                    df['GMV'] = pd.to_numeric(df[gmv_col], errors='coerce').fillna(0)
                    st.success(f"✅ Copied '{gmv_col}' to standardized 'GMV' column")
                except Exception as e:
                    st.error(f"❌ Error processing GMV column {gmv_col}: {e}")
                    df['GMV'] = 0.0
            elif not gmv_col:
                # No GMV column found, create one with zeros
                df['GMV'] = 0.0
                st.warning("⚠️ No GMV column found - created 'GMV' column with zeros")
            else:
                # GMV column exists, ensure it's numeric
                try:
                    df['GMV'] = pd.to_numeric(df['GMV'], errors='coerce').fillna(0)
                    st.success("✅ Existing 'GMV' column processed and validated")
                except Exception as e:
                    st.error(f"❌ Error processing existing GMV column: {e}")
                    df['GMV'] = 0.0

            formatted_date = current_time.strftime('%Y%m%d_%H%M%S')
            file_key = f"{queue_type}_{project_title}_{priority}_{formatted_date}"
            
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

def show_analytics_page():
    if st.session_state.current_user['role'] != "Admin":
        st.error("🚫 Access denied. Admins only.")
        return
        
    show_back_button('analytics')
    st.header("📈 Analytics Dashboard")

    # Refresh data to ensure we see latest changes from all users
    refresh_session_state()
    
    # Add refresh button
    if st.button("🔄 Refresh Data", help="Refresh to see latest analytics data"):
        refresh_session_state()
        st.rerun()

    # Collect all project data for analytics
    all_projects = []
    detailed_analytics = []
    
    for file_key, df in st.session_state.uploaded_files.items():
        parts = file_key.split('_')
        if len(parts) < 2:
            continue
            
        queue_type = parts[0]
        project_name = parts[1]
        uploader = df['uploader'].iloc[0] if 'uploader' in df.columns else "Unknown"
        
        # Basic project stats
        total_records = len(df)
        reviewed = len(df[df['status'] == 'Reviewed'])
        gmv = get_gmv_sum(df)
        
        # Advanced FIDO Analytics for reviewed items only
        reviewed_df = df[df['status'] == 'Reviewed']
        total_reviewed = len(reviewed_df)
        
        if total_reviewed > 0:
            # GMV calculations
            beginning_gmv = get_gmv_sum(reviewed_df)  # Total GMV of reviewed FIDOs
            
            # Calculate various update counts
            total_updated = 0
            category_only_updated = 0
            brand_only_updated = 0
            both_updated = 0
            no_updates = 0
            description_updated = 0
            
            # GMV breakdowns
            category_only_gmv = 0
            brand_only_gmv = 0
            both_updated_gmv = 0
            no_updates_gmv = 0
            
            # Special movements
            brand_id_null_moved = 0
            false_positive_moved = 0
            
            for _, row in reviewed_df.iterrows():
                row_gmv = get_gmv_value(row, list(reviewed_df.columns))
                
                # Check if category was updated
                category_changed = (str(row.get('CATEGORY', '')) != str(row.get('updated_category', '')))
                
                # Check if brand was updated
                brand_changed = (str(row.get('BRAND', '')) != str(row.get('updated_brand', '')))
                
                # Check if description was updated
                desc_changed = (str(row.get('DESCRIPTION', '')) != str(row.get('updated_description', '')))
                
                # Check if marked as no change
                no_change = row.get('no_change', False)
                
                # Count updates
                if not no_change and (category_changed or brand_changed or desc_changed):
                    total_updated += 1
                
                if desc_changed:
                    description_updated += 1
                
                # Categorize update types
                if category_changed and brand_changed:
                    both_updated += 1
                    both_updated_gmv += row_gmv
                elif category_changed and not brand_changed:
                    category_only_updated += 1
                    category_only_gmv += row_gmv
                elif brand_changed and not category_changed:
                    brand_only_updated += 1
                    brand_only_gmv += row_gmv
                else:
                    no_updates += 1
                    no_updates_gmv += row_gmv
                
                # Special cases
                if str(row.get('BRAND_ID', '')).lower() in ['null', 'none', '']:
                    brand_id_null_moved += 1
                
                # Check for false positive (simplified - could be enhanced with more logic)
                if 'false' in str(row.get('comments', '')).lower() and 'positive' in str(row.get('comments', '')).lower():
                    false_positive_moved += 1
            
            # Calculate ending GMV and changes
            removed_gmv = 0  # Simplified - would need more complex logic to determine removed FIDOs
            added_gmv_null = 0  # Simplified
            added_gmv_false_pos = 0  # Simplified
            added_fido_gmv = 0  # Simplified
            ending_gmv = beginning_gmv  # Simplified
            net_change_gmv = ending_gmv - beginning_gmv
        else:
            # No reviews completed yet
            beginning_gmv = removed_gmv = added_gmv_null = added_gmv_false_pos = 0
            added_fido_gmv = ending_gmv = net_change_gmv = 0
            total_updated = category_only_updated = brand_only_updated = both_updated = no_updates = 0
            category_only_gmv = brand_only_gmv = both_updated_gmv = no_updates_gmv = 0
            description_updated = brand_id_null_moved = false_positive_moved = 0
        
        # Percentages
        pct_total_updated = (total_updated / total_reviewed * 100) if total_reviewed > 0 else 0
        pct_category_only = (category_only_updated / total_reviewed * 100) if total_reviewed > 0 else 0
        pct_brand_only = (brand_only_updated / total_reviewed * 100) if total_reviewed > 0 else 0
        pct_both_updated = (both_updated / total_reviewed * 100) if total_reviewed > 0 else 0
        pct_no_updates = (no_updates / total_reviewed * 100) if total_reviewed > 0 else 0
        pct_description_updated = (description_updated / total_reviewed * 100) if total_reviewed > 0 else 0
        
        # Totals check
        totals_check_number = category_only_updated + brand_only_updated + both_updated + no_updates
        totals_check_tf = "T" if totals_check_number == total_reviewed else "F"
        
        detailed_analytics.append({
            "project_name": project_name,
            "queue_type": queue_type,
            "uploader": uploader,
            
            # FIDO GMV STATS
            "beginning_fido_gmv": beginning_gmv,
            "removed_gmv": removed_gmv,
            "added_gmv_null": added_gmv_null,
            "added_gmv_false_pos": added_gmv_false_pos,
            "added_fido_gmv": added_fido_gmv,
            "ending_fido_gmv": ending_gmv,
            "net_change_gmv": net_change_gmv,
            
            # FIDO STATS
            "total_fidos_reviewed": total_reviewed,
            "total_fidos_updated": total_updated,
            "pct_total_updated": pct_total_updated,
            "brand_id_null_moved": brand_id_null_moved,
            "false_positive_moved": false_positive_moved,
            
            # CATEGORY UPDATED ONLY
            "category_only_count": category_only_updated,
            "pct_category_only": pct_category_only,
            "gmv_category_only": category_only_gmv,
            
            # BRAND UPDATED ONLY
            "brand_only_count": brand_only_updated,
            "pct_brand_only": pct_brand_only,
            "gmv_brand_only": brand_only_gmv,
            
            # CATEGORY & BRAND UPDATED
            "both_updated_count": both_updated,
            "pct_both_updated": pct_both_updated,
            "gmv_both_updated": both_updated_gmv,
            
            # NO UPDATES NEEDED
            "no_updates_count": no_updates,
            "pct_no_updates": pct_no_updates,
            "gmv_no_updates": no_updates_gmv,
            
            # DESCRIPTION UPDATES
            "description_updated_count": description_updated,
            "pct_description_updated": pct_description_updated,
            
            # TOTALS CHECK
            "totals_check_number": totals_check_number,
            "totals_check_tf": totals_check_tf
        })
        
        # Keep basic project info for summary
        all_projects.append({
            "queue_type": queue_type,
            "project_name": project_name,
            "uploader": uploader,
            "total": total_records,
            "reviewed": reviewed,
            "progress": (reviewed / total_records * 100) if total_records > 0 else 0,
            "gmv": gmv
        })
    
    if not all_projects:
        st.info("📊 No projects available for analytics.")
        return
    
    # Analytics metrics summary
    total_gmv = sum(p['gmv'] for p in all_projects)
    total_projects = len(all_projects)
    total_records = sum(p['total'] for p in all_projects)
    total_reviewed = sum(p['reviewed'] for p in all_projects)
    avg_progress = (total_reviewed / total_records * 100) if total_records > 0 else 0
    
    # Summary cards
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
                <div class="stats-label">Overall Progress</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed FIDO Analytics Table
    st.subheader("📊 Detailed FIDO Analytics")
    
    if detailed_analytics:
        import pandas as pd
        
        # Create comprehensive analytics DataFrame
        analytics_df = pd.DataFrame(detailed_analytics)
        
        # Display table with all requested metrics
        st.markdown("### 🎯 FIDO GMV Statistics")
        gmv_cols = ['project_name', 'beginning_fido_gmv', 'removed_gmv', 'added_gmv_null', 
                   'added_gmv_false_pos', 'added_fido_gmv', 'ending_fido_gmv', 'net_change_gmv']
        
        gmv_display = analytics_df[gmv_cols].copy()
        gmv_display.columns = ['Project', 'Beginning GMV', 'Removed GMV', 'Added GMV (Null)', 
                              'Added GMV (False+)', 'Added FIDO GMV', 'Ending GMV', 'Net Change']
        
        # Format currency columns
        currency_cols = ['Beginning GMV', 'Removed GMV', 'Added GMV (Null)', 'Added GMV (False+)', 
                        'Added FIDO GMV', 'Ending GMV', 'Net Change']
        for col in currency_cols:
            gmv_display[col] = gmv_display[col].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(gmv_display, use_container_width=True)
        
        st.markdown("### 📈 FIDO Update Statistics")
        fido_cols = ['project_name', 'total_fidos_reviewed', 'total_fidos_updated', 'pct_total_updated',
                    'brand_id_null_moved', 'false_positive_moved']
        
        fido_display = analytics_df[fido_cols].copy()
        fido_display.columns = ['Project', 'Total Reviewed', 'Total Updated', '% Updated',
                               'Brand ID Null Moved', 'False Positive Moved']
        fido_display['% Updated'] = fido_display['% Updated'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(fido_display, use_container_width=True)
        
        st.markdown("### 🏷️ Category & Brand Update Analysis")
        update_cols = ['project_name', 'category_only_count', 'pct_category_only', 'gmv_category_only',
                      'brand_only_count', 'pct_brand_only', 'gmv_brand_only',
                      'both_updated_count', 'pct_both_updated', 'gmv_both_updated',
                      'no_updates_count', 'pct_no_updates', 'gmv_no_updates']
        
        update_display = analytics_df[update_cols].copy()
        update_display.columns = ['Project', 'Cat Only #', 'Cat Only %', 'Cat Only GMV',
                                 'Brand Only #', 'Brand Only %', 'Brand Only GMV',
                                 'Both Updated #', 'Both Updated %', 'Both Updated GMV',
                                 'No Updates #', 'No Updates %', 'No Updates GMV']
        
        # Format percentage and currency columns
        pct_cols = ['Cat Only %', 'Brand Only %', 'Both Updated %', 'No Updates %']
        for col in pct_cols:
            update_display[col] = update_display[col].apply(lambda x: f"{x:.1f}%")
        
        gmv_cols = ['Cat Only GMV', 'Brand Only GMV', 'Both Updated GMV', 'No Updates GMV']
        for col in gmv_cols:
            update_display[col] = update_display[col].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(update_display, use_container_width=True)
        
        st.markdown("### 📝 Description Updates & Validation")
        desc_cols = ['project_name', 'description_updated_count', 'pct_description_updated',
                    'totals_check_number', 'totals_check_tf']
        
        desc_display = analytics_df[desc_cols].copy()
        desc_display.columns = ['Project', 'Description Updated #', 'Description Updated %',
                               'Totals Check Number', 'Totals Check T/F']
        desc_display['Description Updated %'] = desc_display['Description Updated %'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(desc_display, use_container_width=True)
        
        # Download option for detailed analytics
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            # Prepare comprehensive export
            export_df = analytics_df.copy()
            
            # Rename columns to match requested format
            export_df = export_df.rename(columns={
                'beginning_fido_gmv': 'Beginning FIDO GMV (Correct Brand)',
                'removed_gmv': 'Removed GMV (Incorrectly Assigned FIDOs)',
                'added_gmv_null': 'Added GMV from Brand ID Null',
                'added_gmv_false_pos': 'Added GMV from False Positive Brand Match',
                'added_fido_gmv': 'Added FIDO GMV',
                'ending_fido_gmv': 'Ending FIDO GMV',
                'net_change_gmv': 'Net Change of FIDO GMV',
                'total_fidos_reviewed': 'Total FIDOs Reviewed',
                'total_fidos_updated': 'Total # of FIDOs Updated',
                'pct_total_updated': '% Total FIDOs Updated',
                'brand_id_null_moved': '# of Brand ID Null FIDOs moved to brand',
                'false_positive_moved': '# of False Positive Brand Match FIDOs moved to brand',
                'category_only_count': '# of FIDOs where ONLY Category was Updated',
                'pct_category_only': '% of Total FIDOs where ONLY Category was Updated',
                'gmv_category_only': 'GMV if ONLY Category was Updated',
                'brand_only_count': '# of FIDOs where ONLY Brand was Updated',
                'pct_brand_only': '% of Total FIDOs where ONLY Brand was Updated',
                'gmv_brand_only': 'GMV if ONLY Brand was Updated',
                'both_updated_count': '# of FIDOs where Category & Brand were BOTH Updated',
                'pct_both_updated': '% of Total FIDOs where Category & Brand were BOTH Updated',
                'gmv_both_updated': 'GMV if Category & Brand were BOTH Updated in Same FIDO',
                'no_updates_count': '# of FIDOs where Category & Brand were NOT changed',
                'pct_no_updates': '% of Total FIDOs where Category & Brand were NOT changed',
                'gmv_no_updates': 'GMV if Category & Brand were NOT changed',
                'description_updated_count': 'FIDO Description Updated',
                'pct_description_updated': '% FIDO Description Updated',
                'totals_check_number': 'Totals Check - Number',
                'totals_check_tf': 'Totals Check - T or F'
            })
            
            csv = export_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Detailed Analytics",
                data=csv,
                file_name="FIDO_Detailed_Analytics.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Summary totals
            total_reviewed = analytics_df['total_fidos_reviewed'].sum()
            total_updated = analytics_df['total_fidos_updated'].sum()
            total_gmv_change = analytics_df['net_change_gmv'].sum()
            
            st.markdown(f"""
                <div class="stats-card">
                    <div class="stats-number">{total_reviewed:,}</div>
                    <div class="stats-label">Total FIDOs Reviewed</div>
                </div>
            """, unsafe_allow_html=True)
    
    else:
        st.info("📊 No detailed analytics available. Complete some reviews first!")
    
    st.markdown("---")
    
    # Basic analytics charts (existing functionality)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Progress by Queue Type")
        queue_stats = {}
        for proj in all_projects:
            queue = proj['queue_type']
            if queue not in queue_stats:
                queue_stats[queue] = {'total': 0, 'reviewed': 0}
            queue_stats[queue]['total'] += proj['total']
            queue_stats[queue]['reviewed'] += proj['reviewed']
        
        for queue, stats in queue_stats.items():
            progress = (stats['reviewed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            st.write(f"**{queue.title()}**: {stats['reviewed']}/{stats['total']} ({progress:.1f}%)")
            st.progress(progress / 100)
    
    with col2:
        st.subheader("💰 GMV by Queue Type")
        queue_gmv = {}
        for proj in all_projects:
            queue = proj['queue_type']
            if queue not in queue_gmv:
                queue_gmv[queue] = 0
            queue_gmv[queue] += proj['gmv']
        
        for queue, gmv in queue_gmv.items():
            percentage = (gmv / total_gmv * 100) if total_gmv > 0 else 0
            st.write(f"**{queue.title()}**: ${gmv:,.2f} ({percentage:.1f}%)")

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
        mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
        
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
                    <div class="share-link" onclick="copyToClipboard('{share_url}', 'FIDO {fido_id}')">
                        🔗 Share
                    </div>
                </div>
                <div class="fido-content">
                    <div>
                        <div class="fido-field"><strong>UPC:</strong><span>{row.get('BARCODE', 'N/A')}</span></div>
                        <div class="fido-field"><strong>Brand ID:</strong><span>{row.get('BRAND_ID', 'N/A')}</span></div>
                        <div class="fido-field"><strong>Original Brand:</strong><span>{row.get('BRAND', 'N/A')}</span></div>
                        <div class="fido-field"><strong>GMV:</strong><span>${get_gmv_value(row, list(filtered_df.columns)):,.2f}</span></div>
                    </div>
                    <div>
                        <div class="fido-field"><strong>Original Category:</strong><span>{row.get('CATEGORY', 'N/A')}</span></div>
                        <div class="fido-field"><strong>Original Description:</strong><span>{row.get('DESCRIPTION', 'N/A')}</span></div>
                        <div class="fido-field"><strong>Status:</strong><span class="fido-status {status_class}">{row['status']}</span></div>""" + (f"""
                        <div class="fido-field"><strong>Reviewer:</strong><span>{str(row.get("reviewer", ""))}</span></div>""" if row.get('reviewer') else "") + """
                    </div>
                </div>""" + (f"""
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color);">
                    <h5 style="margin: 0 0 0.5rem 0; color: var(--text-primary); font-weight: 600;">📋 Updated Information:</h5>
                    <div class="fido-content">
                        <div>
                            <div class="fido-field"><strong>Updated Brand:</strong><span>{row.get('updated_brand', 'N/A')}</span></div>
                            <div class="fido-field"><strong>Updated Category:</strong><span>{row.get('updated_category', 'N/A')}</span></div>
                        </div>
                        <div>
                            <div class="fido-field"><strong>Updated Description:</strong><span>{row.get('updated_description', 'N/A')}</span></div>
                            <div class="fido-field"><strong>Comments:</strong><span>{row.get('comments', 'N/A')}</span></div>
                        </div>
                    </div>
                    <div class="fido-field"><strong>No Change Required:</strong><span>{'Yes' if row.get('no_change') else 'No'}</span></div>
                    <div class="fido-field"><strong>Review Date:</strong><span>{row.get('review_date', 'N/A')}</span></div>
                </div>""" if row['status'] == 'Reviewed' else "") + """
            </div>
        """, unsafe_allow_html=True)
        
        # Review form for pending items OR editing reviewed items
        if row['status'] == 'Pending Review' or row['status'] == 'Reviewed':
            with st.container():
                # For reviewed items, use an expander to keep interface clean
                if row['status'] == 'Reviewed':
                    with st.expander("🔽 Edit Review", expanded=False):
                        st.markdown('<div class="review-actions">', unsafe_allow_html=True)
                        show_review_form = True
                else:
                    # For pending reviews, show form directly
                    st.markdown('<div class="review-actions">', unsafe_allow_html=True)
                    show_review_form = True
                
                if show_review_form:
                    col1, col2 = st.columns(2)
                    
                    # Pre-populate with existing updated values if available, handle NaN/None values
                    current_updated_desc = row.get('updated_description', '')
                    if pd.isna(current_updated_desc) or current_updated_desc == 'nan':
                        current_updated_desc = row.get('DESCRIPTION', '')
                        if pd.isna(current_updated_desc) or current_updated_desc == 'nan':
                            current_updated_desc = ''
                    
                    current_updated_cat = row.get('updated_category', '')
                    if pd.isna(current_updated_cat) or current_updated_cat == 'nan':
                        current_updated_cat = get_relevant_category(row.get('CATEGORY', ''))
                        if pd.isna(current_updated_cat) or current_updated_cat == 'nan':
                            current_updated_cat = ''
                    
                    current_updated_brand = row.get('updated_brand', '')
                    if pd.isna(current_updated_brand) or current_updated_brand == 'nan':
                        current_updated_brand = row.get('BRAND', '')
                        if pd.isna(current_updated_brand) or current_updated_brand == 'nan':
                            current_updated_brand = ''
                    
                    current_comments = row.get('comments', '')
                    if pd.isna(current_comments) or current_comments == 'nan':
                        current_comments = ''
                    
                    current_no_change = row.get('no_change', False)
                    if pd.isna(current_no_change):
                        current_no_change = False
                    
                    with col1:
                        updated_desc = st.text_area(
                            "📝 Updated Description",
                            value=current_updated_desc,
                            key=f"desc_{idx}_{fido_id}",
                            height=100
                        )
                        
                        updated_cat = st.text_input(
                            "📦 Updated Category",
                            value=current_updated_cat,
                            key=f"cat_{idx}_{fido_id}"
                        )
                    
                    with col2:
                        updated_brand = st.text_input(
                            "🏷️ Updated Brand",
                            value=current_updated_brand,
                            key=f"brand_{idx}_{fido_id}"
                        )
                        
                        comments = st.text_input(
                            "💬 Comments",
                            value=current_comments,
                            key=f"comment_{idx}_{fido_id}"
                        )
                    
                    col_check, col_submit = st.columns([1, 1])
                    with col_check:
                        no_change = st.checkbox(
                            "✅ No Change Required", 
                            value=current_no_change,
                            key=f"nochange_{idx}_{fido_id}"
                        )
                    
                    with col_submit:
                        button_text = "💾 Update Review" if row['status'] == 'Reviewed' else "✅ Submit Review"
                        if st.button(
                            button_text, 
                            type="primary", 
                            key=f"submit_{idx}_{fido_id}",
                            use_container_width=True
                        ):
                            # Check if user made changes to the data
                            original_desc = row.get('DESCRIPTION', '')
                            original_cat = get_relevant_category(row.get('CATEGORY', ''))
                            original_brand = row.get('BRAND', '')
                            
                            desc_changed = updated_desc != original_desc
                            cat_changed = updated_cat != original_cat
                            brand_changed = updated_brand != original_brand
                            has_comments = comments.strip() != ''
                            
                            changes_made = desc_changed or cat_changed or brand_changed or has_comments
                            
                            # Validation: Prevent conflicting selections
                            if changes_made and no_change:
                                st.error("❌ You cannot make changes to the FIDO data AND select 'No Change Required'. Please either make changes OR select 'No Change Required', but not both.")
                                st.stop()
                            
                            # Validation: Must make changes OR select no change
                            if not changes_made and not no_change:
                                st.error("❌ Please make changes to the FIDO data OR check 'No Change Required' before submitting.")
                                st.stop()
                            
                            # Update the dataframe
                            try:
                                # Find the correct row index
                                if 'FIDO' in df.columns:
                                    row_mask = df['FIDO'] == fido_id
                                    matching_rows = df[row_mask]
                                    if not matching_rows.empty:
                                        actual_idx = matching_rows.index[0]
                                    else:
                                        # Fallback to using the enumeration index
                                        actual_idx = df.index[idx]
                                else:
                                    actual_idx = df.index[idx]
                                
                                # DON'T update the original columns - keep them as-is
                                # Only store in updated columns for tracking changes
                                df.at[actual_idx, 'updated_description'] = updated_desc
                                df.at[actual_idx, 'updated_category'] = updated_cat
                                df.at[actual_idx, 'updated_brand'] = updated_brand
                                df.at[actual_idx, 'no_change'] = no_change
                                df.at[actual_idx, 'comments'] = comments
                                df.at[actual_idx, 'status'] = 'Reviewed'
                                df.at[actual_idx, 'reviewer'] = st.session_state.current_user['name']
                                df.at[actual_idx, 'review_date'] = datetime.now().strftime("%Y-%m-%d")
                                
                            except Exception as e:
                                st.error(f"❌ Error updating row: {e}")
                                continue
                            
                            st.session_state.uploaded_files[file_key] = df
                            save_session_state()
                            
                            # Refresh to ensure immediate visibility across users
                            refresh_session_state()
                            
                            action_text = "updated" if row['status'] == 'Reviewed' else "submitted"
                            st.success(f"✅ Review {action_text} for FIDO {fido_id}!")
                            time.sleep(1)
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
    
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
    elif current_page == 'analytics':
        show_analytics_page()
    elif current_page in ['nonlicensed', 'licensed', 'catq']:
        show_project_selection_page(current_page)
    elif current_page.endswith('_review'):
        show_reviewer_page(current_page.split('_')[0])
else:
    show_login_panel()