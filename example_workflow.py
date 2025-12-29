#!/usr/bin/env python3
"""
Example Workflow: Complete Brand Management Cycle
Demonstrates using all modules together for a real brand scenario

Scenario: You're the brand manager for Traveller Whiskey preparing for:
1. Weekly business review
2. Summer campaign development
3. Innovation pipeline review
4. Executive presentation

This script shows how to use all modules in sequence for a complete workflow.
"""

import os
from brand_manager_assistant import BrandManagerAssistant
from powerpoint_generator import PowerPointGenerator, create_deck_from_outline
import json

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def save_to_file(content, filename):
    """Save output to file"""
    with open(f"outputs/{filename}", 'w') as f:
        f.write(content)
    print(f"💾 Saved to: outputs/{filename}")

# Create outputs directory
os.makedirs("outputs", exist_ok=True)

# Initialize assistant
assistant = BrandManagerAssistant()

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    BRAND MANAGER AI ASSISTANT                              ║
║                    Complete Workflow Example                               ║
╚════════════════════════════════════════════════════════════════════════════╝

Scenario: Traveller Whiskey Brand Manager
Tasks: Weekly review, campaign planning, innovation, executive presentation
""")

# ============================================================================
# STEP 1: WEEKLY BUSINESS REVIEW - Data Analysis
# ============================================================================

print_section("STEP 1: WEEKLY BUSINESS REVIEW - Market Data Analysis")

# Sample Nielsen-style data
market_data = {
    "period": "Latest 4 weeks ending 12/21/2024",
    "brand_performance": {
        "Traveller Whiskey": {
            "dollar_sales_mm": {"current": 45.2, "yoy_change": 15.3, "vs_category": "+12 pts"},
            "unit_sales_mm": {"current": 1.8, "yoy_change": 8.7},
            "market_share_pct": {"current": 12.3, "yoy_change": 1.2},
            "avg_price": {"current": 24.99, "yoy_change": 6.1},
            "distribution_acv_pct": {"current": 72.0, "yoy_change": 5.0},
            "velocity": {"current": 2.1, "yoy_change": 3.5}
        },
        "Jack Daniels": {
            "dollar_sales_mm": {"current": 105.8, "yoy_change": 3.2},
            "market_share_pct": {"current": 28.5, "yoy_change": -0.8},
            "distribution_acv_pct": {"current": 95.0, "yoy_change": 0.0}
        },
        "Jim Beam": {
            "dollar_sales_mm": {"current": 82.3, "yoy_change": 1.5},
            "market_share_pct": {"current": 22.1, "yoy_change": -1.1},
            "distribution_acv_pct": {"current": 89.0, "yoy_change": -2.0}
        },
        "Category Total": {
            "dollar_sales_mm": {"current": 372.5, "yoy_change": 3.3},
            "unit_sales_mm": {"current": 15.2, "yoy_change": 1.8}
        }
    },
    "key_channels": {
        "Food": {"share": 8.2, "yoy_change": 2.1},
        "Mass": {"share": 15.8, "yoy_change": 3.5},
        "Liquor": {"share": 11.1, "yoy_change": 0.5}
    }
}

print("📊 Analyzing market data...")
analysis = assistant.analyze_market_data(
    data_dict=market_data,
    analysis_focus="Distribution gains and velocity trends driving growth"
)

print("\n" + analysis)
save_to_file(analysis, "01_weekly_business_review.txt")

input("\n⏸️  Press Enter to continue to Campaign Planning...")

# ============================================================================
# STEP 2: CAMPAIGN DEVELOPMENT - Brand Positioning
# ============================================================================

print_section("STEP 2: CAMPAIGN DEVELOPMENT - Brand Positioning Review")

brand_inputs = {
    "brand_name": "Traveller Whiskey",
    "category": "Premium American Whiskey",
    "target_audience": """
    Primary: Males 35-50
    - HHI $100K+
    - College educated professionals
    - Urban/suburban dwellers
    - Adventure-oriented lifestyle
    - Value authenticity and craftsmanship
    - See themselves as 'doers' not just dreamers
    """,
    "brand_purpose": "Celebrate the journey, not just the destination",
    "brand_values": "Authenticity, Adventure, Craftsmanship, Independence",
    "brand_personality": "Rugged sophistication - confident but never arrogant, adventurous but never reckless",
    "current_positioning": "Premium American whiskey for men who live deliberately and chart their own course",
    "competitive_context": "Jack Daniels owns 'classic American', Jim Beam owns 'family tradition', need to own 'modern adventure'"
}

print("🎨 Developing brand positioning...")
positioning = assistant.develop_brand_positioning(
    brand_os_inputs=brand_inputs,
    positioning_challenge="Differentiate in premium whiskey segment against established heritage brands with clear positioning around 'personal journey' and modern masculinity"
)

print("\n" + positioning)
save_to_file(positioning, "02_brand_positioning.txt")

input("\n⏸️  Press Enter to continue to Creative Brief...")

# ============================================================================
# STEP 3: SUMMER CAMPAIGN - Creative Brief
# ============================================================================

print_section("STEP 3: SUMMER CAMPAIGN - Creative Brief Generation")

brief_inputs = {
    "campaign_name": "Summer 2025 'Your Journey' Campaign",
    "objective": """
    Drive trial among premium whiskey consideration set
    - Increase household penetration by 15% in target demo
    - Drive 20% lift in brand consideration
    - Achieve 12MM impressions in target audience
    """,
    "target": """
    Males 35-50, HHI $100K+, college educated
    Urban/suburban professionals with adventurous lifestyles
    Currently drinking Jack, Woodford, or Maker's Mark
    See whiskey choice as reflection of personal values
    """,
    "key_insight": """
    Premium whiskey drinkers don't just buy a drink - they buy into a narrative.
    They see their whiskey choice as a statement about the kind of person they are
    and the life they're living. It's not about where they've been (heritage),
    it's about where they're going (journey).
    """,
    "proposition": "Traveller is the whiskey for men charting their own course",
    "channels": ["Digital Video", "Social Media", "OOH (Key Markets)", "Experiential", "Influencer Partnerships"],
    "budget": "$2.5M production + $5M media",
    "timing": "Launch Memorial Day 2025, run through Labor Day",
    "tone": "Confident without being cocky, aspirational without being pretentious, authentic and real",
    "mandatories": """
    - Must feature product in use occasions
    - Must include 'Chart Your Own Course' tagline
    - Must show diverse definitions of adventure (not just extreme sports)
    - Must comply with responsible drinking guidelines
    - Cannot show anyone appearing under 30
    """
}

print("✍️  Generating creative brief...")
creative_brief = assistant.generate_creative_brief(
    brief_inputs=brief_inputs
)

print("\n" + creative_brief)
save_to_file(creative_brief, "03_summer_campaign_brief.txt")

input("\n⏸️  Press Enter to continue to Innovation...")

# ============================================================================
# STEP 4: INNOVATION PIPELINE - Ideation
# ============================================================================

print_section("STEP 4: INNOVATION PIPELINE - Concept Generation")

print("💡 Generating innovation concepts...")
innovation = assistant.generate_innovation_ideas(
    innovation_brief="""
    Expand Traveller portfolio to capture more consumption occasions
    and increase brand relevance with core target.
    
    Current portfolio: Core Traveller American Whiskey (750ml, $24.99)
    
    White space: Ready-to-drink occasions, on-the-go consumption, 
    new serve occasions (outdoor, travel, etc.)
    """,
    category="Premium Whiskey / Spirits-based RTD",
    target="Males 35-50, premium whiskey drinkers, active lifestyle",
    constraints="Must leverage existing Traveller brand equity, maintain premium positioning, target 40% margin minimum"
)

print("\n" + innovation)
save_to_file(innovation, "04_innovation_concepts.txt")

input("\n⏸️  Press Enter to continue to Executive Presentation...")

# ============================================================================
# STEP 5: EXECUTIVE PRESENTATION - PowerPoint Generation
# ============================================================================

print_section("STEP 5: EXECUTIVE PRESENTATION - Deck Creation")

# First, generate the deck structure
print("📑 Generating presentation structure...")
deck_outline = assistant.generate_presentation_deck(
    objective="""
    Secure CMO approval for:
    1. Increased summer media investment (+$2M)
    2. Summer campaign creative direction
    3. Innovation pipeline funding ($500K for RTD development)
    
    Decision needed by end of week to meet production timelines.
    """,
    key_messages="""
    Traveller is significantly outperforming category and competitors
    Distribution gains and strong velocity validate our strategy
    Summer campaign will capitalize on momentum with 'Your Journey' platform
    RTD innovation addresses key white space and consumption occasions
    Investment will drive +$20M incremental revenue over next 12 months
    """,
    audience="CMO, CFO, VP Marketing",
    data_points={
        "Current Market Share": "12.3%",
        "YOY Growth": "+15.3%",
        "Distribution Gain": "+5 pts to 72% ACV",
        "ROI Last Campaign": "3.8x",
        "Target Revenue Lift": "$20M",
        "Investment Request": "$7.5M total"
    },
    template_slides="Title, Section Divider, Key Metric, Data Chart, Two Column Compare, Recommendation"
)

print("\n" + deck_outline)
save_to_file(deck_outline, "05_executive_presentation_outline.txt")

# Now create actual PowerPoint file
print("\n📊 Creating PowerPoint file...")
ppt = PowerPointGenerator()

# Title slide
ppt.add_title_slide(
    "Traveller Whiskey: Investment Recommendation",
    "Q1 2025 Business Review & Summer Campaign Approval"
)

# Section: Business Performance
ppt.add_section_header("Business Performance")

# Performance highlights
ppt.add_content_slide(
    "Traveller Significantly Outperforming Category",
    [
        "Market share increased 1.2 points to 12.3% (+10% YOY)",
        "Dollar sales up 15.3% vs category +3.3%",
        "Distribution gains of 5 points driving 40% of growth",
        "Strong velocity (+3.5%) showing consumer demand"
    ]
)

# Data slide
ppt.add_data_slide(
    "Key Performance Metrics",
    {
        "Market Share": "12.3%",
        "YOY Growth": "+15.3%",
        "Distribution": "72% ACV",
        "Velocity": "+3.5%",
        "Price Realization": "+6.1%"
    }
)

# Two column: Drivers
ppt.add_two_column_slide(
    "Growth Drivers & Opportunities",
    [
        "✓ Distribution expansion in Mass channel",
        "✓ Premium positioning resonating",
        "✓ Strong velocity vs competitors",
        "✓ Price premium sustainable"
    ],
    [
        "→ 23 pts ACV gap vs category leader",
        "→ RTD/convenience occasions untapped",
        "→ Limited SKU variety vs competitors",
        "→ Need awareness boost in target demo"
    ]
)

# Section: Summer Campaign
ppt.add_section_header("Summer 2025 Campaign")

# Campaign overview
ppt.add_content_slide(
    "'Your Journey' Campaign Overview",
    [
        "Platform: Traveller is the whiskey for men charting their own course",
        "Target: Males 35-50, premium whiskey drinkers, $100K+ HHI",
        "Objective: +15% household penetration, +20% consideration",
        "Channels: Digital video, social, OOH, experiential, influencer",
        "Investment: $7.5M ($2.5M production + $5M media)"
    ]
)

# Section: Innovation
ppt.add_section_header("Innovation Pipeline")

# Innovation concepts
ppt.add_content_slide(
    "RTD Innovation: Capture New Occasions",
    [
        "Traveller & Cola RTD (4-pack 12oz cans)",
        "Target: On-the-go, outdoor, casual occasions",
        "Positioning: Premium whiskey cocktail without the bartender",
        "Margin: 42% (vs 38% core whiskey)",
        "Investment: $500K development + tooling"
    ]
)

# Section: Recommendation
ppt.add_section_header("Recommendation")

# Final recommendation
ppt.add_content_slide(
    "Investment Recommendation: $7.5M",
    [
        "Summer Campaign: $7M (media + production)",
        "RTD Development: $500K (tooling + launch)",
        "Expected Return: $20M incremental revenue (2.7x ROI)",
        "Timing: Approval needed by 1/31 for Memorial Day launch",
        "Risk: Low - proven platform, validated innovation concept"
    ]
)

# Save PowerPoint
ppt_filename = ppt.save("outputs/05_executive_presentation.pptx")
print(f"💾 Saved PowerPoint to: {ppt_filename}")

# ============================================================================
# WORKFLOW COMPLETE
# ============================================================================

print_section("🎉 WORKFLOW COMPLETE!")

print("""
Generated Outputs:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Weekly Business Review
   📄 outputs/01_weekly_business_review.txt
   → Market data analysis with drivers and actions

2. Brand Positioning
   📄 outputs/02_brand_positioning.txt
   → Complete Brand OS framework

3. Summer Campaign Brief
   📄 outputs/03_summer_campaign_brief.txt
   → Strategic creative brief ready for agency

4. Innovation Concepts
   📄 outputs/04_innovation_concepts.txt
   → RTD innovation ideas with packaging concepts

5. Executive Presentation
   📄 outputs/05_executive_presentation_outline.txt
   📊 outputs/05_executive_presentation.pptx
   → Complete deck structure + PowerPoint file

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
1. Review all outputs in the /outputs folder
2. Customize PowerPoint with your brand template
3. Share creative brief with agency
4. Schedule executive presentation
5. Begin RTD innovation development

Total Time: ~3-5 minutes
Total Cost: ~$0.15-0.30 in API calls
Total Value: Priceless ✨

This workflow demonstrates how all modules work together for real
brand management tasks. Customize the inputs for your brand!
""")

print("\n" + "="*80)
print("Thanks for using Brand Manager AI Assistant!")
print("="*80 + "\n")
