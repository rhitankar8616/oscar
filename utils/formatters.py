"""Data formatting utilities."""
from datetime import datetime
import config
import sqlite3


def format_currency(amount: float, currency_code: str = "USD") -> str:
    """
    Format amount as currency.
    
    Args:
        amount: Amount to format
        currency_code: Currency code (USD, EUR, etc.)
        
    Returns:
        Formatted currency string
    """
    symbol = config.CURRENCIES.get(currency_code, "$")
    return f"{symbol}{amount:,.2f}"


def format_date(date_obj, format_str: str = "%b %d, %Y") -> str:
    """
    Format date object to string.
    
    Args:
        date_obj: Date object or string
        format_str: Output format string
        
    Returns:
        Formatted date string
    """
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
        except:
            return date_obj
    
    return date_obj.strftime(format_str)


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format value as percentage.
    
    Args:
        value: Value to format (0-100)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimals}f}%"


def truncate_text(text: str, length: int = 50) -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= length:
        return text
    return text[:length-3] + "..."