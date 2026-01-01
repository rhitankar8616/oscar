import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager

def render_dates(user: dict, db: DatabaseManager):
    """Render dates and reminders page"""
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
            reminder_type = st.selectbox(
                "Type",
                ["Bill Payment", "Subscription", "EMI", "Insurance", "Tax", "Other"]
            )
        
        with col2:
            due_date = st.date_input("Due Date*", min_value=datetime.now().date())
        
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("Amount (optional)", min_value=0.0, step=100.0)
        
        with col2:
            notify_days_before = st.number_input("Notify days before", min_value=0, max_value=30, value=3)
        
        description = st.text_area("Description (optional)", placeholder="Add notes...")
        
        recurring = st.checkbox("Recurring reminder")
        recurrence_type = None
        if recurring:
            recurrence_type = st.selectbox("Repeat every", ["Weekly", "Monthly", "Yearly"])
        
        submit = st.form_submit_button("Add Reminder", use_container_width=True, type="primary")
        
        if submit:
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
                    'notify_days_before': notify_days_before,
                    'recurring': recurring,
                    'recurrence_type': recurrence_type,
                    'status': 'pending'
                }
                
                if db.add_reminder(reminder_data):
                    st.success("Reminder added!")
                    st.rerun()
                else:
                    st.error("Failed to add reminder")

def render_upcoming_reminders(user: dict, db: DatabaseManager):
    """Render upcoming reminders"""
    st.markdown("#### Upcoming (Next 30 Days)")
    
    reminders = db.get_reminders(user['id'], status='pending')
    
    if not reminders:
        st.info("No upcoming reminders")
        return
    
    df = pd.DataFrame(reminders)
    df['due_date'] = pd.to_datetime(df['due_date'])
    
    today = datetime.now()
    thirty_days = today + timedelta(days=30)
    upcoming = df[(df['due_date'] >= today) & (df['due_date'] <= thirty_days)]
    upcoming = upcoming.sort_values('due_date')
    
    if upcoming.empty:
        st.info("No reminders in the next 30 days")
        return
    
    for _, reminder in upcoming.iterrows():
        days_until = (reminder['due_date'] - today).days
        
        # Color based on urgency
        if days_until <= 3:
            border_color = "#F44336"
        elif days_until <= 7:
            border_color = "#FF9800"
        else:
            border_color = "#4CAF50"
        
        reminder_type = reminder.get('type') or reminder.get('reminder_type') or 'Reminder'
        desc_text = reminder.get('description', '') if pd.notna(reminder.get('description')) else ''
        
        if days_until == 0:
            days_text = "Today!"
        elif days_until == 1:
            days_text = "Tomorrow"
        else:
            days_text = f"In {days_until} days"
        
        amount_html = ""
        if pd.notna(reminder.get('amount')) and reminder['amount'] > 0:
            amount_html = f'<span style="color: #FF9000; font-weight: 600;">${reminder["amount"]:,.2f}</span>'
        
        st.markdown(f'''
        <div style="border-left: 3px solid {border_color}; padding: 10px 12px; margin: 8px 0; background: rgba(30, 45, 65, 0.5); border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 6px;">
                <div style="flex: 1; min-width: 140px;">
                    <p style="color: #ffffff; font-size: 0.9rem; font-weight: 600; margin: 0 0 3px 0;">{reminder['title']}</p>
                    <p style="color: rgba(255,255,255,0.5); font-size: 0.7rem; margin: 0;">{reminder_type}</p>
                </div>
                <div style="text-align: right;">
                    <p style="color: {border_color}; font-size: 0.8rem; font-weight: 600; margin: 0;">{days_text}</p>
                    <p style="color: rgba(255,255,255,0.5); font-size: 0.65rem; margin: 2px 0;">{reminder['due_date'].strftime('%b %d')}</p>
                    {amount_html}
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Compact action button
        if st.button("✓ Done", key=f"done_{reminder['id']}", help="Mark as done"):
            db.update_reminder_status(reminder['id'], 'completed')
            st.success("Completed!")
            st.rerun()

def render_all_reminders(user: dict, db: DatabaseManager):
    """Render all reminders with filters"""
    st.markdown("#### All Reminders")
    
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by status", ["All", "Pending", "Completed", "Cancelled"])
    with col2:
        type_filter = st.selectbox("Filter by type", ["All", "Bill Payment", "Subscription", "EMI", "Insurance", "Tax", "Other"])
    
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
        if 'type' in df.columns:
            df = df[df['type'] == type_filter]
        elif 'reminder_type' in df.columns:
            df = df[df['reminder_type'] == type_filter]
    
    if df.empty:
        st.info("No reminders found with selected filters")
        return
    
    df = df.sort_values('due_date', ascending=False)
    
    for _, reminder in df.iterrows():
        display_reminder_card(reminder, db)

def display_reminder_card(reminder, db):
    """Display a single reminder card"""
    reminder_type = reminder.get('type') or reminder.get('reminder_type') or 'Reminder'
    status = reminder.get('status', 'pending').capitalize()
    
    status_colors = {'Pending': '#FF9800', 'Completed': '#4CAF50', 'Cancelled': '#9E9E9E'}
    status_color = status_colors.get(status, '#FF9800')
    
    due_date_str = reminder['due_date'].strftime('%b %d, %Y')
    notify_days = reminder.get('notify_days_before', 3)
    
    # Build card HTML
    html_parts = []
    html_parts.append('<div style="background: rgba(30, 45, 65, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px; margin-bottom: 8px;">')
    html_parts.append('<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 6px;">')
    
    # Left side
    html_parts.append('<div style="flex: 1; min-width: 140px;">')
    html_parts.append(f'<p style="color: #ffffff; font-size: 0.9rem; font-weight: 600; margin: 0 0 3px 0;">{reminder["title"]}</p>')
    html_parts.append(f'<p style="color: rgba(255,255,255,0.5); font-size: 0.7rem; margin: 0 0 2px 0;">{reminder_type}</p>')
    html_parts.append(f'<p style="color: {status_color}; font-size: 0.7rem; font-weight: 500; margin: 0;">{status}</p>')
    
    if pd.notna(reminder.get('amount')) and reminder['amount'] > 0:
        html_parts.append(f'<p style="color: rgba(255,255,255,0.6); font-size: 0.75rem; margin: 3px 0 0 0;">${reminder["amount"]:,.2f}</p>')
    
    html_parts.append('</div>')
    
    # Right side
    html_parts.append('<div style="text-align: right;">')
    html_parts.append(f'<p style="color: rgba(255,255,255,0.8); font-size: 0.8rem; font-weight: 500; margin: 0;">{due_date_str}</p>')
    html_parts.append(f'<p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; margin: 2px 0;">Notify: {notify_days}d before</p>')
    
    if reminder.get('recurring'):
        recurrence = reminder.get('recurrence_type', 'N/A')
        html_parts.append(f'<p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; margin: 0;">Recurring: {recurrence}</p>')
    
    html_parts.append('</div>')
    html_parts.append('</div>')
    
    # Description
    if pd.notna(reminder.get('description')) and reminder.get('description'):
        desc = reminder['description'][:60] + ('...' if len(reminder['description']) > 60 else '')
        html_parts.append(f'<p style="color: rgba(255,255,255,0.4); font-size: 0.7rem; margin: 8px 0 0 0; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.05);">{desc}</p>')
    
    html_parts.append('</div>')
    
    st.markdown(''.join(html_parts), unsafe_allow_html=True)
    
    # Compact action buttons with icons
    cols = st.columns([1, 1, 1, 2])
    
    with cols[0]:
        if reminder.get('status') == 'pending':
            if st.button("✓", key=f"complete_{reminder['id']}", help="Complete"):
                db.update_reminder_status(reminder['id'], 'completed')
                st.rerun()
    
    with cols[1]:
        if reminder.get('status') != 'cancelled':
            if st.button("⊘", key=f"cancel_{reminder['id']}", help="Cancel"):
                db.update_reminder_status(reminder['id'], 'cancelled')
                st.rerun()
    
    with cols[2]:
        if st.button("✕", key=f"delete_{reminder['id']}", help="Delete"):
            db.delete_reminder(reminder['id'])
            st.rerun()
    
    # Custom button styling
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        /* Green check button */
        button:has(div:contains("✓")) {
            background: rgba(76, 175, 80, 0.15) !important;
            color: #4CAF50 !important;
            border: 1px solid rgba(76, 175, 80, 0.3) !important;
            padding: 4px 10px !important;
            font-size: 1rem !important;
        }
        /* Gray cancel button */
        button:has(div:contains("⊘")) {
            background: rgba(158, 158, 158, 0.15) !important;
            color: #9E9E9E !important;
            border: 1px solid rgba(158, 158, 158, 0.3) !important;
            padding: 4px 10px !important;
            font-size: 1rem !important;
        }
        /* Red delete button */
        button:has(div:contains("✕")) {
            background: rgba(255, 80, 80, 0.15) !important;
            color: #ff6b6b !important;
            border: 1px solid rgba(255, 80, 80, 0.3) !important;
            padding: 4px 10px !important;
            font-size: 1rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)