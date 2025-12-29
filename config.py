"""Configuration settings for Oscar Finance Tracker."""
import os
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

# Database Configuration
DATABASE_NAME = os.getenv('DATABASE_NAME', 'oscar_finance.db')

# Security Configuration
SECRET_KEY = os.getenv('SECRET_KEY')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in .env file")

# Email Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Validate email configuration
if not EMAIL_USER or not EMAIL_PASSWORD:
    print("WARNING: EMAIL_USER or EMAIL_PASSWORD not set in .env file")
    print(f"Current EMAIL_USER: {EMAIL_USER}")
    print("Email verification will not work!")

# Application Configuration
APP_URL = os.getenv('APP_URL', 'http://localhost:8501')
APP_NAME = "Oscar Finance Tracker"

# Session Configuration
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# UI Configuration
CATEGORIES = [
    "Bills & Rents",
    "Education",
    "Entertainment",
    "Food & Dining",
    "Groceries",
    "Healthcare",
    "Personal Care",
    "Shopping",
    "Transportation",
    "Travel",
    "Other"
]

REMINDER_TYPES = [
    "Salary Day",
    "Rent Payment",
    "EMI Payment",
    "Bill Payment",
    "Subscription",
    "Shopping",
    "Other"
]

CURRENCIES = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "INR": "₹",
    "JPY": "¥"
}

# Payment Methods
PAYMENT_METHODS = [
    "Cash",
    "Credit Card",
    "Debit Card",
    "UPI",
    "Net Banking",
    "Other"
]

# Print configuration for debugging (remove in production)
print(f"[CONFIG] EMAIL_USER: {EMAIL_USER}")
print(f"[CONFIG] SMTP_SERVER: {SMTP_SERVER}")
print(f"[CONFIG] SMTP_PORT: {SMTP_PORT}")
print(f"[CONFIG] APP_URL: {APP_URL}")