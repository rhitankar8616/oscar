import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_manager import DatabaseManager

def render_expenses(user: dict, db: DatabaseManager):
    """Render expenses page"""
    st.markdown("### Expenses")
    
    tab1, tab2 = st.tabs(["Add Expense", "View Expenses"])
    
    with tab1:
        render_add_expense(user, db)
    
    with tab2:
        render_view_expenses(user, db)

def render_add_expense(user: dict, db: DatabaseManager):
    """Render add expense form"""
    st.markdown("#### Add New Expense")
    
    with st.form("expense_form", clear_on_submit=True):
        title = st.text_input("Title*", placeholder="e.g., Grocery shopping")
        
        # Two columns for compact layout
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("Amount*", min_value=0.01, step=0.01)
            category = st.selectbox(
                "Category",
                ["Food & Dining", "Transportation", "Shopping", "Entertainment", 
                 "Bills & Utilities", "Healthcare", "Education", "Travel", "Other"]
            )
        
        with col2:
            date = st.date_input("Date", value=datetime.now())
            payment_method = st.selectbox(
                "Payment Method",
                ["Cash", "Credit Card", "Debit Card", "UPI", "Net Banking", "Other"]
            )
        
        notes = st.text_area("Notes (optional)", placeholder="Add any notes...", height=60)
        
        submit = st.form_submit_button("Add Expense", use_container_width=True, type="primary")
        
        if submit:
            if not title:
                st.error("Please enter a title")
            elif amount <= 0:
                st.error("Please enter a valid amount")
            else:
                success = db.add_expense(
                    user_id=user['id'],
                    title=title,
                    amount=amount,
                    category=category,
                    payment_method=payment_method,
                    date=date.strftime("%Y-%m-%d"),
                    notes=notes
                )
                
                if success:
                    st.success("Expense added!")
                    st.rerun()
                else:
                    st.error("Failed to add expense")

def render_view_expenses(user: dict, db: DatabaseManager):
    """Render view expenses section with compact list"""
    st.markdown("#### Your Expenses")
    
    # Filters side by side
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.selectbox(
            "Category",
            ["All Categories", "Food & Dining", "Transportation", "Shopping", 
             "Entertainment", "Bills & Utilities", "Healthcare", "Education", "Travel", "Other"],
            key="expense_cat_filter"
        )
    
    with col2:
        months = ["All Time"]
        current_year = datetime.now().year
        for i in range(12):
            month_date = datetime(current_year, 12 - i, 1)
            months.append(month_date.strftime("%Y-%m"))
        month_filter = st.selectbox("Month", months, key="expense_month_filter")
    
    # Get expenses
    category = category_filter if category_filter != "All Categories" else None
    month = month_filter if month_filter != "All Time" else None
    expenses = db.get_user_expenses(user['id'], category=category, month=month)
    
    if not expenses:
        st.info("No expenses found")
        return
    
    # Total summary - compact
    total = sum(e['amount'] for e in expenses)
    st.markdown(f"""
    <div style="background: rgba(30, 45, 65, 0.5); border-radius: 8px; padding: 8px 12px; margin-bottom: 10px;">
        <span style="color: rgba(255,255,255,0.6); font-size: 0.7rem;">Total: </span>
        <span style="color: #FF9000; font-size: 1rem; font-weight: 700;">${total:,.2f}</span>
        <span style="color: rgba(255,255,255,0.4); font-size: 0.65rem; margin-left: 8px;">({len(expenses)} items)</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Compact expense list with delete button on right
    for expense in expenses:
        expense_id = expense['id']
        
        try:
            exp_date = datetime.strptime(expense['date'], "%Y-%m-%d").strftime("%b %d")
        except:
            exp_date = expense['date'][:10] if expense['date'] else ""
        
        # Create columns: main content (large) + delete button (small)
        col_main, col_del = st.columns([6, 1])
        
        with col_main:
            st.markdown(f"""
            <div style="background: rgba(30, 45, 65, 0.4); border-radius: 8px; padding: 8px 10px; border-left: 2px solid #FF9000;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1; min-width: 0;">
                        <p style="color: #ffffff; font-size: 0.82rem; font-weight: 500; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{expense['title']}</p>
                        <p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; margin: 0;">{expense['category']} • {expense['payment_method']} • {exp_date}</p>
                    </div>
                    <p style="color: #FF9000; font-size: 0.9rem; font-weight: 600; margin: 0 0 0 8px;">${expense['amount']:,.2f}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_del:
            if st.button("🗑", key=f"del_{expense_id}", help="Delete"):
                db.delete_expense(user['id'], expense_id)
                st.rerun()
        
        # Minimal spacing between items
        st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)