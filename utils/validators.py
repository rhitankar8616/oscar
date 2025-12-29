"""Input validation utilities."""
import re
from email_validator import validate_email as email_validate, EmailNotValidError
import logging
import sqlite3

logger = logging.getLogger(__name__)


def validate_email(email: str) -> tuple[bool, str, str]:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, validated_email, message)
    """
    email = email.strip().lower()  # normalize
    
    try:
        valid = email_validate(email)
        return True, valid.email, "Valid email"
    except EmailNotValidError as e:
        return False, email, str(e)

def validate_phone(phone: str) -> tuple[bool, str, str]:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (is_valid, cleaned_phone, message)
    """
    if not phone or phone.strip() == "":
        return True, "", ""  # Empty phone is valid (optional field)
    
    # Remove spaces and common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it's numeric and has reasonable length
    if not cleaned.isdigit():
        return False, "", "Phone number must contain only digits"
    
    if len(cleaned) < 10 or len(cleaned) > 15:
        return False, "", "Phone number must be between 10-15 digits"
    
    return True, cleaned, ""

def validate_amount(amount: str) -> tuple[bool, float, str]:
    """
    Validate monetary amount.
    
    Args:
        amount: Amount string to validate
        
    Returns:
        Tuple of (is_valid, amount_float, message)
    """
    try:
        amount_float = float(amount)
        
        if amount_float < 0:
            return False, 0.0, "Amount cannot be negative"
        
        if amount_float > 999999999:
            return False, 0.0, "Amount is too large"
        
        return True, round(amount_float, 2), ""
    
    except ValueError:
        return False, 0.0, "Invalid amount format"


def validate_date(date_str: str) -> tuple[bool, str]:
    """
    Validate date format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False, "Date must be in YYYY-MM-DD format"
    
    return True, ""


def sanitize_input(text: str, max_length: int = 500) -> str:
    """
    Sanitize user input text.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    # Remove any potentially harmful characters
    sanitized = re.sub(r'[<>\"\'`]', '', text)
    return sanitized[:max_length].strip()