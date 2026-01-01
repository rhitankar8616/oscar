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

# Custom CSS for responsive design
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    *, html, body, [class*="st-"], .stApp, .stMarkdown, p, span, div, label, button, input, textarea, select, h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #1a2332 0%, #2d3e50 100%);
    }
    
    /* Hide sidebar collapse */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="baseButton-headerNoPadding"] {
        display: none !important;
    }
    
    /* Desktop Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        min-width: 260px !important;
        width: 260px !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
        padding-top: 1rem !important;
    }
    
    [data-testid="stSidebar"] .stElementContainer,
    [data-testid="stSidebar"] .element-container {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    
    /* Main content */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px !important;
    }
    
    /* Headers */
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        background: linear-gradient(135deg, #ffffff 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    h2 { color: #ffffff !important; font-weight: 600 !important; font-size: 1.8rem !important; }
    h3 { color: #ffffff !important; font-weight: 600 !important; font-size: 1.5rem !important; margin-bottom: 1.5rem !important; }
    h4, h5, h6 { color: #ffffff !important; font-weight: 600 !important; }
    
    p, span, label, .stMarkdown { color: rgba(255, 255, 255, 0.85) !important; }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: rgba(30, 45, 65, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 24px !important;
    }
    
    [data-testid="stMetric"] label { color: rgba(255, 255, 255, 0.6) !important; font-size: 0.85rem !important; text-transform: uppercase; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2rem !important; font-weight: 700 !important; }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] > div > div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    [data-baseweb="popover"] {
        background: rgba(15, 20, 30, 0.98) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
    }
    
    [role="option"] { color: #ffffff !important; padding: 12px 16px !important; border-radius: 8px !important; }
    [role="option"]:hover { background: rgba(59, 130, 246, 0.15) !important; }
    
    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF9000 0%, #FF7A00 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
    }
    
    /* Secondary buttons */
    .stButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
    }
    
    .stButton > button:hover { background: rgba(255, 255, 255, 0.1) !important; }
    
    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton { margin: 0 !important; padding: 0 !important; }
    [data-testid="stSidebar"] .stButton > button { margin: 2px 0 !important; padding: 10px 16px !important; border-radius: 8px !important; }
    
    /* Tabs */
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
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(59, 130, 246, 0.15) !important;
        color: #3b82f6 !important;
    }
    
    /* Form */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 24px !important;
    }
    
    /* Alerts */
    .stAlert {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    /* Progress */
    .stProgress > div > div > div > div { background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%) !important; }
    .stProgress > div > div > div { background: rgba(255, 255, 255, 0.1) !important; }
    
    /* Hide branding */
    #MainMenu, footer, header { visibility: hidden; }
    
    hr { border-color: rgba(255, 255, 255, 0.1) !important; margin: 0.5rem 0 !important; }
    
    /* ========== MOBILE TOP BAR (CSS only, no JS) ========== */
    .mobile-header {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 56px;
        background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        z-index: 99999;
        padding: 8px 16px;
        align-items: center;
        justify-content: space-between;
    }
    
    .mobile-header-logo {
        display: flex;
        flex-direction: column;
    }
    
    .mobile-header-logo h1 {
        font-size: 1.2rem !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }
    
    .mobile-header-logo p {
        font-size: 0.5rem !important;
        color: rgba(255, 255, 255, 0.4) !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0 !important;
    }
    
    .mobile-header-avatar {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #6366f1);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 13px;
        border: 2px solid rgba(255,255,255,0.2);
    }
    
    /* ========== MOBILE BOTTOM NAV ========== */
    .mobile-nav-wrapper {
        display: none;
    }
    
    /* ========== MOBILE RESPONSIVE ========== */
    @media (max-width: 768px) {
        /* Show mobile elements */
        .mobile-header { display: flex !important; }
        .mobile-nav-wrapper { display: block !important; }
        
        /* Hide desktop sidebar */
        [data-testid="stSidebar"] { display: none !important; }
        
        /* Adjust main content */
        .block-container {
            padding-top: 70px !important;
            padding-bottom: 90px !important;
            padding-left: 10px !important;
            padding-right: 10px !important;
            max-width: 100% !important;
        }
        
        /* Smaller headers */
        h1 { font-size: 1.4rem !important; margin-bottom: 0.5rem !important; }
        h2 { font-size: 1.2rem !important; margin-bottom: 0.5rem !important; }
        h3 { font-size: 1rem !important; margin-bottom: 0.5rem !important; }
        h4 { font-size: 0.9rem !important; }
        
        p, span, label, .stMarkdown { font-size: 0.82rem !important; }
        
        /* Compact metrics */
        [data-testid="stMetric"] { padding: 10px !important; border-radius: 10px !important; }
        [data-testid="stMetric"] label { font-size: 0.6rem !important; }
        [data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
        
        /* Compact inputs */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input,
        .stTextArea textarea {
            padding: 8px 10px !important;
            font-size: 0.82rem !important;
            border-radius: 8px !important;
        }
        
        /* Compact buttons */
        .stButton > button {
            padding: 6px 12px !important;
            font-size: 0.75rem !important;
            border-radius: 8px !important;
        }
        
        .stButton > button[kind="primary"] { padding: 8px 16px !important; }
        
        /* Compact tabs */
        .stTabs [data-baseweb="tab-list"] {
            padding: 3px;
            gap: 2px;
            border-radius: 10px;
            overflow-x: auto;
            flex-wrap: nowrap;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 6px 10px !important;
            font-size: 0.7rem !important;
            border-radius: 8px !important;
            white-space: nowrap;
        }
        
        /* Compact form */
        [data-testid="stForm"] { padding: 12px !important; border-radius: 10px !important; }
        
        /* Compact selectbox */
        .stSelectbox > div > div { border-radius: 8px !important; }
        [role="option"] { padding: 8px 10px !important; font-size: 0.82rem !important; }
        
        /* Compact alerts */
        .stAlert { padding: 8px 10px !important; border-radius: 8px !important; }
        
        hr { margin: 0.3rem 0 !important; }
        
        /* Compact expander */
        .streamlit-expanderHeader { padding: 10px !important; border-radius: 8px !important; font-size: 0.82rem !important; }
        .streamlit-expanderContent { padding: 10px !important; }
        
        /* Mobile bottom nav styling */
        .mobile-bottom-nav-container {
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            right: 0 !important;
            background: linear-gradient(180deg, #1a1f2e 0%, #0f1419 100%) !important;
            border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
            z-index: 99999 !important;
            padding: 8px 4px !important;
        }
        
        .mobile-bottom-nav-container .stButton > button {
            background: transparent !important;
            border: none !important;
            padding: 4px 2px !important;
            font-size: 0.55rem !important;
            color: rgba(255, 255, 255, 0.5) !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            min-height: 50px !important;
        }
        
        .mobile-bottom-nav-container .stButton > button:hover {
            background: rgba(255, 255, 255, 0.05) !important;
            color: #FF9000 !important;
        }
    }
    
    @media (max-width: 480px) {
        .block-container { padding-left: 6px !important; padding-right: 6px !important; }
        h1 { font-size: 1.2rem !important; }
        h2 { font-size: 1.05rem !important; }
        h3 { font-size: 0.92rem !important; }
        
        [data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 1rem !important; }
        
        .stTabs [data-baseweb="tab"] { padding: 5px 8px !important; font-size: 0.65rem !important; }
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"


def render_mobile_header(user: dict):
    """Render mobile header (CSS-only, no JavaScript)"""
    initial = user.get('full_name', 'U')[0].upper() if user else 'U'
    
    st.markdown(f"""
    <div class="mobile-header">
        <div class="mobile-header-logo">
            <h1>OSCAR</h1>
            <p>Track. Save. Review.</p>
        </div>
        <div class="mobile-header-avatar">{initial}</div>
    </div>
    """, unsafe_allow_html=True)


def render_mobile_bottom_nav():
    """Render mobile bottom navigation using Streamlit native buttons"""
    
    # This container will be styled via CSS to appear at bottom on mobile
    st.markdown('<div class="mobile-nav-wrapper">', unsafe_allow_html=True)
    
    # Create bottom navigation container
    nav_container = st.container()
    
    with nav_container:
        cols = st.columns(7)
        
        nav_items = [
            ("🏠", "Dashboard"),
            ("💰", "Expenses"),
            ("📅", "Dates"),
            ("💳", "Budget Tracker"),
            ("👥", "Friends"),
            ("📊", "Analytics"),
            ("👤", "Profile")
        ]
        
        for idx, (icon, name) in enumerate(nav_items):
            with cols[idx]:
                short_name = name.replace(" Tracker", "")
                if st.button(f"{icon}\n{short_name}", key=f"mob_nav_{name}", use_container_width=True):
                    st.session_state.current_page = name
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CSS to position this at bottom on mobile
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .mobile-nav-wrapper {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(180deg, #1a1f2e 0%, #0f1419 100%);
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            z-index: 99999;
            padding: 4px;
        }
        
        .mobile-nav-wrapper [data-testid="column"] {
            padding: 0 2px !important;
        }
        
        .mobile-nav-wrapper .stButton > button {
            background: transparent !important;
            border: none !important;
            padding: 6px 2px !important;
            font-size: 0.5rem !important;
            color: rgba(255, 255, 255, 0.6) !important;
            white-space: pre-line !important;
            line-height: 1.3 !important;
            min-height: 52px !important;
        }
        
        .mobile-nav-wrapper .stButton > button:hover {
            background: rgba(255, 144, 0, 0.15) !important;
            color: #FF9000 !important;
        }
    }
    
    @media (min-width: 769px) {
        .mobile-nav-wrapper {
            display: none !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar(user: dict):
    """Render desktop sidebar navigation"""
    
    # Logo and tagline
    st.sidebar.markdown("""
        <div style="padding: 0 0 8px 0;">
            <h1 style="font-size: 1.8rem; font-weight: 700; margin: 0;
                background: linear-gradient(135deg, #ffffff 0%, #3b82f6 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;">OSCAR</h1>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.7rem; 
                letter-spacing: 0.15em; text-transform: uppercase; margin-top: 4px;">
                Track. Save. Review.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Navigation items
    nav_items = ["Dashboard", "Expenses", "Dates", "Budget Tracker", "Friends", "Analytics", "Profile"]
    
    for item in nav_items:
        if st.sidebar.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.current_page = item
            st.rerun()
    
    st.sidebar.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # User info
    if user:
        full_name = user.get('full_name', 'User')
        email = user.get('email', '')
        initial = full_name[0].upper() if full_name else 'U'
        
        st.sidebar.markdown(f'''
            <div style="display: flex; align-items: center; gap: 12px; padding: 8px 0; margin-bottom: 8px;">
                <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #3b82f6, #6366f1); 
                    border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                    color: white; font-weight: 600; font-size: 14px;">{initial}</div>
                <div>
                    <p style="color: rgba(255,255,255,0.85); font-size: 0.85rem; margin: 0; font-weight: 500;">{full_name}</p>
                    <p style="color: rgba(255,255,255,0.45); font-size: 0.7rem; margin: 0;">{email}</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    
    # Logout button
    if st.sidebar.button("Logout", use_container_width=True, key="logout_btn"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.current_page = "Dashboard"
        st.rerun()
    
    return st.session_state.current_page


def render_main_content(user: dict):
    """Render main content"""
    db = DatabaseManager()
    
    # Render mobile header (hidden on desktop via CSS)
    render_mobile_header(user)
    
    # Render desktop sidebar
    page = render_sidebar(user)
    
    # Render page content
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
    
    # Render mobile bottom nav (hidden on desktop via CSS)
    render_mobile_bottom_nav()


def main():
    """Main entry point"""
    initialize_session_state()
    
    if not st.session_state.authenticated:
        render_auth()
    else:
        render_main_content(st.session_state.user)


if __name__ == "__main__":
    main()