from dotenv import load_dotenv
load_dotenv()

#!/usr/bin/env python3
"""
Brand Manager AI Assistant - Web Interface
Streamlit-based UI for all brand management functions
"""

import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from brand_manager_assistant import BrandManagerAssistant
import pandas as pd
import json

# Page config
st.set_page_config(
    page_title="Brand Manager AI Assistant",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'assistant' not in st.session_state:
    st.session_state.assistant = BrandManagerAssistant()

# Sidebar
with st.sidebar:
    st.title("🎯 Brand Manager AI")
    st.markdown("---")
    
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
    st.markdown("### About")
    st.markdown("""
    AI-powered assistant for:
    - Market data analysis
    - Brief generation
    - Brand strategy
    - Innovation concepts
    - Presentation creation
    """)

# Main content
st.title("Brand Manager AI Assistant")

# MODULE 1: DATA PERFORMANCE ANALYSIS
if module == "📊 Data Performance Analysis":
    st.header("Data Performance Analysis")
    st.markdown("Upload Nielsen/IRI data or paste performance metrics for analysis")
    
    tab1, tab2 = st.tabs(["📁 Upload Data", "⌨️ Manual Entry"])
    
    with tab1:
        uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx'])
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.dataframe(df.head(10))
                st.success(f"Loaded {len(df)} rows of data")
            except Exception as e:
                st.error(f"Error loading file: {e}")
    
    with tab2:
        st.markdown("**Enter performance data as JSON:**")
        sample_json = {
            "brand_performance": {
                "Your Brand": {
                    "market_share": {"current": 12.3, "yoy_change": 1.2},
                    "dollar_sales": {"current": 45.2, "yoy_change": 15.3},
                    "volume": {"current": 38.1, "yoy_change": 8.7}
                },
                "Competitor A": {
                    "market_share": {"current": 28.5, "yoy_change": -0.8},
                    "dollar_sales": {"current": 105.8, "yoy_change": 3.2}
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
        placeholder="e.g., Distribution gains, pricing strategy, velocity trends"
    )
    
    if st.button("🔍 Analyze Performance", type="primary"):
        with st.spinner("Analyzing data..."):
            try:
                if uploaded_file:
                    # Use uploaded file
                    analysis = st.session_state.assistant.analyze_market_data(
                        data_file=uploaded_file,
                        analysis_focus=analysis_focus if analysis_focus else None
                    )
                else:
                    # Use manual entry
                    data_dict = json.loads(data_input)
                    analysis = st.session_state.assistant.analyze_market_data(
                        data_dict=data_dict,
                        analysis_focus=analysis_focus if analysis_focus else None
                    )
                
                st.markdown("### Analysis Results")
                st.markdown(analysis)
                
                # Download button
                st.download_button(
                    "📥 Download Analysis",
                    analysis,
                    file_name="performance_analysis.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"Error: {e}")

# MODULE 2: CREATIVE BRIEF GENERATOR
elif module == "✍️ Creative Brief Generator":
    st.header("Creative Brief Generator")
    st.markdown("Generate comprehensive creative briefs for campaigns and programs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        campaign_name = st.text_input("Campaign/Program Name*")
        objective = st.text_area("Business Objective*", height=100)
        target = st.text_area("Target Audience*", height=100)
        key_insight = st.text_area("Key Consumer Insight*", height=100)
    
    with col2:
        proposition = st.text_input("Single-Minded Proposition")
        channels = st.multiselect(
            "Marketing Channels",
            ["TV", "Digital Video", "Social Media", "OOH", "Print", "Radio", "Experiential", "Influencer"]
        )
        budget = st.text_input("Budget")
        timing = st.text_input("Campaign Timing")
    
    tone = st.text_area("Tone & Manner")
    mandatories = st.text_area("Mandatories / Must-Haves")
    
    template_file = st.file_uploader("Upload Brief Template (optional)", type=['txt', 'docx', 'pdf'])
    
    if st.button("✍️ Generate Brief", type="primary"):
        if not all([campaign_name, objective, target, key_insight]):
            st.error("Please fill in all required fields (*)")
        else:
            with st.spinner("Generating creative brief..."):
                brief_inputs = {
                    "campaign_name": campaign_name,
                    "objective": objective,
                    "target": target,
                    "key_insight": key_insight,
                    "proposition": proposition,
                    "channels": channels,
                    "budget": budget,
                    "timing": timing,
                    "tone": tone,
                    "mandatories": mandatories
                }
                
                brief = st.session_state.assistant.generate_creative_brief(
                    template_file=template_file,
                    brief_inputs=brief_inputs
                )
                
                st.markdown("### Generated Brief")
                st.markdown(brief)
                
                st.download_button(
                    "📥 Download Brief",
                    brief,
                    file_name=f"{campaign_name.replace(' ', '_')}_brief.txt",
                    mime="text/plain"
                )

# MODULE 3: BRAND POSITIONING
elif module == "🎨 Brand Positioning":
    st.header("Brand Positioning Workshop")
    st.markdown("Develop comprehensive brand positioning using Brand OS framework")
    
    st.subheader("Brand OS Inputs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        brand_name = st.text_input("Brand Name*")
        category = st.text_input("Category*")
        target_audience = st.text_area("Target Audience*", height=100)
        brand_purpose = st.text_area("Brand Purpose", height=100)
    
    with col2:
        brand_vision = st.text_area("Brand Vision", height=100)
        brand_values = st.text_area("Brand Values (comma separated)")
        brand_personality = st.text_area("Brand Personality")
        current_positioning = st.text_area("Current Positioning (if applicable)", height=100)
    
    positioning_challenge = st.text_area(
        "Positioning Challenge / Brief",
        placeholder="e.g., Differentiate against established competitors in crowded market",
        height=150
    )
    
    if st.button("🎨 Develop Positioning", type="primary"):
        if not all([brand_name, category, target_audience]):
            st.error("Please fill in all required fields (*)")
        else:
            with st.spinner("Developing brand positioning..."):
                brand_os_inputs = {
                    "brand_name": brand_name,
                    "category": category,
                    "target_audience": target_audience,
                    "brand_purpose": brand_purpose,
                    "brand_vision": brand_vision,
                    "brand_values": brand_values,
                    "brand_personality": brand_personality,
                    "current_positioning": current_positioning
                }
                
                positioning = st.session_state.assistant.develop_brand_positioning(
                    brand_os_inputs=brand_os_inputs,
                    positioning_challenge=positioning_challenge if positioning_challenge else None
                )
                
                st.markdown("### Brand Positioning")
                st.markdown(positioning)
                
                st.download_button(
                    "📥 Download Positioning",
                    positioning,
                    file_name=f"{brand_name.replace(' ', '_')}_positioning.txt",
                    mime="text/plain"
                )

# MODULE 4: INNOVATION IDEATION
elif module == "💡 Innovation Ideation":
    st.header("Innovation Ideation & Packaging")
    st.markdown("Generate innovation concepts with packaging descriptions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.text_input("Category*")
        target_consumer = st.text_area("Target Consumer*", height=100)
        innovation_brief = st.text_area("Innovation Brief / Challenge*", height=150)
    
    with col2:
        innovation_type = st.multiselect(
            "Innovation Type",
            ["Core Renovation", "Adjacent Innovation", "Transformational Innovation"],
            default=["Adjacent Innovation"]
        )
        constraints = st.text_area("Constraints (cost, capabilities, timing, etc.)", height=100)
        num_concepts = st.slider("Number of concepts to generate", 1, 5, 3)
    
    if st.button("💡 Generate Innovation Ideas", type="primary"):
        if not all([category, target_consumer, innovation_brief]):
            st.error("Please fill in all required fields (*)")
        else:
            with st.spinner("Generating innovation concepts..."):
                ideas = st.session_state.assistant.generate_innovation_ideas(
                    innovation_brief=f"{innovation_brief}\n\nGenerate {num_concepts} concepts across these types: {', '.join(innovation_type)}",
                    category=category,
                    target=target_consumer,
                    constraints=constraints if constraints else None
                )
                
                st.markdown("### Innovation Concepts")
                st.markdown(ideas)
                
                st.download_button(
                    "📥 Download Concepts",
                    ideas,
                    file_name="innovation_concepts.txt",
                    mime="text/plain"
                )

# MODULE 5: POWERPOINT DECK GENERATOR
elif module == "📑 PowerPoint Deck Generator":
    st.header("PowerPoint Deck Generator")
    st.markdown("Generate presentation structure and content for business meetings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        presentation_title = st.text_input("Presentation Title*")
        objective = st.text_area("Meeting Objective*", height=100)
        audience = st.text_input("Audience*", placeholder="e.g., CMO, Executive Team, Board")
    
    with col2:
        num_slides = st.slider("Target Number of Slides", 5, 30, 15)
        deck_type = st.selectbox(
            "Deck Type",
            ["Business Update", "Strategic Recommendation", "Campaign Review", "Performance Analysis", "Budget Request"]
        )
    
    key_messages = st.text_area(
        "Key Messages (one per line)*",
        height=150,
        placeholder="Message 1\nMessage 2\nMessage 3"
    )
    
    data_points = st.text_area(
        "Data Points to Include",
        height=150,
        placeholder='{"metric": "value", "trend": "direction"}'
    )
    
    template_slides = st.text_area(
        "Available Template Slide Types",
        value="Title Slide, Section Divider, Key Metric, 2-Column Compare, Data Visualization, Executive Summary, Recommendation",
        height=100
    )
    
    if st.button("📑 Generate Deck", type="primary"):
        if not all([presentation_title, objective, audience, key_messages]):
            st.error("Please fill in all required fields (*)")
        else:
            with st.spinner("Generating presentation deck..."):
                try:
                    data_dict = json.loads(data_points) if data_points else None
                except:
                    data_dict = None
                
                deck = st.session_state.assistant.generate_presentation_deck(
                    objective=f"{objective}\n\nTarget: {num_slides} slides\nDeck Type: {deck_type}",
                    key_messages=key_messages,
                    audience=audience,
                    template_slides=template_slides,
                    data_points=data_dict
                )
                
                st.markdown("### Presentation Structure")
                st.markdown(deck)
                
                st.download_button(
                    "📥 Download Deck Outline",
                    deck,
                    file_name=f"{presentation_title.replace(' ', '_')}_deck.txt",
                    mime="text/plain"
                )
                
                st.info("💡 Tip: Use this structure to build your deck in PowerPoint with your branded templates")

# Footer
st.markdown("---")
st.markdown("**Brand Manager AI Assistant** | Powered by Claude Sonnet 4.5")
