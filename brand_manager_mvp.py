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
import anthropic
import pandas as pd

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

# Professional page configuration
st.set_page_config(
    page_title="Brand Manager AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E3A8A 0%, #2E5CFF 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


class BrandManagerAssistant:
    def __init__(self, api_key=None):
        """Initialize the Brand Manager Assistant"""
        self.client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
        self.conversation_history = {}
        self.current_date = datetime.now().strftime("%B %d, %Y")  # e.g., "December 31, 2025"
        
    def _chat(self, module_name, user_message, system_prompt, max_tokens=6000):
        """Internal chat method with conversation history"""
        if module_name not in self.conversation_history:
            self.conversation_history[module_name] = []
        
        self.conversation_history[module_name].append({
            "role": "user",
            "content": user_message
        })
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=self.conversation_history[module_name]
        )
        
        assistant_message = response.content[0].text
        self.conversation_history[module_name].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def _chat_with_tools(self, module_name, user_message, system_prompt, max_tokens=6000, 
                        use_web_search=False, use_history=True):
        """Internal chat method with tool support (web search)"""
        
        # For competitive intelligence and other one-off analyses, don't use conversation history
        # to avoid rate limits from accumulated context
        if use_history:
            if module_name not in self.conversation_history:
                self.conversation_history[module_name] = []
            
            self.conversation_history[module_name].append({
                "role": "user",
                "content": user_message
            })
            
            messages = self.conversation_history[module_name]
        else:
            # One-off request without history
            messages = [{"role": "user", "content": user_message}]
        
        # Add tools if web search is enabled
        tools = []
        if use_web_search:
            tools.append({
                "type": "web_search_20250305",
                "name": "web_search"
            })
        
        # Make API call with tools if enabled
        if tools:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
                tools=tools
            )
        else:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages
            )
        
        # Extract text from response (may contain multiple content blocks if tools were used)
        assistant_message = ""
        for content_block in response.content:
            if content_block.type == "text":
                assistant_message += content_block.text + "\n"
        
        assistant_message = assistant_message.strip()
        
        if use_history:
            self.conversation_history[module_name].append({
                "role": "assistant",
                "content": assistant_message
            })
        
        return assistant_message
    
    def generate_gamma_prompt(self, analysis_content, deck_type="competitive_intelligence"):
        """
        Generate a specific Gamma.ai prompt based on actual analysis content
        
        Args:
            analysis_content: The actual analysis output
            deck_type: Type of deck (competitive_intelligence, creative_review, etc.)
        """
        system_prompt = f"""You are an expert at creating detailed Gamma.ai presentation prompts.

CURRENT DATE: {self.current_date}

Your role is to:
1. Read the analysis content provided
2. Extract the key insights, data points, and recommendations
3. Create a SPECIFIC Gamma.ai prompt that will recreate this analysis as a presentation
4. Include actual data, quotes, and findings from the analysis (not generic placeholders)

IMPORTANT:
- Use SPECIFIC information from the analysis (actual brand names, numbers, dates, campaign names)
- Include ACTUAL quotes and findings, not "Insert competitor name here"
- Reference SPECIFIC insights and recommendations from the analysis
- Make the prompt detailed enough that Gamma.ai can create accurate slides

Output Format:
Create a Gamma.ai prompt that starts with clear instructions, then includes slide-by-slide 
specifications with ACTUAL CONTENT from the analysis."""

        prompt_templates = {
            "competitive_intelligence": """Based on the competitive intelligence analysis, create a detailed Gamma.ai prompt for a presentation deck. Include:

1. Specific competitor insights (use actual findings)
2. Campaign names and dates from the analysis
3. Data visualizations with actual numbers
4. Strategic implications (use actual recommendations)
5. Visual suggestions based on content""",
            
            "creative_review": """Based on the creative review, create a detailed Gamma.ai prompt for a presentation deck. Include:

1. Specific creative elements to showcase
2. Evaluation scores (use actual scores)
3. Improvement recommendations (use actual suggestions)
4. Persona insights (use actual persona feedback)
5. Before/after suggestions"""
        }
        
        template = prompt_templates.get(deck_type, prompt_templates["competitive_intelligence"])
        
        user_message = f"""Here is the analysis:

{analysis_content}

{template}

Create a SPECIFIC Gamma.ai prompt with actual data, names, and findings from above."""

        # Don't use history for Gamma prompt generation - it's a one-off task
        return self._chat("gamma_prompt_gen", user_message, system_prompt, max_tokens=4000)

    # ==================== MODULE 1: DATA PERFORMANCE ANALYSIS ====================
    
    def analyze_market_data(self, data_file=None, data_dict=None, analysis_focus=None,
                           generate_ai_prompt=False, reference_context=None):
        """
        Analyze Nielsen/IRI market data for brand and competitive performance
        
        Args:
            data_file: Path to CSV/Excel data file
            data_dict: Dictionary of data if not using file
            analysis_focus: Specific areas to focus on (e.g., "YOY growth", "market share shifts")
            generate_ai_prompt: Whether to generate presentation prompt (deprecated - handled separately)
            reference_context: Additional reference materials
        """
        system_prompt = f"""You are an expert brand performance analyst specializing in Nielsen and IRI data analysis.

CURRENT DATE: {self.current_date}

CRITICAL: When analyzing data and making recommendations:
- Focus on the most recent time periods and trends
- Prioritize current market conditions and recent developments
- If data includes multiple time periods, emphasize the latest periods
- Flag any data that appears outdated or stale

Your role is to:
1. Analyze market data for brand performance vs competitors
2. Identify clear drivers of performance (distribution, pricing, velocity, household penetration, etc.)
3. Provide actionable recommendations based on RECENT data insights
4. Highlight risks and opportunities in the CURRENT market environment
5. Present findings in a clear, executive-ready format

When analyzing data:
- Focus on YOY and period-over-period trends
- Compare brand performance to category and key competitors
- Identify statistical significance in changes
- Connect data points to strategic implications
- Provide specific, actionable next steps for TODAY'S market

Output format should include:
- Executive Summary (3-4 key takeaways focused on recent insights)
- Performance Overview (brand vs category vs competitors)
- Key Drivers Analysis
- Risks & Opportunities (in current market context)
- Recommended Actions (prioritized for immediate execution)"""

        # Prepare the data message
        if data_file:
            df = pd.read_csv(data_file) if data_file.endswith('.csv') else pd.read_excel(data_file)
            data_summary = df.to_string()
        elif data_dict:
            data_summary = json.dumps(data_dict, indent=2)
        else:
            data_summary = "No data provided"
        
        focus_text = f"\n\nSpecific Analysis Focus: {analysis_focus}" if analysis_focus else ""
        ref_text = f"\n\nReference Context:\n{reference_context}" if reference_context else ""
        
        user_message = f"""Please analyze the following market data:

{data_summary}
{focus_text}{ref_text}

Provide a comprehensive performance analysis with clear drivers and actionable recommendations."""

        return self._chat("data_analysis", user_message, system_prompt, max_tokens=8000)

    # ==================== MODULE 2: CREATIVE BRIEF GENERATOR ====================
    
    def generate_creative_brief(self, template_file=None, brief_inputs=None, 
                               generate_ai_prompt=False, reference_context=None):
        """
        Generate creative or program briefs based on template
        
        Args:
            template_file: Path to brief template (Word, PDF, or text)
            brief_inputs: Dictionary of inputs to populate template
            generate_ai_prompt: Whether to generate presentation prompt (deprecated - handled separately)
            reference_context: Additional reference materials
        """
        system_prompt = f"""You are an expert creative brief writer and brand strategist.

CURRENT DATE: {self.current_date}

Your role is to:
1. Take user inputs and template structures to create comprehensive creative briefs
2. Ensure all sections are strategically sound and actionable
3. Write clear, inspiring creative direction
4. Define success metrics and guardrails
5. Provide context that empowers creative teams

A great creative brief includes:
- Background/Context (current market situation, business challenge)
- Objective (what we need to achieve)
- Target Audience (deep psychographic understanding for today's consumer)
- Key Insight (human truth that drives the work)
- Single-Minded Proposition (one clear message)
- Supporting Reasons to Believe
- Tone & Manner (brand voice guidance)
- Mandatories (must-haves and must-not-haves)
- Success Metrics (relevant for current market)

Write in clear, confident language. Be specific, not generic. Consider current market trends and consumer expectations."""

        if template_file:
            with open(template_file, 'r') as f:
                template = f.read()
            template_text = f"\n\nTemplate Structure:\n{template}"
        else:
            template_text = ""
        
        inputs_text = f"\n\nBrief Inputs:\n{json.dumps(brief_inputs, indent=2)}" if brief_inputs else ""
        ref_text = f"\n\nReference Materials:\n{reference_context}" if reference_context else ""
        
        user_message = f"""Please generate a creative brief using the following information:
{template_text}
{inputs_text}{ref_text}

Create a comprehensive, actionable creative brief that will inspire great work."""

        return self._chat("creative_brief", user_message, system_prompt, max_tokens=8000)

    # ==================== MODULE 3: BRAND POSITIONING ====================
    
    def develop_brand_positioning(self, brand_os_inputs=None, positioning_challenge=None,
                                  generate_ai_prompt=False, reference_context=None):
        """
        Develop or refine brand positioning using Brand OS framework
        
        Args:
            brand_os_inputs: Dictionary with Brand OS elements (purpose, values, personality, etc.)
            positioning_challenge: Specific positioning challenge to address
            generate_ai_prompt: Whether to generate presentation prompt (deprecated - handled separately)
            reference_context: Additional reference materials
        """
        system_prompt = f"""You are an expert brand strategist specializing in brand positioning and Brand OS development.

CURRENT DATE: {self.current_date}

Your role is to:
1. Develop clear, differentiated brand positioning for today's market
2. Ensure internal consistency across all Brand OS elements
3. Create positioning that is ownable, credible, and compelling
4. Provide strategic rationale for positioning choices
5. Pressure-test positioning against current competitive set

Brand OS Framework includes:
- Brand Purpose (why the brand exists beyond profit)
- Brand Vision (aspirational future state)
- Brand Values (what the brand stands for)
- Brand Personality (how the brand shows up)
- Target Audience (who we serve today, current psychographics)
- Brand Promise (what we deliver)
- Positioning Statement (competitive frame + POD in current market)
- Key Messages (proof points and RTBs)
- Visual & Verbal Identity guidelines

Ensure positioning is:
- Differentiated (unique in today's category landscape)
- Credible (can we deliver on it?)
- Relevant (does today's target care?)
- Sustainable (can we own it long-term?)

Provide strategic rationale for all recommendations considering current market dynamics."""

        inputs_text = f"Brand OS Inputs:\n{json.dumps(brand_os_inputs, indent=2)}\n\n" if brand_os_inputs else ""
        challenge_text = f"Positioning Challenge:\n{positioning_challenge}\n\n" if positioning_challenge else ""
        ref_text = f"Reference Materials:\n{reference_context}\n\n" if reference_context else ""
        
        user_message = f"""Please develop brand positioning based on:

{inputs_text}{challenge_text}{ref_text}
Create a comprehensive Brand OS with clear strategic rationale."""

        return self._chat("brand_positioning", user_message, system_prompt, max_tokens=8000)

    # ==================== MODULE 4: INNOVATION IDEATION ====================
    
    def generate_innovation_ideas(self, innovation_brief=None, category=None, target=None, 
                                 constraints=None, generate_ai_prompt=False, reference_context=None):
        """
        Generate innovation ideas with packaging concepts
        
        Args:
            innovation_brief: Strategic brief for innovation
            category: Product category
            target: Target consumer
            constraints: Any constraints (cost, capabilities, etc.)
            generate_ai_prompt: Whether to generate presentation prompt (deprecated - handled separately)
            reference_context: Additional reference materials
        """
        system_prompt = f"""You are an expert innovation strategist and product developer specializing in CPG brands.

CURRENT DATE: {self.current_date}

Your role is to:
1. Generate breakthrough innovation ideas that solve real consumer needs TODAY
2. Ensure ideas are strategically sound and commercially viable in current market
3. Consider the full innovation spectrum (core renovations to transformational)
4. Provide packaging concepts that bring ideas to life
5. Include go-to-market considerations for today's retail landscape

Innovation Framework:
- Consumer Insight (unmet need or friction point - what's relevant NOW?)
- Innovation Concept (product/service solution)
- Benefit Proposition (why consumers care)
- Reason to Believe (credibility)
- Packaging & Design (visual identity aligned with current trends)
- Route to Market (distribution strategy for today's channels)
- Business Case (volume/margin potential in current market)

For each innovation:
1. Define the consumer problem being solved (relevant today)
2. Describe the product in detail
3. Explain the benefit hierarchy
4. Outline packaging approach (size, format, graphics, messaging)
5. Assess feasibility and business potential in current market

Generate multiple ideas across the innovation spectrum:
- Core Renovation (optimizing existing)
- Adjacent Innovation (logical extension)
- Transformational (category disruption)

Consider current trends: sustainability, health & wellness, convenience, digital integration, etc."""

        brief_text = f"Innovation Brief:\n{innovation_brief}\n\n" if innovation_brief else ""
        category_text = f"Category: {category}\n" if category else ""
        target_text = f"Target Consumer: {target}\n" if target else ""
        constraints_text = f"Constraints: {constraints}\n\n" if constraints else ""
        ref_text = f"Reference Materials:\n{reference_context}\n\n" if reference_context else ""
        
        user_message = f"""Please generate innovation ideas:

{brief_text}{category_text}{target_text}{constraints_text}{ref_text}
Generate 3-5 innovation concepts with detailed packaging descriptions."""

        return self._chat("innovation", user_message, system_prompt, max_tokens=8000)

    # ==================== MODULE 5: POWERPOINT DECK GENERATOR ====================
    
    def generate_presentation_deck(self, objective=None, key_messages=None, audience=None, 
                                  template_slides=None, data_points=None, generate_ai_prompt=False,
                                  reference_context=None):
        """
        Generate PowerPoint deck structure and content
        
        Args:
            objective: Meeting/presentation objective
            key_messages: Main points to communicate
            audience: Who you're presenting to
            template_slides: Available slide templates
            data_points: Data to include
            generate_ai_prompt: Whether to generate presentation prompt (deprecated - handled separately)
            reference_context: Additional reference materials
        """
        system_prompt = f"""You are an expert presentation strategist and storyteller specializing in executive communications.

CURRENT DATE: {self.current_date}

Your role is to:
1. Develop compelling presentation narratives that drive decisions
2. Structure decks with clear flow and logic
3. Write executive-ready slide content (headlines, body copy)
4. Recommend visual treatments for maximum impact
5. Ensure presentations lead to action

Presentation Best Practices:
- Start with the end in mind (what decision/action needed?)
- Use pyramid principle (answer first, then support)
- One idea per slide
- Headlines should be complete thoughts (not labels)
- Use data to prove, not decorate
- Build to a clear recommendation or ask
- Consider current business context and market conditions

Slide Structure Output:
For each slide provide:
- Slide Number & Title (action-oriented headline)
- Slide Type (title, content, data visualization, etc.)
- Key Message (what this slide proves)
- Talking Points (what to say)
- Visual Recommendation (chart type, image, layout)
- Data/Content to include

Consider:
- Executive audience = fewer slides, bigger ideas
- Build logical argument flow
- Use appendix for backup data
- Strong opening and closing
- Ensure content is relevant to current business environment"""

        obj_text = f"Presentation Objective:\n{objective}\n\n" if objective else ""
        msg_text = f"Key Messages:\n{key_messages}\n\n" if key_messages else ""
        aud_text = f"Audience: {audience}\n\n" if audience else ""
        template_text = f"Available Templates:\n{template_slides}\n\n" if template_slides else ""
        data_text = f"Data Points:\n{json.dumps(data_points, indent=2)}\n\n" if data_points else ""
        ref_text = f"Reference Materials:\n{reference_context}\n\n" if reference_context else ""
        
        user_message = f"""Please generate a presentation deck:

{obj_text}{msg_text}{aud_text}{template_text}{data_text}{ref_text}
Create a complete deck structure with slide-by-slide content and recommendations."""

        return self._chat("presentation", user_message, system_prompt, max_tokens=8000)

    # ==================== MODULE 6: COMPETITIVE INTELLIGENCE ====================
    
    def analyze_competitor(self, competitor_brand, user_brand=None, category=None, 
                          focus_areas=None, use_web_search=False, reference_context=None):
        """
        Analyze competitor positioning, campaigns, and strategy
        
        Args:
            competitor_brand: Name of competitor to analyze
            user_brand: Your brand name for comparison
            category: Product category
            focus_areas: Specific areas to focus on
            use_web_search: Whether to use web search for latest information
            reference_context: Additional reference materials
        """
        system_prompt = f"""You are a competitive intelligence analyst.

CURRENT DATE: {self.current_date}

RECENCY: Focus on campaigns from last 6 months. Prioritize Q4 2025 activities.

CITATIONS: Include [Source: Publication, Date, URL] for all claims.

Analyze:
1. Current brand positioning
2. Recent campaigns (last 6 months) with specific dates
3. Media spend and channel mix
4. Strategic implications
5. Recommended counter-strategies

Search for: "{competitor_brand} 2025 campaign", "{competitor_brand} recent marketing", "{competitor_brand} Q4 2025"

Include specific campaign names, dates, spend estimates, and source URLs."""

        user_text = f"Your Brand: {user_brand}\n" if user_brand else ""
        cat_text = f"Category: {category}\n" if category else ""
        focus_text = f"\nSpecific Focus Areas:\n{focus_areas}\n" if focus_areas else ""
        ref_text = f"\n\nReference Context:\n{reference_context}\n" if reference_context else ""
        
        search_instruction = "\n\n🌐 USE WEB SEARCH to find the most recent campaigns, press releases, news articles, and marketing activities. Search for terms like: '{} 2025 campaign', '{} recent news', '{} latest marketing', '{} Q4 2025'.\n\nCite all sources with publication name, date, and URL.".format(
            competitor_brand, competitor_brand, competitor_brand, competitor_brand
        ) if use_web_search else ""
        
        user_message = f"""Please analyze the following competitor:

Competitor Brand: {competitor_brand}
{user_text}{cat_text}{focus_text}{ref_text}{search_instruction}

Provide a comprehensive competitive intelligence analysis with specific dates, campaign names, and SOURCE CITATIONS (including URLs) for all claims."""

        # Don't use conversation history for competitive intelligence to avoid rate limits
        # Each analysis should be independent anyway
        return self._chat_with_tools("competitive_intel", user_message, system_prompt, 
                                     max_tokens=8000, use_web_search=use_web_search, 
                                     use_history=False)

    # ==================== MODULE 7: CREATIVE ASSET REVIEW ====================
    
    def review_creative_asset(self, creative_description, objective, target_consumer, 
                             medium, brand_context=None, reference_context=None):
        """
        Review and provide feedback on creative assets
        
        Args:
            creative_description: Description or copy of the asset
            objective: Campaign objective
            target_consumer: Target audience description
            medium: Type of creative (TV, digital, social, print, etc.)
            brand_context: Brand guidelines and positioning
            reference_context: Additional reference materials
        """
        system_prompt = f"""You are an expert creative strategist and brand guardian specializing in advertising effectiveness.

CURRENT DATE: {self.current_date}

Your role is to:
1. Evaluate creative assets against brand standards and best practices
2. Assess message clarity, emotional resonance, and call-to-action strength
3. Identify what's working well and what needs improvement
4. Provide specific, actionable recommendations for optimization
5. Consider CURRENT market trends and consumer expectations

Evaluation Framework:
- Strategic Alignment (does it ladder to brand strategy?)
- Message Clarity (is the main message clear and compelling?)
- Brand Consistency (voice, tone, visual identity)
- Target Relevance (will it resonate with the audience?)
- Emotional Impact (does it create the intended feeling?)
- Call-to-Action (is the desired action clear and motivating?)
- Production Quality (appropriate for channel and audience)
- Competitive Context (how does it compare to current category norms?)

Provide:
1. Overall Assessment (Strong, Good, Needs Work)
2. What's Working Well (specific strengths)
3. Areas for Improvement (specific issues)
4. Recommendations (prioritized, actionable fixes)
5. Optimization Opportunities (how to make it great)

Be constructive but honest. Focus on making the work better."""

        brand_text = f"\n\nBrand Context:\n{brand_context}" if brand_context else ""
        ref_text = f"\n\nReference Materials:\n{reference_context}" if reference_context else ""
        
        user_message = f"""Please review the following creative asset:

Medium: {medium}
Campaign Objective: {objective}
Target Consumer: {target_consumer}

Creative Description:
{creative_description}{brand_text}{ref_text}

Provide a comprehensive creative review with specific recommendations for improvement."""

        return self._chat("creative_review", user_message, system_prompt, max_tokens=8000)

    # ==================== UTILITY METHODS ====================
    
    def reset_conversation(self, module_name=None):
        """Reset conversation history for a module or all modules"""
        if module_name:
            self.conversation_history[module_name] = []
        else:
            self.conversation_history = {}
    
    def save_output(self, content, filename, format='txt'):
        """Save output to file"""
        output_dir = Path('brand_manager_outputs')
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return str(filepath)


# ==================== EXAMPLE USAGE ====================


# ============================================================================
# USER MANAGEMENT & AUTHENTICATION
# ============================================================================

USERS_FILE = "users.json"

SUBSCRIPTION_TIERS = {
    "free": {
        "name": "Free",
        "price": 0,
        "analyses_per_month": 5,
        "features": ["5 analyses per month", "Basic support"]
    },
    "pro": {
        "name": "Professional",
        "price": 49,
        "analyses_per_month": 200,
        "features": ["200 analyses per month", "Priority support", "Advanced features"]
    },
    "team": {
        "name": "Team",
        "price": 199,
        "analyses_per_month": 1000,
        "features": ["1000 analyses per month", "Team collaboration", "Dedicated support"]
    }
}

def load_users():
    """Load users from JSON file"""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    """Hash password with SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password):
    """Create new user account"""
    users = load_users()
    
    if email in users:
        return False, "Email already registered"
    
    users[email] = {
        "password_hash": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "tier": "free",
        "usage": {
            "analyses_used": 0,
            "current_month": datetime.now().strftime("%Y-%m"),
            "last_reset": datetime.now().isoformat()
        }
    }
    
    save_users(users)
    return True, "Account created successfully"

def verify_user(email, password):
    """Verify user credentials"""
    users = load_users()
    
    if email not in users:
        return False
    
    return users[email]["password_hash"] == hash_password(password)

def get_user(email):
    """Get user data by email"""
    users = load_users()
    
    if email not in users:
        return None
    
    return users[email]

def record_usage(email):
    """Record analysis usage"""
    users = load_users()
    
    if email not in users:
        return False
    
    user = users[email]
    current_month = datetime.now().strftime("%Y-%m")
    
    if user["usage"]["current_month"] != current_month:
        user["usage"]["current_month"] = current_month
        user["usage"]["analyses_used"] = 0
        user["usage"]["last_reset"] = datetime.now().isoformat()
    
    user["usage"]["analyses_used"] += 1
    save_users(users)
    return True

# Alias for compatibility
update_user_usage = record_usage

def check_usage_limit(email):
    """Check if user has remaining analyses"""
    users = load_users()
    
    if email not in users:
        return False, "User not found"
    
    user = users[email]
    tier = SUBSCRIPTION_TIERS[user["tier"]]
    current_month = datetime.now().strftime("%Y-%m")
    
    if user["usage"]["current_month"] != current_month:
        user["usage"]["current_month"] = current_month
        user["usage"]["analyses_used"] = 0
        user["usage"]["last_reset"] = datetime.now().isoformat()
        save_users(users)
    
    remaining = tier["analyses_per_month"] - user["usage"]["analyses_used"]
    
    if remaining <= 0:
        return False, f"Monthly limit reached. Upgrade to Pro for more analyses."
    
    return True, remaining

def upgrade_user_tier(email, new_tier):
    """Upgrade user's subscription tier"""
    users = load_users()
    
    if email not in users:
        return False, "User not found"
    
    if new_tier not in SUBSCRIPTION_TIERS:
        return False, "Invalid tier"
    
    users[email]["tier"] = new_tier
    users[email]["tier_updated_at"] = datetime.now().isoformat()
    
    save_users(users)
    return True, f"User upgraded to {SUBSCRIPTION_TIERS[new_tier]['name']}"



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
# HELPER FUNCTIONS
# ============================================================================

def display_file_uploader(module_name, help_text=None):
    """Display file uploader for reference materials
    
    Args:
        module_name: Name of the module (for unique key)
        help_text: Optional help text to display
    
    Returns:
        List of uploaded files or None
    """
    st.markdown("### 📎 Upload Reference Files (Optional)")
    
    if help_text:
        st.info(f"💡 **Tip:** {help_text}")
    
    uploaded_files = st.file_uploader(
        "Choose reference files",
        type=["pdf", "docx", "txt", "pptx", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key=f"ref_files_{module_name.lower().replace(' ', '_')}",
        help="Upload brand guidelines, past reports, strategic docs, or any materials to inform the analysis"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        with st.expander("📄 View uploaded files"):
            for file in uploaded_files:
                file_size = len(file.getvalue()) / 1024  # KB
                st.write(f"• **{file.name}** ({file_size:.1f} KB)")
    
    return uploaded_files if uploaded_files else None

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main_app():
    """Main application with all modules"""
    
    # Initialize session state
    if 'assistant' not in st.session_state:
        # API key will be automatically loaded from environment variable
        st.session_state.assistant = BrandManagerAssistant()
    
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
                label_visibility="collapsed",
                key="main_module_selector"
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
        try:
            # Check if already numeric
            if pd.api.types.is_numeric_dtype(series):
                return series
                
            # Try to clean string-formatted numbers
            if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
                # Remove common formatting
                cleaned = series.astype(str).str.replace('$', '', regex=False)
                cleaned = cleaned.str.replace('%', '', regex=False)
                cleaned = cleaned.str.replace(',', '', regex=False)
                cleaned = cleaned.str.strip()
                
                # Convert to numeric, coerce errors to NaN
                return pd.to_numeric(cleaned, errors='coerce')
            
            return series
        except Exception:
            # If anything fails, return original series
            return series
    
    def standardize_column_names(df: 'pd.DataFrame', source: str) -> 'pd.DataFrame':
        """Standardize column names based on detected source"""
        try:
            df = df.copy()
            
            # Just clean column names, don't try to standardize them
            # This prevents creating duplicate column names
            new_columns = []
            for col in df.columns:
                col_str = str(col).strip()
                # Clean up special characters but preserve uniqueness
                col_clean = col_str.replace(' / ', '_per_')
                col_clean = col_clean.replace('/', '_')
                col_clean = col_clean.replace('  ', ' ')
                col_clean = col_clean.replace(' ', '_')
                col_clean = col_clean.replace('%', 'pct')
                col_clean = col_clean.replace('$', 'dollar')
                col_clean = col_clean.lower()
                new_columns.append(col_clean)
            
            # Check if cleaning created any duplicates
            if len(new_columns) != len(set(new_columns)):
                # Keep original column names to avoid duplicates
                return df
            
            df.columns = new_columns
            return df
            
        except Exception:
            # If anything fails, return original dataframe
            return df
    
    def preprocess_syndicated_data(df: 'pd.DataFrame', source: str) -> 'pd.DataFrame':
        """Apply source-specific preprocessing and cleaning"""
        try:
            df = df.copy()
            
            # Standardize column names
            try:
                df = standardize_column_names(df, source)
            except:
                pass  # If standardization fails, continue with original names
            
            # Clean numeric columns
            numeric_patterns = ['sales', 'units', 'share', 'volume', 'tdp', 'acv', 
                              'price', 'distribution', 'penetration', 'count']
            
            for col in df.columns:
                try:
                    # Check if column name suggests numeric data
                    if any(pattern in str(col).lower() for pattern in numeric_patterns):
                        df[col] = clean_numeric_column(df[col])
                except:
                    continue  # Skip problematic columns
            
            # Source-specific processing (with error handling for each)
            try:
                if source == 'Nielsen':
                    # Nielsen often has summary rows - remove them
                    if 'geography' in df.columns:
                        df = df[df['geography'].notna()]
                        df = df[~df['geography'].str.contains('total', case=False, na=False)]
                
                elif source == 'IRI':
                    # IRI may have multiple header rows
                    if 'dollar_sales' in df.columns:
                        df = df[pd.to_numeric(df['dollar_sales'], errors='coerce').notna()]
                
                elif source == 'Circana':
                    # Circana combines IRI + NPD
                    if 'dollar_sales' in df.columns:
                        df = df[pd.to_numeric(df['dollar_sales'], errors='coerce').notna()]
                
                elif source == 'Numerator':
                    # Numerator has household panel data
                    if 'household_count' in df.columns:
                        df = df[df['household_count'] > 0]
                
                elif source == 'SPINS':
                    # SPINS focuses on natural/organic
                    if 'channel' in df.columns:
                        df = df[df['channel'].notna()]
            except:
                pass  # If source-specific processing fails, continue
            
            # Remove any completely empty rows
            df = df.dropna(how='all')
            
            # Reset index
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception:
            # If all preprocessing fails, return original dataframe
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
                    
                    # Basic data validation
                    if df.empty:
                        st.error("The uploaded file is empty. Please upload a file with data.")
                        df = None
                    else:
                        st.success(f"✅ Loaded {len(df):,} rows and {len(df.columns)} columns")
                        
                        # Try to detect data source (optional, doesn't fail if detection fails)
                        try:
                            data_source, confidence = detect_data_source(df)
                            if data_source and confidence >= 30:
                                st.info(f"📊 Detected {data_source} data ({confidence:.0f}% confidence)")
                                # Only preprocess if we're confident about the source
                                df = preprocess_syndicated_data(df, data_source)
                        except:
                            # If detection/preprocessing fails, just use raw data
                            pass
                        
                        # Show preview
                        st.dataframe(df.head(10))
                        
                        # Show helpful tip based on file size
                        if len(df) > 1000:
                            st.info(f"""
                            💡 **Large dataset detected:** {len(df):,} rows. 
                            
                            When you analyze, data will be automatically summarized by brand/product 
                            for faster processing and executive-level insights.
                            """)
                    
                except Exception as e:
                    st.error(f"Error loading file: {str(e)}")
                    st.info("Make sure your file is a valid CSV or Excel file with data.")
                    df = None
        
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
                            # Check if dataset needs summarization
                            # Consider BOTH row count AND column count
                            total_cells = len(df) * len(df.columns)
                            
                            # Summarize if: >1000 rows OR >100 rows with >20 columns OR >2500 total cells
                            needs_summary = (
                                len(df) > 1000 or 
                                (len(df) > 100 and len(df.columns) > 20) or
                                total_cells > 2500
                            )
                            
                            # For large datasets, summarize the data first
                            if needs_summary:
                                # Show informative message about what's happening
                                st.info(f"""
                                🔄 **Processing:** {len(df):,} rows × {len(df.columns)} columns = {total_cells:,} data points
                                
                                Summarizing for optimal analysis:
                                - Selecting key metrics
                                - Grouping by brand/product
                                - Focusing on current period data
                                
                                **Please wait...**
                                """)
                                
                                # For wide datasets (many columns), select only key columns first
                                key_columns = []
                                
                                # Identify key columns
                                for col in df.columns:
                                    col_str = str(col)
                                    col_lower = col_str.lower()
                                    
                                    # Keep identifier columns
                                    if any(x in col_lower for x in ['brand', 'item', 'product', 'category', 'market', 'period']):
                                        key_columns.append(col)
                                    # Keep current metrics (skip YA and change columns)
                                    elif any(x in col_str for x in ['$', 'CASE', 'TDP', '%ACV']) and not any(x in col_str for x in ['YA', 'Chg', 'Change']):
                                        key_columns.append(col)
                                
                                # Use key columns or first 12 columns if none identified
                                if key_columns and len(key_columns) < len(df.columns):
                                    df_working = df[key_columns].copy()
                                    st.success(f"✅ Selected {len(key_columns)} key metrics from {len(df.columns)} total columns")
                                else:
                                    df_working = df.iloc[:, :min(12, len(df.columns))].copy()
                                    st.success(f"✅ Using first 12 columns for analysis")
                                
                                # Group by brand/product
                                summary_columns = []
                                for col in df_working.columns:
                                    col_lower = str(col).lower()
                                    if any(x in col_lower for x in ['brand', 'item', 'product']):
                                        summary_columns.append(col)
                                        if len(summary_columns) >= 2:  # Max 2 grouping columns
                                            break
                                
                                if summary_columns:
                                    # Find numeric columns
                                    numeric_cols = df_working.select_dtypes(include=['number']).columns.tolist()
                                    
                                    if numeric_cols:
                                        # Group and sum
                                        df_summary = df_working.groupby(summary_columns)[numeric_cols].sum().reset_index()
                                        
                                        # Keep top 80 by dollar sales if still too large
                                        if len(df_summary) > 80:
                                            dollar_cols = [c for c in df_summary.columns if '$' in str(c) or 'sales' in str(c).lower()]
                                            if dollar_cols:
                                                df_summary = df_summary.nlargest(80, dollar_cols[0])
                                            else:
                                                df_summary = df_summary.head(80)
                                        
                                        st.success(f"✅ Ready! Summarized to {len(df_summary)} brands/products × {len(df_summary.columns)} metrics")
                                        data_dict = df_summary.to_dict('records')
                                    else:
                                        st.success(f"✅ Using top 80 rows")
                                        data_dict = df_working.head(80).to_dict('records')
                                else:
                                    # No grouping columns, take top 80 rows
                                    st.success(f"✅ Analyzing top 80 rows × {len(df_working.columns)} metrics")
                                    data_dict = df_working.head(80).to_dict('records')
                            else:
                                # Small dataset - check if it's truly small or just narrow
                                if len(df.columns) > 30:
                                    # Many columns but few rows - still select key columns
                                    st.info(f"📊 Wide dataset: {len(df)} rows × {len(df.columns)} columns - selecting key metrics")
                                    
                                    key_columns = []
                                    for col in df.columns:
                                        col_str = str(col)
                                        col_lower = col_str.lower()
                                        if any(x in col_lower for x in ['brand', 'item', 'product', 'category', 'market', 'period']):
                                            key_columns.append(col)
                                        elif any(x in col_str for x in ['$', 'CASE', 'TDP', '%ACV']) and not any(x in col_str for x in ['YA', 'Chg']):
                                            key_columns.append(col)
                                    
                                    if key_columns and len(key_columns) < len(df.columns):
                                        df_subset = df[key_columns]
                                        st.success(f"✅ Using {len(key_columns)} key columns")
                                    else:
                                        df_subset = df.iloc[:, :min(12, len(df.columns))]
                                        st.success(f"✅ Using first 12 columns")
                                    
                                    data_dict = df_subset.to_dict('records')
                                else:
                                    # Truly small dataset, use all data
                                    st.info(f"📊 Analyzing {len(df)} rows × {len(df.columns)} columns")
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

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "page" not in st.session_state:
        st.session_state.page = "main"  # Skip landing, go straight to main app
    
    # Route to appropriate page
    if st.query_params.get("admin") == "true":
        show_admin_page()
    elif not st.session_state.authenticated:
        show_auth_page()
    else:
        if st.session_state.page == "landing":
            show_landing_page()
        elif st.session_state.page == "subscription":
            show_subscription_page()
        else:
            main_app()
