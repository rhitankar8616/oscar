import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_manager import DatabaseManager

def render_friends(user: dict, db: DatabaseManager):
    """Render friends page"""
    st.markdown("### Friends & Shared Expenses")
    
    tab1, tab2, tab3 = st.tabs(["Overview", "Add Friend", "Transactions"])
    
    with tab1:
        render_friends_overview(user, db)
    
    with tab2:
        render_add_friend(user, db)
    
    with tab3:
        render_transactions(user, db)

def render_friends_overview(user: dict, db: DatabaseManager):
    """Render friends overview with side-by-side summary"""
    friends = db.get_user_friends(user['id'])
    
    if not friends:
        st.info("No friends added yet. Add a friend to start tracking shared expenses!")
        return
    
    # Summary - You're Owed and You Owe SIDE BY SIDE
    total_owed = sum(f['balance'] for f in friends if f['balance'] > 0)
    total_owe = sum(abs(f['balance']) for f in friends if f['balance'] < 0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(76, 175, 80, 0.12); border: 1px solid rgba(76, 175, 80, 0.3); border-radius: 8px; padding: 10px; text-align: center;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; margin: 0; text-transform: uppercase;">You're Owed</p>
            <p style="color: #4CAF50; font-size: 1.1rem; font-weight: 700; margin: 4px 0 0 0;">${total_owed:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: rgba(244, 67, 54, 0.12); border: 1px solid rgba(244, 67, 54, 0.3); border-radius: 8px; padding: 10px; text-align: center;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.6rem; margin: 0; text-transform: uppercase;">You Owe</p>
            <p style="color: #F44336; font-size: 1.1rem; font-weight: 700; margin: 4px 0 0 0;">${total_owe:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### Your Friends")
    
    for friend in friends:
        balance = friend['balance']
        
        if balance > 0:
            balance_color = "#4CAF50"
            balance_text = f"owes you ${balance:,.2f}"
        elif balance < 0:
            balance_color = "#F44336"
            balance_text = f"you owe ${abs(balance):,.2f}"
        else:
            balance_color = "#9E9E9E"
            balance_text = "settled up"
        
        initial = friend['name'][0].upper() if friend['name'] else 'F'
        
        # Friend card with actions on right
        col_main, col_actions = st.columns([5, 2])
        
        with col_main:
            st.markdown(f"""
            <div style="background: rgba(30, 45, 65, 0.5); border-radius: 8px; padding: 10px; display: flex; align-items: center; gap: 10px;">
                <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #3b82f6, #6366f1); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 12px; flex-shrink: 0;">{initial}</div>
                <div style="flex: 1;">
                    <p style="color: #ffffff; font-size: 0.85rem; font-weight: 500; margin: 0;">{friend['name']}</p>
                    <p style="color: {balance_color}; font-size: 0.7rem; margin: 2px 0 0 0;">{balance_text}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_actions:
            # Action buttons side by side
            btn_cols = st.columns(3)
            with btn_cols[0]:
                if st.button("↑", key=f"lent_{friend['id']}", help="You lent"):
                    st.session_state.selected_friend = friend['id']
                    st.session_state.transaction_type = 'lent'
            with btn_cols[1]:
                if st.button("↓", key=f"bor_{friend['id']}", help="You borrowed"):
                    st.session_state.selected_friend = friend['id']
                    st.session_state.transaction_type = 'borrowed'
            with btn_cols[2]:
                if st.button("🗑", key=f"del_f_{friend['id']}", help="Delete"):
                    db.delete_friend(user['id'], friend['id'])
                    st.rerun()
        
        st.markdown('<div style="height: 4px;"></div>', unsafe_allow_html=True)
    
    # Quick transaction form
    if 'selected_friend' in st.session_state and st.session_state.selected_friend:
        render_quick_transaction(user, db)

def render_quick_transaction(user: dict, db: DatabaseManager):
    """Render quick transaction form"""
    friend_id = st.session_state.selected_friend
    trans_type = st.session_state.get('transaction_type', 'lent')
    
    friends = db.get_user_friends(user['id'])
    friend = next((f for f in friends if f['id'] == friend_id), None)
    
    if not friend:
        st.session_state.selected_friend = None
        return
    
    st.markdown("---")
    action = "Lent to" if trans_type == 'lent' else "Borrowed from"
    st.markdown(f"#### {action} {friend['name']}")
    
    with st.form("quick_trans"):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("Amount", min_value=0.01, step=1.0)
        with col2:
            description = st.text_input("Description", placeholder="e.g., Lunch")
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.form_submit_button("Add", type="primary", use_container_width=True):
                if amount > 0:
                    db.add_transaction(
                        user_id=user['id'],
                        friend_id=friend_id,
                        transaction_type=trans_type,
                        amount=amount,
                        description=description or "Transaction",
                        date=datetime.now().strftime("%Y-%m-%d")
                    )
                    st.session_state.selected_friend = None
                    st.success("Added!")
                    st.rerun()
        
        with btn_col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.selected_friend = None
                st.rerun()

def render_add_friend(user: dict, db: DatabaseManager):
    """Render add friend form"""
    st.markdown("#### Add New Friend")
    
    with st.form("add_friend_form", clear_on_submit=True):
        name = st.text_input("Name*", placeholder="Friend's name")
        
        col1, col2 = st.columns(2)
        with col1:
            phone = st.text_input("Phone (optional)")
        with col2:
            email = st.text_input("Email (optional)")
        
        notes = st.text_area("Notes (optional)", height=60)
        
        if st.form_submit_button("Add Friend", type="primary", use_container_width=True):
            if not name:
                st.error("Please enter a name")
            else:
                result = db.add_friend(
                    user_id=user['id'],
                    name=name,
                    phone=phone if phone else None,
                    email=email if email else None,
                    notes=notes if notes else None
                )
                
                if result:
                    st.success(f"{name} added!")
                    st.rerun()
                else:
                    st.error("Failed to add friend")

def render_transactions(user: dict, db: DatabaseManager):
    """Render transactions tab"""
    st.markdown("#### Transaction History")
    
    friends = db.get_user_friends(user['id'])
    
    if not friends:
        st.info("Add friends to see transactions")
        return
    
    friend_options = {f['name']: f['id'] for f in friends}
    selected_name = st.selectbox("Select Friend", list(friend_options.keys()))
    
    if selected_name:
        friend_id = friend_options[selected_name]
        transactions = db.get_friend_transactions(user['id'], friend_id)
        
        if not transactions:
            st.info(f"No transactions with {selected_name}")
            return
        
        for trans in transactions:
            trans_type = trans['transaction_type']
            
            if trans_type == 'lent':
                icon = "↑"
                color = "#4CAF50"
                text = "You lent"
            else:
                icon = "↓"
                color = "#F44336"
                text = "You borrowed"
            
            try:
                trans_date = datetime.strptime(trans['date'], "%Y-%m-%d").strftime("%b %d")
            except:
                trans_date = trans['date']
            
            st.markdown(f"""
            <div style="background: rgba(30, 45, 65, 0.4); border-radius: 6px; padding: 8px 10px; margin-bottom: 4px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: {color}; font-size: 1rem; font-weight: bold;">{icon}</span>
                        <div>
                            <p style="color: #ffffff; font-size: 0.8rem; font-weight: 500; margin: 0;">{trans['description']}</p>
                            <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 0;">{text} • {trans_date}</p>
                        </div>
                    </div>
                    <p style="color: {color}; font-size: 0.9rem; font-weight: 600; margin: 0;">${trans['amount']:,.2f}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)