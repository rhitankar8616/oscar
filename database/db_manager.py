"""Database manager for Oscar Finance Tracker with PostgreSQL/SQLite support."""
import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
from contextlib import contextmanager

# Try to import psycopg2 for PostgreSQL
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

import sqlite3

logger = logging.getLogger(__name__)


def get_database_url():
    """Get database URL from Streamlit secrets or environment."""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'database' in st.secrets:
            return st.secrets['database'].get('url', None)
    except:
        pass
    return os.environ.get('DATABASE_URL', None)


class DatabaseManager:
    """Manages all database operations with PostgreSQL/SQLite support."""
    
    def __init__(self, db_name: str = None):
        """Initialize database manager."""
        self.database_url = get_database_url()
        self.use_postgres = HAS_POSTGRES and self.database_url is not None
        
        if not self.use_postgres:
            # Fall back to SQLite for local development
            self.db_name = db_name or "oscar.db"
            logger.info("Using SQLite database")
        else:
            logger.info("Using PostgreSQL database")
        
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Get database connection - works with both PostgreSQL and SQLite."""
        if self.use_postgres:
            conn = psycopg2.connect(self.database_url)
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        else:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            finally:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False, 
                      fetchone: bool = False):
        """Execute a query with automatic parameter placeholder conversion."""
        # Convert ? to %s for PostgreSQL
        if self.use_postgres:
            query = query.replace('?', '%s')
        
        with self.get_connection() as conn:
            if self.use_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if fetch:
                    rows = cursor.fetchall()
                    if self.use_postgres:
                        return [dict(row) for row in rows]
                    else:
                        return [dict(row) for row in rows]
                elif fetchone:
                    row = cursor.fetchone()
                    if row:
                        return dict(row)
                    return None
                
                # For INSERT, try to get lastrowid
                if query.strip().upper().startswith('INSERT'):
                    if self.use_postgres:
                        return cursor.fetchone()['id'] if cursor.description else True
                    else:
                        return cursor.lastrowid
                return True
            except Exception as e:
                logger.error(f"Database error: {e}")
                return None if (fetch or fetchone) else False
    
    def init_database(self):
        """Initialize database schema."""
        if self.use_postgres:
            self._init_postgres_schema()
        else:
            self._init_sqlite_schema()
        logger.info("Database initialized successfully")
    
    def _init_postgres_schema(self):
        """Initialize PostgreSQL schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    phone VARCHAR(50),
                    date_of_birth DATE,
                    occupation VARCHAR(255),
                    monthly_budget DECIMAL(12,2) DEFAULT 0,
                    hot_charges_threshold DECIMAL(12,2) DEFAULT 0,
                    currency_symbol VARCHAR(10) DEFAULT '$',
                    salary_days VARCHAR(50) DEFAULT '',
                    is_verified BOOLEAN DEFAULT FALSE,
                    verification_token VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Expenses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR(255) NOT NULL,
                    amount DECIMAL(12,2) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    payment_method VARCHAR(100) NOT NULL,
                    date DATE NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Reminders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR(255) NOT NULL,
                    type VARCHAR(100) NOT NULL,
                    due_date DATE NOT NULL,
                    amount DECIMAL(12,2),
                    description TEXT,
                    notify_days_before INTEGER DEFAULT 3,
                    recurring BOOLEAN DEFAULT FALSE,
                    recurrence_type VARCHAR(50),
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Budget settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS budget_settings (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                    total_budget DECIMAL(12,2) NOT NULL,
                    currency VARCHAR(10) DEFAULT 'USD',
                    category_budgets TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Friends table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS friends (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(50),
                    email VARCHAR(255),
                    notes TEXT,
                    balance DECIMAL(12,2) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    friend_id INTEGER REFERENCES friends(id) ON DELETE CASCADE,
                    transaction_type VARCHAR(50) NOT NULL,
                    amount DECIMAL(12,2) NOT NULL,
                    description TEXT NOT NULL,
                    date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_friends_user_id ON friends(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_budget_user_id ON budget_settings(user_id)')
    
    def _init_sqlite_schema(self):
        """Initialize SQLite schema."""
        conn = sqlite3.connect(self.db_name)
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
        
        # Reminders table
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
        
        # Transactions table
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
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_friends_user_id ON friends(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_budget_user_id ON budget_settings(user_id)')
        
        conn.commit()
        conn.close()
    
    def _convert_user_types(self, user: Dict) -> Dict:
        """Convert PostgreSQL types to Python types for user."""
        if user and self.use_postgres:
            user['is_verified'] = bool(user.get('is_verified'))
            if user.get('date_of_birth'):
                user['date_of_birth'] = str(user['date_of_birth'])
            if user.get('created_at'):
                user['created_at'] = str(user['created_at'])
            if user.get('monthly_budget'):
                user['monthly_budget'] = float(user['monthly_budget'])
            if user.get('hot_charges_threshold'):
                user['hot_charges_threshold'] = float(user['hot_charges_threshold'])
        return user
    
    # ============ USER OPERATIONS ============
    
    def create_user(self, email: str, password_hash: str, full_name: str, 
                    verification_token: str) -> Optional[int]:
        """Create a new user."""
        try:
            if self.use_postgres:
                query = '''
                    INSERT INTO users (email, password_hash, full_name, verification_token)
                    VALUES (%s, %s, %s, %s) RETURNING id
                '''
                with self.get_connection() as conn:
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                    cursor.execute(query, (email.lower(), password_hash, full_name, verification_token))
                    result = cursor.fetchone()
                    user_id = result['id'] if result else None
            else:
                query = '''
                    INSERT INTO users (email, password_hash, full_name, verification_token)
                    VALUES (?, ?, ?, ?)
                '''
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, (email.lower(), password_hash, full_name, verification_token))
                    user_id = cursor.lastrowid
            
            logger.info(f"User created: {email}")
            return user_id
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        try:
            query = 'SELECT * FROM users WHERE email = ?'
            user = self.execute_query(query, (email.lower(),), fetchone=True)
            return self._convert_user_types(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID."""
        try:
            query = 'SELECT * FROM users WHERE id = ?'
            user = self.execute_query(query, (user_id,), fetchone=True)
            return self._convert_user_types(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def verify_user(self, email: str) -> bool:
        """Verify user email."""
        try:
            if self.use_postgres:
                query = '''
                    UPDATE users SET is_verified = TRUE, verification_token = NULL
                    WHERE email = %s
                '''
            else:
                query = '''
                    UPDATE users SET is_verified = 1, verification_token = NULL
                    WHERE email = ?
                '''
            return self.execute_query(query, (email.lower(),))
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return False
    
    def update_user_profile(self, user_id: int, updates: Dict) -> bool:
        """Update user profile."""
        try:
            allowed_fields = ['full_name', 'phone', 'date_of_birth', 'occupation',
                            'monthly_budget', 'hot_charges_threshold', 'currency_symbol',
                            'salary_days']
            
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            if not filtered_updates:
                return False
            
            set_clause = ', '.join([f"{k} = ?" for k in filtered_updates.keys()])
            values = list(filtered_updates.values())
            values.append(user_id)
            
            query = f'UPDATE users SET {set_clause} WHERE id = ?'
            return self.execute_query(query, tuple(values))
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False
    
    # ============ EXPENSE OPERATIONS ============
    
    def add_expense(self, user_id: int, title: str, amount: float, category: str,
                    payment_method: str, date: str, notes: str = None) -> Optional[int]:
        """Add a new expense."""
        try:
            if self.use_postgres:
                query = '''
                    INSERT INTO expenses (user_id, title, amount, category, payment_method, date, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
                '''
                with self.get_connection() as conn:
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                    cursor.execute(query, (user_id, title, amount, category, payment_method, date, notes))
                    result = cursor.fetchone()
                    expense_id = result['id'] if result else None
            else:
                query = '''
                    INSERT INTO expenses (user_id, title, amount, category, payment_method, date, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                '''
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, (user_id, title, amount, category, payment_method, date, notes))
                    expense_id = cursor.lastrowid
            
            logger.info(f"Expense added for user {user_id}")
            return expense_id
        except Exception as e:
            logger.error(f"Error adding expense: {e}")
            return None
    
    def get_expenses(self, user_id: int, limit: int = 100) -> List[Dict]:
        """Get user expenses."""
        try:
            query = '''
                SELECT * FROM expenses 
                WHERE user_id = ?
                ORDER BY date DESC, created_at DESC 
                LIMIT ?
            '''
            expenses = self.execute_query(query, (user_id, limit), fetch=True)
            if expenses and self.use_postgres:
                for exp in expenses:
                    if exp.get('date'):
                        exp['date'] = str(exp['date'])
                    if exp.get('amount'):
                        exp['amount'] = float(exp['amount'])
            return expenses or []
        except Exception as e:
            logger.error(f"Error getting expenses: {e}")
            return []
    
    def get_user_expenses(self, user_id: int, limit: int = 100, 
                          category: str = None, month: str = None) -> List[Dict]:
        """Get user expenses with optional filters."""
        try:
            query = 'SELECT * FROM expenses WHERE user_id = ?'
            params = [user_id]
            
            if category and category != "All Categories":
                query += ' AND category = ?'
                params.append(category)
            
            if month:
                if self.use_postgres:
                    query += " AND TO_CHAR(date, 'YYYY-MM') = ?"
                else:
                    query += ' AND strftime("%Y-%m", date) = ?'
                params.append(month)
            
            query += ' ORDER BY date DESC, created_at DESC LIMIT ?'
            params.append(limit)
            
            expenses = self.execute_query(query, tuple(params), fetch=True)
            if expenses and self.use_postgres:
                for exp in expenses:
                    if exp.get('date'):
                        exp['date'] = str(exp['date'])
                    if exp.get('amount'):
                        exp['amount'] = float(exp['amount'])
            return expenses or []
        except Exception as e:
            logger.error(f"Error getting expenses: {e}")
            return []
    
    def delete_expense(self, user_id: int, expense_id: int) -> bool:
        """Delete an expense."""
        try:
            query = 'DELETE FROM expenses WHERE id = ? AND user_id = ?'
            return self.execute_query(query, (expense_id, user_id))
        except Exception as e:
            logger.error(f"Error deleting expense: {e}")
            return False
    
    def get_expense_stats(self, user_id: int, month: str = None) -> Dict:
        """Get expense statistics for user."""
        try:
            # Total stats
            query = '''
                SELECT 
                    COUNT(*) as total_count,
                    COALESCE(SUM(amount), 0) as total_spent,
                    COALESCE(AVG(amount), 0) as avg_expense
                FROM expenses 
                WHERE user_id = ?
            '''
            params = [user_id]
            
            if month:
                if self.use_postgres:
                    query += " AND TO_CHAR(date, 'YYYY-MM') = ?"
                else:
                    query += ' AND strftime("%Y-%m", date) = ?'
                params.append(month)
            
            stats = self.execute_query(query, tuple(params), fetchone=True)
            if stats:
                stats['total_spent'] = float(stats['total_spent'] or 0)
                stats['avg_expense'] = float(stats['avg_expense'] or 0)
            else:
                stats = {'total_count': 0, 'total_spent': 0, 'avg_expense': 0}
            
            # Category breakdown
            query = '''
                SELECT category, SUM(amount) as amount
                FROM expenses
                WHERE user_id = ?
            '''
            params = [user_id]
            
            if month:
                if self.use_postgres:
                    query += " AND TO_CHAR(date, 'YYYY-MM') = ?"
                else:
                    query += ' AND strftime("%Y-%m", date) = ?'
                params.append(month)
            
            query += ' GROUP BY category ORDER BY amount DESC'
            
            categories = self.execute_query(query, tuple(params), fetch=True)
            if categories:
                for cat in categories:
                    cat['amount'] = float(cat['amount'] or 0)
            stats['categories'] = categories or []
            
            return stats
        except Exception as e:
            logger.error(f"Error getting expense stats: {e}")
            return {'total_count': 0, 'total_spent': 0, 'avg_expense': 0, 'categories': []}
    
    # ============ BUDGET OPERATIONS ============
    
    def get_budget_settings(self, user_id: int) -> Optional[Dict]:
        """Get budget settings for user."""
        try:
            query = 'SELECT * FROM budget_settings WHERE user_id = ?'
            result = self.execute_query(query, (user_id,), fetchone=True)
            
            if result:
                if result.get('total_budget'):
                    result['total_budget'] = float(result['total_budget'])
                if result.get('category_budgets'):
                    result['category_budgets'] = json.loads(result['category_budgets'])
                return result
            return None
        except Exception as e:
            logger.error(f"Error getting budget settings: {e}")
            return None
    
    def save_budget_settings(self, user_id: int, total_budget: float, 
                             currency: str, category_budgets: Dict) -> bool:
        """Save or update budget settings."""
        try:
            category_budgets_json = json.dumps(category_budgets)
            
            # Check if exists
            existing = self.get_budget_settings(user_id)
            
            if existing:
                query = '''
                    UPDATE budget_settings 
                    SET total_budget = ?, currency = ?, category_budgets = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                '''
                params = (total_budget, currency, category_budgets_json, user_id)
            else:
                query = '''
                    INSERT INTO budget_settings (user_id, total_budget, currency, category_budgets)
                    VALUES (?, ?, ?, ?)
                '''
                params = (user_id, total_budget, currency, category_budgets_json)
            
            result = self.execute_query(query, params)
            logger.info(f"Budget settings saved for user {user_id}")
            return bool(result)
        except Exception as e:
            logger.error(f"Error saving budget settings: {e}")
            return False
    
    # ============ REMINDER OPERATIONS ============
    
    def add_reminder(self, reminder_data: dict) -> bool:
        """Add a new reminder."""
        try:
            recurring_val = reminder_data.get('recurring', False)
            if not self.use_postgres:
                recurring_val = 1 if recurring_val else 0
            
            if self.use_postgres:
                query = '''
                    INSERT INTO reminders (
                        user_id, title, type, due_date, amount, 
                        description, notify_days_before, recurring, 
                        recurrence_type, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
            else:
                query = '''
                    INSERT INTO reminders (
                        user_id, title, type, due_date, amount, 
                        description, notify_days_before, recurring, 
                        recurrence_type, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
            
            params = (
                reminder_data['user_id'],
                reminder_data['title'],
                reminder_data['type'],
                reminder_data['due_date'],
                reminder_data.get('amount'),
                reminder_data.get('description'),
                reminder_data.get('notify_days_before', 3),
                recurring_val,
                reminder_data.get('recurrence_type'),
                reminder_data.get('status', 'pending')
            )
            
            return self.execute_query(query, params)
        except Exception as e:
            logger.error(f"Error adding reminder: {e}")
            return False
    
    def _convert_reminder_types(self, reminders: List[Dict]) -> List[Dict]:
        """Convert reminder types for PostgreSQL."""
        if reminders and self.use_postgres:
            for rem in reminders:
                rem['recurring'] = bool(rem.get('recurring'))
                if rem.get('due_date'):
                    rem['due_date'] = str(rem['due_date'])
                if rem.get('amount'):
                    rem['amount'] = float(rem['amount'])
                if rem.get('created_at'):
                    rem['created_at'] = str(rem['created_at'])
        return reminders
    
    def get_reminders(self, user_id: int, status: str = 'pending') -> List[Dict]:
        """Get reminders for a user by status."""
        try:
            query = '''
                SELECT * FROM reminders 
                WHERE user_id = ? AND status = ?
                ORDER BY due_date ASC
            '''
            reminders = self.execute_query(query, (user_id, status), fetch=True)
            return self._convert_reminder_types(reminders or [])
        except Exception as e:
            logger.error(f"Error getting reminders: {e}")
            return []
    
    def get_all_reminders(self, user_id: int) -> List[Dict]:
        """Get all reminders for a user."""
        try:
            query = '''
                SELECT * FROM reminders 
                WHERE user_id = ?
                ORDER BY due_date DESC
            '''
            reminders = self.execute_query(query, (user_id,), fetch=True)
            return self._convert_reminder_types(reminders or [])
        except Exception as e:
            logger.error(f"Error getting all reminders: {e}")
            return []
    
    def get_user_reminders(self, user_id: int, include_completed: bool = False) -> List[Dict]:
        """Get user reminders."""
        try:
            if include_completed:
                query = 'SELECT * FROM reminders WHERE user_id = ? ORDER BY due_date ASC'
                params = (user_id,)
            else:
                query = 'SELECT * FROM reminders WHERE user_id = ? AND status = ? ORDER BY due_date ASC'
                params = (user_id, 'pending')
            
            reminders = self.execute_query(query, params, fetch=True)
            return self._convert_reminder_types(reminders or [])
        except Exception as e:
            logger.error(f"Error getting reminders: {e}")
            return []
    
    def update_reminder_status(self, reminder_id: int, status: str) -> bool:
        """Update reminder status."""
        try:
            query = 'UPDATE reminders SET status = ? WHERE id = ?'
            return self.execute_query(query, (status, reminder_id))
        except Exception as e:
            logger.error(f"Error updating reminder status: {e}")
            return False
    
    def mark_reminder_complete(self, user_id: int, reminder_id: int) -> bool:
        """Mark reminder as complete."""
        try:
            query = "UPDATE reminders SET status = 'completed' WHERE id = ? AND user_id = ?"
            return self.execute_query(query, (reminder_id, user_id))
        except Exception as e:
            logger.error(f"Error marking reminder complete: {e}")
            return False
    
    def delete_reminder(self, reminder_id: int) -> bool:
        """Delete a reminder."""
        try:
            query = 'DELETE FROM reminders WHERE id = ?'
            return self.execute_query(query, (reminder_id,))
        except Exception as e:
            logger.error(f"Error deleting reminder: {e}")
            return False
    
    # ============ FRIEND OPERATIONS ============
    
    def add_friend(self, user_id: int, name: str, phone: str = None,
                   email: str = None, notes: str = None) -> Optional[int]:
        """Add a new friend."""
        try:
            if self.use_postgres:
                query = '''
                    INSERT INTO friends (user_id, name, phone, email, notes)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                '''
                with self.get_connection() as conn:
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                    cursor.execute(query, (user_id, name, phone, email, notes))
                    result = cursor.fetchone()
                    friend_id = result['id'] if result else None
            else:
                query = '''
                    INSERT INTO friends (user_id, name, phone, email, notes)
                    VALUES (?, ?, ?, ?, ?)
                '''
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, (user_id, name, phone, email, notes))
                    friend_id = cursor.lastrowid
            
            logger.info(f"Friend added for user {user_id}")
            return friend_id
        except Exception as e:
            logger.error(f"Error adding friend: {e}")
            return None
    
    def get_user_friends(self, user_id: int) -> List[Dict]:
        """Get user's friends."""
        try:
            query = 'SELECT * FROM friends WHERE user_id = ? ORDER BY name'
            friends = self.execute_query(query, (user_id,), fetch=True)
            if friends and self.use_postgres:
                for friend in friends:
                    if friend.get('balance'):
                        friend['balance'] = float(friend['balance'])
            return friends or []
        except Exception as e:
            logger.error(f"Error getting friends: {e}")
            return []
    
    def get_friends(self, user_id: int) -> List[Dict]:
        """Alias for get_user_friends."""
        return self.get_user_friends(user_id)
    
    def delete_friend(self, user_id: int, friend_id: int) -> bool:
        """Delete a friend."""
        try:
            query = 'DELETE FROM friends WHERE id = ? AND user_id = ?'
            return self.execute_query(query, (friend_id, user_id))
        except Exception as e:
            logger.error(f"Error deleting friend: {e}")
            return False
    
    def update_friend_balance(self, friend_id: int, amount: float) -> bool:
        """Update friend balance."""
        try:
            query = 'UPDATE friends SET balance = balance + ? WHERE id = ?'
            return self.execute_query(query, (amount, friend_id))
        except Exception as e:
            logger.error(f"Error updating friend balance: {e}")
            return False
    
    # ============ TRANSACTION OPERATIONS ============
    
    def add_transaction(self, user_id: int, friend_id: int, transaction_type: str,
                        amount: float, description: str, date: str) -> Optional[int]:
        """Add a transaction with a friend."""
        try:
            if self.use_postgres:
                query = '''
                    INSERT INTO transactions 
                    (user_id, friend_id, transaction_type, amount, description, date)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                '''
                with self.get_connection() as conn:
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                    cursor.execute(query, (user_id, friend_id, transaction_type, amount, description, date))
                    result = cursor.fetchone()
                    transaction_id = result['id'] if result else None
                    
                    # Update friend balance
                    balance_change = amount if transaction_type == "lent" else -amount
                    cursor.execute(
                        'UPDATE friends SET balance = balance + %s WHERE id = %s AND user_id = %s',
                        (balance_change, friend_id, user_id)
                    )
            else:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
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
            
            return transaction_id
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            return None
    
    def get_friend_transactions(self, user_id: int, friend_id: int) -> List[Dict]:
        """Get transactions for a specific friend."""
        try:
            query = '''
                SELECT * FROM transactions 
                WHERE user_id = ? AND friend_id = ?
                ORDER BY date DESC, created_at DESC
            '''
            transactions = self.execute_query(query, (user_id, friend_id), fetch=True)
            if transactions and self.use_postgres:
                for t in transactions:
                    if t.get('date'):
                        t['date'] = str(t['date'])
                    if t.get('amount'):
                        t['amount'] = float(t['amount'])
            return transactions or []
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            return []
    
    def delete_transaction(self, user_id: int, transaction_id: int) -> bool:
        """Delete a transaction and reverse balance."""
        try:
            # Get transaction details first
            query = '''
                SELECT friend_id, transaction_type, amount 
                FROM transactions 
                WHERE id = ? AND user_id = ?
            '''
            transaction = self.execute_query(query, (transaction_id, user_id), fetchone=True)
            
            if not transaction:
                return False
            
            friend_id = transaction['friend_id']
            trans_type = transaction['transaction_type']
            amount = float(transaction['amount'])
            
            # Delete transaction
            delete_query = 'DELETE FROM transactions WHERE id = ? AND user_id = ?'
            self.execute_query(delete_query, (transaction_id, user_id))
            
            # Reverse balance change
            balance_change = -amount if trans_type == "lent" else amount
            self.update_friend_balance(friend_id, balance_change)
            
            return True
        except Exception as e:
            logger.error(f"Error deleting transaction: {e}")
            return False