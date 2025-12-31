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
                st.error("⚠️ Please enter a title")
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
                    st.success("✅ Reminder added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add reminder")

def render_upcoming_reminders(user: dict, db: DatabaseManager):
    """Render upcoming reminders (next 30 days)"""
    st.markdown("#### Upcoming Reminders (Next 30 Days)")
    
    reminders = db.get_reminders(user['id'], status='pending')
    
    if not reminders:
        st.info("ℹ️ No upcoming reminders")
        return
    
    df = pd.DataFrame(reminders)
    df['due_date'] = pd.to_datetime(df['due_date'])
    
    # Filter for next 30 days
    today = datetime.now()
    thirty_days = today + timedelta(days=30)
    upcoming = df[(df['due_date'] >= today) & (df['due_date'] <= thirty_days)]
    upcoming = upcoming.sort_values('due_date')
    
    if upcoming.empty:
        st.info("ℹ️ No reminders in the next 30 days")
        return
    
    for _, reminder in upcoming.iterrows():
        days_until = (reminder['due_date'] - today).days
        
        # Color code based on urgency
        if days_until <= 3:
            border_color = "rgba(255, 68, 68, 0.5)"  # Red
            emoji = "🔴"
        elif days_until <= 7:
            border_color = "rgba(255, 170, 0, 0.5)"  # Orange
            emoji = "🟡"
        else:
            border_color = "rgba(0, 255, 170, 0.3)"  # Green
            emoji = "🟢"
        
        with st.container():
            st.markdown(f"""
            <div style="
                border-left: 4px solid {border_color};
                padding: 16px;
                margin: 12px 0;
                background: rgba(255, 255, 255, 0.03);
                border-radius: 12px;
            ">
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{emoji} {reminder['title']}**")
                st.caption(f"{reminder['type']} • {reminder['description'] if pd.notna(reminder['description']) else 'No description'}")
            
            with col2:
                st.markdown(f"**Due:** {reminder['due_date'].strftime('%b %d, %Y')}")
                if days_until == 0:
                    st.caption("⚠️ Today!")
                elif days_until == 1:
                    st.caption("⚠️ Tomorrow")
                else:
                    st.caption(f"In {days_until} days")
            
            with col3:
                if pd.notna(reminder['amount']) and reminder['amount'] > 0:
                    st.markdown(f"**Amount:**")
                    st.markdown(f"${reminder['amount']:,.2f}")
                
                if st.button("✓ Mark Done", key=f"complete_{reminder['id']}", use_container_width=True):
                    db.update_reminder_status(reminder['id'], 'completed')
                    st.success("✅ Reminder marked as completed!")
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

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
        st.info("ℹ️ No reminders found")
        return
    
    df = pd.DataFrame(reminders)
    df['due_date'] = pd.to_datetime(df['due_date'])
    
    # Apply type filter
    if type_filter != "All":
        df = df[df['type'] == type_filter]
    
    if df.empty:
        st.info("ℹ️ No reminders found with selected filters")
        return
    
    df = df.sort_values('due_date', ascending=False)
    
    # Display reminders
    for _, reminder in df.iterrows():
        with st.expander(f"{reminder['title']} - Due: {reminder['due_date'].strftime('%b %d, %Y')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Type:** {reminder['type']}")
                st.markdown(f"**Status:** {reminder['status'].capitalize()}")
                if pd.notna(reminder['amount']) and reminder['amount'] > 0:
                    st.markdown(f"**Amount:** ${reminder['amount']:,.2f}")
            
            with col2:
                st.markdown(f"**Due Date:** {reminder['due_date'].strftime('%b %d, %Y')}")
                if reminder['recurring']:
                    st.markdown(f"**Recurring:** Yes ({reminder.get('recurrence_type', 'N/A')})")
                st.markdown(f"**Notify:** {reminder['notify_days_before']} days before")
            
            if pd.notna(reminder['description']):
                st.markdown(f"**Description:** {reminder['description']}")
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if reminder['status'] == 'pending':
                    if st.button("✓ Mark Complete", key=f"complete_all_{reminder['id']}", use_container_width=True):
                        db.update_reminder_status(reminder['id'], 'completed')
                        st.success("✅ Marked as completed!")
                        st.rerun()
            
            with col2:
                if reminder['status'] != 'cancelled':
                    if st.button("✗ Cancel", key=f"cancel_{reminder['id']}", use_container_width=True):
                        db.update_reminder_status(reminder['id'], 'cancelled')
                        st.success("✅ Reminder cancelled")
                        st.rerun()
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{reminder['id']}", use_container_width=True):
                    db.delete_reminder(reminder['id'])
                    st.success("✅ Reminder deleted")
                    st.rerun()