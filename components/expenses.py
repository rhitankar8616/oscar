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
        
        notes = st.text_area("Notes (optional)", placeholder="Add notes...", height=60)
        
        if st.form_submit_button("Add Expense", use_container_width=True, type="primary"):
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
    """Render view expenses - compact with delete inside card"""
    st.markdown("#### Your Expenses")
    
    # Filters side by side using HTML
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.selectbox(
            "Category",
            ["All Categories", "Food & Dining", "Transportation", "Shopping", 
             "Entertainment", "Bills & Utilities", "Healthcare", "Education", "Travel", "Other"],
            key="exp_cat"
        )
    
    with col2:
        months = ["All Time"]
        for i in range(6):
            m = (datetime.now().replace(day=1) - pd.DateOffset(months=i))
            months.append(m.strftime("%Y-%m"))
        month_filter = st.selectbox("Month", months, key="exp_month")
    
    category = category_filter if category_filter != "All Categories" else None
    month = month_filter if month_filter != "All Time" else None
    expenses = db.get_user_expenses(user['id'], category=category, month=month)
    
    if not expenses:
        st.info("No expenses found")
        return
    
    total = sum(e['amount'] for e in expenses)
    st.markdown(f"""
    <div style="background: rgba(30, 45, 65, 0.5); border-radius: 8px; padding: 8px 12px; margin-bottom: 10px;">
        <span style="color: rgba(255,255,255,0.6); font-size: 0.7rem;">Total: </span>
        <span style="color: #FF9000; font-size: 1rem; font-weight: 700;">${total:,.2f}</span>
        <span style="color: rgba(255,255,255,0.4); font-size: 0.65rem; margin-left: 8px;">({len(expenses)} items)</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Expense list with delete button INSIDE the card
    for expense in expenses:
        expense_id = expense['id']
        
        try:
            exp_date = datetime.strptime(expense['date'], "%Y-%m-%d").strftime("%b %d")
        except:
            exp_date = str(expense['date'])[:10] if expense['date'] else ""
        
        # Card with delete button inside, using flexbox
        st.markdown(f"""
        <div style="background: rgba(30, 45, 65, 0.4); border-radius: 8px; padding: 10px; margin-bottom: 6px; border-left: 3px solid #FF9000;">
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px;">
                <div style="flex: 1; min-width: 0;">
                    <p style="color: #ffffff; font-size: 0.85rem; font-weight: 500; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{expense['title']}</p>
                    <p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; margin: 2px 0 0 0;">{expense['category']} • {expense['payment_method']} • {exp_date}</p>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: #FF9000; font-size: 0.95rem; font-weight: 600;">${expense['amount']:,.2f}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Delete button right after HTML (will appear inline on mobile)
        col_spacer, col_btn = st.columns([5, 1])
        with col_btn:
            if st.button("🗑", key=f"del_{expense_id}", help="Delete"):
                db.delete_expense(user['id'], expense_id)
                st.rerun()
        
        # Custom CSS to position delete button
        st.markdown(f"""
        <style>
        [data-testid="stHorizontalBlock"]:has(button[key="del_{expense_id}"]) {{
            margin-top: -45px !important;
            margin-bottom: 8px !important;
        }}
        [data-testid="stHorizontalBlock"]:has(button[key="del_{expense_id}"]) .stButton > button {{
            background: rgba(244, 67, 54, 0.15) !important;
            border: 1px solid rgba(244, 67, 54, 0.3) !important;
            padding: 4px 8px !important;
            min-height: 28px !important;
        }}
        </style>
        """, unsafe_allow_html=True)