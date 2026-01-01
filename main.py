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

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    *, html, body, [class*="st-"], .stApp, .stMarkdown, p, span, div, label, button, input, textarea, select, h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1a2332 0%, #2d3e50 100%);
    }
    
    /* Hide sidebar collapse button */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {
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
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px !important;
    }
    
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        background: linear-gradient(135deg, #ffffff 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    h2 { color: #ffffff !important; font-weight: 600 !important; font-size: 1.8rem !important; }
    h3 { color: #ffffff !important; font-weight: 600 !important; font-size: 1.5rem !important; }
    h4, h5, h6 { color: #ffffff !important; font-weight: 600 !important; }
    p, span, label, .stMarkdown { color: rgba(255, 255, 255, 0.85) !important; }
    
    [data-testid="stMetric"] {
        background: rgba(30, 45, 65, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 24px !important;
    }
    
    [data-testid="stMetric"] label { color: rgba(255, 255, 255, 0.6) !important; font-size: 0.85rem !important; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2rem !important; }
    
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
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF9000 0%, #FF7A00 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
    }
    
    .stButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
    }
    
    .stButton > button:hover { background: rgba(255, 255, 255, 0.1) !important; }
    
    [data-testid="stSidebar"] .stButton { margin: 0 !important; padding: 0 !important; }
    [data-testid="stSidebar"] .stButton > button { margin: 2px 0 !important; padding: 10px 16px !important; border-radius: 8px !important; }
    
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
    
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 24px !important;
    }
    
    .stAlert {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    .stProgress > div > div > div > div { background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%) !important; }
    .stProgress > div > div > div { background: rgba(255, 255, 255, 0.1) !important; }
    
    #MainMenu, footer, header { visibility: hidden; }
    hr { border-color: rgba(255, 255, 255, 0.1) !important; margin: 0.5rem 0 !important; }
    
    /* ========== MOBILE STYLES ========== */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] { display: none !important; }
        
        .block-container {
            padding-top: 70px !important;
            padding-bottom: 80px !important;
            padding-left: 8px !important;
            padding-right: 8px !important;
            max-width: 100% !important;
        }
        
        h1 { font-size: 1.3rem !important; }
        h2 { font-size: 1.1rem !important; }
        h3 { font-size: 0.95rem !important; }
        h4 { font-size: 0.85rem !important; }
        p, span, label, .stMarkdown { font-size: 0.8rem !important; }
        
        [data-testid="stMetric"] { padding: 8px !important; border-radius: 8px !important; }
        [data-testid="stMetric"] label { font-size: 0.55rem !important; }
        [data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 0.9rem !important; }
        
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input,
        .stTextArea textarea {
            padding: 6px 8px !important;
            font-size: 0.8rem !important;
            border-radius: 6px !important;
        }
        
        .stButton > button {
            padding: 5px 10px !important;
            font-size: 0.7rem !important;
            border-radius: 6px !important;
        }
        
        .stTabs [data-baseweb="tab-list"] { padding: 2px; gap: 2px; border-radius: 8px; }
        .stTabs [data-baseweb="tab"] { padding: 5px 8px !important; font-size: 0.65rem !important; border-radius: 6px !important; }
        
        [data-testid="stForm"] { padding: 10px !important; border-radius: 8px !important; }
        [role="option"] { padding: 6px 8px !important; font-size: 0.8rem !important; }
        .stAlert { padding: 6px 8px !important; border-radius: 6px !important; }
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"


def render_mobile_top_bar(user: dict):
    """Render mobile top bar"""
    initial = user.get('full_name', 'U')[0].upper() if user else 'U'
    
    st.markdown(f"""
    <style>
    @media (min-width: 769px) {{ .mobile-top-bar {{ display: none !important; }} }}
    </style>
    <div class="mobile-top-bar" style="
        display: flex;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 56px;
        background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        z-index: 99999;
        padding: 8px 12px;
        align-items: center;
        justify-content: space-between;
    ">
        <div style="display: flex; flex-direction: column;">
            <span style="font-size: 1.1rem; font-weight: 700; color: white; 
                background: linear-gradient(135deg, #ffffff 0%, #3b82f6 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;">OSCAR</span>
            <span style="font-size: 0.45rem; color: rgba(255, 255, 255, 0.4); 
                text-transform: uppercase; letter-spacing: 0.1em;">Track. Save. Review.</span>
        </div>
        <div style="width: 32px; height: 32px; border-radius: 50%; 
            background: linear-gradient(135deg, #3b82f6, #6366f1);
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: 600; font-size: 12px;
            border: 2px solid rgba(255,255,255,0.2);">{initial}</div>
    </div>
    """, unsafe_allow_html=True)


def render_mobile_bottom_nav():
    """Render mobile bottom navigation - HORIZONTAL using HTML"""
    
    # Get current page to highlight active
    current = st.session_state.get('current_page', 'Dashboard')
    
    nav_items = [
        ("🏠", "Dashboard", "Home"),
        ("💰", "Expenses", "Expense"),
        ("📅", "Dates", "Dates"),
        ("💳", "Budget Tracker", "Budget"),
        ("👥", "Friends", "Friends"),
        ("📊", "Analytics", "Stats"),
        ("👤", "Profile", "Profile")
    ]
    
    # Build nav items HTML
    nav_html = ""
    for icon, page, label in nav_items:
        is_active = current == page
        active_style = "color: #FF9000; background: rgba(255, 144, 0, 0.15);" if is_active else "color: rgba(255,255,255,0.6);"
        nav_html += f'''
        <div style="flex: 1; display: flex; flex-direction: column; align-items: center; 
            padding: 6px 2px; border-radius: 8px; cursor: pointer; {active_style}" 
            class="nav-item-{page.replace(' ', '-')}">
            <span style="font-size: 16px;">{icon}</span>
            <span style="font-size: 9px; margin-top: 2px;">{label}</span>
        </div>
        '''
    
    st.markdown(f"""
    <style>
    @media (min-width: 769px) {{ .mobile-bottom-nav {{ display: none !important; }} }}
    </style>
    <div class="mobile-bottom-nav" style="
        display: flex;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 60px;
        background: linear-gradient(180deg, #1a1f2e 0%, #0f1419 100%);
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        z-index: 99999;
        padding: 4px 8px 8px 8px;
        flex-direction: row;
        justify-content: space-around;
        align-items: center;
    ">
        {nav_html}
    </div>
    """, unsafe_allow_html=True)
    
    # Streamlit buttons for navigation (hidden but functional)
    st.markdown('<div style="position: fixed; bottom: 0; left: 0; right: 0; z-index: 100000; height: 60px; display: flex; flex-direction: row;">', unsafe_allow_html=True)
    
    cols = st.columns(7)
    for idx, (icon, page, label) in enumerate(nav_items):
        with cols[idx]:
            # Invisible button overlay
            if st.button(f"{icon}", key=f"nav_mob_{page}", help=label):
                st.session_state.current_page = page
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Style to make buttons invisible but clickable
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"]:has([key*="nav_mob"]) {
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            right: 0 !important;
            z-index: 100001 !important;
            height: 60px !important;
            background: transparent !important;
        }
        
        [data-testid="stHorizontalBlock"]:has([key*="nav_mob"]) .stButton > button {
            background: transparent !important;
            border: none !important;
            height: 60px !important;
            opacity: 0 !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar(user: dict):
    """Render desktop sidebar"""
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
    
    for item in ["Dashboard", "Expenses", "Dates", "Budget Tracker", "Friends", "Analytics", "Profile"]:
        if st.sidebar.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.current_page = item
            st.rerun()
    
    st.sidebar.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
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
    
    if st.sidebar.button("Logout", use_container_width=True, key="logout_btn"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.current_page = "Dashboard"
        st.rerun()
    
    return st.session_state.current_page


def render_main_content(user: dict):
    db = DatabaseManager()
    
    render_mobile_top_bar(user)
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
    
    render_mobile_bottom_nav()


def main():
    initialize_session_state()
    
    if not st.session_state.authenticated:
        render_auth()
    else:
        render_main_content(st.session_state.user)


if __name__ == "__main__":
    main()