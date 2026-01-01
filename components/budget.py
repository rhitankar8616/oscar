import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_manager import DatabaseManager

def render_budget(user: dict, db: DatabaseManager):
    """Render budget tracker page"""
    st.markdown("### Budget Tracker")
    
    tab1, tab2 = st.tabs(["Overview", "Set Budgets"])
    
    with tab1:
        render_budget_overview(user, db)
    
    with tab2:
        render_set_budgets(user, db)

def render_budget_overview(user: dict, db: DatabaseManager):
    """Render budget overview"""
    monthly_budget = user.get('monthly_budget', 0) or 0
    current_month = datetime.now().strftime("%Y-%m")
    expenses = db.get_user_expenses(user['id'], month=current_month)
    
    total_spent = sum(exp['amount'] for exp in expenses) if expenses else 0
    remaining = monthly_budget - total_spent
    
    if monthly_budget > 0:
        percentage_used = (total_spent / monthly_budget) * 100
    else:
        percentage_used = 0
    
    # Overall budget summary - side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(30, 45, 65, 0.5); border-radius: 10px; padding: 12px; text-align: center;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.65rem; text-transform: uppercase; margin: 0;">Monthly Budget</p>
            <p style="color: white; font-size: 1.3rem; font-weight: 700; margin: 4px 0;">${monthly_budget:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        remaining_color = "#4CAF50" if remaining >= 0 else "#F44336"
        st.markdown(f"""
        <div style="background: rgba(30, 45, 65, 0.5); border-radius: 10px; padding: 12px; text-align: center;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.65rem; text-transform: uppercase; margin: 0;">Remaining</p>
            <p style="color: {remaining_color}; font-size: 1.3rem; font-weight: 700; margin: 4px 0;">${remaining:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Progress bar
    st.markdown(f"""
    <div style="margin: 12px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="color: rgba(255,255,255,0.5); font-size: 0.7rem;">Spent: ${total_spent:,.2f}</span>
            <span style="color: rgba(255,255,255,0.5); font-size: 0.7rem;">{percentage_used:.0f}%</span>
        </div>
        <div style="background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px;">
            <div style="background: {'#4CAF50' if percentage_used < 80 else '#F44336'}; height: 100%; width: {min(percentage_used, 100)}%; border-radius: 4px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Category breakdown
    st.markdown("#### Spending by Category")
    
    if expenses:
        df = pd.DataFrame(expenses)
        category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        # Display in 2x2 grid
        categories = list(category_totals.items())
        
        for i in range(0, len(categories), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                if i < len(categories):
                    cat, amount = categories[i]
                    pct = (amount / total_spent * 100) if total_spent > 0 else 0
                    st.markdown(f"""
                    <div style="background: rgba(30, 45, 65, 0.4); border-radius: 8px; padding: 10px; margin-bottom: 6px;">
                        <p style="color: white; font-size: 0.8rem; font-weight: 500; margin: 0;">{cat}</p>
                        <p style="color: #FF9000; font-size: 0.95rem; font-weight: 600; margin: 2px 0;">${amount:,.2f}</p>
                        <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 0;">{pct:.0f}% of total</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                if i + 1 < len(categories):
                    cat, amount = categories[i + 1]
                    pct = (amount / total_spent * 100) if total_spent > 0 else 0
                    st.markdown(f"""
                    <div style="background: rgba(30, 45, 65, 0.4); border-radius: 8px; padding: 10px; margin-bottom: 6px;">
                        <p style="color: white; font-size: 0.8rem; font-weight: 500; margin: 0;">{cat}</p>
                        <p style="color: #FF9000; font-size: 0.95rem; font-weight: 600; margin: 2px 0;">${amount:,.2f}</p>
                        <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 0;">{pct:.0f}% of total</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("No expenses this month")

def render_set_budgets(user: dict, db: DatabaseManager):
    """Render set budgets form with 2x2 grid layout"""
    st.markdown("#### Set Category Budgets")
    
    categories = ["Food & Dining", "Transportation", "Shopping", "Entertainment", 
                  "Bills & Utilities", "Healthcare", "Education", "Travel", "Other"]
    
    # Get existing budgets
    existing_budgets = db.get_category_budgets(user['id']) if hasattr(db, 'get_category_budgets') else {}
    
    with st.form("category_budgets"):
        st.markdown("Set monthly limits for each category:")
        
        budget_values = {}
        
        # Display categories in 2x2 grid
        for i in range(0, len(categories), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                if i < len(categories):
                    cat = categories[i]
                    default_val = existing_budgets.get(cat, 0.0)
                    budget_values[cat] = st.number_input(
                        cat,
                        min_value=0.0,
                        value=float(default_val),
                        step=50.0,
                        key=f"budget_{cat}"
                    )
            
            with col2:
                if i + 1 < len(categories):
                    cat = categories[i + 1]
                    default_val = existing_budgets.get(cat, 0.0)
                    budget_values[cat] = st.number_input(
                        cat,
                        min_value=0.0,
                        value=float(default_val),
                        step=50.0,
                        key=f"budget_{cat}"
                    )
        
        if st.form_submit_button("Save Budgets", type="primary", use_container_width=True):
            if hasattr(db, 'save_category_budgets'):
                db.save_category_budgets(user['id'], budget_values)
                st.success("Budgets saved!")
                st.rerun()
            else:
                st.info("Category budgets feature will be available soon!")
    
    st.markdown("---")
    
    # Quick tip
    st.markdown("""
    <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 12px;">
        <p style="color: #3b82f6; font-size: 0.8rem; font-weight: 500; margin: 0 0 4px 0;">💡 Tip</p>
        <p style="color: rgba(255,255,255,0.7); font-size: 0.75rem; margin: 0;">Set your overall monthly budget in your Profile settings. Category budgets help you track spending in specific areas.</p>
    </div>
    """, unsafe_allow_html=True)