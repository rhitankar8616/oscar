import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager

def render_analytics(user: dict, db: DatabaseManager):
    """Render analytics page"""
    st.markdown("### Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Overview", "Trends", "Insights"])
    
    with tab1:
        render_analytics_overview(user, db)
    
    with tab2:
        render_trends(user, db)
    
    with tab3:
        render_insights(user, db)

def render_analytics_overview(user: dict, db: DatabaseManager):
    """Render analytics overview"""
    current_month = datetime.now().strftime("%Y-%m")
    last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    
    current_expenses = db.get_user_expenses(user['id'], month=current_month)
    last_expenses = db.get_user_expenses(user['id'], month=last_month)
    
    current_total = sum(exp['amount'] for exp in current_expenses) if current_expenses else 0
    last_total = sum(exp['amount'] for exp in last_expenses) if last_expenses else 0
    
    if last_total > 0:
        change = ((current_total - last_total) / last_total) * 100
        change_text = f"{'+' if change > 0 else ''}{change:.0f}%"
        change_color = "#F44336" if change > 0 else "#4CAF50"
    else:
        change_text = "N/A"
        change_color = "#9E9E9E"
    
    st.markdown("#### Monthly Comparison")
    
    # Current Month and Last Month SIDE BY SIDE using HTML flexbox
    st.markdown(f"""
    <div style="display: flex; flex-direction: row; gap: 8px; margin-bottom: 8px;">
        <div style="flex: 1; background: rgba(30, 45, 65, 0.5); border-radius: 10px; padding: 12px; text-align: center;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; text-transform: uppercase; margin: 0;">This Month</p>
            <p style="color: #FF9000; font-size: 1.2rem; font-weight: 700; margin: 4px 0 0 0;">${current_total:,.2f}</p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.55rem; margin: 2px 0 0 0;">{len(current_expenses)} transactions</p>
        </div>
        <div style="flex: 1; background: rgba(30, 45, 65, 0.5); border-radius: 10px; padding: 12px; text-align: center;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; text-transform: uppercase; margin: 0;">Last Month</p>
            <p style="color: white; font-size: 1.2rem; font-weight: 700; margin: 4px 0 0 0;">${last_total:,.2f}</p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.55rem; margin: 2px 0 0 0;">{len(last_expenses)} transactions</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Change indicator
    st.markdown(f"""
    <div style="background: rgba(30, 45, 65, 0.3); border-radius: 8px; padding: 8px; text-align: center; margin-bottom: 16px;">
        <span style="color: rgba(255,255,255,0.5); font-size: 0.7rem;">Change: </span>
        <span style="color: {change_color}; font-size: 0.9rem; font-weight: 600;">{change_text}</span>
        <span style="color: rgba(255,255,255,0.4); font-size: 0.6rem;"> vs last month</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### Spending by Category")
    
    if current_expenses:
        df = pd.DataFrame(current_expenses)
        category_totals = df.groupby('category')['amount'].sum().reset_index()
        
        fig = px.pie(
            category_totals, 
            values='amount', 
            names='category',
            color_discrete_sequence=px.colors.sequential.Oranges_r,
            hole=0.4
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font=dict(size=10)),
            margin=dict(l=10, r=10, t=10, b=10),
            height=280
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expenses this month")

def render_trends(user: dict, db: DatabaseManager):
    """Render spending trends"""
    st.markdown("#### Spending Trends")
    
    all_expenses = db.get_user_expenses(user['id'])
    
    if not all_expenses:
        st.info("Start tracking expenses to see trends!")
        return
    
    df = pd.DataFrame(all_expenses)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    
    monthly_totals = df.groupby('month')['amount'].sum().reset_index()
    monthly_totals['month'] = monthly_totals['month'].astype(str)
    monthly_totals = monthly_totals.tail(6)
    
    if len(monthly_totals) < 2:
        st.info("Need at least 2 months of data")
        return
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_totals['month'],
        y=monthly_totals['amount'],
        mode='lines+markers',
        line=dict(color='#FF9000', width=3),
        marker=dict(size=10),
        fill='tozeroy',
        fillcolor='rgba(255, 144, 0, 0.1)'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis=dict(showgrid=False, title=''),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title=''),
        margin=dict(l=10, r=10, t=10, b=30),
        height=250
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_insights(user: dict, db: DatabaseManager):
    """Render spending insights"""
    st.markdown("#### Spending Insights")
    
    all_expenses = db.get_user_expenses(user['id'])
    
    if not all_expenses:
        st.info("Add expenses to see insights!")
        return
    
    df = pd.DataFrame(all_expenses)
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.day_name()
    
    top_category = df.groupby('category')['amount'].sum().idxmax()
    top_amount = df.groupby('category')['amount'].sum().max()
    top_day = df.groupby('day_of_week')['amount'].sum().idxmax()
    avg_transaction = df['amount'].mean()
    
    # 2x2 grid using HTML flexbox
    st.markdown(f"""
    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
        <div style="flex: 1 1 45%; min-width: 140px; background: rgba(255, 144, 0, 0.1); border: 1px solid rgba(255, 144, 0, 0.3); border-radius: 8px; padding: 10px;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; text-transform: uppercase; margin: 0;">Top Category</p>
            <p style="color: #FF9000; font-size: 0.95rem; font-weight: 600; margin: 4px 0;">{top_category}</p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 0;">${top_amount:,.2f} total</p>
        </div>
        <div style="flex: 1 1 45%; min-width: 140px; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 10px;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; text-transform: uppercase; margin: 0;">Busiest Day</p>
            <p style="color: #3b82f6; font-size: 0.95rem; font-weight: 600; margin: 4px 0;">{top_day}</p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 0;">Most spending</p>
        </div>
        <div style="flex: 1 1 45%; min-width: 140px; background: rgba(76, 175, 80, 0.1); border: 1px solid rgba(76, 175, 80, 0.3); border-radius: 8px; padding: 10px;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; text-transform: uppercase; margin: 0;">Avg Transaction</p>
            <p style="color: #4CAF50; font-size: 0.95rem; font-weight: 600; margin: 4px 0;">${avg_transaction:,.2f}</p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 0;">Per expense</p>
        </div>
        <div style="flex: 1 1 45%; min-width: 140px; background: rgba(156, 39, 176, 0.1); border: 1px solid rgba(156, 39, 176, 0.3); border-radius: 8px; padding: 10px;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; text-transform: uppercase; margin: 0;">Total Expenses</p>
            <p style="color: #9C27B0; font-size: 0.95rem; font-weight: 600; margin: 4px 0;">{len(df)}</p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 0;">All time</p>
        </div>
    </div>
    """, unsafe_allow_html=True)