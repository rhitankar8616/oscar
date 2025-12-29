"""Email service for sending verification emails."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import config

logger = logging.getLogger(__name__)


class EmailService:
    """Handles email sending operations."""
    
    def __init__(self):
        """Initialize email service."""
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.email_user = config.EMAIL_USER
        self.email_password = config.EMAIL_PASSWORD
    
    def send_verification_email(self, to_email: str, verification_token: str) -> bool:
        """
        Send verification email to user.
        
        Args:
            to_email: Recipient email address
            verification_token: Verification token
            
        Returns:
            True if email sent successfully
        """
        # Check if email configuration is available
        if not self.email_user or not self.email_password:
            logger.error("Email configuration missing. Please set EMAIL_USER and EMAIL_PASSWORD in .env")
            return False
        
        try:
            verification_link = f"{config.APP_URL}/?verify={verification_token}&email={to_email}"
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Verify your {config.APP_NAME} account"
            msg['From'] = self.email_user
            msg['To'] = to_email
            
            # Plain text version
            text = f"""
            Welcome to {config.APP_NAME}!
            
            Please verify your email address by clicking the link below or copying it to your browser:
            
            {verification_link}
            
            If you didn't create an account, you can safely ignore this email.
            
            Best regards,
            {config.APP_NAME} Team
            """
            
            # HTML email body
            html = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #2C3E50; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                        .content {{ padding: 30px; background-color: #f4f4f4; border-radius: 0 0 10px 10px; }}
                        .button {{ 
                            display: inline-block; 
                            padding: 15px 40px; 
                            background-color: #FF9800; 
                            color: white; 
                            text-decoration: none; 
                            border-radius: 8px;
                            margin: 20px 0;
                            font-weight: bold;
                        }}
                        .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
                        .link {{ color: #666; word-break: break-all; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1 style="margin: 0;">💰 {config.APP_NAME}</h1>
                        </div>
                        <div class="content">
                            <h2>Welcome! Please verify your email</h2>
                            <p>Thank you for signing up for {config.APP_NAME}. To get started, please verify your email address by clicking the button below:</p>
                            <center>
                                <a href="{verification_link}" class="button">Verify Email Address</a>
                            </center>
                            <p>Or copy and paste this link into your browser:</p>
                            <p class="link">{verification_link}</p>
                            <p style="margin-top: 30px; color: #888;">If you didn't create an account, you can safely ignore this email.</p>
                        </div>
                        <div class="footer">
                            <p>© 2025 {config.APP_NAME}. All rights reserved.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            logger.info(f"Attempting to send verification email to: {to_email}")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.set_debuglevel(0)  # Set to 1 for debugging
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Verification email sent successfully to: {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed. Check EMAIL_USER and EMAIL_PASSWORD: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending verification email: {e}")
            return False
    
    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email."""
        # Implement password reset functionality if needed
        pass