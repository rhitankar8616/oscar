import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager

def render_dates(user: dict, db: DatabaseManager):
    """Render dates page"""
    st.markdown("### Important Dates & Reminders")
    
    tab1, tab2, tab3 = st.tabs(["Add Reminder", "Upcoming", "All Reminders"])
    
    with tab1:
        render_add_reminder(user, db)
    
    with tab2:
        render_upcoming_reminders(user, db)
    
    with tab3:
        render_all_reminders(user, db)

def render_add_reminder(user: dict, db: DatabaseManager):
    """Render add reminder form"""
    st.markdown("#### Create New Reminder")
    
    with st.form("reminder_form", clear_on_submit=True):
        title = st.text_input("Title*", placeholder="e.g., Pay rent")
        
        col1, col2 = st.columns(2)
        with col1:
            reminder_type = st.selectbox("Type", ["Bill Payment", "Subscription", "EMI", "Insurance", "Tax", "Other"])
            amount = st.number_input("Amount (optional)", min_value=0.0, step=100.0)
        
        with col2:
            due_date = st.date_input("Due Date*", min_value=datetime.now().date())
            notify_days = st.number_input("Notify days before", min_value=0, max_value=30, value=3)
        
        description = st.text_area("Description (optional)", height=60)
        
        if st.form_submit_button("Add Reminder", type="primary", use_container_width=True):
            if not title:
                st.error("Please enter a title")
            else:
                reminder_data = {
                    'user_id': user['id'],
                    'title': title,
                    'type': reminder_type,
                    'due_date': due_date.strftime("%Y-%m-%d"),
                    'amount': amount if amount > 0 else None,
                    'description': description if description else None,
                    'notify_days_before': notify_days,
                    'status': 'pending'
                }
                
                if db.add_reminder(reminder_data):
                    st.success("Reminder added!")
                    st.rerun()
                else:
                    st.error("Failed to add reminder")

def render_upcoming_reminders(user: dict, db: DatabaseManager):
    """Render upcoming reminders with horizontal action buttons"""
    st.markdown("#### Upcoming (Next 30 Days)")
    
    reminders = db.get_reminders(user['id'], status='pending')
    
    if not reminders:
        st.info("No upcoming reminders")
        return
    
    df = pd.DataFrame(reminders)
    df['due_date'] = pd.to_datetime(df['due_date'])
    
    today = datetime.now()
    thirty_days = today + timedelta(days=30)
    upcoming = df[(df['due_date'] >= today) & (df['due_date'] <= thirty_days)].sort_values('due_date')
    
    if upcoming.empty:
        st.info("No reminders in the next 30 days")
        return
    
    for _, reminder in upcoming.iterrows():
        days_until = (reminder['due_date'] - today).days
        color = "#F44336" if days_until <= 3 else "#FF9800" if days_until <= 7 else "#4CAF50"
        days_text = "Today!" if days_until == 0 else f"{days_until}d"
        reminder_type = reminder.get('type') or reminder.get('reminder_type') or 'Reminder'
        amount_text = f" • ${reminder['amount']:,.0f}" if pd.notna(reminder.get('amount')) and reminder['amount'] > 0 else ""
        
        # Card with info
        st.markdown(f"""
        <div style="border-left: 3px solid {color}; padding: 10px; background: rgba(30, 45, 65, 0.5); border-radius: 6px; margin-bottom: 4px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <p style="color: #ffffff; font-size: 0.85rem; font-weight: 500; margin: 0;">{reminder['title']}</p>
                    <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 2px 0 0 0;">{reminder_type}{amount_text}</p>
                </div>
                <div style="text-align: right;">
                    <p style="color: {color}; font-size: 0.8rem; font-weight: 600; margin: 0;">{days_text}</p>
                    <p style="color: rgba(255,255,255,0.4); font-size: 0.55rem; margin: 0;">{reminder['due_date'].strftime('%b %d')}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons HORIZONTAL using HTML flexbox
        reminder_id = reminder['id']
        st.markdown(f"""
        <div id="actions_{reminder_id}" style="display: flex; flex-direction: row; gap: 6px; margin-bottom: 12px; margin-top: 4px;">
        """, unsafe_allow_html=True)
        
        btn_cols = st.columns([1, 1, 4])
        with btn_cols[0]:
            if st.button("✓ Done", key=f"done_{reminder_id}"):
                db.update_reminder_status(reminder_id, 'completed')
                st.rerun()
        with btn_cols[1]:
            if st.button("🗑", key=f"del_up_{reminder_id}"):
                db.delete_reminder(reminder_id)
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_all_reminders(user: dict, db: DatabaseManager):
    """Render all reminders with filters and horizontal action buttons"""
    st.markdown("#### All Reminders")
    
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Pending", "Completed", "Cancelled"], key="rem_status")
    with col2:
        type_filter = st.selectbox("Type", ["All", "Bill Payment", "Subscription", "EMI", "Insurance", "Tax", "Other"], key="rem_type")
    
    if status_filter == "All":
        reminders = db.get_all_reminders(user['id'])
    else:
        reminders = db.get_reminders(user['id'], status=status_filter.lower())
    
    if not reminders:
        st.info("No reminders found")
        return
    
    df = pd.DataFrame(reminders)
    df['due_date'] = pd.to_datetime(df['due_date'])
    
    if type_filter != "All":
        type_col = 'type' if 'type' in df.columns else 'reminder_type'
        if type_col in df.columns:
            df = df[df[type_col] == type_filter]
    
    if df.empty:
        st.info("No reminders with selected filters")
        return
    
    df = df.sort_values('due_date', ascending=False)
    
    for _, reminder in df.iterrows():
        reminder_type = reminder.get('type') or reminder.get('reminder_type') or 'Reminder'
        status = reminder.get('status', 'pending').capitalize()
        status_colors = {'Pending': '#FF9800', 'Completed': '#4CAF50', 'Cancelled': '#9E9E9E'}
        status_color = status_colors.get(status, '#FF9800')
        due_date_str = reminder['due_date'].strftime('%b %d, %Y')
        amount_text = f"${reminder['amount']:,.0f}" if pd.notna(reminder.get('amount')) and reminder['amount'] > 0 else ""
        
        st.markdown(f"""
        <div style="background: rgba(30, 45, 65, 0.5); border-radius: 6px; padding: 10px; border-left: 3px solid {status_color}; margin-bottom: 4px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1;">
                    <p style="color: #ffffff; font-size: 0.85rem; font-weight: 500; margin: 0;">{reminder['title']}</p>
                    <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 2px 0;">{reminder_type} • {due_date_str}</p>
                    <p style="color: {status_color}; font-size: 0.6rem; font-weight: 500; margin: 0;">{status} {amount_text}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons HORIZONTAL
        reminder_id = reminder['id']
        btn_cols = st.columns([1, 1, 1, 3])
        
        with btn_cols[0]:
            if reminder.get('status') == 'pending':
                if st.button("✓", key=f"comp_{reminder_id}", help="Complete"):
                    db.update_reminder_status(reminder_id, 'completed')
                    st.rerun()
        
        with btn_cols[1]:
            if reminder.get('status') != 'cancelled':
                if st.button("✕", key=f"canc_{reminder_id}", help="Cancel"):
                    db.update_reminder_status(reminder_id, 'cancelled')
                    st.rerun()
        
        with btn_cols[2]:
            if st.button("🗑", key=f"del_all_{reminder_id}", help="Delete"):
                db.delete_reminder(reminder_id)
                st.rerun()
        
        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)