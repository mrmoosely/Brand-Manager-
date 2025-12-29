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
        
    def _chat(self, module_name, user_message, system_prompt, max_tokens=4000):
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
        system_prompt = """You are an expert brand performance analyst specializing in Nielsen and IRI data analysis.

Your role is to:
1. Analyze market data for brand performance vs competitors
2. Identify clear drivers of performance (distribution, pricing, velocity, household penetration, etc.)
3. Provide actionable recommendations based on data insights
4. Highlight risks and opportunities
5. Present findings in a clear, executive-ready format

When analyzing data:
- Focus on YOY and period-over-period trends
- Compare brand performance to category and key competitors
- Identify statistical significance in changes
- Connect data points to strategic implications
- Provide specific, actionable next steps

Output format should include:
- Executive Summary (3-4 key takeaways)
- Performance Overview (brand vs category vs competitors)
- Key Drivers Analysis
- Risks & Opportunities
- Recommended Actions (prioritized)"""

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

        return self._chat("data_analysis", user_message, system_prompt)

    # ==================== MODULE 2: CREATIVE BRIEF GENERATOR ====================
    
    def generate_creative_brief(self, template_file=None, brief_inputs=None):
        """
        Generate creative or program briefs based on template
        
        Args:
            template_file: Path to brief template (Word, PDF, or text)
            brief_inputs: Dictionary of inputs to populate template
        """
        system_prompt = """You are an expert creative brief writer and brand strategist.

Your role is to:
1. Take user inputs and template structures to create comprehensive creative briefs
2. Ensure all sections are strategically sound and actionable
3. Write clear, inspiring creative direction
4. Define success metrics and guardrails
5. Provide context that empowers creative teams

A great creative brief includes:
- Background/Context (market situation, business challenge)
- Objective (what we need to achieve)
- Target Audience (deep psychographic understanding)
- Key Insight (human truth that drives the work)
- Single-Minded Proposition (one clear message)
- Supporting Reasons to Believe
- Tone & Manner (brand voice guidance)
- Mandatories (must-haves and must-not-haves)
- Success Metrics

Write in clear, confident language. Be specific, not generic."""

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

        return self._chat("creative_brief", user_message, system_prompt)

    # ==================== MODULE 3: BRAND POSITIONING ====================
    
    def develop_brand_positioning(self, brand_os_inputs=None, positioning_challenge=None):
        """
        Develop or refine brand positioning using Brand OS framework
        
        Args:
            brand_os_inputs: Dictionary with Brand OS elements (purpose, values, personality, etc.)
            positioning_challenge: Specific positioning challenge to address
        """
        system_prompt = """You are an expert brand strategist specializing in brand positioning and Brand OS development.

Your role is to:
1. Develop clear, differentiated brand positioning
2. Ensure internal consistency across all Brand OS elements
3. Create positioning that is ownable, credible, and compelling
4. Provide strategic rationale for positioning choices
5. Pressure-test positioning against competitive set

Brand OS Framework includes:
- Brand Purpose (why the brand exists beyond profit)
- Brand Vision (aspirational future state)
- Brand Values (what the brand stands for)
- Brand Personality (how the brand shows up)
- Target Audience (who we serve, psychographics)
- Brand Promise (what we deliver)
- Positioning Statement (competitive frame + POD)
- Key Messages (proof points and RTBs)
- Visual & Verbal Identity guidelines

Ensure positioning is:
- Differentiated (unique in category)
- Credible (can we deliver on it?)
- Relevant (does target care?)
- Sustainable (can we own it long-term?)

Provide strategic rationale for all recommendations."""

        inputs_text = f"Brand OS Inputs:\n{json.dumps(brand_os_inputs, indent=2)}\n\n" if brand_os_inputs else ""
        challenge_text = f"Positioning Challenge:\n{positioning_challenge}\n\n" if positioning_challenge else ""
        
        user_message = f"""Please develop brand positioning based on:

{inputs_text}{challenge_text}
Create a comprehensive Brand OS with clear strategic rationale."""

        return self._chat("brand_positioning", user_message, system_prompt)

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
        system_prompt = """You are an expert innovation strategist and product developer specializing in CPG brands.

Your role is to:
1. Generate breakthrough innovation ideas that solve real consumer needs
2. Ensure ideas are strategically sound and commercially viable
3. Consider the full innovation spectrum (core renovations to transformational)
4. Provide packaging concepts that bring ideas to life
5. Include go-to-market considerations

Innovation Framework:
- Consumer Insight (unmet need or friction point)
- Innovation Concept (product/service solution)
- Benefit Proposition (why consumers care)
- Reason to Believe (credibility)
- Packaging & Design (visual identity)
- Route to Market (distribution strategy)
- Business Case (volume/margin potential)

For each innovation:
1. Define the consumer problem being solved
2. Describe the product in detail
3. Explain the benefit hierarchy
4. Outline packaging approach (size, format, graphics, messaging)
5. Assess feasibility and business potential

Generate multiple ideas across the innovation spectrum:
- Core Renovation (optimizing existing)
- Adjacent Innovation (logical extension)
- Transformational (category disruption)"""

        brief_text = f"Innovation Brief:\n{innovation_brief}\n\n" if innovation_brief else ""
        category_text = f"Category: {category}\n" if category else ""
        target_text = f"Target Consumer: {target}\n" if target else ""
        constraints_text = f"Constraints: {constraints}\n\n" if constraints else ""
        
        user_message = f"""Please generate innovation ideas:

{brief_text}{category_text}{target_text}{constraints_text}
Generate 3-5 innovation concepts with detailed packaging descriptions."""

        return self._chat("innovation", user_message, system_prompt)

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
        system_prompt = """You are an expert presentation strategist and storyteller specializing in executive communications.

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
- Strong opening and closing"""

        obj_text = f"Presentation Objective:\n{objective}\n\n" if objective else ""
        msg_text = f"Key Messages:\n{key_messages}\n\n" if key_messages else ""
        aud_text = f"Audience: {audience}\n\n" if audience else ""
        template_text = f"Available Templates:\n{template_slides}\n\n" if template_slides else ""
        data_text = f"Data Points:\n{json.dumps(data_points, indent=2)}\n\n" if data_points else ""
        
        user_message = f"""Please generate a presentation deck:

{obj_text}{msg_text}{aud_text}{template_text}{data_text}
Create a complete deck structure with slide-by-slide content and recommendations."""

        return self._chat("presentation", user_message, system_prompt)

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
