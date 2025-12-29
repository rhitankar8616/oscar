"""Manual email verification script - Run this to verify your stuck email."""
import sqlite3
import sys

def verify_email_manually(email):
    """Manually verify an email in the database."""
    try:
        # Connect to database
        conn = sqlite3.connect('oscar.db')
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id, email, is_verified FROM users WHERE email = ?', (email.lower(),))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ No user found with email: {email}")
            conn.close()
            return False
        
        user_id, user_email, is_verified = user
        
        if is_verified:
            print(f"✅ Email {user_email} is already verified!")
            conn.close()
            return True
        
        # Verify the user
        cursor.execute('''
            UPDATE users 
            SET is_verified = 1, verification_token = NULL 
            WHERE email = ?
        ''', (email.lower(),))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Successfully verified email: {user_email}")
        print(f"   User ID: {user_id}")
        print(f"\nYou can now login with this email!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("OSCAR - Manual Email Verification")
    print("="*60)
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("\nEnter the email address to verify: ").strip()
    
    if not email:
        print("❌ No email provided!")
        sys.exit(1)
    
    print(f"\nAttempting to verify: {email}")
    print("-"*60)
    
    verify_email_manually(email)