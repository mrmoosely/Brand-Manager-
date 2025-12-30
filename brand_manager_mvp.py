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
import re
from typing import Tuple, Optional, Dict

# Load API key from Streamlit secrets or environment
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except (KeyError, FileNotFoundError):
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    st.error("API key not found! Please add ANTHROPIC_API_KEY to Streamlit secrets or .env file")
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
            st.warning("Running low on analyses!")
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
    
    # ============================================================================
    # SYNDICATED DATA SOURCE HANDLERS
    # ============================================================================
    
    def detect_data_source(df: pd.DataFrame) -> Tuple[Optional[str], float]:
        """
        Detect which syndicated data source the DataFrame is from.
        Returns: (source_name, confidence_score)
        """
        if df is None or df.empty:
            return None, 0.0
        
        # Convert column names to lowercase for easier matching
        cols = [str(col).lower() for col in df.columns]
        col_str = ' '.join(cols)
        
        # Detection patterns with confidence scoring
        patterns = {
            'Nielsen': {
                'keywords': ['nielsen', 'scantrack', 'homescan', 'market', 'tdp', 'acv'],
                'typical_cols': ['market', '$ sales', 'unit sales', 'tdp', 'acv %'],
                'confidence': 0.0
            },
            'IRI': {
                'keywords': ['iri', 'infoscan', 'total us', 'multi outlet'],
                'typical_cols': ['total us', '$ sales', 'units', 'eq volume'],
                'confidence': 0.0
            },
            'Circana': {
                'keywords': ['circana', 'market advantage', 'total us-mulo'],
                'typical_cols': ['circana', 'total us', '$ sales', 'units'],
                'confidence': 0.0
            },
            'Numerator': {
                'keywords': ['numerator', 'household', 'buyer', 'panel'],
                'typical_cols': ['household', 'penetration', 'buyer', 'trip'],
                'confidence': 0.0
            },
            'SPINS': {
                'keywords': ['spins', 'natural', 'organic', 'spins total us'],
                'typical_cols': ['spins', 'natural channel', 'total us natural'],
                'confidence': 0.0
            }
        }
        
        # Score each source
        for source, pattern in patterns.items():
            score = 0.0
            
            # Check for keywords in column names or first few rows
            for keyword in pattern['keywords']:
                if keyword in col_str:
                    score += 25.0
                # Also check first few rows for source name
                try:
                    first_rows = ' '.join([str(v).lower() for v in df.iloc[:3].values.flatten()])
                    if keyword in first_rows:
                        score += 15.0
                except:
                    pass
            
            # Check for typical column patterns
            for typical_col in pattern['typical_cols']:
                if any(typical_col in col for col in cols):
                    score += 10.0
            
            patterns[source]['confidence'] = min(score, 100.0)
        
        # Find highest confidence source
        best_source = max(patterns.items(), key=lambda x: x[1]['confidence'])
        
        if best_source[1]['confidence'] >= 30.0:
            return best_source[0], best_source[1]['confidence']
        
        return None, 0.0
    
    def clean_numeric_column(series: pd.Series) -> pd.Series:
        """Clean numeric data by removing $, %, commas, and converting to float"""
        if series.dtype == 'object':
            # Remove common formatting
            cleaned = series.astype(str).str.replace('$', '', regex=False)
            cleaned = cleaned.str.replace('%', '', regex=False)
            cleaned = cleaned.str.replace(',', '', regex=False)
            cleaned = cleaned.str.strip()
            
            # Convert to numeric, coerce errors to NaN
            try:
                return pd.to_numeric(cleaned, errors='coerce')
            except:
                return series
        return series
    
    def standardize_column_names(df: pd.DataFrame, source: str) -> pd.DataFrame:
        """Standardize column names based on detected source"""
        df = df.copy()
        
        # Common mappings for each source
        mappings = {
            'Nielsen': {
                '$ sales': 'dollar_sales',
                'dollar sales': 'dollar_sales',
                'unit sales': 'unit_sales',
                'units': 'unit_sales',
                'market': 'geography',
                'tdp': 'tdp_distribution',
                'acv %': 'acv_distribution',
                'acv': 'acv_distribution',
                'period': 'time_period',
                'share': 'market_share'
            },
            'IRI': {
                '$ sales': 'dollar_sales',
                'dollar sales': 'dollar_sales',
                'units': 'unit_sales',
                'eq volume': 'equivalent_volume',
                'total us': 'geography',
                'multi outlet': 'channel',
                'period': 'time_period',
                'share': 'market_share'
            },
            'Circana': {
                '$ sales': 'dollar_sales',
                'dollar sales': 'dollar_sales',
                'units': 'unit_sales',
                'total us': 'geography',
                'mulo': 'channel',
                'fdm': 'channel',
                'period': 'time_period',
                'share': 'market_share'
            },
            'Numerator': {
                'dollar sales': 'dollar_sales',
                '$ sales': 'dollar_sales',
                'households': 'household_count',
                'penetration': 'household_penetration',
                'buyers': 'buyer_count',
                'trips': 'trip_count',
                'period': 'time_period'
            },
            'SPINS': {
                '$ sales': 'dollar_sales',
                'dollar sales': 'dollar_sales',
                'units': 'unit_sales',
                'natural channel': 'channel',
                'total us natural': 'geography',
                'period': 'time_period',
                'share': 'market_share'
            }
        }
        
        # Get mapping for this source
        mapping = mappings.get(source, {})
        
        # Standardize column names
        new_columns = {}
        for col in df.columns:
            col_lower = str(col).lower().strip()
            # Check if column matches any mapping
            matched = False
            for pattern, standard_name in mapping.items():
                if pattern.lower() in col_lower:
                    new_columns[col] = standard_name
                    matched = True
                    break
            # If no match, keep original but clean it
            if not matched:
                clean_name = col_lower.replace(' ', '_').replace('-', '_')
                new_columns[col] = clean_name
        
        df.rename(columns=new_columns, inplace=True)
        return df
    
    def preprocess_syndicated_data(df: pd.DataFrame, source: str) -> pd.DataFrame:
        """Apply source-specific preprocessing and cleaning"""
        df = df.copy()
        
        # Standardize column names
        df = standardize_column_names(df, source)
        
        # Clean numeric columns
        numeric_patterns = ['sales', 'units', 'share', 'volume', 'tdp', 'acv', 
                          'price', 'distribution', 'penetration', 'count']
        
        for col in df.columns:
            # Check if column name suggests numeric data
            if any(pattern in col.lower() for pattern in numeric_patterns):
                df[col] = clean_numeric_column(df[col])
        
        # Source-specific processing
        if source == 'Nielsen':
            # Nielsen often has summary rows - remove them
            if 'market' in df.columns:
                df = df[df['market'].notna()]
                df = df[~df['market'].str.contains('total', case=False, na=False)]
        
        elif source == 'IRI':
            # IRI may have multiple header rows
            # Remove rows where dollar_sales is not numeric
            if 'dollar_sales' in df.columns:
                df = df[pd.to_numeric(df['dollar_sales'], errors='coerce').notna()]
        
        elif source == 'Circana':
            # Circana combines IRI + NPD, similar cleaning
            if 'dollar_sales' in df.columns:
                df = df[pd.to_numeric(df['dollar_sales'], errors='coerce').notna()]
        
        elif source == 'Numerator':
            # Numerator has household panel data - different structure
            # Ensure household counts are positive
            if 'household_count' in df.columns:
                df = df[df['household_count'] > 0]
        
        elif source == 'SPINS':
            # SPINS focuses on natural/organic - clean channel data
            if 'channel' in df.columns:
                df = df[df['channel'].notna()]
        
        # Remove any completely empty rows
        df = df.dropna(how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def get_source_guidance(source: str) -> str:
        """Get helpful guidance for working with specific data sources"""
        guidance = {
            'Nielsen': """
            📊 **Nielsen Data Detected**
            
            Your data includes:
            - Market/geography information
            - Dollar sales and unit sales
            - Distribution metrics (TDP/ACV)
            
            **Best for:** Retail performance tracking, distribution analysis, competitive share
            """,
            'IRI': """
            📊 **IRI Data Detected**
            
            Your data includes:
            - Multi-outlet retail sales
            - Category and segment performance
            - Pricing and promotional insights
            
            **Best for:** Total US retail tracking, category trends, promotional effectiveness
            """,
            'Circana': """
            📊 **Circana Data Detected**
            
            Your data includes:
            - Combined retail + consumer insights
            - Cross-category visibility
            - Market dynamics
            
            **Best for:** Holistic market view, consumer + retail trends, strategic planning
            """,
            'Numerator': """
            📊 **Numerator Data Detected**
            
            Your data includes:
            - Household purchase behavior
            - Buyer demographics
            - Trip and basket analysis
            
            **Best for:** Consumer behavior, loyalty analysis, shopper insights
            """,
            'SPINS': """
            📊 **SPINS Data Detected**
            
            Your data includes:
            - Natural and organic channel sales
            - Specialty retail performance
            - Health & wellness trends
            
            **Best for:** Natural channel strategy, emerging trends, specialty retail
            """
        }
        
        return guidance.get(source, "")
    
    # ============================================================================
    # END SYNDICATED DATA SOURCE HANDLERS
    # ============================================================================
    
    # MODULE 1: DATA PERFORMANCE ANALYSIS
    if module == "📊 Data Performance Analysis":
        st.header("Data Performance Analysis")
        st.markdown("Upload syndicated data (Nielsen, IRI, Circana, Numerator, SPINS) or paste performance metrics for AI-powered analysis")
        
        # User instructions
        with st.expander("📖 How to use this tool", expanded=False):
            st.markdown("""
            **What this does:**
            - Automatically detects and processes major syndicated data sources
            - Analyzes market data (Nielsen, IRI, Circana, Numerator, SPINS)
            - Identifies key performance drivers and trends
            - Provides competitive insights and recommendations
            
            **Supported Data Sources:**
            - 📊 **Nielsen:** ScanTrack, Homescan retail data
            - 📊 **IRI:** InfoScan multi-outlet data
            - 📊 **Circana:** Combined retail + consumer insights
            - 📊 **Numerator:** Household panel purchase data
            - 📊 **SPINS:** Natural/organic channel data
            - 📁 **Custom:** Any CSV/Excel with sales/market data
            
            **Best practices:**
            - **Small datasets (<1,000 rows):** Upload as-is for detailed analysis
            - **Large datasets (>1,000 rows):** Automatically summarized by brand/product for faster, executive-level insights
            - **For focused analysis:** Use the "Analysis Focus" field to specify what you want (e.g., "Traveller vs competitors")
            
            **File requirements:**
            - Formats: CSV or Excel (.xlsx, .xls)
            - Max file size: 200MB
            - Should include: Brand names, dollar sales, volume, time periods
            
            **Large file tip:** If you have 10K+ rows, the tool will automatically group by brand and product to provide clean summary insights. For SKU-level detail, filter your data first!
            """)
        
        tab1, tab2 = st.tabs(["📁 Upload Data", "⌨️ Manual Entry"])
        
        with tab1:
            uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx', 'xls'])
            
            df = None  # Initialize df
            data_source = None  # Initialize data source
            
            if uploaded_file:
                try:
                    # Read the file based on extension
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    # Detect syndicated data source
                    data_source, confidence = detect_data_source(df)
                    
                    if data_source:
                        st.success(f"✅ {data_source} data detected ({confidence:.0f}% confidence)")
                        
                        # Show source-specific guidance
                        st.info(get_source_guidance(data_source))
                        
                        # Preprocess the data
                        with st.spinner(f"Preprocessing {data_source} data..."):
                            df = preprocess_syndicated_data(df, data_source)
                        
                        st.success(f"✅ Loaded and cleaned {len(df):,} rows of {data_source} data")
                    else:
                        st.success(f"✅ Loaded {len(df):,} rows of data")
                        st.info("💡 **Tip:** This tool works great with Nielsen, IRI, Circana, Numerator, and SPINS data!")
                    
                    st.dataframe(df.head(10))
                    
                    # Show helpful tip based on file size
                    if len(df) > 1000:
                        st.info(f"""
                        💡 **Pro tip:** Your file has {len(df):,} rows. 
                        
                        When you click Analyze, I'll automatically group this by brand/product 
                        to give you strategic insights. Perfect for executive summaries!
                        
                        *Want SKU-level detail? Filter your Excel file to <1,000 rows first.*
                        """)
                    
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
            st.warning("Please upload a file or enter data in the Manual Entry tab")
        
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
                            # For large datasets, summarize the data first
                            if len(df) > 1000:
                                # Show informative message about what's happening
                                st.info(f"""
                                🔄 **Large dataset detected:** {len(df):,} rows
                                
                                To provide fast, executive-level insights, I'll automatically:
                                - Group by brand and product
                                - Aggregate sales, volume, and metrics
                                - Focus on strategic trends
                                
                                **Processing...**
                                """)
                                
                                # Aggregate data by key columns
                                # Group by brand and item, sum dollar values
                                summary_columns = []
                                
                                # Find key grouping columns
                                if 'ALC BRAND FAMILY' in df.columns:
                                    summary_columns.append('ALC BRAND FAMILY')
                                if 'ITEM' in df.columns:
                                    summary_columns.append('ITEM')
                                elif 'ALC CATEGORY' in df.columns:
                                    summary_columns.append('ALC CATEGORY')
                                
                                if summary_columns:
                                    # Find numeric columns to sum
                                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                                    
                                    # Group and aggregate
                                    df_summary = df.groupby(summary_columns)[numeric_cols].sum().reset_index()
                                    
                                    st.success(f"✅ **Ready!** Summarized {len(df):,} rows → {len(df_summary)} strategic data points")
                                    data_dict = df_summary.to_dict('records')
                                else:
                                    # If no grouping columns, take top 500 rows by dollar sales
                                    dollar_col = [col for col in df.columns if '$' in col or 'sales' in col.lower()]
                                    if dollar_col:
                                        df_top = df.nlargest(500, dollar_col[0])
                                        st.success(f"✅ **Ready!** Analyzing top 500 highest-value items")
                                    else:
                                        df_top = df.head(500)
                                        st.success(f"✅ **Ready!** Analyzing first 500 rows")
                                    data_dict = df_top.to_dict('records')
                            else:
                                # Small dataset, use all data
                                data_dict = df.to_dict('records')
                        else:
                            # Use manual entry
                            data_dict = json.loads(data_input)
                        
                        # Run analysis
                        # Build context about data source
                        source_context = ""
                        if uploaded_file and data_source:
                            source_context = f"\n\nDATA SOURCE: {data_source}\nThis data has been preprocessed and standardized from {data_source} format."
                        
                        analysis = st.session_state.assistant.analyze_market_data(
                            data_dict=data_dict,
                            analysis_focus=(analysis_focus + source_context) if analysis_focus else source_context.strip()
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
                        error_msg = str(e)
                        
                        # Handle rate limit errors
                        if "rate_limit" in error_msg.lower():
                            st.error("Rate limit exceeded. Your dataset is too large.")
                            st.info("💡 **Solutions:**")
                            st.markdown("""
                            1. The data has been automatically summarized, but it's still too large
                            2. Try filtering to specific brands or time periods
                            3. Export a smaller subset of your data
                            4. Wait 60 seconds and try again
                            """)
                        else:
                            st.error(f"Error analyzing data: {error_msg}")
                            st.info("Try using the sample data or check your file format.")
    
    # MODULE 2: CREATIVE BRIEF GENERATOR
    elif module == "✍️ Creative Brief Generator":
        st.header("Creative Brief Generator")
        st.markdown("Generate comprehensive creative briefs for campaigns and projects")
        
        # Instructions
        with st.expander("📖 How to use this tool", expanded=False):
            st.markdown("""
            **What this does:**
            - Generates complete, strategic creative briefs
            - Ensures all key elements are covered
            - Ready to share with agencies or internal teams
            
            **Best practices:**
            - Be specific about objectives and target audience
            - Include key insights if you have them
            - The more detail you provide, the better the brief
            
            **Optional:** Upload your own brief template for customized output
            """)
        
        # Input fields
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.text_input("Campaign Name*", placeholder="e.g., Summer 2025 Launch")
            objective = st.text_area("Campaign Objective*", placeholder="What do you want to achieve?", height=100)
            target_audience = st.text_area("Target Audience*", placeholder="Who are you trying to reach?", height=100)
        
        with col2:
            key_message = st.text_area("Key Message/Insight", placeholder="Main idea or consumer insight", height=100)
            channels = st.text_input("Channels", placeholder="TV, Digital, Social, OOH, etc.")
            budget = st.text_input("Budget (optional)", placeholder="$500K")
        
        timeline = st.text_input("Timeline", placeholder="Launch date, campaign duration")
        
        # Template upload
        template_file = st.file_uploader("Upload Custom Template (optional)", type=['txt', 'docx'])
        
        if st.button("✍️ Generate Brief", type="primary", disabled=not (campaign_name and objective and target_audience)):
            can_use, message = check_usage_limit(st.session_state.user_email)
            
            if not can_use:
                st.error(message)
                st.info("Upgrade your plan to continue")
                if st.button("View Plans"):
                    st.session_state.page = "subscription"
                    st.rerun()
            else:
                with st.spinner("Generating creative brief..."):
                    try:
                        brief = st.session_state.assistant.generate_creative_brief(
                            campaign_name=campaign_name,
                            objective=objective,
                            target_audience=target_audience,
                            key_message=key_message if key_message else None,
                            channels=channels if channels else None,
                            budget=budget if budget else None,
                            timeline=timeline if timeline else None
                        )
                        
                        update_user_usage(st.session_state.user_email)
                        _, remaining = check_usage_limit(st.session_state.user_email)
                        
                        st.markdown("### Your Creative Brief")
                        st.markdown(brief)
                        
                        st.download_button(
                            "📥 Download Brief",
                            brief,
                            file_name=f"{campaign_name.replace(' ', '_')}_brief.txt",
                            mime="text/plain"
                        )
                        
                        st.success(f"Brief generated! {remaining} analyses remaining this month")
                        
                    except Exception as e:
                        st.error(f"Error generating brief: {str(e)}")
    
    # MODULE 3: BRAND POSITIONING
    elif module == "🎨 Brand Positioning":
        st.header("Brand Positioning Workshop")
        st.markdown("Develop comprehensive brand positioning and Brand OS framework")
        
        with st.expander("📖 How to use this tool", expanded=False):
            st.markdown("""
            **What this does:**
            - Creates complete Brand OS (Operating System)
            - Develops positioning statement
            - Defines brand essence, purpose, and values
            
            **Best practices:**
            - Think deeply about your brand's role in consumers' lives
            - Be authentic - positioning should reflect reality
            - Consider your competitive set
            
            **Output:** Complete Brand OS framework ready for team alignment
            """)
        
        # Input fields
        brand_name = st.text_input("Brand Name*", placeholder="e.g., Traveller Whiskey")
        
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.text_input("Category*", placeholder="e.g., Premium Blended Whiskey")
            target = st.text_area("Target Consumer*", placeholder="Who is your brand for?", height=100)
            brand_purpose = st.text_area("Brand Purpose", placeholder="Why does your brand exist?", height=100)
        
        with col2:
            competitive_set = st.text_input("Key Competitors", placeholder="e.g., Jack Daniel's, Jameson")
            unique_benefit = st.text_area("Unique Benefit*", placeholder="What makes you different?", height=100)
            brand_personality = st.text_input("Brand Personality", placeholder="e.g., Adventurous, authentic, bold")
        
        positioning_challenge = st.text_area(
            "Positioning Challenge (optional)",
            placeholder="Any specific positioning questions or challenges?",
            height=80
        )
        
        if st.button("🎨 Develop Positioning", type="primary", disabled=not (brand_name and category and target and unique_benefit)):
            can_use, message = check_usage_limit(st.session_state.user_email)
            
            if not can_use:
                st.error(message)
                st.info("Upgrade your plan to continue")
                if st.button("View Plans"):
                    st.session_state.page = "subscription"
                    st.rerun()
            else:
                with st.spinner("Developing brand positioning..."):
                    try:
                        # Create Brand OS dict
                        brand_os = {
                            "brand_name": brand_name,
                            "category": category,
                            "target": target,
                            "purpose": brand_purpose if brand_purpose else None,
                            "personality": brand_personality if brand_personality else None,
                            "unique_benefit": unique_benefit,
                            "competitors": competitive_set if competitive_set else None
                        }
                        
                        positioning = st.session_state.assistant.develop_brand_positioning(
                            brand_os=brand_os,
                            positioning_challenge=positioning_challenge if positioning_challenge else None
                        )
                        
                        update_user_usage(st.session_state.user_email)
                        _, remaining = check_usage_limit(st.session_state.user_email)
                        
                        st.markdown("### Your Brand Positioning")
                        st.markdown(positioning)
                        
                        st.download_button(
                            "📥 Download Positioning",
                            positioning,
                            file_name=f"{brand_name.replace(' ', '_')}_positioning.txt",
                            mime="text/plain"
                        )
                        
                        st.success(f"Positioning developed! {remaining} analyses remaining this month")
                        
                    except Exception as e:
                        st.error(f"Error developing positioning: {str(e)}")
    
    # MODULE 4: INNOVATION IDEATION
    elif module == "💡 Innovation Ideation":
        st.header("Innovation Ideation & Packaging")
        st.markdown("Generate innovation concepts with packaging descriptions")
        
        with st.expander("📖 How to use this tool", expanded=False):
            st.markdown("""
            **What this does:**
            - Generates 3-5 innovation concepts
            - Includes packaging descriptions
            - Covers renovation, adjacent, and transformational ideas
            
            **Best practices:**
            - Be specific about your innovation challenge
            - Include any constraints (cost, timing, capabilities)
            - Specify innovation type if you have a preference
            
            **Output:** Actionable concepts ready for evaluation
            """)
        
        # Input fields
        category = st.text_input("Category*", placeholder="e.g., Blended Whiskey")
        target = st.text_area("Target Consumer*", placeholder="Who are you innovating for?", height=100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            innovation_brief = st.text_area(
                "Innovation Challenge/Brief*",
                placeholder="What consumer need or opportunity are you addressing?",
                height=150
            )
        
        with col2:
            constraints = st.text_area(
                "Constraints",
                placeholder="Budget, timing, manufacturing capabilities, etc.",
                height=150
            )
        
        # Innovation type selection
        innovation_types = st.multiselect(
            "Innovation Type (optional)",
            ["Renovation", "Adjacent Innovation", "Transformational Innovation"],
            help="Leave blank for mix of all types"
        )
        
        num_concepts = st.slider("Number of Concepts", 3, 5, 3)
        
        if st.button("💡 Generate Innovation Ideas", type="primary", disabled=not (category and target and innovation_brief)):
            can_use, message = check_usage_limit(st.session_state.user_email)
            
            if not can_use:
                st.error(message)
                st.info("Upgrade your plan to continue")
                if st.button("View Plans"):
                    st.session_state.page = "subscription"
                    st.rerun()
            else:
                with st.spinner("Generating innovation concepts..."):
                    try:
                        ideas = st.session_state.assistant.generate_innovation_ideas(
                            category=category,
                            target_consumer=target,
                            innovation_brief=innovation_brief,
                            constraints=constraints if constraints else None,
                            innovation_type=innovation_types if innovation_types else None,
                            num_concepts=num_concepts
                        )
                        
                        update_user_usage(st.session_state.user_email)
                        _, remaining = check_usage_limit(st.session_state.user_email)
                        
                        st.markdown("### Innovation Concepts")
                        st.markdown(ideas)
                        
                        st.download_button(
                            "📥 Download Concepts",
                            ideas,
                            file_name="innovation_concepts.txt",
                            mime="text/plain"
                        )
                        
                        st.success(f"Concepts generated! {remaining} analyses remaining this month")
                        
                    except Exception as e:
                        st.error(f"Error generating ideas: {str(e)}")
    
    # MODULE 5: POWERPOINT DECK GENERATOR
    elif module == "📑 PowerPoint Deck Generator":
        st.header("PowerPoint Deck Generator")
        st.markdown("Generate presentation structures and talking points")
        
        with st.expander("📖 How to use this tool", expanded=False):
            st.markdown("""
            **What this does:**
            - Creates slide-by-slide deck structure
            - Generates headlines and talking points
            - Provides visual recommendations
            - Can export actual .pptx files
            
            **Best practices:**
            - Be specific about your objective and audience
            - Include key messages you want to convey
            - Mention data points or facts to include
            
            **Output:** Complete deck outline ready to build
            """)
        
        # Input fields
        presentation_title = st.text_input("Presentation Title*", placeholder="e.g., Q4 Business Review")
        objective = st.text_area("Objective*", placeholder="What's the goal of this presentation?", height=100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            audience = st.text_input("Audience*", placeholder="e.g., Executive leadership, Board")
            key_messages = st.text_area("Key Messages", placeholder="Main points to communicate", height=100)
        
        with col2:
            data_points = st.text_area("Data/Facts to Include", placeholder="Stats, metrics, findings", height=100)
            num_slides = st.slider("Approximate Slide Count", 5, 20, 10)
        
        if st.button("📑 Generate Deck", type="primary", disabled=not (presentation_title and objective and audience)):
            can_use, message = check_usage_limit(st.session_state.user_email)
            
            if not can_use:
                st.error(message)
                st.info("Upgrade your plan to continue")
                if st.button("View Plans"):
                    st.session_state.page = "subscription"
                    st.rerun()
            else:
                with st.spinner("Generating presentation structure..."):
                    try:
                        deck = st.session_state.assistant.generate_presentation_deck(
                            objective=objective,
                            audience=audience,
                            key_messages=key_messages if key_messages else None,
                            data_points=data_points if data_points else None
                        )
                        
                        update_user_usage(st.session_state.user_email)
                        _, remaining = check_usage_limit(st.session_state.user_email)
                        
                        st.markdown("### Your Presentation Structure")
                        st.markdown(deck)
                        
                        st.download_button(
                            "📥 Download Deck Outline",
                            deck,
                            file_name=f"{presentation_title.replace(' ', '_')}_deck.txt",
                            mime="text/plain"
                        )
                        
                        st.success(f"Deck structure generated! {remaining} analyses remaining this month")
                        
                    except Exception as e:
                        st.error(f"Error generating deck: {str(e)}")
    
    else:
        st.warning("Please select a module from the sidebar")

# ============================================================================
# ADMIN DASHBOARD (Password Protected)
# ============================================================================

def show_admin_page():
    """Admin dashboard for managing users"""
    
    st.title("🔧 Admin Dashboard")
    
    # Simple password protection
    admin_password = st.text_input("Admin Password", type="password")
    
    if admin_password != "admin123":  # Change this!
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
