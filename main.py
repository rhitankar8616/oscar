import streamlit as st
from database.db_manager import DatabaseManager
from components.auth import render_auth
from components.dashboard import render_dashboard
from components.expenses import render_expenses
from components.dates import render_dates
from components.budget import render_budget
from components.friends import render_friends
from components.analytics import render_analytics
from components.profile import render_profile

# Page config
st.set_page_config(
    page_title="OSCAR - Smart Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, classy AI-like design
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Main app background - dark with subtle gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
    }
    
    /* Sidebar styling - glassmorphism effect */
    [data-testid="stSidebar"] {
        background: rgba(20, 20, 20, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    
    /* Sidebar navigation items */
    [data-testid="stSidebar"] .stRadio > label {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 18px !important;
        margin: 6px 0 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stSidebar"] .stRadio > label:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(0, 255, 170, 0.3);
        transform: translateX(4px);
        box-shadow: 0 4px 16px rgba(0, 255, 170, 0.1);
    }
    
    /* Remove radio button circles */
    [data-testid="stSidebar"] .stRadio > label > div:first-child {
        display: none !important;
    }
    
    /* Selected navigation item - no border, just background glow */
    [data-testid="stSidebar"] .stRadio input:checked + div {
        background: linear-gradient(135deg, rgba(0, 255, 170, 0.15) 0%, rgba(0, 212, 170, 0.1) 100%) !important;
        border: none !important;
        box-shadow: 0 0 20px rgba(0, 255, 170, 0.2) !important;
    }
    
    /* Main content area */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        background: linear-gradient(135deg, #ffffff 0%, #00ffaa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h3 {
        font-size: 1.5rem !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* Text colors */
    p, span, label, .stMarkdown {
        color: rgba(255, 255, 255, 0.85) !important;
    }
    
    /* Metric cards - glassmorphism */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px !important;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        background: rgba(255, 255, 255, 0.06) !important;
        border-color: rgba(0, 255, 170, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 255, 170, 0.15);
    }
    
    [data-testid="stMetric"] label {
        color: rgba(255, 255, 255, 0.6) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > input,
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stDateInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: #00ffaa !important;
        box-shadow: 0 0 0 2px rgba(0, 255, 170, 0.2) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Buttons - primary (reduced fluorescence) */
    .stButton > button[kind="primary"],
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00d4aa 0%, #00b89d 100%) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(0, 212, 170, 0.2);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 212, 170, 0.3);
        background: linear-gradient(135deg, #00e6bb 0%, #00c9aa 100%) !important;
    }
    
    /* Secondary buttons */
    .stButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-2px);
    }
    
    /* Tabs */
    .stTabs {
        background: transparent !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 6px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 12px !important;
        color: rgba(255, 255, 255, 0.6) !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(0, 255, 170, 0.15) !important;
        color: #00ffaa !important;
        box-shadow: 0 0 20px rgba(0, 255, 170, 0.2);
    }
    
    /* Data frames / tables */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        overflow: hidden;
    }
    
    [data-testid="stDataFrame"] > div {
        background: transparent !important;
    }
    
    /* Selectbox and dropdown styling */
    [data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        min-height: 45px !important;
    }
    
    [data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        padding: 8px 12px !important;
    }
    
    /* Dropdown menu */
    [data-baseweb="popover"] {
        background: rgba(20, 20, 20, 0.98) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        margin-top: 4px !important;
    }
    
    [role="listbox"] {
        background: transparent !important;
        padding: 8px !important;
    }
    
    [role="option"] {
        background: transparent !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
        margin: 2px 0 !important;
        min-height: 40px !important;
        line-height: 1.5 !important;
    }
    
    [role="option"]:hover {
        background: rgba(0, 255, 170, 0.1) !important;
    }
    
    [aria-selected="true"] {
        background: rgba(0, 255, 170, 0.15) !important;
    }
    
    /* Expander text visibility */
    .streamlit-expanderHeader p {
        color: #ffffff !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    .streamlit-expanderContent p {
        color: rgba(255, 255, 255, 0.85) !important;
        line-height: 1.6 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00ffaa 0%, #00d4aa 100%) !important;
        border-radius: 8px;
    }
    
    .stProgress > div > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px;
    }
    
    /* Info/Success/Warning/Error boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
        padding: 16px 20px !important;
    }
    
    [data-testid="stNotification"] {
        background: rgba(20, 20, 20, 0.95) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 2px dashed rgba(255, 255, 255, 0.2) !important;
        border-radius: 16px !important;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(0, 255, 170, 0.5) !important;
        background: rgba(255, 255, 255, 0.06) !important;
    }
    
    /* Checkbox and radio */
    .stCheckbox, .stRadio {
        color: rgba(255, 255, 255, 0.85) !important;
    }
    
    /* Plotly charts */
    .js-plotly-plot {
        border-radius: 16px;
        overflow: hidden;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 255, 170, 0.3);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 255, 170, 0.5);
    }
    
    /* Column spacing */
    [data-testid="column"] {
        padding: 0 8px !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
        margin: 2rem 0 !important;
    }
    
    /* Code blocks */
    code {
        background: rgba(0, 255, 170, 0.1) !important;
        color: #00ffaa !important;
        padding: 2px 6px !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9em !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #00ffaa !important;
    }
    
    /* Form styling */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        backdrop-filter: blur(10px);
    }
    
    /* Caption text */
    .caption {
        color: rgba(255, 255, 255, 0.5) !important;
        font-size: 0.85rem !important;
    }
    
    /* Card-like containers */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 16px;
        padding: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    /* Logo/Header styling */
    [data-testid="stSidebarNav"] {
        padding-top: 2rem !important;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        /* Sidebar becomes collapsible */
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
        
        /* Adjust padding for mobile */
        .block-container {
            padding: 1rem !important;
        }
        
        /* Stack columns on mobile */
        [data-testid="column"] {
            width: 100% !important;
            padding: 0 !important;
            margin-bottom: 1rem;
        }
        
        /* Reduce font sizes on mobile */
        h1 {
            font-size: 1.8rem !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
        }
        
        /* Make buttons full width on mobile */
        .stButton > button {
            width: 100% !important;
        }
        
        /* Adjust metric cards for mobile */
        [data-testid="stMetric"] {
            padding: 15px !important;
        }
    }
    
    /* Sidebar logo and tagline styling */
    [data-testid="stSidebar"] h1 {
        text-align: center;
        margin-bottom: 0.5rem !important;
        font-size: 2rem !important;
    }
    
    [data-testid="stSidebar"] .tagline {
        text-align: center;
        color: rgba(0, 255, 170, 0.8) !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.1em;
        margin-bottom: 2rem !important;
        text-transform: uppercase;
    }
    
    /* Logout button at bottom */
    [data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    
    .sidebar-logout {
        margin-top: auto !important;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None

def render_sidebar(user: dict):
    """Render sidebar navigation - minimal, no icons"""
    with st.sidebar:
        # Logo
        st.markdown("# OSCAR")
        
        # Tagline
        st.markdown('<p class="tagline">Save. Spend. Track.</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation without icons - clean minimal
        page = st.radio(
            "Navigate",
            [
                "Dashboard",
                "Expenses", 
                "Dates",
                "Budget Tracker",
                "Friends",
                "Analytics",
                "Profile"
            ],
            label_visibility="collapsed"
        )
        
        # Spacer to push logout to bottom
        st.markdown('<div style="flex-grow: 1;"></div>', unsafe_allow_html=True)
        
        # Logout button at bottom
        st.markdown("---")
        if st.button("Logout", use_container_width=True, key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
        
    return page

def render_main_content(user: dict):
    """Render main content based on selected page"""
    db = DatabaseManager()
    page = render_sidebar(user)
    
    if page == "Dashboard":
        render_dashboard(user, db)
    elif page == "Expenses":
        render_expenses(user, db)
    elif page == "Dates":
        render_dates(user, db)
    elif page == "Budget Tracker":
        render_budget(user, db)
    elif page == "Friends":
        render_friends(user, db)
    elif page == "Analytics":
        render_analytics(user, db)
    elif page == "Profile":
        render_profile(user, db)

def main():
    """Main application entry point"""
    initialize_session_state()
    
    if not st.session_state.authenticated:
        render_auth()
    else:
        render_main_content(st.session_state.user)

if __name__ == "__main__":
    main()