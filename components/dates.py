import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager

def render_dates(user: dict, db: DatabaseManager):
    """Render dates and reminders page"""
    st.markdown("### Important Dates & Reminders")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Add Reminder", "Upcoming", "All Reminders"])
    
    with tab1:
        render_add_reminder(user, db)
    
    with tab2:
        render_upcoming_reminders(user, db)
    
    with tab3:
        render_all_reminders(user, db)

def render_add_reminder(user: dict, db: DatabaseManager):
    """Render form to add new reminder"""
    st.markdown("#### Create New Reminder")
    
    with st.form("reminder_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Title*", placeholder="e.g., Pay rent")
            reminder_type = st.selectbox(
                "Type",
                ["Bill Payment", "Subscription", "EMI", "Insurance", "Tax", "Other"]
            )
        
        with col2:
            due_date = st.date_input(
                "Due Date*",
                min_value=datetime.now().date()
            )
            amount = st.number_input(
                "Amount (optional)",
                min_value=0.0,
                step=100.0,
                help="Amount associated with this reminder"
            )
        
        description = st.text_area(
            "Description (optional)",
            placeholder="Add any additional notes..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            notify_days_before = st.number_input(
                "Notify days before",
                min_value=0,
                max_value=30,
                value=3,
                help="Get notified X days before due date"
            )
        
        with col2:
            recurring = st.checkbox("Recurring reminder")
        
        if recurring:
            recurrence_type = st.selectbox(
                "Repeat every",
                ["Weekly", "Monthly", "Yearly"]
            )
        else:
            recurrence_type = None
        
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
                
                success = db.add_reminder(reminder_data)
                
                if success:
                    st.success("Reminder added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add reminder")

def render_upcoming_reminders(user: dict, db: DatabaseManager):
    """Render upcoming reminders (next 30 days)"""
    st.markdown("#### Upcoming Reminders (Next 30 Days)")
    
    reminders = db.get_reminders(user['id'], status='pending')
    
    if not reminders:
        st.info("No upcoming reminders")
        return
    
    df = pd.DataFrame(reminders)
    df['due_date'] = pd.to_datetime(df['due_date'])
    
    # Filter for next 30 days
    today = datetime.now()
    thirty_days = today + timedelta(days=30)
    upcoming = df[(df['due_date'] >= today) & (df['due_date'] <= thirty_days)]
    upcoming = upcoming.sort_values('due_date')
    
    if upcoming.empty:
        st.info("No reminders in the next 30 days")
        return
    
    for _, reminder in upcoming.iterrows():
        days_until = (reminder['due_date'] - today).days
        
        # Color code based on urgency
        if days_until <= 3:
            border_color = "#F44336"
        elif days_until <= 7:
            border_color = "#FF9800"
        else:
            border_color = "#4CAF50"
        
        # Get reminder type
        reminder_type = reminder.get('type') or reminder.get('reminder_type') or 'Reminder'
        
        # Get description
        desc_text = reminder.get('description', '') if pd.notna(reminder.get('description')) else 'No description'
        
        # Get days text
        if days_until == 0:
            days_text = "Today!"
        elif days_until == 1:
            days_text = "Tomorrow"
        else:
            days_text = f"In {days_until} days"
        
        # Build amount section
        amount_section = ""
        if pd.notna(reminder.get('amount')) and reminder['amount'] > 0:
            amount_section = f'<p style="color: #FF9000; font-size: 1.1rem; font-weight: 600; margin: 8px 0;">${reminder["amount"]:,.2f}</p>'
        
        card_html = f'''
        <div style="border-left: 4px solid {border_color}; padding: 16px; margin: 12px 0; background: rgba(30, 45, 65, 0.5); border-radius: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 200px;">
                    <h4 style="color: #ffffff; margin: 0 0 8px 0; font-size: 1.1rem;">{reminder['title']}</h4>
                    <p style="color: rgba(255,255,255,0.6); margin: 4px 0; font-size: 0.85rem;"><strong>Type:</strong> {reminder_type}</p>
                    <p style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin: 4px 0;">{desc_text}</p>
                </div>
                <div style="text-align: right; min-width: 150px;">
                    <p style="color: {border_color}; font-size: 1rem; font-weight: 600; margin: 0;">{days_text}</p>
                    <p style="color: rgba(255,255,255,0.6); margin: 4px 0; font-size: 0.85rem;"><strong>Due:</strong> {reminder['due_date'].strftime('%b %d, %Y')}</p>
                    {amount_section}
                </div>
            </div>
        </div>
        '''
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Action button
        if st.button("Mark Done", key=f"complete_{reminder['id']}", use_container_width=True):
            db.update_reminder_status(reminder['id'], 'completed')
            st.success("Reminder marked as completed!")
            st.rerun()

def render_all_reminders(user: dict, db: DatabaseManager):
    """Render all reminders with filters"""
    st.markdown("#### All Reminders")
    
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Pending", "Completed", "Cancelled"]
        )
    
    with col2:
        type_filter = st.selectbox(
            "Filter by type",
            ["All", "Bill Payment", "Subscription", "EMI", "Insurance", "Tax", "Other"]
        )
    
    # Get reminders based on filter
    if status_filter == "All":
        reminders = db.get_all_reminders(user['id'])
    else:
        reminders = db.get_reminders(user['id'], status=status_filter.lower())
    
    if not reminders:
        st.info("No reminders found")
        return
    
    df = pd.DataFrame(reminders)
    df['due_date'] = pd.to_datetime(df['due_date'])
    
    # Apply type filter
    if type_filter != "All":
        if 'type' in df.columns:
            df = df[df['type'] == type_filter]
        elif 'reminder_type' in df.columns:
            df = df[df['reminder_type'] == type_filter]
    
    if df.empty:
        st.info("No reminders found with selected filters")
        return
    
    df = df.sort_values('due_date', ascending=False)
    
    # Display reminders
    for _, reminder in df.iterrows():
        display_reminder_card(reminder, db)

def display_reminder_card(reminder, db):
    """Display a single reminder as a styled card"""
    # Get reminder type
    reminder_type = reminder.get('type') or reminder.get('reminder_type') or 'Reminder'
    status = reminder.get('status', 'pending').capitalize()
    
    # Status color
    status_colors = {
        'Pending': '#FF9800',
        'Completed': '#4CAF50',
        'Cancelled': '#9E9E9E'
    }
    status_color = status_colors.get(status, '#FF9800')
    
    # Format date
    due_date_str = reminder['due_date'].strftime('%b %d, %Y')
    
    # Get notify days
    notify_days = reminder.get('notify_days_before', 3)
    
    # Start building HTML
    html_parts = []
    html_parts.append('<div style="background: rgba(30, 45, 65, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px; margin-bottom: 12px;">')
    html_parts.append('<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">')
    
    # Left column
    html_parts.append('<div style="flex: 1; min-width: 200px;">')
    html_parts.append(f'<h4 style="color: #ffffff; margin: 0 0 8px 0; font-size: 1.1rem;">{reminder["title"]}</h4>')
    html_parts.append(f'<p style="color: rgba(255,255,255,0.6); margin: 4px 0; font-size: 0.85rem;"><strong>Type:</strong> {reminder_type}</p>')
    html_parts.append(f'<p style="color: rgba(255,255,255,0.6); margin: 4px 0; font-size: 0.85rem;"><strong>Status:</strong> <span style="color: {status_color};">{status}</span></p>')
    
    # Amount if exists
    if pd.notna(reminder.get('amount')) and reminder['amount'] > 0:
        html_parts.append(f'<p style="color: rgba(255,255,255,0.6); margin: 4px 0; font-size: 0.85rem;"><strong>Amount:</strong> ${reminder["amount"]:,.2f}</p>')
    
    html_parts.append('</div>')
    
    # Right column
    html_parts.append('<div style="text-align: right; min-width: 150px;">')
    html_parts.append(f'<p style="color: rgba(255,255,255,0.8); font-size: 0.95rem; font-weight: 500; margin: 0;">{due_date_str}</p>')
    html_parts.append(f'<p style="color: rgba(255,255,255,0.5); margin: 4px 0; font-size: 0.8rem;">Notify: {notify_days} days before</p>')
    
    # Recurring if exists
    if reminder.get('recurring'):
        recurrence = reminder.get('recurrence_type', 'N/A')
        html_parts.append(f'<p style="color: rgba(255,255,255,0.5); margin: 4px 0; font-size: 0.8rem;">Recurring: {recurrence}</p>')
    
    html_parts.append('</div>')
    html_parts.append('</div>')
    
    # Description if exists - as separate section
    if pd.notna(reminder.get('description')) and reminder.get('description'):
        desc = reminder['description']
        html_parts.append(f'<p style="color: rgba(255,255,255,0.5); margin: 12px 0 0 0; font-size: 0.85rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 12px;"><strong>Description:</strong> {desc}</p>')
    
    html_parts.append('</div>')
    
    # Join all parts and render
    full_html = ''.join(html_parts)
    st.markdown(full_html, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if reminder.get('status') == 'pending':
            if st.button("Mark Complete", key=f"complete_all_{reminder['id']}", use_container_width=True):
                db.update_reminder_status(reminder['id'], 'completed')
                st.success("Marked as completed!")
                st.rerun()
    
    with col2:
        if reminder.get('status') != 'cancelled':
            if st.button("Cancel", key=f"cancel_{reminder['id']}", use_container_width=True):
                db.update_reminder_status(reminder['id'], 'cancelled')
                st.success("Reminder cancelled")
                st.rerun()
    
    with col3:
        if st.button("Delete", key=f"delete_{reminder['id']}", use_container_width=True):
            db.delete_reminder(reminder['id'])
            st.success("Reminder deleted")
            st.rerun()
    
    st.markdown("")