"""Configuration settings for Oscar Finance Tracker."""
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file (for local development)
load_dotenv()

# Get configuration from environment variables or Streamlit secrets
def get_config(key, default=None):
    """Get config from environment or Streamlit secrets."""
    # First try environment variable
    value = os.getenv(key)
    if value:
        return value
    
    # Then try Streamlit secrets (for cloud deployment)
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    
    return default

# Application settings
APP_NAME = "OSCAR"
APP_URL = get_config("APP_URL", "http://localhost:8501")
DATABASE_NAME = "oscar.db"

# Email settings (for verification emails)
EMAIL_USER = get_config("EMAIL_USER", "")
EMAIL_PASSWORD = get_config("EMAIL_PASSWORD", "")
SMTP_SERVER = get_config("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(get_config("SMTP_PORT", "587"))

# Print config status (for debugging)
print("[CONFIG] EMAIL_USER:", EMAIL_USER if EMAIL_USER else "Not configured")
print("[CONFIG] SMTP_SERVER:", SMTP_SERVER)
print("[CONFIG] SMTP_PORT:", SMTP_PORT)
print("[CONFIG] APP_URL:", APP_URL)