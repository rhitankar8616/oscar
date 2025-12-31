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
    page_icon="O",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, classy design matching Base44 style
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Main app background - navy blue gradient */
    .stApp {
        background: linear-gradient(135deg, #1a2332 0%, #2d3e50 100%);
    }
    
    /* Sidebar styling - darker navy like Base44 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        min-width: 240px !important;
        width: 240px !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
        padding-top: 1.5rem !important;
    }
    
    /* Hide radio button label text "Navigation" */
    section[data-testid="stSidebar"] .stRadio > label:first-of-type {
        display: none !important;
    }
    
    /* Navigation container */
    section[data-testid="stSidebar"] .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    /* Navigation items - Base44 style */
    section[data-testid="stSidebar"] .stRadio > div > label {
        background: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        margin: 2px 12px !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
    }
    
    section[data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(255, 255, 255, 0.06) !important;
    }
    
    /* Hide the radio circle completely */
    section[data-testid="stSidebar"] .stRadio > div > label > div:first-child {
        display: none !important;
    }
    
    /* Navigation text styling */
    section[data-testid="stSidebar"] .stRadio > div > label p {
        color: rgba(255, 255, 255, 0.55) !important;
        font-size: 0.9rem !important;
        font-weight: 400 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Selected navigation item - orange highlight like Base44 */
    section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
    section[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        background: rgba(255, 144, 0, 0.12) !important;
    }
    
    section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] p,
    section[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) p {
        color: #FF9000 !important;
        font-weight: 500 !important;
    }
    
    /* Logout button styling */
    section[data-testid="stSidebar"] .logout-btn button {
        background: rgba(255, 100, 100, 0.08) !important;
        color: #ff6b6b !important;
        border: 1px solid rgba(255, 100, 100, 0.15) !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    section[data-testid="stSidebar"] .logout-btn button:hover {
        background: rgba(255, 100, 100, 0.15) !important;
        border-color: rgba(255, 100, 100, 0.3) !important;
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
    
    /* Metric cards - navy blue boxes style */
    [data-testid="stMetric"] {
        background: rgba(30, 45, 65, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        background: rgba(30, 45, 65, 0.7) !important;
        border-color: rgba(255, 144, 0, 0.2) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
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
    
    /* Buttons - primary (orange accent like Base44) */
    .stButton > button[kind="primary"],
    .stDownloadButton > button {
        background: linear-gradient(135deg, #FF9000 0%, #FF7A00 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(255, 144, 0, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(255, 144, 0, 0.5);
        background: linear-gradient(135deg, #FFA500 0%, #FF8C00 100%) !important;
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
    
    /* Selectbox and dropdown styling - WHITE TEXT */
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
    
    /* Selected value text - FORCE WHITE */
    [data-baseweb="select"] div {
        color: #ffffff !important;
    }
    
    /* Dropdown menu */
    [data-baseweb="popover"] {
        background: rgba(20, 30, 45, 0.98) !important;
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
        background: rgba(0, 212, 170, 0.1) !important;
    }
    
    [aria-selected="true"] {
        background: rgba(0, 212, 170, 0.15) !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(30, 45, 65, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        transition: all 0.3s ease;
        padding: 16px !important;
        margin: 8px 0 !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(30, 45, 65, 0.8) !important;
        border-color: rgba(0, 212, 170, 0.3) !important;
    }
    
    .streamlit-expanderHeader p {
        color: #ffffff !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        margin: 0 !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(20, 30, 45, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 0 0 12px 12px !important;
        padding: 20px !important;
        margin-top: -8px !important;
    }
    
    .streamlit-expanderContent p {
        color: rgba(255, 255, 255, 0.85) !important;
        line-height: 1.8 !important;
        margin: 8px 0 !important;
    }
    
    .streamlit-expanderContent strong {
        color: #ffffff !important;
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
    
    /* Checkbox and radio (not in sidebar) */
    .main .stCheckbox, .main .stRadio {
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
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            min-width: 100% !important;
            width: 100% !important;
        }
        
        .block-container {
            padding: 1rem !important;
        }
        
        [data-testid="column"] {
            width: 100% !important;
            padding: 0 !important;
            margin-bottom: 1rem;
        }
        
        h1 {
            font-size: 1.8rem !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
        }
        
        .stButton > button {
            width: 100% !important;
        }
        
        [data-testid="stMetric"] {
            padding: 15px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

def render_sidebar(user: dict):
    """Render sidebar navigation - Base44 style with clean minimal design"""
    with st.sidebar:
        # Logo and tagline at top
        st.markdown("""
            <div style="padding: 0 16px; margin-bottom: 2.5rem;">
                <h1 style="font-size: 1.8rem; font-weight: 700; color: #ffffff; margin: 0; 
                    background: none; -webkit-text-fill-color: #ffffff;">OSCAR</h1>
                <p style="color: rgba(255,255,255,0.4); font-size: 0.7rem; font-weight: 400; 
                    letter-spacing: 0.15em; text-transform: uppercase; margin-top: 4px;">
                    Track. Save. Review.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation options - clean text labels
        page = st.radio(
            "Navigation",
            options=[
                "Dashboard",
                "Expenses",
                "Dates",
                "Budget Tracker",
                "Friends",
                "Analytics",
                "Profile"
            ],
            label_visibility="collapsed",
            key="nav_radio"
        )
        
        # Spacer to push logout to bottom
        st.markdown("""<div style="flex-grow: 1; min-height: 180px;"></div>""", unsafe_allow_html=True)
        
        # User info section at bottom
        if user:
            first_name = user.get('first_name', 'User')
            email = user.get('email', '')
            initial = first_name[0].upper() if first_name else 'U'
            display_email = email[:22] + '...' if len(email) > 22 else email
            
            st.markdown(f"""
                <div style="padding: 12px 16px; border-top: 1px solid rgba(255,255,255,0.05); margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #3b82f6, #6366f1); 
                            border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                            color: white; font-weight: 600; font-size: 13px; flex-shrink: 0;">{initial}</div>
                        <p style="color: rgba(255,255,255,0.45); font-size: 0.72rem; margin: 0; 
                            overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{display_email}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Logout button
        st.markdown('<div class="logout-btn" style="padding: 0 12px 16px 12px;">', unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True, key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
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