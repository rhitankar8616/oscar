"""Database manager for Oscar Finance Tracker."""
import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import config
from utils.encryption import encrypt_data, decrypt_data

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages all database operations with user data isolation."""
    
    def __init__(self, db_name: str = None):
        """Initialize database manager."""
        self.db_name = db_name or config.DATABASE_NAME
        self.init_database()
    
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database schema."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT,
                date_of_birth TEXT,
                occupation TEXT,
                monthly_budget REAL DEFAULT 0,
                hot_charges_threshold REAL DEFAULT 0,
                currency_symbol TEXT DEFAULT '$',
                salary_days TEXT DEFAULT '',
                is_verified INTEGER DEFAULT 0,
                verification_token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                date TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Reminders table (updated schema)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                type TEXT NOT NULL,
                due_date TEXT NOT NULL,
                amount REAL,
                description TEXT,
                notify_days_before INTEGER DEFAULT 3,
                recurring BOOLEAN DEFAULT 0,
                recurrence_type TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Budget settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                total_budget REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                category_budgets TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Friends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS friends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                notes TEXT,
                balance REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Transactions table (for friend expenses)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                friend_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (friend_id) REFERENCES friends(id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_friends_user_id ON friends(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_budget_user_id ON budget_settings(user_id)')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    # User operations
    def create_user(self, email: str, password_hash: str, full_name: str, 
                   verification_token: str) -> Optional[int]:
        """Create a new user."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name, verification_token)
                VALUES (?, ?, ?, ?)
            ''', (email.lower(), password_hash, full_name, verification_token))
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"User created: {email}")
            return user_id
        except sqlite3.IntegrityError:
            logger.warning(f"User already exists: {email}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email.lower(),))
            user = cursor.fetchone()
            conn.close()
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def verify_user(self, email: str) -> bool:
        """Verify user email."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET is_verified = 1, verification_token = NULL
                WHERE email = ?
            ''', (email.lower(),))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return False
    
    def update_user_profile(self, user_id: int, updates: Dict) -> bool:
        """Update user profile."""
        try:
            allowed_fields = ['full_name', 'phone', 'date_of_birth', 'occupation',
                            'monthly_budget', 'hot_charges_threshold', 'currency_symbol',
                            'salary_days']
            
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys() if k in allowed_fields])
            values = [v for k, v in updates.items() if k in allowed_fields]
            values.append(user_id)
            
            if not set_clause:
                return False
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f'UPDATE users SET {set_clause} WHERE id = ?', values)
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False
    
    # Expense operations
    def add_expense(self, user_id: int, title: str, amount: float, category: str,
                   payment_method: str, date: str, notes: str = None) -> Optional[int]:
        """Add a new expense."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO expenses (user_id, title, amount, category, payment_method, date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, title, amount, category, payment_method, date, notes))
            expense_id = cursor.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"Expense added for user {user_id}")
            return expense_id
        except Exception as e:
            logger.error(f"Error adding expense: {e}")
            return None
    
    def get_expenses(self, user_id: int, limit: int = 100) -> List[Dict]:
        """Get user expenses."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM expenses 
                WHERE user_id = ?
                ORDER BY date DESC, created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            expenses = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return expenses
        except Exception as e:
            logger.error(f"Error getting expenses: {e}")
            return []
    
    def get_user_expenses(self, user_id: int, limit: int = 100, 
                         category: str = None, month: str = None) -> List[Dict]:
        """Get user expenses with optional filters."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = 'SELECT * FROM expenses WHERE user_id = ?'
            params = [user_id]
            
            if category and category != "All Categories":
                query += ' AND category = ?'
                params.append(category)
            
            if month:
                query += ' AND strftime("%Y-%m", date) = ?'
                params.append(month)
            
            query += ' ORDER BY date DESC, created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            expenses = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return expenses
        except Exception as e:
            logger.error(f"Error getting expenses: {e}")
            return []
    
    def delete_expense(self, user_id: int, expense_id: int) -> bool:
        """Delete an expense (with user_id check for security)."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?',
                          (expense_id, user_id))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            logger.error(f"Error deleting expense: {e}")
            return False
    
    def get_expense_stats(self, user_id: int, month: str = None) -> Dict:
        """Get expense statistics for user."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT 
                    COUNT(*) as total_count,
                    SUM(amount) as total_spent,
                    AVG(amount) as avg_expense
                FROM expenses 
                WHERE user_id = ?
            '''
            params = [user_id]
            
            if month:
                query += ' AND strftime("%Y-%m", date) = ?'
                params.append(month)
            
            cursor.execute(query, params)
            stats = dict(cursor.fetchone())
            
            # Get category breakdown
            query = '''
                SELECT category, SUM(amount) as amount
                FROM expenses
                WHERE user_id = ?
            '''
            params = [user_id]
            
            if month:
                query += ' AND strftime("%Y-%m", date) = ?'
                params.append(month)
            
            query += ' GROUP BY category ORDER BY amount DESC'
            
            cursor.execute(query, params)
            stats['categories'] = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return stats
        except Exception as e:
            logger.error(f"Error getting expense stats: {e}")
            return {'total_count': 0, 'total_spent': 0, 'avg_expense': 0, 'categories': []}
    
    # Budget operations
    def get_budget_settings(self, user_id: int) -> Optional[Dict]:
        """Get budget settings for user."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM budget_settings WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                budget = dict(result)
                # Parse JSON category_budgets
                if budget.get('category_budgets'):
                    budget['category_budgets'] = json.loads(budget['category_budgets'])
                return budget
            return None
        except Exception as e:
            logger.error(f"Error getting budget settings: {e}")
            return None
    
    def save_budget_settings(self, user_id: int, total_budget: float, 
                           currency: str, category_budgets: Dict) -> bool:
        """Save or update budget settings."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Convert category_budgets dict to JSON string
            category_budgets_json = json.dumps(category_budgets)
            
            # Check if settings exist
            cursor.execute('SELECT id FROM budget_settings WHERE user_id = ?', (user_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing
                cursor.execute('''
                    UPDATE budget_settings 
                    SET total_budget = ?, currency = ?, category_budgets = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (total_budget, currency, category_budgets_json, user_id))
            else:
                # Insert new
                cursor.execute('''
                    INSERT INTO budget_settings (user_id, total_budget, currency, category_budgets)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, total_budget, currency, category_budgets_json))
            
            conn.commit()
            conn.close()
            logger.info(f"Budget settings saved for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving budget settings: {e}")
            return False
    
    # Reminder operations (updated for new schema)
    def add_reminder(self, reminder_data: dict) -> bool:
        """Add a new reminder with new schema."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reminders (
                    user_id, title, type, due_date, amount, 
                    description, notify_days_before, recurring, 
                    recurrence_type, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                reminder_data['user_id'],
                reminder_data['title'],
                reminder_data['type'],
                reminder_data['due_date'],
                reminder_data.get('amount'),
                reminder_data.get('description'),
                reminder_data.get('notify_days_before', 3),
                1 if reminder_data.get('recurring', False) else 0,
                reminder_data.get('recurrence_type'),
                reminder_data.get('status', 'pending')
            ))
            conn.commit()
            conn.close()
            logger.info(f"Reminder added for user {reminder_data['user_id']}")
            return True
        except Exception as e:
            logger.error(f"Error adding reminder: {e}")
            return False
    
    def get_reminders(self, user_id: int, status: str = 'pending') -> List[Dict]:
        """Get reminders for a user by status."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM reminders 
                WHERE user_id = ? AND status = ?
                ORDER BY due_date ASC
            ''', (user_id, status))
            
            reminders = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return reminders
        except Exception as e:
            logger.error(f"Error getting reminders: {e}")
            return []
    
    def get_all_reminders(self, user_id: int) -> List[Dict]:
        """Get all reminders for a user."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM reminders 
                WHERE user_id = ?
                ORDER BY due_date DESC
            ''', (user_id,))
            
            reminders = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return reminders
        except Exception as e:
            logger.error(f"Error getting all reminders: {e}")
            return []
    
    def get_user_reminders(self, user_id: int, include_completed: bool = False) -> List[Dict]:
        """Get user reminders (legacy method for compatibility)."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = 'SELECT * FROM reminders WHERE user_id = ?'
            params = [user_id]
            
            if not include_completed:
                query += ' AND status = "pending"'
            
            query += ' ORDER BY due_date ASC'
            
            cursor.execute(query, params)
            reminders = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return reminders
        except Exception as e:
            logger.error(f"Error getting reminders: {e}")
            return []
    
    def update_reminder_status(self, reminder_id: int, status: str) -> bool:
        """Update reminder status."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE reminders 
                SET status = ?
                WHERE id = ?
            ''', (status, reminder_id))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            logger.error(f"Error updating reminder status: {e}")
            return False
    
    def mark_reminder_complete(self, user_id: int, reminder_id: int) -> bool:
        """Mark reminder as complete (legacy method)."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE reminders SET status = 'completed'
                WHERE id = ? AND user_id = ?
            ''', (reminder_id, user_id))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            logger.error(f"Error marking reminder complete: {e}")
            return False
    
    def delete_reminder(self, reminder_id: int) -> bool:
        """Delete a reminder."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            logger.error(f"Error deleting reminder: {e}")
            return False
    
    # Friend operations
    def add_friend(self, user_id: int, name: str, phone: str = None,
                  email: str = None, notes: str = None) -> Optional[int]:
        """Add a new friend."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO friends (user_id, name, phone, email, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, name, phone, email, notes))
            friend_id = cursor.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"Friend added for user {user_id}")
            return friend_id
        except Exception as e:
            logger.error(f"Error adding friend: {e}")
            return None
    
    def get_user_friends(self, user_id: int) -> List[Dict]:
        """Get user's friends."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM friends WHERE user_id = ? ORDER BY name',
                          (user_id,))
            friends = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return friends
        except Exception as e:
            logger.error(f"Error getting friends: {e}")
            return []
    
    def delete_friend(self, user_id: int, friend_id: int) -> bool:
        """Delete a friend."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM friends WHERE id = ? AND user_id = ?',
                          (friend_id, user_id))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            logger.error(f"Error deleting friend: {e}")
            return False
    
    # Transaction operations
    def add_transaction(self, user_id: int, friend_id: int, transaction_type: str,
                       amount: float, description: str, date: str) -> Optional[int]:
        """Add a transaction with a friend."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Add transaction
            cursor.execute('''
                INSERT INTO transactions 
                (user_id, friend_id, transaction_type, amount, description, date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, friend_id, transaction_type, amount, description, date))
            
            # Update friend balance
            balance_change = amount if transaction_type == "lent" else -amount
            cursor.execute('''
                UPDATE friends SET balance = balance + ? 
                WHERE id = ? AND user_id = ?
            ''', (balance_change, friend_id, user_id))
            
            transaction_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return transaction_id
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            return None
    
    def get_friend_transactions(self, user_id: int, friend_id: int) -> List[Dict]:
        """Get transactions for a specific friend."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM transactions 
                WHERE user_id = ? AND friend_id = ?
                ORDER BY date DESC, created_at DESC
            ''', (user_id, friend_id))
            transactions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return transactions
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            return []
    
    def delete_transaction(self, user_id: int, transaction_id: int) -> bool:
        """Delete a transaction."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get transaction details first
            cursor.execute('''
                SELECT friend_id, transaction_type, amount 
                FROM transactions 
                WHERE id = ? AND user_id = ?
            ''', (transaction_id, user_id))
            
            transaction = cursor.fetchone()
            if not transaction:
                return False
            
            friend_id, trans_type, amount = transaction
            
            # Delete transaction
            cursor.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?',
                          (transaction_id, user_id))
            
            # Reverse balance change
            balance_change = -amount if trans_type == "lent" else amount
            cursor.execute('''
                UPDATE friends SET balance = balance + ? 
                WHERE id = ? AND user_id = ?
            ''', (balance_change, friend_id, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting transaction: {e}")
            return False