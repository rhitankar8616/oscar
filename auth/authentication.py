"""Authentication manager."""
import bcrypt
import secrets
import logging
from typing import Optional, Dict
from database.db_manager import DatabaseManager
import sqlite3

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages user authentication."""
    
    def __init__(self):
        """Initialize authentication manager."""
        self.db = DatabaseManager()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def generate_verification_token(self) -> str:
        """Generate a secure verification token."""
        return secrets.token_urlsafe(32)
    
    def register_user(self, email: str, password: str, full_name: str) -> Optional[Dict]:
        """
        Register a new user.
        
        Returns:
            Dictionary with user_id and verification_token, or None if failed
        """
        # Hash password
        password_hash = self.hash_password(password)
        
        # Generate verification token
        verification_token = self.generate_verification_token()
        
        # Create user
        user_id = self.db.create_user(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            verification_token=verification_token
        )
        
        if user_id:
            return {
                'user_id': user_id,
                'verification_token': verification_token
            }
        return None
    
    def login_user(self, email: str, password: str) -> Optional[Dict]:
        """
        Authenticate user login.
        
        Returns:
            User dictionary if successful, None otherwise
        """
        user = self.db.get_user_by_email(email)
        
        if not user:
            logger.warning(f"Login attempt for non-existent user: {email}")
            return None
        
        if not self.verify_password(password, user['password_hash']):
            logger.warning(f"Invalid password for user: {email}")
            return None
        
        if not user['is_verified']:
            logger.warning(f"Unverified user attempted login: {email}")
            return None
        
        logger.info(f"Successful login: {email}")
        return user
    
    def verify_email(self, email: str, token: str) -> bool:
        """
        Verify user email with token.
        
        Returns:
            True if verification successful
        """
        user = self.db.get_user_by_email(email)
        
        if not user:
            return False
        
        if user['verification_token'] != token:
            logger.warning(f"Invalid verification token for: {email}")
            return False
        
        return self.db.verify_user(email)