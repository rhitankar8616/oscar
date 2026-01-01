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
        
        notes = st.text_area("Notes (optional)", placeholder="Add any notes...")
        
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
                    st.success("Expense added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add expense")

def render_view_expenses(user: dict, db: DatabaseManager):
    """Render view expenses section"""
    st.markdown("#### Your Expenses")
    
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
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
        month_filter = st.selectbox("Filter by Month", months, key="expense_month_filter")
    
    # Get expenses
    category = category_filter if category_filter != "All Categories" else None
    month = month_filter if month_filter != "All Time" else None
    expenses = db.get_user_expenses(user['id'], category=category, month=month)
    
    if not expenses:
        st.info("No expenses found")
        return
    
    # Calculate total
    total = sum(e['amount'] for e in expenses)
    st.markdown(f"""
    <div style="background: rgba(30, 45, 65, 0.5); border-radius: 10px; padding: 12px 16px; margin-bottom: 16px;">
        <span style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">Total:</span>
        <span style="color: #FF9000; font-size: 1.2rem; font-weight: 700; margin-left: 8px;">${total:,.2f}</span>
        <span style="color: rgba(255,255,255,0.5); font-size: 0.75rem; margin-left: 8px;">({len(expenses)} expenses)</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Display expenses as compact cards
    for expense in expenses:
        expense_id = expense['id']
        
        # Format date
        try:
            exp_date = datetime.strptime(expense['date'], "%Y-%m-%d").strftime("%b %d, %Y")
        except:
            exp_date = expense['date']
        
        # Card HTML
        st.markdown(f"""
        <div style="
            background: rgba(30, 45, 65, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 8px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                <div style="flex: 1; min-width: 150px;">
                    <p style="color: #ffffff; font-size: 0.95rem; font-weight: 600; margin: 0 0 4px 0;">{expense['title']}</p>
                    <p style="color: rgba(255,255,255,0.5); font-size: 0.75rem; margin: 0;">
                        {expense['category']} | {expense['payment_method']}
                    </p>
                </div>
                <div style="text-align: right;">
                    <p style="color: #FF9000; font-size: 1rem; font-weight: 700; margin: 0;">${expense['amount']:,.2f}</p>
                    <p style="color: rgba(255,255,255,0.5); font-size: 0.7rem; margin: 0;">{exp_date}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action row with compact delete button
        col1, col2, col3 = st.columns([3, 3, 1])
        
        with col1:
            if expense.get('notes'):
                st.markdown(f"""
                <p style="color: rgba(255,255,255,0.5); font-size: 0.7rem; margin: 0; padding-left: 4px;">
                    {expense['notes'][:50]}{'...' if len(expense.get('notes', '')) > 50 else ''}
                </p>
                """, unsafe_allow_html=True)
        
        with col3:
            # Compact delete button with icon styling via CSS
            if st.button("✕", key=f"del_exp_{expense_id}", help="Delete"):
                db.delete_expense(user['id'], expense_id)
                st.success("Deleted!")
                st.rerun()
        
        st.markdown('<div style="height: 4px;"></div>', unsafe_allow_html=True)
    
    # Add custom CSS for delete button styling
    st.markdown("""
    <style>
    /* Style delete buttons on mobile */
    @media (max-width: 768px) {
        button[kind="secondary"]:has(div:contains("✕")),
        button:has(div:contains("✕")) {
            background: rgba(255, 80, 80, 0.15) !important;
            color: #ff6b6b !important;
            border: 1px solid rgba(255, 80, 80, 0.3) !important;
            padding: 4px 8px !important;
            min-width: 32px !important;
            font-size: 0.9rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)