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

# Custom CSS - keeping sidebar visible
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #1a2332 0%, #2d3e50 100%);
    }
    
    /* FORCE SIDEBAR TO BE VISIBLE */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%) !important;
        min-width: 260px !important;
        width: 260px !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Text colors */
    p, span, label, .stMarkdown {
        color: rgba(255, 255, 255, 0.85) !important;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: rgba(30, 45, 65, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 24px !important;
    }
    
    [data-testid="stMetric"] label {
        color: rgba(255, 255, 255, 0.6) !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }
    
    /* Buttons - primary orange */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF9000 0%, #FF7A00 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
    }
    
    /* Secondary buttons */
    .stButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 6px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(0, 255, 170, 0.15) !important;
        color: #00ffaa !important;
    }
    
    /* Selectbox dropdown */
    [data-baseweb="select"] div {
        color: #ffffff !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(30, 45, 65, 0.6) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00ffaa 0%, #00d4aa 100%) !important;
    }
    
    /* Info boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    /* Form styling */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 24px !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar selectbox styling */
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background: rgba(255, 144, 0, 0.1) !important;
        border-radius: 8px !important;
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
    """Render sidebar navigation"""
    # Sidebar content
    st.sidebar.markdown("""
        <h2 style="font-size: 1.6rem; font-weight: 700; color: #ffffff; margin-bottom: 0;">OSCAR</h2>
        <p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; letter-spacing: 0.15em; 
            text-transform: uppercase; margin-top: 2px;">Track. Save. Review.</p>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Navigation
    pages = [
        "Dashboard",
        "Expenses",
        "Dates",
        "Budget Tracker",
        "Friends",
        "Analytics",
        "Profile"
    ]
    
    page = st.sidebar.selectbox(
        "Navigate to",
        options=pages,
        index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0,
        key="nav_select"
    )
    
    st.session_state.current_page = page
    
    # Spacer
    st.sidebar.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # User info
    if user:
        full_name = user.get('full_name', 'User')
        email = user.get('email', '')
        initial = full_name[0].upper() if full_name else 'U'
        
        st.sidebar.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; padding: 8px 0;">
                <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #3b82f6, #6366f1); 
                    border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                    color: white; font-weight: 600; font-size: 13px;">{initial}</div>
                <div>
                    <p style="color: rgba(255,255,255,0.7); font-size: 0.8rem; margin: 0; font-weight: 500;">{full_name}</p>
                    <p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; margin: 0;">{email}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Logout button
    if st.sidebar.button("Logout", use_container_width=True, key="logout_btn"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.current_page = "Dashboard"
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