"""UI components for Oscar Finance Tracker."""
from .dashboard import render_dashboard
from .expenses import render_expenses
from .reminders import render_reminders
from .budget import render_budget
from .friends import render_friends
from .analytics import render_analytics
from .profile import render_profile
import sqlite3

__all__ = [
    'render_dashboard',
    'render_expenses',
    'render_reminders',
    'render_budget',
    'render_friends',
    'render_analytics',
    'render_profile'
]