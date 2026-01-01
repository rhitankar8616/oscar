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
    """Render analytics overview with side-by-side monthly comparison"""
    current_month = datetime.now().strftime("%Y-%m")
    last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    
    current_expenses = db.get_user_expenses(user['id'], month=current_month)
    last_expenses = db.get_user_expenses(user['id'], month=last_month)
    
    current_total = sum(exp['amount'] for exp in current_expenses) if current_expenses else 0
    last_total = sum(exp['amount'] for exp in last_expenses) if last_expenses else 0
    
    # Calculate change
    if last_total > 0:
        change = ((current_total - last_total) / last_total) * 100
        change_text = f"{'+' if change > 0 else ''}{change:.0f}%"
        change_color = "#F44336" if change > 0 else "#4CAF50"
    else:
        change_text = "N/A"
        change_color = "#9E9E9E"
    
    st.markdown("#### Monthly Comparison")
    
    # Current month and Last month SIDE BY SIDE
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(30, 45, 65, 0.5); border-radius: 10px; padding: 12px; text-align: center;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; text-transform: uppercase; margin: 0;">This Month</p>
            <p style="color: #FF9000; font-size: 1.3rem; font-weight: 700; margin: 4px 0;">${current_total:,.2f}</p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 0;">{len(current_expenses)} transactions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: rgba(30, 45, 65, 0.5); border-radius: 10px; padding: 12px; text-align: center;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; text-transform: uppercase; margin: 0;">Last Month</p>
            <p style="color: white; font-size: 1.3rem; font-weight: 700; margin: 4px 0;">${last_total:,.2f}</p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 0;">{len(last_expenses)} transactions</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Change indicator
    st.markdown(f"""
    <div style="background: rgba(30, 45, 65, 0.3); border-radius: 8px; padding: 8px; text-align: center; margin-top: 8px;">
        <span style="color: rgba(255,255,255,0.5); font-size: 0.7rem;">Change: </span>
        <span style="color: {change_color}; font-size: 0.9rem; font-weight: 600;">{change_text}</span>
        <span style="color: rgba(255,255,255,0.4); font-size: 0.65rem;"> vs last month</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Category breakdown chart
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
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                font=dict(size=10)
            ),
            margin=dict(l=10, r=10, t=10, b=10),
            height=280
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expenses this month to analyze")

def render_trends(user: dict, db: DatabaseManager):
    """Render spending trends"""
    st.markdown("#### Spending Trends")
    
    # Get last 6 months of data
    all_expenses = db.get_user_expenses(user['id'])
    
    if not all_expenses:
        st.info("Not enough data to show trends. Start tracking your expenses!")
        return
    
    df = pd.DataFrame(all_expenses)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    
    monthly_totals = df.groupby('month')['amount'].sum().reset_index()
    monthly_totals['month'] = monthly_totals['month'].astype(str)
    
    # Limit to last 6 months
    monthly_totals = monthly_totals.tail(6)
    
    if len(monthly_totals) < 2:
        st.info("Need at least 2 months of data to show trends")
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
    
    # Daily spending this month
    st.markdown("#### Daily Spending (This Month)")
    
    current_month = datetime.now().strftime("%Y-%m")
    current_expenses = db.get_user_expenses(user['id'], month=current_month)
    
    if current_expenses:
        df_current = pd.DataFrame(current_expenses)
        df_current['date'] = pd.to_datetime(df_current['date'])
        daily = df_current.groupby('date')['amount'].sum().reset_index()
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=daily['date'],
            y=daily['amount'],
            marker_color='#3b82f6'
        ))
        
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis=dict(showgrid=False, title=''),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title=''),
            margin=dict(l=10, r=10, t=10, b=30),
            height=200
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No expenses this month")

def render_insights(user: dict, db: DatabaseManager):
    """Render spending insights"""
    st.markdown("#### Spending Insights")
    
    all_expenses = db.get_user_expenses(user['id'])
    
    if not all_expenses:
        st.info("Add more expenses to see insights!")
        return
    
    df = pd.DataFrame(all_expenses)
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.day_name()
    
    # Top spending category
    top_category = df.groupby('category')['amount'].sum().idxmax()
    top_amount = df.groupby('category')['amount'].sum().max()
    
    # Highest spending day
    top_day = df.groupby('day_of_week')['amount'].sum().idxmax()
    
    # Average transaction
    avg_transaction = df['amount'].mean()
    
    # Display insights in 2x2 grid
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(255, 144, 0, 0.1); border: 1px solid rgba(255, 144, 0, 0.3); border-radius: 8px; padding: 10px; margin-bottom: 8px;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; text-transform: uppercase; margin: 0;">Top Category</p>
            <p style="color: #FF9000; font-size: 0.95rem; font-weight: 600; margin: 4px 0;">{top_category}</p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; margin: 0;">${top_amount:,.2f} total</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 10px; margin-bottom: 8px;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; text-transform: uppercase; margin: 0;">Busiest Day</p>
            <p style="color: #3b82f6; font-size: 0.95rem; font-weight: 600; margin: 4px 0;">{top_day}</p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; margin: 0;">Most spending</p>
        </div>
        """, unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown(f"""
        <div style="background: rgba(76, 175, 80, 0.1); border: 1px solid rgba(76, 175, 80, 0.3); border-radius: 8px; padding: 10px;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; text-transform: uppercase; margin: 0;">Avg Transaction</p>
            <p style="color: #4CAF50; font-size: 0.95rem; font-weight: 600; margin: 4px 0;">${avg_transaction:,.2f}</p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; margin: 0;">Per expense</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: rgba(156, 39, 176, 0.1); border: 1px solid rgba(156, 39, 176, 0.3); border-radius: 8px; padding: 10px;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; text-transform: uppercase; margin: 0;">Total Expenses</p>
            <p style="color: #9C27B0; font-size: 0.95rem; font-weight: 600; margin: 4px 0;">{len(df)}</p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; margin: 0;">All time</p>
        </div>
        """, unsafe_allow_html=True)