"""Analytics component."""
import streamlit as st
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager
from utils.formatters import format_currency
import pandas as pd

def render_analytics(user: dict, db: DatabaseManager):
    """Render analytics page."""
    
    st.markdown("#### Analytics")
    st.caption("Visualize your spending patterns")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    time_range = st.selectbox("Time Range", ["7 Days", "14 Days", "30 Days"], index=2)
    
    days = int(time_range.split()[0])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    expenses = db.get_user_expenses(user['id'], limit=1000)
    
    if not expenses:
        st.info("No data available yet. Start adding expenses to see analytics!")
        return
    
    df = pd.DataFrame(expenses)
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] >= datetime.now() - timedelta(days=days)]
    
    st.markdown("### Daily Spending Pattern")
    
    if not df.empty:
        daily_spending = df.groupby('date')['amount'].sum().reset_index()
        daily_spending = daily_spending.sort_values('date')
        
        chart_data = pd.DataFrame({
            'Date': daily_spending['date'].dt.strftime('%b %d'),
            'Amount': daily_spending['amount']
        })
        
        st.bar_chart(chart_data.set_index('Date'))
    else:
        st.info(f"No expenses in the last {days} days")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Monthly Comparison")
    
    current_month = datetime.now().strftime("%Y-%m")
    last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m")
    
    current_expenses = db.get_user_expenses(user['id'], month=current_month)
    last_expenses = db.get_user_expenses(user['id'], month=last_month)
    
    current_total = sum(e['amount'] for e in current_expenses)
    last_total = sum(e['amount'] for e in last_expenses)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style='background-color: #2C3E50; padding: 20px; border-radius: 10px; text-align: center;'>
            <p style='color: #888; font-size: 14px; margin: 0;'>Current Month</p>
            <h2 style='color: #FF9800; margin: 10px 0;'>{format_currency(current_total, 'USD')}</h2>
            <p style='color: #888; font-size: 12px; margin: 0;'>{len(current_expenses)} transactions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background-color: #2C3E50; padding: 20px; border-radius: 10px; text-align: center;'>
            <p style='color: #888; font-size: 14px; margin: 0;'>Last Month</p>
            <h2 style='color: #888; margin: 10px 0;'>{format_currency(last_total, 'USD')}</h2>
            <p style='color: #888; font-size: 12px; margin: 0;'>{len(last_expenses)} transactions</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Category Distribution")
    
    stats = db.get_expense_stats(user['id'], month=current_month)
    categories = stats.get('categories', [])
    
    if categories:
        cat_df = pd.DataFrame(categories)
        st.bar_chart(cat_df.set_index('category')['amount'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        for cat in categories:
            percentage = (cat['amount'] / current_total * 100) if current_total > 0 else 0
            st.markdown(f"""
            <div style='margin-bottom: 10px;'>
                <div style='display: flex; justify-content: space-between;'>
                    <span style='color: white;'>{cat['category']}</span>
                    <span style='color: #FF9800;'>{format_currency(cat['amount'], 'USD')} ({percentage:.1f}%)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No category data available")