"""Data models for Oscar Finance Tracker."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import sqlite3


@dataclass
class User:
    """User model."""
    id: Optional[int]
    email: str
    password_hash: str
    full_name: str
    phone: Optional[str]
    date_of_birth: Optional[str]
    occupation: Optional[str]
    monthly_budget: float
    hot_charges_threshold: float
    currency_symbol: str
    salary_days: str
    is_verified: bool
    verification_token: Optional[str]
    created_at: datetime


@dataclass
class Expense:
    """Expense model."""
    id: Optional[int]
    user_id: int
    title: str
    amount: float
    category: str
    payment_method: str
    date: str
    notes: Optional[str]
    created_at: datetime


@dataclass
class Reminder:
    """Reminder model."""
    id: Optional[int]
    user_id: int
    title: str
    reminder_type: str
    date: str
    amount: Optional[float]
    frequency: Optional[str]
    is_recurring: bool
    notes: Optional[str]
    is_completed: bool
    created_at: datetime


@dataclass
class Budget:
    """Budget model."""
    id: Optional[int]
    user_id: int
    month: str
    total_budget: float
    total_spent: float
    created_at: datetime


@dataclass
class Friend:
    """Friend model."""
    id: Optional[int]
    user_id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    notes: Optional[str]
    balance: float
    created_at: datetime


@dataclass
class Transaction:
    """Friend transaction model."""
    id: Optional[int]
    user_id: int
    friend_id: int
    transaction_type: str
    amount: float
    description: str
    date: str
    created_at: datetime