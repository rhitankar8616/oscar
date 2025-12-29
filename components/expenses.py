"""Expenses component."""
import streamlit as st
from datetime import datetime
from database.db_manager import DatabaseManager
from utils.formatters import format_currency, format_date
from utils.validators import validate_amount, sanitize_input
import config

def render_expenses(user: dict, db: DatabaseManager):
    """Render expenses management page."""
    
    st.markdown("#### Expenses")
    st.caption("Track and manage your spending")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Add Expense", type="primary", use_container_width=True):
            st.session_state.show_add_expense = True
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.get('show_add_expense', False):
        with st.container():
            st.markdown("### Add New Expense")
            
            with st.form("add_expense_form"):
                form_col1, form_col2 = st.columns(2)
                
                with form_col1:
                    title = st.text_input("Title *", placeholder="e.g., Grocery Shopping")
                    amount = st.text_input("Amount ($) *", placeholder="15.00")
                    category = st.selectbox("Category *", config.CATEGORIES)
                    date = st.date_input("Date *", value=datetime.now())
                
                with form_col2:
                    payment_method = st.selectbox("Payment Method *", config.PAYMENT_METHODS)
                    notes = st.text_area("Notes", placeholder="Additional details...")
                
                submit_col1, submit_col2 = st.columns([1, 1])
                
                with submit_col1:
                    submitted = st.form_submit_button("Add Expense", use_container_width=True, type="primary")
                
                with submit_col2:
                    cancelled = st.form_submit_button("Cancel", use_container_width=True)
                
                if cancelled:
                    st.session_state.show_add_expense = False
                    st.rerun()
                
                if submitted:
                    if not title or not amount:
                        st.error("Please fill in all required fields")
                    else:
                        is_valid, amount_float, error_msg = validate_amount(amount)
                        
                        if not is_valid:
                            st.error(error_msg)
                        else:
                            expense_id = db.add_expense(
                                user_id=user['id'],
                                title=sanitize_input(title),
                                amount=amount_float,
                                category=category,
                                payment_method=payment_method,
                                date=date.strftime("%Y-%m-%d"),
                                notes=sanitize_input(notes) if notes else None
                            )
                            
                            if expense_id:
                                st.success("Expense added successfully!")
                                st.session_state.show_add_expense = False
                                st.rerun()
                            else:
                                st.error("Failed to add expense. Please try again.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    filter_col1, filter_col2 = st.columns([3, 1])
    
    with filter_col1:
        search = st.text_input("Search expenses...", placeholder="Search by title or notes", label_visibility="collapsed")
    
    with filter_col2:
        category_filter = st.selectbox("All Categories", 
                                      ["All Categories"] + config.CATEGORIES,
                                      label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    expenses = db.get_user_expenses(
        user['id'], 
        category=category_filter if category_filter != "All Categories" else None
    )
    
    if search:
        search_lower = search.lower()
        expenses = [e for e in expenses if 
                   search_lower in e['title'].lower() or 
                   (e['notes'] and search_lower in e['notes'].lower())]
    
    if expenses:
        expenses_by_date = {}
        for expense in expenses:
            date_key = expense['date']
            if date_key not in expenses_by_date:
                expenses_by_date[date_key] = []
            expenses_by_date[date_key].append(expense)
        
        for date_key in sorted(expenses_by_date.keys(), reverse=True):
            date_expenses = expenses_by_date[date_key]
            date_total = sum(e['amount'] for e in date_expenses)
            
            st.markdown(f"### {format_date(date_key, '%A, %B %d, %Y')}")
            
            for expense in date_expenses:
                with st.container():
                    exp_col1, exp_col2, exp_col3 = st.columns([3, 2, 1])
                    
                    with exp_col1:
                        category_icons = {
                            "Groceries": "🛒",
                            "Food & Dining": "🍽️",
                            "Transportation": "🚗",
                            "Entertainment": "🎬",
                            "Healthcare": "🏥",
                            "Shopping": "🛍️",
                            "Bills & Rents": "💡",
                            "Education": "📚",
                            "Travel": "✈️",
                            "Personal Care": "💆",
                            "Other": "📝"
                        }
                        icon = category_icons.get(expense['category'], "📝")
                        
                        st.markdown(f"{icon} **{expense['title']}**")
                        st.caption(f"{expense['category']} • {expense['payment_method']}")
                        if expense['notes']:
                            st.caption(f"{expense['notes']}")
                    
                    with exp_col2:
                        st.markdown(f"**{format_currency(expense['amount'], 'USD')}**")
                    
                    with exp_col3:
                        if st.button("Delete", key=f"del_{expense['id']}", help="Delete expense"):
                            if db.delete_expense(user['id'], expense['id']):
                                st.success("Expense deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete expense")
                    
                    st.markdown("---")
            
            st.markdown(f"**Day Total: {format_currency(date_total, 'USD')}**")
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No spending data for this month yet")