"""Data encryption utilities."""
from cryptography.fernet import Fernet
import config
import base64
import logging
import sqlite3

logger = logging.getLogger(__name__)


def get_cipher():
    """Get Fernet cipher instance."""
    if not config.ENCRYPTION_KEY:
        # Generate a key if not provided (for development only)
        key = Fernet.generate_key()
        logger.warning("Using generated encryption key. Set ENCRYPTION_KEY in production!")
        return Fernet(key)
    
    return Fernet(config.ENCRYPTION_KEY.encode())


def encrypt_data(data: str) -> str:
    """
    Encrypt sensitive data.
    
    Args:
        data: Plain text string to encrypt
        
    Returns:
        Encrypted string
    """
    try:
        cipher = get_cipher()
        encrypted = cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt encrypted data.
    
    Args:
        encrypted_data: Encrypted string
        
    Returns:
        Decrypted plain text string
    """
    try:
        cipher = get_cipher()
        decoded = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = cipher.decrypt(decoded)
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise