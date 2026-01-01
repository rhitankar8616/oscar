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
    """Render budget overview with horizontal category display"""
    monthly_budget = user.get('monthly_budget', 0) or 0
    current_month = datetime.now().strftime("%Y-%m")
    expenses = db.get_user_expenses(user['id'], month=current_month)
    
    total_spent = sum(exp['amount'] for exp in expenses) if expenses else 0
    remaining = monthly_budget - total_spent
    
    if monthly_budget > 0:
        percentage_used = (total_spent / monthly_budget) * 100
    else:
        percentage_used = 0
    
    remaining_color = "#4CAF50" if remaining >= 0 else "#F44336"
    
    # Budget and Remaining side by side using HTML flexbox
    st.markdown(f"""
    <div style="display: flex; flex-direction: row; gap: 8px; margin-bottom: 12px;">
        <div style="flex: 1; background: rgba(30, 45, 65, 0.5); border-radius: 10px; padding: 12px; text-align: center;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; text-transform: uppercase; margin: 0;">Monthly Budget</p>
            <p style="color: white; font-size: 1.2rem; font-weight: 700; margin: 4px 0 0 0;">${monthly_budget:,.2f}</p>
        </div>
        <div style="flex: 1; background: rgba(30, 45, 65, 0.5); border-radius: 10px; padding: 12px; text-align: center;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; text-transform: uppercase; margin: 0;">Remaining</p>
            <p style="color: {remaining_color}; font-size: 1.2rem; font-weight: 700; margin: 4px 0 0 0;">${remaining:,.2f}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    bar_color = "#4CAF50" if percentage_used < 80 else "#F44336"
    st.markdown(f"""
    <div style="margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="color: rgba(255,255,255,0.5); font-size: 0.7rem;">Spent: ${total_spent:,.2f}</span>
            <span style="color: rgba(255,255,255,0.5); font-size: 0.7rem;">{percentage_used:.0f}%</span>
        </div>
        <div style="background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px;">
            <div style="background: {bar_color}; height: 100%; width: {min(percentage_used, 100)}%; border-radius: 4px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### Spending by Category")
    
    if expenses:
        df = pd.DataFrame(expenses)
        category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        # Each category in HORIZONTAL layout: Category | Amount | Percentage
        for cat, amount in category_totals.items():
            pct = (amount / total_spent * 100) if total_spent > 0 else 0
            st.markdown(f"""
            <div style="background: rgba(30, 45, 65, 0.4); border-radius: 8px; padding: 10px 12px; margin-bottom: 6px;">
                <div style="display: flex; flex-direction: row; justify-content: space-between; align-items: center;">
                    <span style="color: white; font-size: 0.85rem; font-weight: 500; flex: 2;">{cat}</span>
                    <span style="color: #FF9000; font-size: 0.9rem; font-weight: 600; flex: 1; text-align: right;">${amount:,.2f}</span>
                    <span style="color: rgba(255,255,255,0.4); font-size: 0.7rem; flex: 1; text-align: right;">{pct:.0f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No expenses this month")

def render_set_budgets(user: dict, db: DatabaseManager):
    """Render set budgets form"""
    st.markdown("#### Set Category Budgets")
    
    categories = ["Food & Dining", "Transportation", "Shopping", "Entertainment", 
                  "Bills & Utilities", "Healthcare", "Education", "Travel", "Other"]
    
    existing_budgets = db.get_category_budgets(user['id']) if hasattr(db, 'get_category_budgets') else {}
    
    with st.form("category_budgets"):
        st.markdown("Set monthly limits for each category:")
        
        budget_values = {}
        
        col1, col2 = st.columns(2)
        for idx, cat in enumerate(categories):
            default_val = existing_budgets.get(cat, 0.0)
            with col1 if idx % 2 == 0 else col2:
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
                st.info("Category budgets feature coming soon!")
    
    st.markdown("---")
    st.markdown("""
    <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 12px;">
        <p style="color: #3b82f6; font-size: 0.8rem; font-weight: 500; margin: 0 0 4px 0;">💡 Tip</p>
        <p style="color: rgba(255,255,255,0.7); font-size: 0.75rem; margin: 0;">Set your overall monthly budget in Profile settings.</p>
    </div>
    """, unsafe_allow_html=True)