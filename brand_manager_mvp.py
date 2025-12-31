#!/usr/bin/env python3
"""
Brand Manager AI - Professional SaaS Platform
Complete brand management toolkit with AI-powered insights
"""

import streamlit as st
import sys
from pathlib import Path
import os
import json
from datetime import datetime, timedelta
import hashlib
import io
import base64
import re
from typing import Tuple, Optional, Dict

# File processing imports
try:
    from PyPDF2 import PdfReader
    import docx
    from pptx import Presentation
    from PIL import Image
    import pytesseract
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    # Don't show warning on startup - will show contextually when needed

# Professional page configuration
st.set_page_config(
    page_title="Brand Manager AI - Professional Brand Management Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://support.brandmanager.ai',
        'Report a bug': 'https://support.brandmanager.ai/bug-report',
        'About': '**Brand Manager AI** - Your Complete Brand Management Platform. Save 100+ hours per month with AI-powered tools.'
    }
)

# Professional CSS Styling
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main app background */
    .main {
        background-color: #FFFFFF;
    }
    
    /* Sidebar - Professional gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E3A8A 0%, #2E5CFF 100%);
        padding-top: 1rem;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    /* Professional headers */
    h1 {
        color: #1F2937;
        font-weight: 700;
        font-size: 2.5rem;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #1F2937;
        font-weight: 600;
        font-size: 1.75rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #374151;
        font-weight: 600;
        font-size: 1.25rem;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* Professional alert boxes */
    .stAlert {
        border-radius: 0.75rem;
        border: none;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        padding: 1rem;
    }
    
    .stSuccess {
        background-color: #ECFDF5;
        border-left: 4px solid #10B981;
        color: #065F46;
    }
    
    .stError {
        background-color: #FEF2F2;
        border-left: 4px solid #EF4444;
        color: #991B1B;
    }
    
    .stInfo {
        background-color: #EFF6FF;
        border-left: 4px solid #2E5CFF;
        color: #1E3A8A;
    }
    
    .stWarning {
        background-color: #FFFBEB;
        border-left: 4px solid #F59E0B;
        color: #92400E;
    }
    
    /* Premium buttons */
    .stButton > button {
        border-radius: 0.5rem;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border: none;
        transition: all 0.2s ease;
        letter-spacing: 0.01em;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2E5CFF 0%, #1E3A8A 100%);
        color: white;
        box-shadow: 0 4px 6px -1px rgba(46, 92, 255, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 10px 15px -3px rgba(46, 92, 255, 0.4);
        transform: translateY(-2px);
    }
    
    .stButton > button[kind="primary"]:active {
        transform: translateY(0);
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        border-radius: 0.5rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
        transition: all 0.2s ease;
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.3);
        transform: translateY(-1px);
    }
    
    /* Professional input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border-radius: 0.5rem;
        border: 2px solid #E5E7EB;
        padding: 0.75rem;
        transition: all 0.2s ease;
        font-size: 0.95rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #2E5CFF;
        box-shadow: 0 0 0 3px rgba(46, 92, 255, 0.1);
        outline: none;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #E5E7EB;
        border-radius: 0.75rem;
        padding: 2rem;
        background-color: #F9FAFB;
        transition: all 0.2s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #2E5CFF;
        background-color: #EFF6FF;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2E5CFF;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        color: #6B7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #F9FAFB;
        border-radius: 0.5rem;
        font-weight: 600;
        padding: 1rem;
        border: 1px solid #E5E7EB;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #F3F4F6;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: #F9FAFB;
        padding: 0.5rem;
        border-radius: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        border-radius: 0.375rem;
        font-weight: 600;
        background-color: transparent;
        color: #6B7280;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #F3F4F6;
        color: #374151;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #2E5CFF;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    /* Checkboxes */
    .stCheckbox {
        padding: 0.5rem 0;
    }
    
    .stCheckbox > label {
        font-weight: 500;
        color: #374151;
    }
    
    /* Selectbox */
    .stSelectbox > label {
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #2E5CFF 0%, #10B981 100%);
    }
    
    /* Dataframe */
    .dataframe {
        font-size: 0.875rem;
        border-radius: 0.5rem;
        overflow: hidden;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #2E5CFF;
    }
</style>
""", unsafe_allow_html=True)

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
# FILE PROCESSING UTILITIES
# ============================================================================

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    if not PDF_SUPPORT:
        return "Error: PDF processing not available. Please install PyPDF2 or use TXT files instead."
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def extract_text_from_docx(docx_file):
    """Extract text from Word document"""
    if not PDF_SUPPORT:
        return "Error: Word document processing not available. Please install python-docx or use TXT files instead."
    try:
        doc = docx.Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"

def extract_text_from_pptx(pptx_file):
    """Extract text from PowerPoint presentation"""
    if not PDF_SUPPORT:
        return "Error: PowerPoint processing not available. Please install python-pptx or use TXT files instead."
    try:
        prs = Presentation(pptx_file)
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting PPTX: {str(e)}"

def extract_text_from_image(image_file):
    """Extract text from image using OCR"""
    if not PDF_SUPPORT:
        return "Error: Image OCR not available. Please install pytesseract and Pillow or use TXT files instead."
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"Error extracting image text: {str(e)}"

def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text content"""
    if uploaded_file is None:
        return None
    
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_extension == 'pdf':
            return extract_text_from_pdf(uploaded_file)
        elif file_extension in ['docx', 'doc']:
            return extract_text_from_docx(uploaded_file)
        elif file_extension in ['pptx', 'ppt']:
            return extract_text_from_pptx(uploaded_file)
        elif file_extension in ['png', 'jpg', 'jpeg', 'gif']:
            return extract_text_from_image(uploaded_file)
        elif file_extension == 'txt':
            return uploaded_file.read().decode('utf-8')
        else:
            return f"Unsupported file type: {file_extension}"
    except Exception as e:
        return f"Error processing file: {str(e)}"

def display_file_uploader(module_name, help_text=None):
    """Display file uploader with consistent styling"""
    st.markdown(f"""
        <div style='background: #F9FAFB; 
                    border: 2px dashed #E5E7EB; 
                    border-radius: 0.75rem; 
                    padding: 1.5rem; 
                    margin: 1rem 0;'>
            <div style='color: #374151; font-weight: 600; margin-bottom: 0.5rem;'>
                📎 Upload Reference Files (Optional)
            </div>
            <div style='color: #6B7280; font-size: 0.875rem;'>
                Brand guidelines, past decks, competitive docs, etc. to personalize your output
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if help_text is None:
        help_text = "Upload brand guidelines, past presentations, competitive analysis, or any reference materials to make outputs more specific to your brand."
    
    uploaded_files = st.file_uploader(
        f"Upload reference files for {module_name}",
        type=['pdf', 'docx', 'doc', 'pptx', 'ppt', 'txt', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help=help_text,
        label_visibility="collapsed"
    )
    
    return uploaded_files

def process_reference_files(uploaded_files):
    """Process multiple uploaded files and combine their content"""
    if not uploaded_files:
        return None
    
    all_content = []
    
    with st.spinner(f"Processing {len(uploaded_files)} file(s)..."):
        for uploaded_file in uploaded_files:
            content = process_uploaded_file(uploaded_file)
            if content and not content.startswith("Error"):
                all_content.append(f"--- Content from {uploaded_file.name} ---\n{content}\n")
            else:
                st.warning(f"⚠️ Could not process {uploaded_file.name}: {content}")
    
    if all_content:
        combined_content = "\n".join(all_content)
        st.success(f"✅ Successfully processed {len(all_content)} file(s)")
        
        with st.expander("📄 View extracted content", expanded=False):
            st.text_area("Extracted content", combined_content, height=200, disabled=True)
        
        return combined_content
    else:
        st.error("❌ No content could be extracted from uploaded files")
        return None

# ============================================================================
# SUBSCRIPTION TIERS
# ============================================================================

SUBSCRIPTION_TIERS = {
    "free": {
        "name": "Free Trial",
        "price_monthly": "$0/month",
        "price_annual": "$0/year",
        "analyses_per_month": 5,
        "features": [
            "5 analyses per month",
            "Data Performance Analysis only",
            "Email support"
        ],
        "stripe_link_monthly": None,
        "stripe_link_annual": None
    },
    "pro": {
        "name": "Professional",
        "price_monthly": "$49/month",
        "price_annual": "$470/year",  # 20% discount ($588 → $470)
        "annual_savings": "$118",
        "analyses_per_month": 50,
        "features": [
            "50 analyses per month",
            "All 7 modules",
            "Priority support",
            "Gamma.ai presentation prompts",
            "Download outputs"
        ],
        "stripe_link_monthly": "https://buy.stripe.com/test_your_monthly_link",
        "stripe_link_annual": "https://buy.stripe.com/test_your_annual_link"
    },
    "team": {
        "name": "Team",
        "price_monthly": "$149/month",
        "price_annual": "$1,430/year",  # 20% discount ($1,788 → $1,430)
        "annual_savings": "$358",
        "analyses_per_month": 200,
        "features": [
            "200 analyses per month",
            "All 7 modules",
            "5 user seats",
            "Shared templates",
            "Priority support",
            "Team collaboration"
        ],
        "stripe_link_monthly": "https://buy.stripe.com/test_your_monthly_link",
        "stripe_link_annual": "https://buy.stripe.com/test_your_annual_link"
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
    """Professional modern login page inspired by Stripe, Auth0, Notion"""
    
    # Hide Streamlit default elements
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Center container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo and branding
        st.markdown("""
            <div style='text-align: center; margin-bottom: 3rem; margin-top: 3rem;'>
                <div style='font-size: 4rem; margin-bottom: 1rem;'>🎯</div>
                <h1 style='color: white; 
                          font-size: 2.5rem; 
                          font-weight: 800; 
                          margin: 0;
                          text-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    Brand Manager AI
                </h1>
                <p style='color: rgba(255,255,255,0.9); 
                         font-size: 1.125rem; 
                         margin-top: 0.5rem;
                         font-weight: 500;'>
                    AI-Powered Brand Management Suite
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Auth card container
        st.markdown("""
            <div style='background: white; 
                       border-radius: 1.5rem; 
                       padding: 3rem 2.5rem; 
                       box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
                       margin-bottom: 2rem;'>
        """, unsafe_allow_html=True)
        
        # Tabs
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.markdown("""
                <h2 style='color: #1F2937; 
                          font-size: 1.75rem; 
                          font-weight: 700; 
                          margin-bottom: 1.5rem;
                          text-align: center;'>
                    Welcome back
                </h2>
            """, unsafe_allow_html=True)
            
            login_email = st.text_input(
                "Email address",
                key="login_email",
                placeholder="you@company.com"
            )
            login_password = st.text_input(
                "Password",
                type="password",
                key="login_password",
                placeholder="••••••••"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Sign in to your account", type="primary", use_container_width=True):
                if verify_user(login_email, login_password):
                    st.session_state.authenticated = True
                    st.session_state.user_email = login_email
                    st.session_state.page = "landing"
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password")
            
            st.markdown("""
                <div style='text-align: center; 
                           margin-top: 1.5rem; 
                           color: #6B7280; 
                           font-size: 0.875rem;'>
                    Don't have an account? Switch to <strong>Sign Up</strong> tab above
                </div>
            """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown("""
                <h2 style='color: #1F2937; 
                          font-size: 1.75rem; 
                          font-weight: 700; 
                          margin-bottom: 0.5rem;
                          text-align: center;'>
                    Create your account
                </h2>
                <p style='text-align: center; 
                         color: #6B7280; 
                         margin-bottom: 1.5rem;
                         font-size: 0.95rem;'>
                    Start with 5 free analyses per month
                </p>
            """, unsafe_allow_html=True)
            
            signup_email = st.text_input(
                "Email address",
                key="signup_email",
                placeholder="you@company.com"
            )
            signup_password = st.text_input(
                "Password",
                type="password",
                key="signup_password",
                placeholder="••••••••",
                help="Minimum 6 characters"
            )
            signup_password2 = st.text_input(
                "Confirm password",
                type="password",
                key="signup_password2",
                placeholder="••••••••"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Create account", type="primary", use_container_width=True):
                if not signup_email or not signup_password:
                    st.error("❌ Please fill in all fields")
                elif signup_password != signup_password2:
                    st.error("❌ Passwords don't match")
                elif len(signup_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    success, message = create_user(signup_email, signup_password)
                    if success:
                        st.success("✅ Account created! Please switch to Login tab")
                    else:
                        st.error(f"❌ {message}")
            
            st.markdown("""
                <div style='text-align: center; 
                           margin-top: 1.5rem; 
                           color: #6B7280; 
                           font-size: 0.875rem;'>
                    By signing up, you agree to our Terms of Service
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Features showcase below card
        st.markdown("""
            <div style='background: rgba(255,255,255,0.95); 
                       border-radius: 1rem; 
                       padding: 2rem; 
                       margin-bottom: 2rem;'>
                <h3 style='color: #1F2937; 
                          text-align: center; 
                          margin-bottom: 1.5rem;
                          font-size: 1.25rem;
                          font-weight: 700;'>
                    Why Brand Manager AI?
                </h3>
                <div style='display: grid; 
                           grid-template-columns: repeat(2, 1fr); 
                           gap: 1.5rem;'>
                    <div>
                        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>⚡</div>
                        <div style='color: #1F2937; font-weight: 600; margin-bottom: 0.25rem;'>Save 100+ Hours/Month</div>
                        <div style='color: #6B7280; font-size: 0.875rem;'>Automate day-to-day tasks</div>
                    </div>
                    <div>
                        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🎯</div>
                        <div style='color: #1F2937; font-weight: 600; margin-bottom: 0.25rem;'>7 AI-Powered Tools</div>
                        <div style='color: #6B7280; font-size: 0.875rem;'>Complete brand management</div>
                    </div>
                    <div>
                        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>📊</div>
                        <div style='color: #1F2937; font-weight: 600; margin-bottom: 0.25rem;'>Nielsen, IRI, Circana</div>
                        <div style='color: #6B7280; font-size: 0.875rem;'>Auto-detect syndicated data</div>
                    </div>
                    <div>
                        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>💰</div>
                        <div style='color: #1F2937; font-weight: 600; margin-bottom: 0.25rem;'>204x ROI</div>
                        <div style='color: #6B7280; font-size: 0.875rem;'>$120K-$668K annual value</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
            <div style='text-align: center; 
                       color: rgba(255,255,255,0.8); 
                       font-size: 0.875rem;
                       margin-bottom: 2rem;'>
                Powered by Claude Sonnet 4.5 • Enterprise-grade security
            </div>
        """, unsafe_allow_html=True)

# ============================================================================
# LANDING PAGE UI
# ============================================================================

def show_landing_page():
    """Professional dark-themed landing page"""
    
    # Dark background
    st.markdown("""
        <style>
        .stApp {background-color: #0F172A !important;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
    # Hero
    st.markdown("""
        <div style='max-width: 1200px; margin: 0 auto; padding: 5rem 2rem 3rem 2rem; text-align: center;'>
            <h1 style='font-size: 4rem; font-weight: 900; color: white; margin-bottom: 1.5rem;'>Save 100+ Hours Every Month</h1>
            <p style='font-size: 1.5rem; color: #CBD5E1; max-width: 800px; margin: 0 auto 2.5rem auto;'>From Nielsen data analysis to competitive intelligence, <strong style='color: white;'>automate your day-to-day brand management</strong></p>
            <div style='display: flex; gap: 2rem; justify-content: center; flex-wrap: wrap; margin-bottom: 3rem;'>
                <div><div style='font-size: 2.5rem; font-weight: 800; color: #3B82F6;'>$120K+</div><div style='color: #94A3B8; font-size: 0.875rem;'>Annual Value</div></div>
                <div><div style='font-size: 2.5rem; font-weight: 800; color: #10B981;'>100+</div><div style='color: #94A3B8; font-size: 0.875rem;'>Hours Saved</div></div>
                <div><div style='font-size: 2.5rem; font-weight: 800; color: #F59E0B;'>204x</div><div style='color: #94A3B8; font-size: 0.875rem;'>ROI</div></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Trust Indicators
    st.markdown("""
        <div style='background: #1E293B; padding: 2rem; margin-bottom: 4rem;'>
            <div style='max-width: 1200px; margin: 0 auto; text-align: center;'>
                <div style='color: #94A3B8; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 1.5rem;'>POWERED BY INDUSTRY-LEADING AI</div>
                <div style='display: flex; justify-content: center; gap: 3rem; flex-wrap: wrap;'>
                    <div style='color: white;'>🤖 Claude Sonnet 4.5</div>
                    <div style='color: white;'>🔍 Real-Time Search</div>
                    <div style='color: white;'>📊 Nielsen • IRI</div>
                    <div style='color: white;'>🎨 Gamma.ai</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Section Header
    st.markdown("""
        <div style='max-width: 1200px; margin: 0 auto 3rem auto; padding: 0 2rem; text-align: center;'>
            <h2 style='font-size: 2.75rem; font-weight: 800; color: white; margin-bottom: 1rem;'>7 Modules. Unlimited Possibilities.</h2>
            <p style='font-size: 1.25rem; color: #CBD5E1;'>Every tool you need, powered by AI</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Module Cards
    modules = [
        ("📊", "Data Performance Analysis", "30-65 min", "$18K-52K", "#3B82F6", 
         ["Auto-detects Nielsen/IRI/Circana", "Executive summaries", "YOY trends", "Competitive gaps"]),
        ("✍️", "Creative Brief Generator", "45-90 min", "$20K-54K", "#F59E0B",
         ["Strategic briefs", "Brand alignment", "Audience insights", "Success metrics"]),
        ("🎨", "Brand Positioning", "2-4 hours", "$9K-24K", "#EC4899",
         ["Brand OS frameworks", "Pressure-test vs competitors", "Value propositions", "Internal consistency"]),
        ("💡", "Innovation Ideation", "3-6 hours", "$13K-36K", "#10B981",
         ["3-5 innovation concepts", "Consumer trends", "GTM strategies", "Feasibility assessments"]),
        ("📑", "Presentation Builder", "60-120 min", "$27K-72K", "#8B5CF6",
         ["Gamma.ai prompts", "Executive narratives", "Data viz", "Talking points"]),
        ("🔍", "Competitive Intelligence", "90-180 min", "$20K-54K", "#EF4444",
         ["Latest campaigns", "Cited sources", "Media spend", "Counter-strategies"]),
        ("⭐", "Creative Quality Review", "45-90 min", "$13K-36K", "#F97316",
         ["Brand standards", "Message clarity", "Recommendations", "Optimizations"])
    ]
    
    for i in range(0, len(modules), 2):
        cols = st.columns(2, gap="large")
        for j in range(2):
            if i + j < len(modules):
                icon, name, time, value, color, caps = modules[i + j]
                with cols[j]:
                    st.markdown(f"""
                        <div style='background: #1E293B; border: 2px solid {color}; border-radius: 1rem; padding: 2rem; margin-bottom: 2rem;'>
                            <div style='font-size: 3rem; margin-bottom: 1rem;'>{icon}</div>
                            <h3 style='color: white; font-size: 1.35rem; font-weight: 700; margin-bottom: 1rem;'>{name}</h3>
                            <div style='background: rgba(255,255,255,0.05); border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem;'>
                                <div style='color: {color}; font-weight: 700; margin-bottom: 0.25rem;'>⏱️ {time}</div>
                                <div style='color: {color}; font-weight: 800; font-size: 1.1rem;'>📈 {value}/year</div>
                            </div>
                            <div style='color: #CBD5E1; font-size: 0.7rem; margin-bottom: 0.5rem; text-transform: uppercase;'>KEY CAPABILITIES</div>
                            <ul style='margin: 0; padding-left: 1.25rem; color: #94A3B8; font-size: 0.85rem;'>
                                {"".join([f"<li style='margin-bottom: 0.35rem;'>{cap}</li>" for cap in caps])}
                            </ul>
                        </div>
                    """, unsafe_allow_html=True)
    
    # ROI Section
    st.markdown("""
        <div style='max-width: 1000px; margin: 4rem auto; padding: 0 2rem;'>
            <div style='background: linear-gradient(135deg, #1E3A8A, #1E40AF); border-radius: 1.5rem; padding: 4rem 3rem; text-align: center;'>
                <h2 style='color: white; font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem;'>Total Annual Value</h2>
                <div style='color: rgba(255,255,255,0.9); margin-bottom: 2rem;'>Industry-standard brand manager rates</div>
                <div style='background: rgba(255,255,255,0.1); border: 2px solid rgba(255,255,255,0.3); border-radius: 1rem; padding: 2rem 3rem; display: inline-block; margin-bottom: 2rem;'>
                    <div style='color: #FCD34D; font-size: 3.5rem; font-weight: 900;'>$120K - $668K</div>
                    <div style='color: white; font-size: 1.125rem;'>in value generated annually</div>
                </div>
                <div style='color: rgba(255,255,255,0.7); font-style: italic;'>Focus on strategy. Let AI handle spreadsheets.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # CTA
    st.markdown("""
        <div style='max-width: 800px; margin: 3rem auto; padding: 0 2rem; text-align: center;'>
            <h2 style='color: white; font-size: 2.75rem; font-weight: 800; margin-bottom: 1rem;'>Ready to 10x Your Productivity?</h2>
            <p style='color: #CBD5E1; font-size: 1.25rem; margin-bottom: 2rem;'>Start with <strong style='color: white;'>Free</strong> (5 analyses/month) or unlock all 7 with <strong style='color: white;'>Pro</strong></p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        ca, cb = st.columns(2, gap="medium")
        with ca:
            if st.button("🚀 View Pricing", type="primary", use_container_width=True):
                st.session_state.page = "subscription"
                st.rerun()
        with cb:
            if st.button("📊 Start Analyzing", use_container_width=True):
                st.session_state.page = "main"
                st.rerun()
        st.markdown("<div style='text-align: center; margin-top: 1.5rem; color: #94A3B8; font-size: 0.875rem;'>💳 No credit card • 🔒 Enterprise security</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <div style='background: #1E293B; margin-top: 5rem; padding: 3rem 2rem;'>
            <div style='max-width: 1200px; margin: 0 auto; text-align: center;'>
                <div style='color: white; font-weight: 700; margin-bottom: 1rem;'>🎯 Brand Manager AI</div>
                <div style='color: #94A3B8; font-size: 0.875rem;'>© 2025 Brand Manager AI • Powered by Claude Sonnet 4.5</div>
            </div>
        </div>
    """, unsafe_allow_html=True)



# ============================================================================
# SUBSCRIPTION MANAGEMENT UI
# ============================================================================

def show_subscription_page():
    """Professional subscription management page with monthly/annual pricing"""
    
    user = get_user(st.session_state.user_email)
    current_tier = user["tier"]
    
    # Professional Header
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='color: #1F2937; margin-bottom: 0.5rem;'>Choose Your Plan</h1>
            <p style='color: #6B7280; font-size: 1.25rem; font-weight: 500;'>
                Save 100+ hours per month with AI-powered brand management
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Billing Toggle
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        billing_period = st.radio(
            "Billing Period",
            ["Monthly", "Annual (Save 20%)"],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    is_annual = "Annual" in billing_period
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Current plan info
    tier_info = SUBSCRIPTION_TIERS[current_tier]
    remaining = tier_info["analyses_per_month"] - user["usage"]["analyses_used"]
    
    current_price = tier_info["price_annual"] if is_annual else tier_info["price_monthly"]
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info(f"**Current Plan:** {tier_info['name']} | **{remaining}** of **{tier_info['analyses_per_month']}** analyses remaining")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Professional Pricing Cards
    cols = st.columns(3)
    
    tier_keys = list(SUBSCRIPTION_TIERS.keys())
    
    for idx, tier_key in enumerate(tier_keys):
        tier_data = SUBSCRIPTION_TIERS[tier_key]
        with cols[idx]:
            is_pro = tier_key == "pro"
            is_current = tier_key == current_tier
            
            # Card container with conditional styling
            if is_pro:
                st.markdown("""
                    <div style='text-align: center; background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); 
                                color: white; padding: 0.375rem; border-radius: 0.5rem 0.5rem 0 0; 
                                font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;'>
                        ⭐ MOST POPULAR
                    </div>
                """, unsafe_allow_html=True)
            
            # Card styling
            border_style = "3px solid #2E5CFF" if is_pro else "2px solid #E5E7EB"
            shadow = "0 10px 25px -5px rgba(46, 92, 255, 0.2)" if is_pro else "0 1px 3px 0 rgba(0, 0, 0, 0.1)"
            
            st.markdown(f"""
                <div style='background: white; border: {border_style}; border-radius: {"0 0 1rem 1rem" if is_pro else "1rem"}; 
                            padding: 2rem 1.5rem; box-shadow: {shadow}; min-height: 450px;'>
            """, unsafe_allow_html=True)
            
            # Plan name
            st.markdown(f"""
                <h3 style='text-align: center; color: #1F2937; margin-bottom: 1rem; font-size: 1.5rem; font-weight: 700;'>
                    {tier_data["name"]}
                </h3>
            """, unsafe_allow_html=True)
            
            # Price
            if is_annual:
                price_val = tier_data["price_annual"].split('/')[0]
                period = "year"
                # Show monthly equivalent and savings
                if "annual_savings" in tier_data:
                    monthly_equiv = int(price_val.replace('$', '').replace(',', '')) / 12
                    st.markdown(f"""
                        <div style='text-align: center; margin-bottom: 0.5rem;'>
                            <span style='font-size: 2.5rem; font-weight: 700; color: #2E5CFF;'>{price_val}</span>
                            <span style='font-size: 1rem; color: #6B7280; font-weight: 500;'>/{period}</span>
                        </div>
                        <div style='text-align: center; margin-bottom: 1rem;'>
                            <span style='font-size: 0.875rem; color: #6B7280;'>${monthly_equiv:.0f}/month</span>
                        </div>
                        <div style='text-align: center; background: #ECFDF5; color: #059669; padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                            <span style='font-weight: 600; font-size: 0.875rem;'>💰 Save {tier_data["annual_savings"]}/year</span>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style='text-align: center; margin-bottom: 1.5rem;'>
                            <span style='font-size: 2.5rem; font-weight: 700; color: #2E5CFF;'>{price_val}</span>
                            <span style='font-size: 1rem; color: #6B7280; font-weight: 500;'>/{period}</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                price_val = tier_data["price_monthly"].split('/')[0]
                period = "mo"
                st.markdown(f"""
                    <div style='text-align: center; margin-bottom: 1.5rem;'>
                        <span style='font-size: 3rem; font-weight: 700; color: #2E5CFF;'>{price_val}</span>
                        <span style='font-size: 1.125rem; color: #6B7280; font-weight: 500;'>/{period}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            # Features
            st.markdown("<div style='margin-bottom: 2rem;'>", unsafe_allow_html=True)
            for feature in tier_data["features"]:
                st.markdown(f"""
                    <div style='padding: 0.5rem 0; color: #374151;'>
                        <span style='color: #10B981; font-weight: bold; margin-right: 0.5rem;'>✓</span>
                        {feature}
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Action button (outside the card)
            st.markdown("<div style='margin-top: 1rem;'>", unsafe_allow_html=True)
            if is_current:
                st.success("✓ Current Plan", icon="✅")
            else:
                stripe_link = tier_data["stripe_link_annual"] if is_annual else tier_data["stripe_link_monthly"]
                if stripe_link:
                    button_label = f"Upgrade to {tier_data['name']}" if tier_key != "free" else "Current Plan"
                    period_label = "Annual" if is_annual else "Monthly"
                    if st.button(f"{button_label} ({period_label})", key=f"upgrade_{tier_key}_{period_label}", use_container_width=True, type="primary" if is_pro else "secondary"):
                        st.info(f"🔗 Complete your {period_label.lower()} upgrade")
                        st.markdown(f"[Click here to pay on Stripe]({stripe_link})")
                        st.caption("After payment, email your receipt to upgrade@brandmanagerai.com and we'll upgrade your account within 24 hours.")
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Value Proposition Section
    st.markdown("<div style='margin-top: 4rem;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='color: #1F2937;'>Why Brand Manager AI?</h2>
            <p style='color: #6B7280; font-size: 1.125rem;'>
                The complete toolkit professional brand managers trust
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style='text-align: center; padding: 1.5rem;'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>⚡</div>
                <h3 style='color: #1F2937; font-size: 1.25rem; margin-bottom: 0.5rem;'>Save 100+ Hours</h3>
                <p style='color: #6B7280; font-size: 0.95rem;'>
                    Automate data analysis, brief writing, and strategic planning
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='text-align: center; padding: 1.5rem;'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>🎯</div>
                <h3 style='color: #1F2937; font-size: 1.25rem; margin-bottom: 0.5rem;'>7 AI Tools</h3>
                <p style='color: #6B7280; font-size: 0.95rem;'>
                    Everything from data analysis to creative testing in one platform
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style='text-align: center; padding: 1.5rem;'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>💰</div>
                <h3 style='color: #1F2937; font-size: 1.25rem; margin-bottom: 0.5rem;'>204x ROI</h3>
                <p style='color: #6B7280; font-size: 0.95rem;'>
                    $120K+ annual value for just $470/year
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Back button
    st.markdown("<div style='margin-top: 3rem; text-align: center;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()

# ============================================================================
# MAIN APP (with authentication)
# ============================================================================

def main_app():
    """Main application with all modules"""
    
    # Initialize session state
    if 'assistant' not in st.session_state:
        st.session_state.assistant = BrandManagerAssistant(api_key=api_key)
    
    user = get_user(st.session_state.user_email)
    
    # Professional Sidebar with Branding
    with st.sidebar:
        # Logo and Brand Header
        st.markdown("""
            <div style='text-align: center; padding: 0.5rem 0 1.5rem 0;'>
                <h1 style='color: white; font-size: 1.75rem; margin: 0; font-weight: 700;'>
                    🎯 Brand Manager AI
                </h1>
                <p style='color: rgba(255,255,255,0.8); font-size: 0.875rem; margin-top: 0.5rem; font-weight: 500;'>
                    Professional Brand Management Platform
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User Profile Card
        tier_info = SUBSCRIPTION_TIERS[user["tier"]]
        tier_colors = {
            "free": "#6B7280",
            "pro": "#F59E0B",
            "team": "#8B5CF6"
        }
        tier_color = tier_colors.get(user["tier"], "#6B7280")
        
        st.markdown(f"""
            <div style='background: rgba(255,255,255,0.1); 
                        border-radius: 0.75rem; 
                        padding: 1rem; 
                        margin-bottom: 1.5rem;
                        border: 1px solid rgba(255,255,255,0.2);'>
                <div style='color: rgba(255,255,255,0.9); 
                           font-size: 0.875rem;
                           margin-bottom: 0.5rem;
                           font-weight: 500;'>
                    {st.session_state.user_email}
                </div>
                <div style='margin-top: 0.75rem;'>
                    <span style='background: {tier_color}; 
                                color: white; 
                                padding: 0.375rem 0.875rem; 
                                border-radius: 1rem; 
                                font-size: 0.75rem; 
                                font-weight: 700; 
                                text-transform: uppercase;
                                letter-spacing: 0.05em;'>
                        {tier_info["name"]}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Usage Meter with Progress Bar
        remaining = tier_info["analyses_per_month"] - user["usage"]["analyses_used"]
        usage_percent = (user["usage"]["analyses_used"] / tier_info["analyses_per_month"]) * 100
        
        st.markdown(f"""
            <div style='margin-bottom: 1.5rem;'>
                <div style='color: rgba(255,255,255,0.9); 
                           font-size: 0.75rem; 
                           margin-bottom: 0.5rem;
                           text-transform: uppercase;
                           letter-spacing: 0.05em;
                           font-weight: 600;'>
                    Usage This Month
                </div>
                <div style='color: white; 
                           font-size: 1.75rem; 
                           font-weight: 700;
                           margin-bottom: 0.5rem;'>
                    {user["usage"]["analyses_used"]} <span style='font-size: 1rem; font-weight: 500; color: rgba(255,255,255,0.7);'>/ {tier_info["analyses_per_month"]}</span>
                </div>
                <div style='background: rgba(255,255,255,0.2); 
                           height: 8px; 
                           border-radius: 4px; 
                           overflow: hidden;'>
                    <div style='background: {"#10B981" if usage_percent < 80 else "#F59E0B" if usage_percent < 95 else "#EF4444"}; 
                               height: 100%; 
                               width: {min(usage_percent, 100)}%; 
                               transition: width 0.3s ease;
                               border-radius: 4px;'>
                    </div>
                </div>
                <div style='color: rgba(255,255,255,0.8); 
                           font-size: 0.875rem; 
                           margin-top: 0.5rem;
                           font-weight: 500;'>
                    {remaining} analyses remaining
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Low usage warning
        if remaining <= 5 and remaining > 0:
            st.warning("⚠️ Running low on analyses!")
            if st.button("⬆️ Upgrade Now", use_container_width=True):
                st.session_state.page = "subscription"
                st.rerun()
        elif remaining <= 0:
            st.error("❌ No analyses remaining")
            if st.button("⬆️ Upgrade to Continue", use_container_width=True, type="primary"):
                st.session_state.page = "subscription"
                st.rerun()
        
        st.markdown("---")
        
        # Module Selection (Professional Styling)
        st.markdown("""
            <div style='color: rgba(255,255,255,0.9); 
                       font-size: 0.75rem; 
                       margin-bottom: 0.75rem;
                       text-transform: uppercase;
                       letter-spacing: 0.05em;
                       font-weight: 600;'>
                Select Your Tool
            </div>
        """, unsafe_allow_html=True)
        
        if user["tier"] == "free":
            module = "📊 Data Performance Analysis"
            st.info("🔒 Upgrade to unlock all 7 modules")
        else:
            module = st.selectbox(
                "Module",
                [
                    "📊 Data Performance Analysis",
                    "✍️ Creative Brief Generator",
                    "🎨 Brand Positioning",
                    "💡 Innovation Ideation",
                    "📑 PowerPoint Deck Generator",
                    "🔍 Competitive Intelligence",
                    "⭐ Creative Quality Review"
                ],
                label_visibility="collapsed"
            )
        
        st.markdown("---")
        
        # Navigation Buttons (Professional Styling)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.page = "landing"
                st.rerun()
        with col2:
            if st.button("💳 Plans", use_container_width=True):
                st.session_state.page = "subscription"
                st.rerun()
        with col3:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_email = None
                st.rerun()
        
        # Footer
        st.markdown("""
            <div style='margin-top: 2rem; 
                       padding-top: 1rem; 
                       border-top: 1px solid rgba(255,255,255,0.2);
                       text-align: center;'>
                <div style='color: rgba(255,255,255,0.6); 
                           font-size: 0.75rem;'>
                    © 2024 Brand Manager AI
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Show landing page if selected
    if st.session_state.get("page") == "landing":
        show_landing_page()
        return
    
    # Show subscription page if selected
    if st.session_state.get("page") == "subscription":
        show_subscription_page()
        return
    
    # Professional Welcome Header
    st.markdown("""
        <div style='background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); 
                    border-radius: 1rem; 
                    padding: 2.5rem 2rem; 
                    margin-bottom: 2rem;
                    border: 1px solid #BFDBFE;'>
            <h1 style='color: #1E3A8A; margin: 0; font-size: 2.25rem;'>
                Welcome to Brand Manager AI
            </h1>
            <p style='color: #1E40AF; 
                     font-size: 1.125rem; 
                     margin-top: 0.75rem;
                     margin-bottom: 0;
                     font-weight: 500;'>
                Save 100+ hours per month with AI-powered brand management tools
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # ============================================================================
    # SYNDICATED DATA SOURCE HANDLERS
    # ============================================================================
    
    def detect_data_source(df: 'pd.DataFrame') -> Tuple[Optional[str], float]:
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
    
    def clean_numeric_column(series: 'pd.Series') -> 'pd.Series':
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
    
    def standardize_column_names(df: 'pd.DataFrame', source: str) -> 'pd.DataFrame':
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
    
    def preprocess_syndicated_data(df: 'pd.DataFrame', source: str) -> 'pd.DataFrame':
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
            if 'geography' in df.columns:
                df = df[df['geography'].notna()]
                df = df[~df['geography'].str.contains('total', case=False, na=False)]
        
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
        
        # Reference file uploads
        st.markdown("---")
        uploaded_ref_files = display_file_uploader(
            "Data Performance Analysis",
            help_text="Upload brand guidelines, past performance reports, strategic priorities, or any reference materials to align the analysis with your brand context"
        )
        
        # Validate we have data before showing analyze button
        has_data = (uploaded_file and df is not None) or data_input.strip()
        
        if not has_data:
            st.warning("Please upload a file or enter data in the Manual Entry tab")
        
        # AI prompt generation option
        generate_ai_prompt = st.checkbox(
            "📋 Also generate presentation prompt",
            value=True,
            help="Creates Gamma.ai/Beautiful.ai prompt for instant business review deck"
        )
        
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
                                    
                                    # If still too large after grouping, take top entries
                                    if len(df_summary) > 150:
                                        # Find dollar column for sorting
                                        dollar_col = [col for col in df_summary.columns if '$' in col or 'sales' in col.lower()]
                                        if dollar_col:
                                            df_summary = df_summary.nlargest(150, dollar_col[0])
                                        else:
                                            df_summary = df_summary.head(150)
                                        st.success(f"✅ **Ready!** Summarized {len(df):,} rows → Top 150 brands/products by value")
                                        if len(df) > 5000:
                                            st.warning("⚠️ **Very large dataset:** Presentation prompt disabled to ensure fast processing. Analysis will still be comprehensive!")
                                    else:
                                        st.success(f"✅ **Ready!** Summarized {len(df):,} rows → {len(df_summary)} strategic data points")
                                    
                                    data_dict = df_summary.to_dict('records')
                                else:
                                    # If no grouping columns, take top 150 rows by dollar sales
                                    dollar_col = [col for col in df.columns if '$' in col or 'sales' in col.lower()]
                                    if dollar_col:
                                        df_top = df.nlargest(150, dollar_col[0])
                                        st.success(f"✅ **Ready!** Analyzing top 150 highest-value items")
                                    else:
                                        df_top = df.head(150)
                                        st.success(f"✅ **Ready!** Analyzing first 150 rows")
                                    
                                    if len(df) > 5000:
                                        st.warning("⚠️ **Very large dataset:** Presentation prompt disabled to ensure fast processing. Analysis will still be comprehensive!")
                                    
                                    data_dict = df_top.to_dict('records')
                            else:
                                # Small dataset, use all data
                                data_dict = df.to_dict('records')
                        else:
                            # Use manual entry
                            data_dict = json.loads(data_input)
                        
                        # Process reference files if uploaded
                        reference_context = None
                        if uploaded_ref_files:
                            reference_context = process_reference_files(uploaded_ref_files)
                        
                        # Build context about data source
                        source_context = ""
                        if uploaded_file and data_source:
                            source_context = f"\n\nDATA SOURCE: {data_source}\nThis data has been preprocessed and standardized from {data_source} format."
                        
                        # Combine analysis focus with source context
                        enhanced_focus = analysis_focus if analysis_focus else ""
                        if source_context:
                            enhanced_focus = (enhanced_focus + source_context) if enhanced_focus else source_context.strip()
                        
                        # Run analysis
                        analysis = st.session_state.assistant.analyze_market_data(
                            data_dict=data_dict,
                            analysis_focus=enhanced_focus if enhanced_focus else None,
                            reference_context=reference_context
                        )
                        
                        # Generate specific Gamma prompt if requested
                        gamma_prompt = None
                        if generate_ai_prompt:
                            with st.spinner("Generating specific Gamma.ai prompt based on analysis..."):
                                gamma_prompt = st.session_state.assistant.generate_gamma_prompt(
                                    analysis_content=analysis,
                                    deck_type="competitive_intelligence"  # Using same template for now
                                )
                        
                        # Update usage
                        update_user_usage(st.session_state.user_email)
                        
                        # Get updated remaining count
                        _, remaining = check_usage_limit(st.session_state.user_email)
                        
                        st.markdown("### Analysis Results")
                        st.markdown(analysis)
                        
                        # Show Gamma prompt if generated
                        if gamma_prompt:
                            st.markdown("---")
                            st.markdown("### 🎨 Gamma.ai Presentation Prompt")
                            st.info("Copy this prompt and paste it into Gamma.ai to create your performance review deck")
                            st.text_area(
                                "Gamma.ai Prompt",
                                gamma_prompt,
                                height=300,
                                label_visibility="collapsed"
                            )
                            st.download_button(
                                "📥 Download Gamma Prompt",
                                gamma_prompt,
                                file_name="performance_analysis_gamma_prompt.txt",
                                mime="text/plain"
                            )
                        
                        # Download button for analysis
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
        
        # Reference file uploads
        st.markdown("---")
        uploaded_ref_files = display_file_uploader(
            "Creative Brief Generator",
            help_text="Upload brand guidelines, past creative briefs, successful campaign examples, or tone of voice documents to personalize your brief"
        )
        
        # AI prompt generation option
        generate_ai_prompt = st.checkbox(
            "📋 Also generate presentation prompt",
            value=True,
            help="Creates Gamma.ai/Beautiful.ai prompt for campaign brief deck"
        )
        
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
                        # Build brief inputs dictionary
                        brief_inputs = {
                            "campaign_name": campaign_name,
                            "objective": objective,
                            "target_audience": target_audience
                        }
                        
                        # Add optional fields if provided
                        if key_message:
                            brief_inputs["key_message"] = key_message
                        if channels:
                            brief_inputs["channels"] = channels
                        if budget:
                            brief_inputs["budget"] = budget
                        if timeline:
                            brief_inputs["timeline"] = timeline
                        
                        # Process reference files if uploaded
                        reference_context = None
                        if uploaded_ref_files:
                            reference_context = process_reference_files(uploaded_ref_files)
                        
                        brief = st.session_state.assistant.generate_creative_brief(
                            brief_inputs=brief_inputs,
                            generate_ai_prompt=generate_ai_prompt,
                            reference_context=reference_context
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
        
        # Reference file uploads
        st.markdown("---")
        uploaded_ref_files = display_file_uploader(
            "Brand Positioning",
            help_text="Upload current positioning documents, competitive positioning maps, brand architecture, or customer research to inform your positioning strategy"
        )
        
        # AI prompt generation option
        generate_ai_prompt = st.checkbox(
            "📋 Also generate presentation prompt",
            value=True,
            help="Creates Gamma.ai/Beautiful.ai prompt for brand strategy deck"
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
                        brand_os_inputs = {
                            "brand_name": brand_name,
                            "category": category,
                            "target": target,
                            "purpose": brand_purpose if brand_purpose else None,
                            "personality": brand_personality if brand_personality else None,
                            "unique_benefit": unique_benefit,
                            "competitors": competitive_set if competitive_set else None
                        }
                        
                        # Process reference files if uploaded
                        reference_context = None
                        if uploaded_ref_files:
                            reference_context = process_reference_files(uploaded_ref_files)
                        
                        positioning = st.session_state.assistant.develop_brand_positioning(
                            brand_os_inputs=brand_os_inputs,
                            positioning_challenge=positioning_challenge if positioning_challenge else None,
                            generate_ai_prompt=generate_ai_prompt,
                            reference_context=reference_context
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
        
        # Reference file uploads
        st.markdown("---")
        uploaded_ref_files = display_file_uploader(
            "Innovation Ideation",
            help_text="Upload innovation pipeline documents, past product launches, R&D priorities, or category trend reports to inform your ideation"
        )
        
        # AI prompt generation option
        generate_ai_prompt = st.checkbox(
            "📋 Also generate presentation prompt",
            value=True,
            help="Creates Gamma.ai/Beautiful.ai prompt for innovation deck"
        )
        
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
                        # Build innovation brief with all details
                        full_brief = innovation_brief
                        
                        if innovation_types:
                            types_text = ", ".join(innovation_types)
                            full_brief += f"\n\nInnovation Types: Generate {num_concepts} concepts across these types: {types_text}"
                        else:
                            full_brief += f"\n\nGenerate {num_concepts} concepts across the innovation spectrum (renovation, adjacent, transformational)."
                        
                        # Process reference files if uploaded
                        reference_context = None
                        if uploaded_ref_files:
                            reference_context = process_reference_files(uploaded_ref_files)
                        
                        ideas = st.session_state.assistant.generate_innovation_ideas(
                            innovation_brief=full_brief,
                            category=category,
                            target=target,
                            constraints=constraints if constraints else None,
                            generate_ai_prompt=generate_ai_prompt,
                            reference_context=reference_context
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
        
        # Reference file uploads
        st.markdown("---")
        uploaded_ref_files = display_file_uploader(
            "PowerPoint Deck Generator",
            help_text="Upload presentation templates, visual guidelines, past successful decks, or brand style guides to inform your deck structure"
        )
        
        # AI prompt generation option
        generate_ai_prompt = st.checkbox(
            "📋 Also generate Gamma.ai / Beautiful.ai prompt",
            value=True,
            help="Creates a copy-paste ready prompt for AI presentation tools like Gamma.ai and Beautiful.ai"
        )
        
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
                        # Process reference files if uploaded
                        reference_context = None
                        if uploaded_ref_files:
                            reference_context = process_reference_files(uploaded_ref_files)
                        
                        deck = st.session_state.assistant.generate_presentation_deck(
                            objective=objective,
                            audience=audience,
                            key_messages=key_messages if key_messages else None,
                            data_points=data_points if data_points else None,
                            generate_ai_prompt=generate_ai_prompt,
                            reference_context=reference_context
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
    
    # MODULE 6: COMPETITIVE INTELLIGENCE
    elif module == "🔍 Competitive Intelligence":
        st.header("Competitive Intelligence")
        st.markdown("Analyze competitor positioning, campaigns, and media spend")
        
        with st.expander("📖 How to use this tool", expanded=False):
            st.markdown("""
            **What this does:**
            - Analyzes competitor brand positioning
            - Identifies recent campaigns and creative
            - Estimates media spend by channel
            - Provides strategic implications
            
            **Features:**
            - Real-time web search for latest campaigns
            - Media spend estimation
            - Competitive threat analysis
            - Strategic recommendations
            
            **Best practices:**
            - Be specific about competitor name
            - Include category for better context
            - Use focus areas to drill into specific questions
            
            **Output:** Comprehensive competitive intelligence report
            """)
        
        # Input fields
        col1, col2 = st.columns(2)
        
        with col1:
            user_brand = st.text_input(
                "Your Brand Name",
                placeholder="e.g., Traveller Whiskey",
                help="Your brand for comparative analysis"
            )
            competitor_brand = st.text_input(
                "Competitor Brand Name*",
                placeholder="e.g., Jack Daniel's, Jameson, Crown Royal"
            )
        
        with col2:
            category = st.text_input(
                "Category",
                placeholder="e.g., Premium Whiskey, Spirits"
            )
            focus_areas = st.text_area(
                "Focus Areas (optional)",
                placeholder="e.g., Digital strategy, Product innovation, Sports partnerships",
                height=86
            )
        
        # Web search option
        use_web_search = st.checkbox(
            "🌐 Search web for latest campaigns and news",
            value=True,
            help="Searches the internet for recent campaigns, press releases, and marketing activity"
        )
        
        # Reference file uploads
        st.markdown("---")
        uploaded_ref_files = display_file_uploader(
            "Competitive Intelligence",
            help_text="Upload past competitive analyses, market positioning maps, competitor reports, or industry research to enhance your analysis"
        )
        
        # AI prompt generation option
        generate_ai_prompt = st.checkbox(
            "📋 Also generate presentation prompt",
            value=True,
            help="Creates Gamma.ai/Beautiful.ai prompt for competitive intelligence deck"
        )
        
        if st.button("🔍 Analyze Competitor", type="primary", disabled=not competitor_brand):
            can_use, message = check_usage_limit(st.session_state.user_email)
            
            if not can_use:
                st.error(message)
                st.info("Upgrade your plan to continue")
                if st.button("View Plans"):
                    st.session_state.page = "subscription"
                    st.rerun()
            else:
                with st.spinner(f"Analyzing {competitor_brand}..."):
                    try:
                        # Process reference files if uploaded
                        reference_context = None
                        if uploaded_ref_files:
                            reference_context = process_reference_files(uploaded_ref_files)
                        
                        # Perform web search if enabled
                        if use_web_search:
                            st.info("🔍 Searching the web for latest campaigns and news...")
                        
                        # Get competitive analysis with web search
                        analysis = st.session_state.assistant.analyze_competitor(
                            competitor_brand=competitor_brand,
                            user_brand=user_brand if user_brand else None,
                            category=category if category else None,
                            focus_areas=focus_areas if focus_areas else None,
                            use_web_search=use_web_search,
                            reference_context=reference_context
                        )
                        
                        # Generate specific Gamma prompt if requested
                        gamma_prompt = None
                        if generate_ai_prompt:
                            with st.spinner("Generating specific Gamma.ai prompt based on analysis..."):
                                gamma_prompt = st.session_state.assistant.generate_gamma_prompt(
                                    analysis_content=analysis,
                                    deck_type="competitive_intelligence"
                                )
                        
                        update_user_usage(st.session_state.user_email)
                        _, remaining = check_usage_limit(st.session_state.user_email)
                        
                        st.markdown("### Competitive Intelligence Report")
                        st.markdown(analysis)
                        
                        # Show Gamma prompt if generated
                        if gamma_prompt:
                            st.markdown("---")
                            st.markdown("### 🎨 Gamma.ai Presentation Prompt")
                            st.info("Copy this prompt and paste it into Gamma.ai to create your competitive intelligence deck")
                            st.text_area(
                                "Gamma.ai Prompt",
                                gamma_prompt,
                                height=300,
                                label_visibility="collapsed"
                            )
                            st.download_button(
                                "📥 Download Gamma Prompt",
                                gamma_prompt,
                                file_name=f"{competitor_brand.replace(' ', '_')}_gamma_prompt.txt",
                                mime="text/plain"
                            )
                        
                        st.download_button(
                            "📥 Download Report",
                            analysis,
                            file_name=f"{competitor_brand.replace(' ', '_')}_competitive_intel.txt",
                            mime="text/plain"
                        )
                        
                        st.success(f"Analysis complete! {remaining} analyses remaining this month")
                        
                    except Exception as e:
                        error_msg = str(e)
                        
                        # Handle rate limit errors specifically
                        if "rate_limit_error" in error_msg or "429" in error_msg:
                            st.error("⏱️ Rate Limit Reached")
                            st.warning("""
                            The AI assistant has temporarily hit its rate limit. This happens when processing 
                            large amounts of data with web search.
                            
                            **What to do:**
                            - Wait 60 seconds and try again
                            - The system will reset automatically
                            - Your usage count has not been charged
                            
                            **Tip:** Rate limits are per minute - just wait a moment and re-run!
                            """)
                        else:
                            st.error(f"Error analyzing competitor: {error_msg}")
    
    # MODULE 7: CREATIVE QUALITY REVIEW
    elif module == "⭐ Creative Quality Review":
        st.header("Creative Quality Review")
        st.markdown("AI-powered creative testing with 100 consumer personas")
        
        with st.expander("📖 How to use this tool", expanded=False):
            st.markdown("""
            **What this does:**
            - Generates 100 diverse consumer personas
            - Evaluates creative from each persona's perspective
            - Scores on: Brand Recognition, Appeal, Purchase Intent
            - Provides specific improvement recommendations
            
            **How it works:**
            1. Upload your creative asset (image)
            2. Describe the creative and provide context
            3. AI generates 100 personas in your target
            4. Each persona rates the creative
            5. Get aggregate scores and improvement suggestions
            
            **Evaluation criteria:**
            - Brand Recognition (1-10)
            - Emotional Appeal (1-10)
            - Purchase Intent (1-10)
            - Message Clarity
            - Distinctiveness
            
            **Output:** Detailed creative scorecard with actionable improvements
            """)
        
        # Creative upload
        creative_file = st.file_uploader(
            "Upload Creative Asset",
            type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
            help="Upload your ad, social post, packaging, etc."
        )
        
        if creative_file:
            st.image(creative_file, caption="Your Creative Asset", use_container_width=True)
        
        # Creative description
        st.markdown("**Describe the Creative:**")
        creative_description = st.text_area(
            "Creative Description*",
            placeholder="Describe what's in the creative: visuals, copy, layout, colors, etc.",
            height=100,
            help="Be specific about visual elements, copy, brand presence, etc."
        )
        
        # Context inputs
        col1, col2 = st.columns(2)
        
        with col1:
            objective = st.text_area(
                "Campaign Objective*",
                placeholder="e.g., Drive awareness, Increase trial, Build brand love",
                height=80
            )
            target_consumer = st.text_area(
                "Target Consumer*",
                placeholder="e.g., Males 30-50, sports fans, whiskey drinkers",
                height=80
            )
        
        with col2:
            medium = st.selectbox(
                "Medium*",
                ["TV Commercial", "Digital Display", "Social Media", "Print Ad", 
                 "Out of Home", "Packaging", "Email", "Video (Online)", "Other"]
            )
            brand_context = st.text_area(
                "Brand Context (optional)",
                placeholder="Brand positioning, key attributes, competitive set",
                height=80
            )
        
        # Reference file uploads
        st.markdown("---")
        uploaded_ref_files = display_file_uploader(
            "Creative Quality Review",
            help_text="Upload creative standards documentation, brand guidelines, past campaign examples, or testing criteria to inform the review"
        )
        
        # AI prompt generation option
        generate_ai_prompt = st.checkbox(
            "📋 Also generate presentation prompt",
            value=True,
            help="Creates Gamma.ai/Beautiful.ai prompt for creative review deck"
        )
        
        if st.button("⭐ Review Creative", type="primary", disabled=not (creative_description and objective and target_consumer)):
            can_use, message = check_usage_limit(st.session_state.user_email)
            
            if not can_use:
                st.error(message)
                st.info("Upgrade your plan to continue")
                if st.button("View Plans"):
                    st.session_state.page = "subscription"
                    st.rerun()
            else:
                with st.spinner("Generating 100 personas and evaluating creative..."):
                    try:
                        # Add image context if uploaded
                        full_description = creative_description
                        if creative_file:
                            full_description = f"[Creative asset uploaded: {creative_file.name}]\n\n{creative_description}"
                        
                        # Process reference files if uploaded
                        reference_context = None
                        if uploaded_ref_files:
                            reference_context = process_reference_files(uploaded_ref_files)
                        
                        review = st.session_state.assistant.review_creative_asset(
                            creative_description=full_description,
                            objective=objective,
                            target_consumer=target_consumer,
                            medium=medium,
                            brand_context=brand_context if brand_context else None,
                            reference_context=reference_context
                        )
                        
                        # Generate specific Gamma prompt if requested
                        gamma_prompt = None
                        if generate_ai_prompt:
                            with st.spinner("Generating specific Gamma.ai prompt based on review..."):
                                gamma_prompt = st.session_state.assistant.generate_gamma_prompt(
                                    analysis_content=review,
                                    deck_type="creative_review"
                                )
                        
                        update_user_usage(st.session_state.user_email)
                        _, remaining = check_usage_limit(st.session_state.user_email)
                        
                        st.markdown("### Creative Quality Report")
                        st.markdown(review)
                        
                        # Show Gamma prompt if generated
                        if gamma_prompt:
                            st.markdown("---")
                            st.markdown("### 🎨 Gamma.ai Presentation Prompt")
                            st.info("Copy this prompt and paste it into Gamma.ai to create your creative review deck")
                            st.text_area(
                                "Gamma.ai Prompt",
                                gamma_prompt,
                                height=300,
                                label_visibility="collapsed"
                            )
                            st.download_button(
                                "📥 Download Gamma Prompt",
                                gamma_prompt,
                                file_name="creative_review_gamma_prompt.txt",
                                mime="text/plain"
                            )
                        
                        st.download_button(
                            "📥 Download Review",
                            review,
                            file_name="creative_quality_review.txt",
                            mime="text/plain"
                        )
                        
                        st.success(f"Review complete! {remaining} analyses remaining this month")
                        
                    except Exception as e:
                        error_msg = str(e)
                        
                        # Handle rate limit errors specifically
                        if "rate_limit_error" in error_msg or "429" in error_msg:
                            st.error("⏱️ Rate Limit Reached")
                            st.warning("""
                            The AI assistant has temporarily hit its rate limit. This happens when processing 
                            large amounts of data.
                            
                            **What to do:**
                            - Wait 60 seconds and try again
                            - The system will reset automatically
                            - Your usage count has not been charged
                            
                            **Tip:** Rate limits are per minute - just wait a moment and re-run!
                            """)
                        else:
                            st.error(f"Error reviewing creative: {error_msg}")
    
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
    st.session_state.page = "landing"

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
