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

def get_css():
    """Return all CSS styles"""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        *, html, body, [class*="st-"], .stApp, .stMarkdown, p, span, div, label, button, input, textarea, select, h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        .stApp {
            background: linear-gradient(135deg, #1a2332 0%, #2d3e50 100%);
        }
        
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        
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
                padding-bottom: 90px !important;
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
        
        /* Hide mobile elements on desktop */
        @media (min-width: 769px) {
            .mobile-header-bar { display: none !important; }
            .mobile-bottom-bar { display: none !important; }
        }
        
        /* Show mobile elements on mobile */
        @media (max-width: 768px) {
            .mobile-header-bar { display: flex !important; }
            .mobile-bottom-bar { display: flex !important; }
        }
    </style>
    """

# Apply CSS
st.markdown(get_css(), unsafe_allow_html=True)


def initialize_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"


def render_mobile_top_bar(user: dict):
    """Render mobile top bar using HTML"""
    initial = user.get('full_name', 'U')[0].upper() if user else 'U'
    
    html = '<div class="mobile-header-bar" style="'
    html += 'display: none; position: fixed; top: 0; left: 0; right: 0; height: 56px; '
    html += 'background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%); '
    html += 'border-bottom: 1px solid rgba(255, 255, 255, 0.08); z-index: 99999; '
    html += 'padding: 8px 12px; align-items: center; justify-content: space-between;">'
    
    html += '<div style="display: flex; flex-direction: column;">'
    html += '<span style="font-size: 1.1rem; font-weight: 700; color: white; '
    html += 'background: linear-gradient(135deg, #ffffff 0%, #3b82f6 100%); '
    html += '-webkit-background-clip: text; -webkit-text-fill-color: transparent;">OSCAR</span>'
    html += '<span style="font-size: 0.45rem; color: rgba(255, 255, 255, 0.4); '
    html += 'text-transform: uppercase; letter-spacing: 0.1em;">Track. Save. Review.</span>'
    html += '</div>'
    
    html += '<div style="width: 32px; height: 32px; border-radius: 50%; '
    html += 'background: linear-gradient(135deg, #3b82f6, #6366f1); '
    html += 'display: flex; align-items: center; justify-content: center; '
    html += 'color: white; font-weight: 600; font-size: 12px; '
    html += 'border: 2px solid rgba(255,255,255,0.2);">' + initial + '</div>'
    
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)


def render_mobile_bottom_nav():
    """Render mobile bottom navigation using simple HTML with Unicode icons"""
    
    current = st.session_state.get('current_page', 'Dashboard')
    
    # Navigation config: (page_key, icon, label)
    nav_items = [
        ('Dashboard', '⌂', 'Home'),
        ('Expenses', '○', 'Expense'),
        ('Dates', '▦', 'Dates'),
        ('Budget Tracker', '▭', 'Budget'),
        ('Friends', '◐', 'Friends'),
        ('Analytics', '▥', 'Stats'),
        ('Profile', '●', 'Profile'),
    ]
    
    # Build nav HTML with simple string concatenation (no f-strings)
    items_html = ''
    for page, icon, label in nav_items:
        is_active = (current == page)
        color = '#FF9000' if is_active else 'rgba(255,255,255,0.5)'
        bg = 'rgba(255,144,0,0.12)' if is_active else 'transparent'
        
        items_html += '<div style="flex:1; display:flex; flex-direction:column; align-items:center; '
        items_html += 'padding:6px 2px; border-radius:8px; background:' + bg + ';">'
        items_html += '<span style="font-size:18px; color:' + color + ';">' + icon + '</span>'
        items_html += '<span style="font-size:9px; color:' + color + '; margin-top:2px;">' + label + '</span>'
        items_html += '</div>'
    
    # Container HTML
    nav_html = '<div class="mobile-bottom-bar" style="'
    nav_html += 'display:none; position:fixed; bottom:0; left:0; right:0; height:65px; '
    nav_html += 'background:linear-gradient(180deg, #1a1f2e 0%, #0f1419 100%); '
    nav_html += 'border-top:1px solid rgba(255,255,255,0.1); z-index:99998; '
    nav_html += 'padding:6px 8px 12px 8px; flex-direction:row; justify-content:space-around; align-items:center;">'
    nav_html += items_html
    nav_html += '</div>'
    
    st.markdown(nav_html, unsafe_allow_html=True)
    
    # Invisible clickable Streamlit buttons on top
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .nav-click-layer {
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            right: 0 !important;
            height: 65px !important;
            z-index: 99999 !important;
            display: flex !important;
            flex-direction: row !important;
        }
        .nav-click-layer > div {
            flex: 1 !important;
            padding: 0 !important;
        }
        .nav-click-layer > div > div {
            height: 65px !important;
        }
        .nav-click-layer .stButton {
            height: 65px !important;
        }
        .nav-click-layer .stButton > button {
            height: 65px !important;
            width: 100% !important;
            background: transparent !important;
            border: none !important;
            opacity: 0 !important;
            cursor: pointer !important;
        }
    }
    @media (min-width: 769px) {
        .nav-click-layer { display: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Clickable buttons layer
    st.markdown('<div class="nav-click-layer">', unsafe_allow_html=True)
    
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    
    with c1:
        if st.button("a", key="nav_m_dash"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    with c2:
        if st.button("b", key="nav_m_exp"):
            st.session_state.current_page = "Expenses"
            st.rerun()
    with c3:
        if st.button("c", key="nav_m_date"):
            st.session_state.current_page = "Dates"
            st.rerun()
    with c4:
        if st.button("d", key="nav_m_bud"):
            st.session_state.current_page = "Budget Tracker"
            st.rerun()
    with c5:
        if st.button("e", key="nav_m_fri"):
            st.session_state.current_page = "Friends"
            st.rerun()
    with c6:
        if st.button("f", key="nav_m_ana"):
            st.session_state.current_page = "Analytics"
            st.rerun()
    with c7:
        if st.button("g", key="nav_m_pro"):
            st.session_state.current_page = "Profile"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


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