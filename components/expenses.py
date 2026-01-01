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
                st.error("Please fill in all required fields")
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
                    st.success("Expense added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add expense")

def render_view_expenses(user: dict, db: DatabaseManager):
    """Render expense list and filters"""
    st.markdown("#### Your Expenses")
    
    # Filters
    col1, col2 = st.columns(2)
    
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
        st.info("No expenses found. Add your first expense!")
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
    
    # Display expense list using cards instead of expanders to avoid text overlap
    for _, expense in df.iterrows():
        # Create a styled card for each expense
        st.markdown(f"""
        <div style="
            background: rgba(30, 45, 65, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 200px;">
                    <h4 style="color: #ffffff; margin: 0 0 8px 0; font-size: 1.1rem;">{expense['title']}</h4>
                    <p style="color: rgba(255,255,255,0.6); margin: 4px 0; font-size: 0.9rem;">
                        <strong>Category:</strong> {expense['category']}
                    </p>
                    <p style="color: rgba(255,255,255,0.6); margin: 4px 0; font-size: 0.9rem;">
                        <strong>Payment:</strong> {expense['payment_method']}
                    </p>
                </div>
                <div style="text-align: right; min-width: 150px;">
                    <p style="color: #FF9000; font-size: 1.4rem; font-weight: 700; margin: 0;">${expense['amount']:,.2f}</p>
                    <p style="color: rgba(255,255,255,0.5); margin: 4px 0; font-size: 0.85rem;">
                        <strong>Date:</strong> {expense['date']}
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Notes and delete button in columns
        col1, col2 = st.columns([3, 1])
        with col1:
            if expense.get('notes'):
                st.caption(f"Notes: {expense['notes']}")
        with col2:
            if st.button("Delete", key=f"delete_{expense['id']}", use_container_width=True):
                if db.delete_expense(user['id'], expense['id']):
                    st.success("Expense deleted!")
                    st.rerun()
                else:
                    st.error("Failed to delete expense")
        
        st.markdown("")  # Small spacer