"""Friends component for expense splitting."""
import streamlit as st
from datetime import datetime
from database.db_manager import DatabaseManager
from utils.formatters import format_currency, format_date
from utils.validators import validate_amount, validate_phone, sanitize_input

def render_friends(user: dict, db: DatabaseManager):
    """Render friends and expense splitting page."""
    
    st.markdown("#### Friends")
    st.caption("Split expenses and track balances")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Add Friend", type="primary", use_container_width=True):
            st.session_state.show_add_friend = True
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.get('show_add_friend', False):
        with st.container():
            st.markdown("### Add New Friend")
            
            with st.form("add_friend_form"):
                form_col1, form_col2 = st.columns(2)
                
                with form_col1:
                    name = st.text_input("Name *", placeholder="e.g., John Doe")
                    phone = st.text_input("Phone", placeholder="9876543210")
                
                with form_col2:
                    email = st.text_input("Email", placeholder="john@example.com")
                    notes = st.text_area("Notes", placeholder="Additional information...")
                
                submit_col1, submit_col2 = st.columns([1, 1])
                
                with submit_col1:
                    submitted = st.form_submit_button("Add Friend", use_container_width=True, type="primary")
                
                with submit_col2:
                    cancelled = st.form_submit_button("Cancel", use_container_width=True)
                
                if cancelled:
                    st.session_state.show_add_friend = False
                    st.rerun()
                
                if submitted:
                    if not name:
                        st.error("Please enter a name")
                    else:
                        validated_phone = None
                        if phone:
                            is_valid, validated_phone, msg = validate_phone(phone)
                            if not is_valid:
                                st.error(msg)
                                validated_phone = None
                        
                        friend_id = db.add_friend(
                            user_id=user['id'],
                            name=sanitize_input(name),
                            phone=validated_phone,
                            email=email if email else None,
                            notes=sanitize_input(notes) if notes else None
                        )
                        
                        if friend_id:
                            st.success("Friend added successfully!")
                            st.session_state.show_add_friend = False
                            st.rerun()
                        else:
                            st.error("Failed to add friend")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    friends = db.get_user_friends(user['id'])
    
    if friends:
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        
        total_friends = len(friends)
        total_owed_to_you = sum(f['balance'] for f in friends if f['balance'] > 0)
        total_you_owe = sum(abs(f['balance']) for f in friends if f['balance'] < 0)
        
        with summary_col1:
            st.markdown(f"""
            <div style='background-color: #2C3E50; padding: 20px; border-radius: 10px; text-align: center;'>
                <p style='color: #888; font-size: 14px; margin: 0;'>Total Friends</p>
                <h2 style='color: white; margin: 10px 0;'>{total_friends}</h2>
                <p style='color: #888; font-size: 12px; margin: 0;'>People you track with</p>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col2:
            st.markdown(f"""
            <div style='background-color: #2C3E50; padding: 20px; border-radius: 10px; text-align: center;'>
                <p style='color: #888; font-size: 14px; margin: 0;'>You Get Back</p>
                <h2 style='color: #4CAF50; margin: 10px 0;'>{format_currency(total_owed_to_you, 'USD')}</h2>
                <p style='color: #888; font-size: 12px; margin: 0;'>Total owed to you</p>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col3:
            st.markdown(f"""
            <div style='background-color: #2C3E50; padding: 20px; border-radius: 10px; text-align: center;'>
                <p style='color: #888; font-size: 14px; margin: 0;'>You Owe</p>
                <h2 style='color: #F44336; margin: 10px 0;'>{format_currency(total_you_owe, 'USD')}</h2>
                <p style='color: #888; font-size: 12px; margin: 0;'>Total you owe</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        for friend in friends:
            with st.container():
                friend_col1, friend_col2, friend_col3 = st.columns([3, 2, 1])
                
                with friend_col1:
                    st.markdown(f"### {friend['name']}")
                    if friend['phone']:
                        st.caption(f"📞 {friend['phone']}")
                    if friend['email']:
                        st.caption(f"📧 {friend['email']}")
                
                with friend_col2:
                    if friend['balance'] > 0:
                        st.markdown(f"<p style='color: #4CAF50; font-size: 20px; font-weight: bold;'>They owe you {format_currency(friend['balance'], 'USD')}</p>", unsafe_allow_html=True)
                    elif friend['balance'] < 0:
                        st.markdown(f"<p style='color: #F44336; font-size: 20px; font-weight: bold;'>You owe {format_currency(abs(friend['balance']), 'USD')}</p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p style='color: #888; font-size: 20px;'>All settled up!</p>", unsafe_allow_html=True)
                        st.caption("No outstanding balance")
                
                with friend_col3:
                    if st.button("View", key=f"view_{friend['id']}", use_container_width=True):
                        st.session_state.selected_friend = friend['id']
                        st.rerun()
                    
                    if st.button("Delete", key=f"del_{friend['id']}", use_container_width=True):
                        if db.delete_friend(user['id'], friend['id']):
                            st.success("Friend deleted!")
                            st.rerun()
                
                st.markdown("---")
    else:
        st.info("No friends added yet. Add friends to split expenses!")
        
        if st.button("Add Your First Friend", use_container_width=True):
            st.session_state.show_add_friend = True
            st.rerun()
    
    if st.session_state.get('selected_friend'):
        show_friend_detail(user, db, st.session_state.selected_friend)


def show_friend_detail(user: dict, db: DatabaseManager, friend_id: int):
    """Show friend transaction details."""
    
    friends = db.get_user_friends(user['id'])
    friend = next((f for f in friends if f['id'] == friend_id), None)
    
    if not friend:
        st.session_state.selected_friend = None
        st.rerun()
        return
    
    st.markdown("---")
    st.markdown(f"## {friend['name']}")
    
    if friend['phone']:
        st.caption(f"📞 {friend['phone']}")
    
    if friend['balance'] > 0:
        st.markdown(f"<div style='background-color: #2C3E50; padding: 20px; border-radius: 10px; text-align: center;'><p style='color: #4CAF50; font-size: 24px; font-weight: bold;'>They owe you {format_currency(friend['balance'], 'USD')}</p></div>", unsafe_allow_html=True)
    elif friend['balance'] < 0:
        st.markdown(f"<div style='background-color: #2C3E50; padding: 20px; border-radius: 10px; text-align: center;'><p style='color: #F44336; font-size: 24px; font-weight: bold;'>You owe {format_currency(abs(friend['balance']), 'USD')}</p></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background-color: #2C3E50; padding: 20px; border-radius: 10px; text-align: center;'><p style='color: #888; font-size: 24px;'>All settled up!</p><p style='color: #888; font-size: 14px;'>No outstanding balance</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Add Transaction", type="primary"):
        st.session_state.show_add_transaction = True
    
    if st.button("Back to Friends"):
        st.session_state.selected_friend = None
        st.rerun()
    
    if st.session_state.get('show_add_transaction', False):
        with st.form("add_transaction_form"):
            st.markdown("### Add Transaction")
            
            trans_col1, trans_col2 = st.columns(2)
            
            with trans_col1:
                transaction_type = st.radio("Transaction Type", 
                                           ["You lent money", "You borrowed money"],
                                           horizontal=True)
                amount = st.text_input("Amount ($) *", placeholder="10.00")
            
            with trans_col2:
                description = st.text_input("Description *", placeholder="e.g., Groceries at Walmart")
                date = st.date_input("Date *", value=datetime.now())
            
            submit_col1, submit_col2 = st.columns([1, 1])
            
            with submit_col1:
                submitted = st.form_submit_button("Add Transaction", use_container_width=True, type="primary")
            
            with submit_col2:
                cancelled = st.form_submit_button("Cancel", use_container_width=True)
            
            if cancelled:
                st.session_state.show_add_transaction = False
                st.rerun()
            
            if submitted:
                if not amount or not description:
                    st.error("Please fill in all required fields")
                else:
                    is_valid, amount_float, error_msg = validate_amount(amount)
                    
                    if not is_valid:
                        st.error(error_msg)
                    else:
                        trans_type = "lent" if transaction_type == "You lent money" else "borrowed"
                        
                        transaction_id = db.add_transaction(
                            user_id=user['id'],
                            friend_id=friend_id,
                            transaction_type=trans_type,
                            amount=amount_float,
                            description=sanitize_input(description),
                            date=date.strftime("%Y-%m-%d")
                        )
                        
                        if transaction_id:
                            st.success("Transaction added successfully!")
                            st.session_state.show_add_transaction = False
                            st.rerun()
                        else:
                            st.error("Failed to add transaction")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Active Transactions")
    
    transactions = db.get_friend_transactions(user['id'], friend_id)
    
    if transactions:
        for trans in transactions:
            with st.container():
                trans_col1, trans_col2, trans_col3 = st.columns([3, 2, 1])
                
                with trans_col1:
                    st.markdown(f"**{trans['description']}**")
                    st.caption(f"{format_date(trans['date'])}")
                
                with trans_col2:
                    color = "#4CAF50" if trans['transaction_type'] == "lent" else "#F44336"
                    label = "you lent" if trans['transaction_type'] == "lent" else "you borrowed"
                    st.markdown(f"<p style='color: {color}; font-weight: bold;'>{format_currency(trans['amount'], 'USD')}</p>", unsafe_allow_html=True)
                    st.caption(label)
                
                with trans_col3:
                    if st.button("Delete", key=f"del_trans_{trans['id']}"):
                        if db.delete_transaction(user['id'], trans['id']):
                            st.success("Transaction deleted!")
                            st.rerun()
                
                st.markdown("---")
    else:
        st.info("No transactions yet")