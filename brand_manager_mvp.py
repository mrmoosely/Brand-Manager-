#!/usr/bin/env python3
"""
Brand Manager AI Assistant - MVP with Subscriptions
Simple authentication and usage tracking for monetization
"""

import streamlit as st
import sys
from pathlib import Path
import os
import json
from datetime import datetime, timedelta
import hashlib

# Load API key from Streamlit secrets or environment
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except (KeyError, FileNotFoundError):
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    st.error("⚠️ API key not found! Please add ANTHROPIC_API_KEY to Streamlit secrets or .env file")
    st.stop()

sys.path.append(str(Path(__file__).parent))

from brand_manager_assistant import BrandManagerAssistant
import pandas as pd

# ============================================================================
# SUBSCRIPTION TIERS
# ============================================================================

SUBSCRIPTION_TIERS = {
    "free": {
        "name": "Free Trial",
        "price": "$0/month",
        "analyses_per_month": 5,
        "features": [
            "5 analyses per month",
            "Data Performance Analysis only",
            "Email support"
        ],
        "stripe_link": None  # No payment needed
    },
    "pro": {
        "name": "Professional",
        "price": "$49/month",
        "analyses_per_month": 50,
        "features": [
            "50 analyses per month",
            "All 5 modules",
            "Priority support",
            "Custom templates",
            "Download outputs"
        ],
        "stripe_link": "https://buy.stripe.com/test_your_link_here"  # You'll create this
    },
    "team": {
        "name": "Team",
        "price": "$149/month",
        "analyses_per_month": 200,
        "features": [
            "200 analyses per month",
            "All 5 modules",
            "5 user seats",
            "Shared templates",
            "Priority support",
            "Team collaboration"
        ],
        "stripe_link": "https://buy.stripe.com/test_your_link_here"  # You'll create this
    }
}

# ============================================================================
# USER DATABASE (Simple JSON file for MVP - will upgrade later)
# ============================================================================

USERS_FILE = "users_db.json"

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password, tier="free"):
    """Create a new user"""
    users = load_users()
    
    if email in users:
        return False, "User already exists"
    
    users[email] = {
        "password": hash_password(password),
        "tier": tier,
        "created_at": datetime.now().isoformat(),
        "usage": {
            "current_month": datetime.now().strftime("%Y-%m"),
            "analyses_used": 0,
            "last_reset": datetime.now().isoformat()
        }
    }
    
    save_users(users)
    return True, "User created successfully"

def verify_user(email, password):
    """Verify user credentials"""
    users = load_users()
    
    if email not in users:
        return False
    
    return users[email]["password"] == hash_password(password)

def get_user(email):
    """Get user data"""
    users = load_users()
    return users.get(email)

def update_user_usage(email):
    """Update user's usage count"""
    users = load_users()
    
    if email not in users:
        return False
    
    user = users[email]
    current_month = datetime.now().strftime("%Y-%m")
    
    # Reset usage if new month
    if user["usage"]["current_month"] != current_month:
        user["usage"]["current_month"] = current_month
        user["usage"]["analyses_used"] = 0
        user["usage"]["last_reset"] = datetime.now().isoformat()
    
    # Increment usage
    user["usage"]["analyses_used"] += 1
    
    save_users(users)
    return True

def check_usage_limit(email):
    """Check if user has remaining analyses"""
    users = load_users()
    
    if email not in users:
        return False, "User not found"
    
    user = users[email]
    tier = SUBSCRIPTION_TIERS[user["tier"]]
    current_month = datetime.now().strftime("%Y-%m")
    
    # Reset usage if new month
    if user["usage"]["current_month"] != current_month:
        user["usage"]["current_month"] = current_month
        user["usage"]["analyses_used"] = 0
        user["usage"]["last_reset"] = datetime.now().isoformat()
        save_users(users)
    
    remaining = tier["analyses_per_month"] - user["usage"]["analyses_used"]
    
    if remaining <= 0:
        return False, f"Monthly limit reached. Upgrade to {SUBSCRIPTION_TIERS['pro']['name']} for more analyses."
    
    return True, remaining

def upgrade_user_tier(email, new_tier):
    """Upgrade user's subscription tier (admin function)"""
    users = load_users()
    
    if email not in users:
        return False
    
    users[email]["tier"] = new_tier
    save_users(users)
    return True

# ============================================================================
# AUTHENTICATION UI
# ============================================================================

def show_auth_page():
    """Show login/signup page"""
    
    st.title("🎯 Brand Manager AI Assistant")
    st.markdown("### AI-Powered Brand Management Tools")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary"):
            if verify_user(login_email, login_password):
                st.session_state.authenticated = True
                st.session_state.user_email = login_email
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    with tab2:
        st.subheader("Create Free Account")
        st.info("Start with 5 free analyses per month!")
        
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        signup_password2 = st.text_input("Confirm Password", type="password", key="signup_password2")
        
        if st.button("Create Account", type="primary"):
            if not signup_email or not signup_password:
                st.error("Please fill in all fields")
            elif signup_password != signup_password2:
                st.error("Passwords don't match")
            elif len(signup_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                success, message = create_user(signup_email, signup_password)
                if success:
                    st.success("Account created! Please login.")
                else:
                    st.error(message)

# ============================================================================
# SUBSCRIPTION MANAGEMENT UI
# ============================================================================

def show_subscription_page():
    """Show subscription management page"""
    
    user = get_user(st.session_state.user_email)
    current_tier = user["tier"]
    
    st.title("💳 Subscription Management")
    
    # Current plan
    st.subheader("Current Plan")
    tier_info = SUBSCRIPTION_TIERS[current_tier]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Plan", tier_info["name"])
    with col2:
        st.metric("Price", tier_info["price"])
    with col3:
        remaining = tier_info["analyses_per_month"] - user["usage"]["analyses_used"]
        st.metric("Analyses Remaining", f"{remaining}/{tier_info['analyses_per_month']}")
    
    st.markdown("---")
    
    # Upgrade options
    st.subheader("Upgrade Your Plan")
    
    cols = st.columns(3)
    
    for idx, (tier_key, tier_data) in enumerate(SUBSCRIPTION_TIERS.items()):
        with cols[idx]:
            st.markdown(f"### {tier_data['name']}")
            st.markdown(f"**{tier_data['price']}**")
            
            for feature in tier_data['features']:
                st.markdown(f"✓ {feature}")
            
            if tier_key == current_tier:
                st.success("Current Plan")
            elif tier_data['stripe_link']:
                if st.button(f"Upgrade to {tier_data['name']}", key=f"upgrade_{tier_key}"):
                    st.markdown(f"[Complete Payment on Stripe]({tier_data['stripe_link']})")
                    st.info("After payment, email your receipt to upgrade@brandmanagerai.com and we'll upgrade your account within 24 hours.")
            else:
                st.button("Current Tier", disabled=True)

# ============================================================================
# MAIN APP (with authentication)
# ============================================================================

def main_app():
    """Main application with all modules"""
    
    # Initialize session state
    if 'assistant' not in st.session_state:
        st.session_state.assistant = BrandManagerAssistant(api_key=api_key)
    
    user = get_user(st.session_state.user_email)
    
    # Sidebar
    with st.sidebar:
        st.title("🎯 Brand Manager AI")
        
        # User info
        st.markdown(f"**{st.session_state.user_email}**")
        tier_info = SUBSCRIPTION_TIERS[user["tier"]]
        st.caption(f"{tier_info['name']} Plan")
        
        # Usage
        remaining = tier_info["analyses_per_month"] - user["usage"]["analyses_used"]
        st.progress(user["usage"]["analyses_used"] / tier_info["analyses_per_month"])
        st.caption(f"{remaining} analyses remaining this month")
        
        if remaining <= 5:
            st.warning("⚠️ Running low on analyses!")
            if st.button("Upgrade Now"):
                st.session_state.page = "subscription"
                st.rerun()
        
        st.markdown("---")
        
        # Module selection (limited by tier)
        if user["tier"] == "free":
            module = "📊 Data Performance Analysis"
            st.info("Upgrade to access all 5 modules")
        else:
            module = st.selectbox(
                "Select Module",
                [
                    "📊 Data Performance Analysis",
                    "✍️ Creative Brief Generator",
                    "🎨 Brand Positioning",
                    "💡 Innovation Ideation",
                    "📑 PowerPoint Deck Generator"
                ]
            )
        
        st.markdown("---")
        
        # Navigation
        if st.button("💳 Subscription"):
            st.session_state.page = "subscription"
            st.rerun()
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.rerun()
    
    # Show subscription page if selected
    if st.session_state.get("page") == "subscription":
        show_subscription_page()
        return
    
    # Main content
    st.title("Brand Manager AI Assistant")
    
    # MODULE 1: DATA PERFORMANCE ANALYSIS
    if module == "📊 Data Performance Analysis":
        st.header("Data Performance Analysis")
        st.markdown("Upload Nielsen/IRI data or paste performance metrics for analysis")
        
        tab1, tab2 = st.tabs(["📁 Upload Data", "⌨️ Manual Entry"])
        
        with tab1:
            uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx', 'xls'])
            
            df = None  # Initialize df
            
            if uploaded_file:
                try:
                    # Read the file based on extension
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    st.success(f"✅ Loaded {len(df)} rows of data")
                    st.dataframe(df.head(10))
                    
                except Exception as e:
                    st.error(f"Error loading file: {e}")
                    st.info("Make sure your file is a valid CSV or Excel file with data.")
        
        with tab2:
            st.markdown("**Enter performance data as JSON:**")
            sample_json = {
                "brand_performance": {
                    "Your Brand": {
                        "market_share": {"current": 12.3, "yoy_change": 1.2},
                        "dollar_sales": {"current": 45.2, "yoy_change": 15.3}
                    }
                }
            }
            
            data_input = st.text_area(
                "Performance Data (JSON format)",
                value=json.dumps(sample_json, indent=2),
                height=300
            )
        
        analysis_focus = st.text_input(
            "Analysis Focus (optional)",
            placeholder="e.g., Distribution gains, pricing strategy"
        )
        
        # Validate we have data before showing analyze button
        has_data = (uploaded_file and df is not None) or data_input.strip()
        
        if not has_data:
            st.warning("⚠️ Please upload a file or enter data in the Manual Entry tab")
        
        if st.button("🔍 Analyze Performance", type="primary", disabled=not has_data):
            # Check usage limit
            can_use, message = check_usage_limit(st.session_state.user_email)
            
            if not can_use:
                st.error(message)
                st.info("Upgrade your plan to continue analyzing")
                if st.button("View Plans"):
                    st.session_state.page = "subscription"
                    st.rerun()
            else:
                with st.spinner("Analyzing data..."):
                    try:
                        # Prepare data for analysis
                        if uploaded_file:
                            # Convert dataframe to dictionary format
                            data_dict = df.to_dict('records')
                        else:
                            # Use manual entry
                            data_dict = json.loads(data_input)
                        
                        # Run analysis
                        analysis = st.session_state.assistant.analyze_market_data(
                            data_dict=data_dict,
                            analysis_focus=analysis_focus if analysis_focus else None
                        )
                        
                        # Update usage
                        update_user_usage(st.session_state.user_email)
                        
                        # Get updated remaining count
                        _, remaining = check_usage_limit(st.session_state.user_email)
                        
                        st.markdown("### Analysis Results")
                        st.markdown(analysis)
                        
                        # Download button
                        st.download_button(
                            "📥 Download Analysis",
                            analysis,
                            file_name="performance_analysis.txt",
                            mime="text/plain"
                        )
                        
                        # Show updated usage
                        st.success(f"Analysis complete! {remaining} analyses remaining this month")
                        
                    except json.JSONDecodeError as e:
                        st.error("Invalid JSON format in manual entry. Please check your data format.")
                    except Exception as e:
                        st.error(f"Error analyzing data: {str(e)}")
                        st.info("Try using the sample data or check your file format.")
    
    # MODULE 2-5: Only for paid tiers
    elif user["tier"] != "free":
        st.info(f"Module: {module} - Full implementation coming soon!")
        st.markdown("This module is available in your plan. Implementation in progress.")
    else:
        st.warning("Upgrade to Professional or Team plan to access this module")

# ============================================================================
# ADMIN DASHBOARD (Password Protected)
# ============================================================================

def show_admin_page():
    """Admin dashboard for managing users"""
    
    st.title("🔧 Admin Dashboard")
    
    # Simple password protection
    admin_password = st.text_input("Admin Password", type="password")
    
    if admin_password != "Th3m00s389!":  # Change this!
        st.warning("Enter admin password")
        return
    
    st.success("✅ Admin access granted")
    
    # Load all users
    users = load_users()
    
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", len(users))
    with col2:
        free_users = sum(1 for u in users.values() if u["tier"] == "free")
        st.metric("Free Users", free_users)
    with col3:
        paid_users = len(users) - free_users
        revenue = paid_users * 49  # Simplified
        st.metric("Est. MRR", f"${revenue}")
    
    st.markdown("---")
    
    # User list
    st.subheader("User Management")
    
    for email, user_data in users.items():
        with st.expander(f"{email} - {SUBSCRIPTION_TIERS[user_data['tier']]['name']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Tier:** {user_data['tier']}")
                st.write(f"**Created:** {user_data['created_at'][:10]}")
                st.write(f"**Usage:** {user_data['usage']['analyses_used']}/{SUBSCRIPTION_TIERS[user_data['tier']]['analyses_per_month']}")
            
            with col2:
                new_tier = st.selectbox(
                    "Change Tier",
                    ["free", "pro", "team"],
                    index=["free", "pro", "team"].index(user_data['tier']),
                    key=f"tier_{email}"
                )
                
                if st.button("Update", key=f"update_{email}"):
                    upgrade_user_tier(email, new_tier)
                    st.success("Tier updated!")
                    st.rerun()

# ============================================================================
# MAIN APP LOGIC
# ============================================================================

# Page config
st.set_page_config(
    page_title="Brand Manager AI Assistant",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'page' not in st.session_state:
    st.session_state.page = "main"

# Check for admin page
if st.query_params.get("admin") == "true":
    show_admin_page()
elif not st.session_state.authenticated:
    show_auth_page()
else:
    main_app()

# Footer
st.markdown("---")
st.markdown("**Brand Manager AI Assistant** | Powered by Claude Sonnet 4.5")
