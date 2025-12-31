#!/usr/bin/env python3
"""
Brand Manager AI Assistant
A comprehensive tool for day-to-day brand management activities

Modules:
1. Data Performance Analysis (Nielsen/IRI data)
2. Creative/Program Brief Generator
3. Brand Positioning Workshop
4. Innovation Ideation & Packaging
5. PowerPoint Deck Generator
"""

import anthropic
import os
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

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

    # ==================== MODULE 1: DATA PERFORMANCE ANALYSIS ====================
    
    def analyze_market_data(self, data_file=None, data_dict=None, analysis_focus=None):
        """
        Analyze Nielsen/IRI market data for brand and competitive performance
        
        Args:
            data_file: Path to CSV/Excel data file
            data_dict: Dictionary of data if not using file
            analysis_focus: Specific areas to focus on (e.g., "YOY growth", "market share shifts")
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
        
        user_message = f"""Please analyze the following market data:

{data_summary}
{focus_text}

Provide a comprehensive performance analysis with clear drivers and actionable recommendations."""

        return self._chat("data_analysis", user_message, system_prompt, max_tokens=8000)

    # ==================== MODULE 2: CREATIVE BRIEF GENERATOR ====================
    
    def generate_creative_brief(self, template_file=None, brief_inputs=None):
        """
        Generate creative or program briefs based on template
        
        Args:
            template_file: Path to brief template (Word, PDF, or text)
            brief_inputs: Dictionary of inputs to populate template
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
        
        user_message = f"""Please generate a creative brief using the following information:
{template_text}
{inputs_text}

Create a comprehensive, actionable creative brief that will inspire great work."""

        return self._chat("creative_brief", user_message, system_prompt, max_tokens=8000)

    # ==================== MODULE 3: BRAND POSITIONING ====================
    
    def develop_brand_positioning(self, brand_os_inputs=None, positioning_challenge=None):
        """
        Develop or refine brand positioning using Brand OS framework
        
        Args:
            brand_os_inputs: Dictionary with Brand OS elements (purpose, values, personality, etc.)
            positioning_challenge: Specific positioning challenge to address
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
        
        user_message = f"""Please develop brand positioning based on:

{inputs_text}{challenge_text}
Create a comprehensive Brand OS with clear strategic rationale."""

        return self._chat("brand_positioning", user_message, system_prompt, max_tokens=8000)

    # ==================== MODULE 4: INNOVATION IDEATION ====================
    
    def generate_innovation_ideas(self, innovation_brief=None, category=None, target=None, constraints=None):
        """
        Generate innovation ideas with packaging concepts
        
        Args:
            innovation_brief: Strategic brief for innovation
            category: Product category
            target: Target consumer
            constraints: Any constraints (cost, capabilities, etc.)
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
        
        user_message = f"""Please generate innovation ideas:

{brief_text}{category_text}{target_text}{constraints_text}
Generate 3-5 innovation concepts with detailed packaging descriptions."""

        return self._chat("innovation", user_message, system_prompt, max_tokens=8000)

    # ==================== MODULE 5: POWERPOINT DECK GENERATOR ====================
    
    def generate_presentation_deck(self, objective=None, key_messages=None, audience=None, 
                                  template_slides=None, data_points=None):
        """
        Generate PowerPoint deck structure and content
        
        Args:
            objective: Meeting/presentation objective
            key_messages: Main points to communicate
            audience: Who you're presenting to
            template_slides: Available slide templates
            data_points: Data to include
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
        
        user_message = f"""Please generate a presentation deck:

{obj_text}{msg_text}{aud_text}{template_text}{data_text}
Create a complete deck structure with slide-by-slide content and recommendations."""

        return self._chat("presentation", user_message, system_prompt, max_tokens=8000)

    # ==================== MODULE 6: COMPETITIVE INTELLIGENCE ====================
    
    def analyze_competitor(self, competitor_brand, user_brand=None, category=None, 
                          focus_areas=None, generate_ai_prompt=False, reference_context=None):
        """
        Analyze competitor positioning, campaigns, and strategy
        
        Args:
            competitor_brand: Name of competitor to analyze
            user_brand: Your brand name for comparison
            category: Product category
            focus_areas: Specific areas to focus on
            generate_ai_prompt: Whether to generate presentation prompt
            reference_context: Additional reference materials
        """
        system_prompt = f"""You are an expert competitive intelligence analyst specializing in brand strategy and marketing campaigns.

CURRENT DATE: {self.current_date}

CRITICAL RECENCY REQUIREMENTS:
- Focus ONLY on campaigns and activities from the last 6-12 months
- Prioritize campaigns launched in the last 3 months
- If searching the web, explicitly look for "2025", "recent", "latest", "new campaign"
- Flag any information that appears older than 12 months as potentially outdated
- Emphasize current market positioning and active campaigns

Your role is to:
1. Analyze competitor's current brand positioning and messaging
2. Identify their MOST RECENT marketing campaigns and creative strategies
3. Assess media spend and channel mix for CURRENT activities
4. Provide strategic implications and competitive threats
5. Recommend counter-strategies based on RECENT competitor moves

Analysis Framework:
- Brand Positioning (how they position themselves NOW)
- Recent Campaign Analysis (last 6 months)
  * Campaign themes and messaging
  * Creative approach and tonality
  * Media channels and spend estimates
  * Target audience and reach
- Current Competitive Advantages
- Strategic Implications for your brand
- Recommended Actions

IMPORTANT: 
- Use web search to find the LATEST campaigns, press releases, and news
- Include specific dates when discussing campaigns (e.g., "Q4 2025 campaign")
- If you can't find recent information, state that explicitly
- Do not rely on older historical campaigns unless specifically requested"""

        user_text = f"Your Brand: {user_brand}\n" if user_brand else ""
        cat_text = f"Category: {category}\n" if category else ""
        focus_text = f"\nSpecific Focus Areas:\n{focus_areas}\n" if focus_areas else ""
        ref_text = f"\n\nReference Context:\n{reference_context}\n" if reference_context else ""
        
        prompt_instruction = """

Also generate a Gamma.ai presentation prompt for a competitive intelligence deck with slides covering:
- Competitor overview and positioning
- Recent campaign highlights with visuals
- Media strategy and spend
- Competitive threats and opportunities
- Recommended response strategy""" if generate_ai_prompt else ""
        
        user_message = f"""Please analyze the following competitor:

Competitor Brand: {competitor_brand}
{user_text}{cat_text}{focus_text}{ref_text}

IMPORTANT: Use web search to find the MOST RECENT campaigns, news, and marketing activities from the last 6-12 months. Include specific dates and timeframes in your analysis.{prompt_instruction}"""

        return self._chat("competitive_intel", user_message, system_prompt, max_tokens=8000)

    # ==================== MODULE 7: CREATIVE ASSET REVIEW ====================
    
    def review_creative_asset(self, creative_description, objective, target_consumer, 
                             medium, brand_context=None, generate_ai_prompt=False, 
                             reference_context=None):
        """
        Review and provide feedback on creative assets
        
        Args:
            creative_description: Description or copy of the asset
            objective: Campaign objective
            target_consumer: Target audience description
            medium: Type of creative (TV, digital, social, print, etc.)
            brand_context: Brand guidelines and positioning
            generate_ai_prompt: Whether to generate presentation prompt
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
        
        prompt_instruction = """

Also generate a Gamma.ai presentation prompt for a creative review deck with slides covering:
- Creative overview and context
- Persona-based evaluation results
- Key strengths and opportunities
- Specific improvement recommendations
- Optimized creative concepts""" if generate_ai_prompt else ""
        
        user_message = f"""Please review the following creative asset:

Medium: {medium}
Campaign Objective: {objective}
Target Consumer: {target_consumer}

Creative Description:
{creative_description}{brand_text}{ref_text}

Provide a comprehensive creative review with specific recommendations for improvement.{prompt_instruction}"""

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

def example_usage():
    """Example of how to use the Brand Manager Assistant"""
    
    # Initialize
    assistant = BrandManagerAssistant()
    
    # Example 1: Data Analysis
    print("=" * 80)
    print("MODULE 1: DATA PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    sample_data = {
        "brand_performance": {
            "Traveller Whiskey": {
                "market_share": {"current": 12.3, "yoy_change": +1.2},
                "dollar_sales": {"current": 45.2, "yoy_change": +15.3},
                "volume": {"current": 38.1, "yoy_change": +8.7},
                "ACV": {"current": 72.0, "yoy_change": +5.0}
            },
            "Jack Daniels": {
                "market_share": {"current": 28.5, "yoy_change": -0.8},
                "dollar_sales": {"current": 105.8, "yoy_change": +3.2}
            }
        }
    }
    
    analysis = assistant.analyze_market_data(
        data_dict=sample_data,
        analysis_focus="Distribution gains and velocity trends"
    )
    print(analysis)
    
    # Example 2: Creative Brief
    print("\n" + "=" * 80)
    print("MODULE 2: CREATIVE BRIEF GENERATOR")
    print("=" * 80)
    
    brief_inputs = {
        "campaign_name": "Traveller Summer Campaign 2025",
        "objective": "Drive trial among premium whiskey drinkers",
        "target": "Males 35-50, $100K+ HHI, adventure-seekers",
        "key_insight": "Premium whiskey drinkers see their drink choice as reflection of personal journey",
        "channels": ["Digital Video", "OOH", "Social"],
        "budget": "$2.5M",
        "timing": "June-August 2025"
    }
    
    brief = assistant.generate_creative_brief(brief_inputs=brief_inputs)
    print(brief)
    
    # Example 3: Brand Positioning
    print("\n" + "=" * 80)
    print("MODULE 3: BRAND POSITIONING")
    print("=" * 80)
    
    brand_os = {
        "brand_name": "MIDST Mental Energy",
        "category": "Functional Beverages / Mental Energy",
        "target": "Males 32-45, high-performers, knowledge workers",
        "current_challenge": "Position against Red Bull and Monster in mental energy space"
    }
    
    positioning = assistant.develop_brand_positioning(
        brand_os_inputs=brand_os,
        positioning_challenge="Differentiate in crowded energy drink market with mental focus positioning"
    )
    print(positioning)
    
    print("\n" + "=" * 80)
    print("All modules demonstrated. Check outputs above.")
    print("=" * 80)


if __name__ == "__main__":
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Please set ANTHROPIC_API_KEY environment variable")
        print("export ANTHROPIC_API_KEY='your-key-here'")
    else:
        example_usage()
