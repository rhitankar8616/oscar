import streamlit as st
import pandas as pd
from datetime import datetime
import config
from database.db_manager import DatabaseManager

def render_expenses(user: dict, db: DatabaseManager):
    """Render expenses tracking page"""
    st.markdown("### Expenses")
    
    # Create tabs
    tab1, tab2 = st.tabs(["Add Expense", "View Expenses"])
    
    with tab1:
        render_add_expense(user, db)
    
    with tab2:
        render_view_expenses(user, db)

def render_add_expense(user: dict, db: DatabaseManager):
    """Render form to add new expense"""
    st.markdown("#### Add New Expense")
    
    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Title*", placeholder="e.g., Grocery shopping")
            amount = st.number_input("Amount*", min_value=0.0, step=0.01)
            category = st.selectbox(
                "Category*",
                ["All Categories"] + config.CATEGORIES
            )
        
        with col2:
            date = st.date_input("Date*", value=datetime.now())
            payment_method = st.selectbox(
                "Payment Method*",
                ["Cash", "Credit Card", "Debit Card", "UPI", "Net Banking", "Other"]
            )
        
        notes = st.text_area("Notes (optional)", placeholder="Add any additional details...")
        
        # Submit button inside form
        submitted = st.form_submit_button("Add Expense", use_container_width=True, type="primary")
        
        if submitted:
            if not title or amount <= 0 or category == "All Categories":
                st.error("⚠️ Please fill in all required fields")
            else:
                success = db.add_expense(
                    user_id=user['id'],
                    title=title,
                    amount=amount,
                    category=category,
                    payment_method=payment_method,
                    date=date.strftime("%Y-%m-%d"),
                    notes=notes if notes else None
                )
                
                if success:
                    st.success("✅ Expense added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add expense")

def render_view_expenses(user: dict, db: DatabaseManager):
    """Render expense list and filters"""
    st.markdown("#### Your Expenses")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_category = st.selectbox(
            "Filter by Category",
            ["All Categories"] + config.CATEGORIES,
            key="filter_cat"
        )
    
    with col2:
        filter_month = st.selectbox(
            "Filter by Month",
            ["All Time"] + [
                datetime.now().replace(day=1).strftime("%Y-%m"),
                (datetime.now().replace(day=1) - pd.DateOffset(months=1)).strftime("%Y-%m"),
                (datetime.now().replace(day=1) - pd.DateOffset(months=2)).strftime("%Y-%m")
            ],
            key="filter_month"
        )
    
    # Get expenses
    expenses = db.get_user_expenses(
        user['id'],
        category=filter_category if filter_category != "All Categories" else None,
        month=filter_month if filter_month != "All Time" else None
    )
    
    if not expenses:
        st.info("ℹ️ No expenses found. Add your first expense!")
        return
    
    # Display expenses
    df = pd.DataFrame(expenses)
    
    # Summary stats
    total = df['amount'].sum()
    count = len(df)
    avg = df['amount'].mean()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Spent", f"${total:,.2f}")
    with col2:
        st.metric("Transactions", count)
    with col3:
        st.metric("Average", f"${avg:,.2f}")
    
    st.markdown("---")
    
    # Display expense list
    for _, expense in df.iterrows():
        with st.expander(f"{expense['title']} - ${expense['amount']:,.2f} ({expense['date']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Category:** {expense['category']}")
                st.markdown(f"**Payment:** {expense['payment_method']}")
            
            with col2:
                st.markdown(f"**Date:** {expense['date']}")
                if expense.get('notes'):
                    st.markdown(f"**Notes:** {expense['notes']}")
            
            if st.button("🗑️ Delete", key=f"delete_{expense['id']}", use_container_width=True):
                if db.delete_expense(user['id'], expense['id']):
                    st.success("✅ Expense deleted!")
                    st.rerun()
                else:
                    st.error("❌ Failed to delete expense")