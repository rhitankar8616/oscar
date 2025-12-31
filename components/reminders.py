"""Reminders component."""
import streamlit as st
from datetime import datetime
from database.db_manager import DatabaseManager
from utils.formatters import format_currency, format_date
from utils.validators import validate_amount, sanitize_input
import config

def render_reminders(user: dict, db: DatabaseManager):
    """Render dates and reminders page."""
    
    st.markdown("## Dates & Reminders")
    st.caption("Never miss important financial dates")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Add Reminder", type="primary", use_container_width=True):
            st.session_state.show_add_reminder = True
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.get('show_add_reminder', False):
        with st.container():
            st.markdown("### Add New Reminder")
            
            with st.form("add_reminder_form"):
                form_col1, form_col2 = st.columns(2)
                
                with form_col1:
                    title = st.text_input("Title *", placeholder="e.g., Rent Payment")
                    reminder_type = st.selectbox("Type *", config.REMINDER_TYPES)
                    date = st.date_input("Date *", value=datetime.now())
                    is_recurring = st.checkbox("Recurring reminder")
                
                with form_col2:
                    amount = st.text_input("Amount ($)", placeholder="Optional")
                    
                    if is_recurring:
                        frequency = st.selectbox("Frequency", 
                                                ["Daily", "Weekly", "Monthly", "Yearly"])
                    else:
                        frequency = None
                    
                    notes = st.text_area("Notes", placeholder="Additional details...")
                
                submit_col1, submit_col2 = st.columns([1, 1])
                
                with submit_col1:
                    submitted = st.form_submit_button("Add Reminder", use_container_width=True, type="primary")
                
                with submit_col2:
                    cancelled = st.form_submit_button("Cancel", use_container_width=True)
                
                if cancelled:
                    st.session_state.show_add_reminder = False
                    st.rerun()
                
                if submitted:
                    if not title:
                        st.error("Please enter a title")
                    else:
                        amount_float = None
                        if amount:
                            is_valid, amount_float, error_msg = validate_amount(amount)
                            if not is_valid:
                                st.error(error_msg)
                                amount_float = None
                        
                        reminder_id = db.add_reminder(
                            user_id=user['id'],
                            title=sanitize_input(title),
                            reminder_type=reminder_type,
                            date=date.strftime("%Y-%m-%d"),
                            amount=amount_float,
                            frequency=frequency if is_recurring else None,
                            is_recurring=is_recurring,
                            notes=sanitize_input(notes) if notes else None
                        )
                        
                        if reminder_id:
                            st.success("Reminder added successfully!")
                            st.session_state.show_add_reminder = False
                            st.rerun()
                        else:
                            st.error("Failed to add reminder. Please try again.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    reminders = db.get_user_reminders(user['id'])
    
    today = datetime.now().date()
    past_reminders = []
    upcoming_reminders = []
    
    for reminder in reminders:
        reminder_date = datetime.strptime(reminder['date'], "%Y-%m-%d").date()
        if reminder_date < today:
            past_reminders.append(reminder)
        else:
            upcoming_reminders.append(reminder)
    
    if past_reminders:
        st.markdown("### Past Reminders")
        
        for reminder in past_reminders:
            with st.container():
                rem_col1, rem_col2, rem_col3 = st.columns([3, 2, 1])
                
                with rem_col1:
                    st.markdown(f"**{reminder['title']}**")
                    
                    date_str = format_date(reminder['date'])
                    badge = " • Monthly" if reminder['is_recurring'] else ""
                    st.caption(f"{reminder['reminder_type']} • {date_str}{badge}")
                    
                    st.markdown("<span style='color: #F44336; font-size: 12px;'>Overdue</span>", 
                               unsafe_allow_html=True)
                
                with rem_col2:
                    if reminder['amount']:
                        st.markdown(f"**{format_currency(reminder['amount'], 'USD')}**")
                
                with rem_col3:
                    mark_col, del_col = st.columns(2)
                    with mark_col:
                        if st.button("✓", key=f"mark_{reminder['id']}", help="Mark as done"):
                            if db.mark_reminder_complete(user['id'], reminder['id']):
                                st.success("Marked complete!")
                                st.rerun()
                    with del_col:
                        if st.button("✕", key=f"del_{reminder['id']}", help="Delete"):
                            if db.delete_reminder(user['id'], reminder['id']):
                                st.success("Reminder deleted!")
                                st.rerun()
                
                st.markdown("---")
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    if upcoming_reminders:
        st.markdown("### Upcoming Reminders")
        
        for reminder in upcoming_reminders:
            with st.container():
                rem_col1, rem_col2, rem_col3 = st.columns([3, 2, 1])
                
                with rem_col1:
                    st.markdown(f"**{reminder['title']}**")
                    
                    date_str = format_date(reminder['date'])
                    badge = " • Monthly" if reminder['is_recurring'] else ""
                    st.caption(f"{reminder['reminder_type']} • {date_str}{badge}")
                
                with rem_col2:
                    if reminder['amount']:
                        st.markdown(f"**{format_currency(reminder['amount'], 'USD')}**")
                
                with rem_col3:
                    mark_col, del_col = st.columns(2)
                    with mark_col:
                        if st.button("✓", key=f"mark_{reminder['id']}", help="Mark as done"):
                            if db.mark_reminder_complete(user['id'], reminder['id']):
                                st.success("Marked complete!")
                                st.rerun()
                    with del_col:
                        if st.button("✕", key=f"del_{reminder['id']}", help="Delete"):
                            if db.delete_reminder(user['id'], reminder['id']):
                                st.success("Reminder deleted!")
                                st.rerun()
                
                st.markdown("---")
    
    if not past_reminders and not upcoming_reminders:
        st.info("No reminders yet. Add your first reminder!")
        
        if st.button("Add Your First Reminder", use_container_width=True):
            st.session_state.show_add_reminder = True
            st.rerun()