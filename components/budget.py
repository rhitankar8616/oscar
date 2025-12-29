import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_manager import DatabaseManager

def render_budget(user: dict, db: DatabaseManager):
    """Render budget tracking page"""
    st.markdown("#### Budget Tracker")
    
    # Get user's budget settings
    budget_settings = db.get_budget_settings(user['id'])
    
    # Create tabs
    tab1, tab2 = st.tabs(["Set Budget", "Budget Overview"])
    
    with tab1:
        st.markdown("#### Set Your Monthly Budget")
        
        # Wrap everything in a form
        with st.form("budget_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            
            with col1:
                total_budget = st.number_input(
                    "Total Monthly Budget",
                    min_value=0.0,
                    value=float(budget_settings.get('total_budget', 0.0)) if budget_settings else 0.0,
                    step=100.0,
                    help="Your total monthly budget"
                )
            
            with col2:
                currency = st.selectbox(
                    "Currency",
                    ["USD", "EUR", "GBP", "INR", "JPY"],
                    index=["USD", "EUR", "GBP", "INR", "JPY"].index(
                        budget_settings.get('currency', 'USD')
                    ) if budget_settings else 0
                )
            
            st.markdown("#### Category Budgets")
            
            # Default categories
            default_categories = [
                "Food & Dining", "Transportation", "Shopping", 
                "Entertainment", "Bills & Utilities", "Health", "Other"
            ]
            
            category_budgets = {}
            
            # Create two columns for category inputs
            cols = st.columns(2)
            for idx, category in enumerate(default_categories):
                col = cols[idx % 2]
                with col:
                    current_value = 0.0
                    if budget_settings and 'category_budgets' in budget_settings:
                        current_value = float(budget_settings['category_budgets'].get(category, 0.0))
                    
                    category_budgets[category] = st.number_input(
                        category,
                        min_value=0.0,
                        value=current_value,
                        step=50.0,
                        key=f"budget_{category}"
                    )
            
            # Submit button inside the form
            submitted = st.form_submit_button("Save Changes", use_container_width=True, type="primary")
            
            if submitted:
                # Save budget settings
                success = db.save_budget_settings(
                    user['id'],
                    total_budget,
                    currency,
                    category_budgets
                )
                
                if success:
                    st.success("✅ Budget settings saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save budget settings")
    
    with tab2:
        if not budget_settings:
            st.info("ℹ️ Please set your budget in the 'Set Budget' tab first.")
            return
        
        st.markdown("#### Your Budget Overview")
        
        # Get current month expenses
        current_month = datetime.now().strftime("%Y-%m")
        expenses = db.get_expenses(user['id'])
        
        if expenses:
            df = pd.DataFrame(expenses)
            current_month_expenses = df[df['date'].str.startswith(current_month)]
            
            # Total spending
            total_spent = current_month_expenses['amount'].sum()
            total_budget = budget_settings['total_budget']
            remaining = total_budget - total_spent
            
            # Overall progress
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Budget", f"{budget_settings['currency']} {total_budget:,.2f}")
            
            with col2:
                st.metric("Total Spent", f"{budget_settings['currency']} {total_spent:,.2f}")
            
            with col3:
                delta_color = "normal" if remaining >= 0 else "inverse"
                st.metric(
                    "Remaining", 
                    f"{budget_settings['currency']} {remaining:,.2f}",
                    delta=f"{(remaining/total_budget*100):.1f}%" if total_budget > 0 else "0%"
                )
            
            # Progress bar
            progress = min(total_spent / total_budget, 1.0) if total_budget > 0 else 0
            st.progress(progress)
            
            if progress >= 1.0:
                st.error("⚠️ You have exceeded your budget!")
            elif progress >= 0.8:
                st.warning("⚠️ You're approaching your budget limit!")
            
            st.markdown("---")
            st.markdown("#### Category Breakdown")
            
            # Category-wise breakdown
            category_budgets = budget_settings.get('category_budgets', {})
            
            for category, budget_amount in category_budgets.items():
                if budget_amount > 0:
                    category_expenses = current_month_expenses[
                        current_month_expenses['category'] == category
                    ]['amount'].sum()
                    
                    remaining_cat = budget_amount - category_expenses
                    progress_cat = min(category_expenses / budget_amount, 1.0) if budget_amount > 0 else 0
                    
                    st.markdown(f"**{category}**")
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.progress(progress_cat)
                    
                    with col2:
                        percentage = (category_expenses / budget_amount * 100) if budget_amount > 0 else 0
                        st.markdown(f"*{percentage:.1f}%*")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"Budget: {budget_settings['currency']} {budget_amount:,.2f}")
                    with col2:
                        st.caption(f"Spent: {budget_settings['currency']} {category_expenses:,.2f}")
                    with col3:
                        if remaining_cat < 0:
                            st.caption(f"⚠️ Over by: {budget_settings['currency']} {abs(remaining_cat):,.2f}")
                        else:
                            st.caption(f"Left: {budget_settings['currency']} {remaining_cat:,.2f}")
                    
                    st.markdown("")
        else:
            st.info("ℹ️ No expenses recorded yet for this month.")