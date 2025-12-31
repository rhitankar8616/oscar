"""UI components for Oscar Finance Tracker."""
from .auth import render_auth
from .dashboard import render_dashboard
from .expenses import render_expenses
from .reminders import render_reminders
from .dates import render_dates
from .budget import render_budget
from .friends import render_friends
from .analytics import render_analytics
from .profile import render_profile

__all__ = [
    'render_auth',
    'render_dashboard',
    'render_expenses',
    'render_reminders',
    'render_dates',
    'render_budget',
    'render_friends',
    'render_analytics',
    'render_profile'
]