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
    
    def analyze_market_data(self, data_file=None, data_dict=None, analysis_focus=None, generate_ai_prompt=False):
        """
        Analyze Nielsen/IRI market data for brand and competitive performance
        
        Args:
            data_file: Path to CSV/Excel data file
            data_dict: Dictionary of data if not using file
            analysis_focus: Specific areas to focus on (e.g., "YOY growth", "market share shifts")
            generate_ai_prompt: If True, also generate Gamma.ai/Beautiful.ai presentation prompt
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
        
        # Check data size - if very large, limit further and disable AI prompt
        data_size_estimate = len(data_summary)
        if data_size_estimate > 100000:  # If data is very large (>100k chars)
            # Further limit the data
            if isinstance(data_dict, list) and len(data_dict) > 100:
                data_dict = data_dict[:100]  # Limit to top 100 rows
                data_summary = json.dumps(data_dict, indent=2)
                data_summary += "\n\n[Note: Data limited to top 100 entries for analysis]"
            # Disable AI prompt for very large datasets to stay under token limit
            generate_ai_prompt = False
        
        focus_text = f"\n\nSpecific Analysis Focus: {analysis_focus}" if analysis_focus else ""
        
        ai_prompt_instruction = ""
        if generate_ai_prompt:
            # Concise version of AI prompt instruction
            ai_prompt_instruction = """

ADDITIONALLY: After analysis, create a Gamma.ai/Beautiful.ai prompt.

Format:
═══════════════════════════════════════════════════════════════════════════
GAMMA.AI PROMPT
═══════════════════════════════════════════════════════════════════════════

Create a [8-10] slide business review presentation.

Style: Professional, data-driven
Color scheme: Corporate colors

Slide 1: [Title]: [Key headline]
- [Metric 1]
- [Metric 2]
Include: [Chart type]

[Continue for key slides covering: performance, drivers, opportunities, recommendations]

═══════════════════════════════════════════════════════════════════════════

Include all key insights in slide format."""
        
        user_message = f"""Please analyze the following market data:

{data_summary}
{focus_text}

Provide a comprehensive performance analysis with clear drivers and actionable recommendations.{ai_prompt_instruction}"""

        return self._chat("data_analysis", user_message, system_prompt)

    # ==================== MODULE 2: CREATIVE BRIEF GENERATOR ====================
    
    def generate_creative_brief(self, template_file=None, brief_inputs=None, generate_ai_prompt=False):
        """
        Generate creative or program briefs based on template
        
        Args:
            template_file: Path to brief template (Word, PDF, or text)
            brief_inputs: Dictionary of inputs to populate template
            generate_ai_prompt: If True, also generate Gamma.ai/Beautiful.ai presentation prompt
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
        
        ai_prompt_instruction = ""
        if generate_ai_prompt:
            ai_prompt_instruction = """

ADDITIONALLY: Create a Gamma.ai/Beautiful.ai presentation prompt for this creative brief.

Format:

═══════════════════════════════════════════════════════════════════════════
GAMMA.AI / BEAUTIFUL.AI PROMPT (Copy and paste this)
═══════════════════════════════════════════════════════════════════════════

Create an 8-10 slide campaign brief presentation for agency review.

Objective: Present campaign brief and get agency alignment

Style: Creative, inspiring, strategic
Color scheme: Brand colors with vibrant, energetic accents

Slide-by-slide content:

1. Campaign Overview: [Campaign name]
   - Objective: [Objective from brief]
   - Target: [Target audience]
   - Timeline: [Timeline]
   - Budget: [Budget]
   Include: Hero image or campaign visual

2. Consumer Insight: [Insight headline]
   - The truth: [Key insight]
   - Why it matters: [Relevance]
   - The opportunity: [What this unlocks]
   Include: Consumer imagery

3. Creative Challenge: [What we're asking for]
   - [Key message]
   - [Tone and manner]
   - [Mandatories]

[Continue for all sections of brief]

Visual style: Inspiring, creative, strategic
Tone: Collaborative, energizing, clear

═══════════════════════════════════════════════════════════════════════════"""
        
        user_message = f"""Please generate a creative brief using the following information:
{template_text}
{inputs_text}

Create a comprehensive, actionable creative brief that will inspire great work.{ai_prompt_instruction}"""

        return self._chat("creative_brief", user_message, system_prompt)

    # ==================== MODULE 3: BRAND POSITIONING ====================
    
    def develop_brand_positioning(self, brand_os_inputs=None, positioning_challenge=None, generate_ai_prompt=False):
        """
        Develop or refine brand positioning using Brand OS framework
        
        Args:
            brand_os_inputs: Dictionary with Brand OS elements (purpose, values, personality, etc.)
            positioning_challenge: Specific positioning challenge to address
            generate_ai_prompt: If True, also generate Gamma.ai/Beautiful.ai presentation prompt
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
        
        ai_prompt_instruction = ""
        if generate_ai_prompt:
            ai_prompt_instruction = """

ADDITIONALLY: Create a Gamma.ai/Beautiful.ai presentation prompt for this brand positioning.

Format:

═══════════════════════════════════════════════════════════════════════════
GAMMA.AI / BEAUTIFUL.AI PROMPT (Copy and paste this)
═══════════════════════════════════════════════════════════════════════════

Create a 10-12 slide brand strategy presentation for internal team alignment.

Objective: Align organization on brand positioning and Brand OS

Style: Strategic, inspiring, professional
Color scheme: Brand colors with clean, modern aesthetic

Slide-by-slide content:

1. Brand Purpose: [Purpose statement]
   - Why we exist: [Purpose]
   - What we stand for: [Values]
   Include: Inspiring brand imagery

2. Target Consumer: [Who we serve]
   - Demographics: [Basic demographics]
   - Psychographics: [Attitudes, values, lifestyle]
   - Their needs: [What they're looking for]
   Include: Consumer lifestyle imagery

3. Brand Positioning: [Positioning statement]
   - Competitive frame: [Category context]
   - Point of difference: [Unique benefit]
   - Reason to believe: [Credibility]
   Include: Competitive positioning map

4. Brand Personality: [How we show up]
   - [Personality traits]
   - Tone: [Voice characteristics]
   - What we are / What we're not

[Continue for all Brand OS elements]

Visual style: Inspiring, strategic, cohesive
Tone: Confident, purposeful, authentic

═══════════════════════════════════════════════════════════════════════════"""
        
        user_message = f"""Please develop brand positioning based on:

{inputs_text}{challenge_text}
Create a comprehensive Brand OS with clear strategic rationale.{ai_prompt_instruction}"""

        return self._chat("brand_positioning", user_message, system_prompt)

    # ==================== MODULE 4: INNOVATION IDEATION ====================
    
    def generate_innovation_ideas(self, innovation_brief=None, category=None, target=None, constraints=None, generate_ai_prompt=False):
        """
        Generate innovation ideas with packaging concepts
        
        Args:
            innovation_brief: Strategic brief for innovation
            category: Product category
            target: Target consumer
            constraints: Any constraints (cost, capabilities, etc.)
            generate_ai_prompt: If True, also generate Gamma.ai/Beautiful.ai presentation prompt
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
        
        ai_prompt_instruction = ""
        if generate_ai_prompt:
            ai_prompt_instruction = """

ADDITIONALLY: Create a Gamma.ai/Beautiful.ai presentation prompt for these innovation concepts.

Format:

═══════════════════════════════════════════════════════════════════════════
GAMMA.AI / BEAUTIFUL.AI PROMPT (Copy and paste this)
═══════════════════════════════════════════════════════════════════════════

Create a 12-15 slide innovation presentation for leadership review.

Objective: Get approval to develop innovation concepts

Style: Innovative, exciting, strategic
Color scheme: Bold, modern colors that signal innovation

Slide-by-slide content:

1. Innovation Opportunity: [Opportunity headline]
   - Consumer need: [Unmet need]
   - Market size: [Potential]
   - Strategic fit: [Why now]
   Include: Consumer insight imagery

2. Concept 1: [Innovation name]
   - The idea: [Product description]
   - Key benefit: [Main benefit]
   - Target: [Who it's for]
   - Packaging: [Format, size, design]
   Include: Conceptual packaging mockup description

3. Concept 1 Details: Why This Wins
   - Reason to believe: [Credibility]
   - Go-to-market: [Route]
   - Business case: [Volume/margin estimate]
   Include: Business model chart

[Repeat pattern for each concept]

Final Slide: Recommended Next Steps
   - [Action 1]
   - [Action 2]
   - Timeline and investment

Visual style: Innovative, bold, exciting
Tone: Confident, pioneering, strategic

═══════════════════════════════════════════════════════════════════════════"""
        
        user_message = f"""Please generate innovation ideas:

{brief_text}{category_text}{target_text}{constraints_text}
Generate 3-5 innovation concepts with detailed packaging descriptions.{ai_prompt_instruction}"""

        return self._chat("innovation", user_message, system_prompt)

    # ==================== MODULE 5: POWERPOINT DECK GENERATOR ====================
    
    def generate_presentation_deck(self, objective=None, key_messages=None, audience=None, 
                                  template_slides=None, data_points=None, generate_ai_prompt=False):
        """
        Generate PowerPoint deck structure and content
        
        Args:
            objective: Meeting/presentation objective
            key_messages: Main points to communicate
            audience: Who you're presenting to
            template_slides: Available slide templates
            data_points: Data to include
            generate_ai_prompt: If True, also generate Gamma.ai/Beautiful.ai compatible prompt
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
        
        ai_prompt_instruction = ""
        if generate_ai_prompt:
            ai_prompt_instruction = """

ADDITIONALLY: After the deck outline, create a clean, copy-paste ready prompt for Gamma.ai or Beautiful.ai.

Format it EXACTLY as shown below, in a clearly marked section:

═══════════════════════════════════════════════════════════════════════════
GAMMA.AI / BEAUTIFUL.AI PROMPT (Copy and paste this into the AI tool)
═══════════════════════════════════════════════════════════════════════════

Create a [number] slide presentation on [topic] for [audience].

Objective: [Clear objective]

Style: [Professional/Modern/Creative], [color preferences], [tone]

Slide-by-slide content:

1. [Slide title]
   - [Key point 1]
   - [Key point 2]
   - [Key point 3]
   Include: [Visual elements, charts, images]

2. [Slide title]
   - [Key point 1]
   - [Key point 2]
   Include: [Visual elements]

[Continue for all slides...]

Visual style: [Specific design guidance]
Color scheme: [Primary colors to use]
Font style: [Modern/Classic/Bold]

═══════════════════════════════════════════════════════════════════════════

The prompt should be:
- Complete and self-contained
- Copy-paste ready (no modifications needed)
- Formatted in clean markdown
- Include specific visual guidance
- Specify exact slide count and structure
"""
        
        user_message = f"""Please generate a presentation deck:

{obj_text}{msg_text}{aud_text}{template_text}{data_text}
Create a complete deck structure with slide-by-slide content and recommendations.{ai_prompt_instruction}"""

        return self._chat("presentation", user_message, system_prompt)
    
    # ==================== MODULE 6: COMPETITIVE INTELLIGENCE ====================
    
    def analyze_competitor(self, competitor_brand, user_brand=None, category=None, focus_areas=None, generate_ai_prompt=False):
        """
        Analyze competitor brand positioning, campaigns, and media spend
        
        Args:
            competitor_brand: Competitor brand name
            user_brand: User's brand name for comparative analysis
            category: Product category
            focus_areas: Specific areas to analyze
            generate_ai_prompt: If True, also generate Gamma.ai/Beautiful.ai presentation prompt
        """
        system_prompt = """You are an expert competitive intelligence analyst specializing in brand strategy and marketing analysis.

Your role is to:
1. Analyze competitor brand positioning and strategy
2. Identify recent campaigns and marketing initiatives
3. Estimate media spend allocation with rigorous methodology
4. Assess competitive threats and opportunities relative to user's brand
5. Provide actionable competitive insights

For each competitor analysis, provide:

**Brand Positioning Analysis:**
- Target consumer
- Key benefits and messaging
- Brand personality and tone
- Positioning vs category
- Points of differentiation
- Positioning overlap/conflict with user's brand (if provided)

**Recent Campaigns & Initiatives:**
- Campaign themes and creative approach
- Media channels utilized
- Geographic focus (US vs International)
- Estimated campaign timing and duration
- Key messages and claims
- Campaign insights relevant to user's brand

**Estimated Media Spend (with rigorous methodology):**

For spend estimation, use this framework:

1. Total Annual Spend Estimate
   - Base estimate on: Company size, market position, category norms
   - Benchmark against: Public spending data, industry reports, visible media presence
   - Confidence level: High/Medium/Low with rationale

2. US vs Global Breakdown
   - US Spend: $XX million (XX% of total)
   - International Spend: $XX million (XX% of total)
     - Europe: $X million
     - Asia-Pacific: $X million
     - Latin America: $X million
     - Other: $X million
   - Rationale for geographic split

3. Channel Breakdown (US Market)
   - TV/Linear: $XX million (XX%) - National vs local, dayparts, estimated GRPs
   - Digital Display: $XX million (XX%) - Programmatic, direct buys
   - Search (SEM): $XX million (XX%) - Branded vs non-branded
   - Social Media: $XX million (XX%) - Platform breakdown (FB/IG, Twitter, TikTok, etc.)
   - Video/Streaming: $XX million (XX%) - YouTube, Hulu, Connected TV
   - Out of Home: $XX million (XX%) - Billboard, transit, place-based
   - Print: $XX million (XX%) - Magazines, newspapers
   - Sponsorships: $XX million (XX%) - Sports, events, partnerships
   - Other: $XX million (XX%)

4. Spend Trends
   - YoY change estimate (+/- XX%)
   - Channel mix shifts
   - Increased/decreased investment areas
   - Share of voice vs category average

5. Methodology & Confidence
   - Data sources used in estimation
   - Assumptions made
   - Confidence level (High/Medium/Low) for each channel
   - Caveats and limitations

**Strategic Implications (Relative to User's Brand):**
- Direct competitive threats
- White space opportunities
- Recommended strategic responses
- Investment priorities
- Monitoring requirements
- How competitor's strategy impacts user's brand positioning/share

Base analysis on available market intelligence, public campaigns, industry benchmarks, and strategic reasoning."""

        user_brand_text = f" relative to {user_brand}" if user_brand else ""
        category_text = f" in the {category} category" if category else ""
        focus_text = f"\n\nSpecific focus areas: {focus_areas}" if focus_areas else ""
        
        comparative_instruction = ""
        if user_brand:
            comparative_instruction = f"""

IMPORTANT: Provide comparative analysis throughout. How does {competitor_brand} compare to {user_brand}?
- Positioning differences and overlaps
- Relative spend levels
- Campaign approaches
- Competitive threats to {user_brand}
- Opportunities for {user_brand} to exploit"""

        ai_prompt_instruction = ""
        if generate_ai_prompt:
            ai_prompt_instruction = """

ADDITIONALLY: Create a Gamma.ai/Beautiful.ai presentation prompt for this competitive intelligence.

Format:

═══════════════════════════════════════════════════════════════════════════
GAMMA.AI / BEAUTIFUL.AI PROMPT (Copy and paste this)
═══════════════════════════════════════════════════════════════════════════

Create a 12-15 slide competitive intelligence presentation for leadership.

Objective: Inform competitive strategy and response planning

Style: Strategic, analytical, professional
Color scheme: Corporate blue with red accents for threats, green for opportunities

Slide-by-slide content:

1. Competitive Landscape: [Competitor name] Overview
   - Market position: [Share, size]
   - Brand positioning: [Key positioning]
   - Target consumer: [Who they target]
   Include: Competitive positioning map

2. Brand Positioning Analysis: How They Win
   - Key benefits: [Benefits]
   - Brand personality: [Personality]
   - Points of differentiation: [PODs]
   Include: Brand attributes comparison

3. Media Spend Estimate: [Total $ figure]
   - Total annual: $XX million
   - US: $XX million (XX%)
   - Global: $XX million (XX%)
   - Confidence: [High/Medium/Low]
   Include: Pie chart of geographic split

4. US Channel Breakdown: Where They Invest
   - TV: $XX million (XX%)
   - Digital: $XX million (XX%)
   - Social: $XX million (XX%)
   - [Other channels]
   Include: Bar chart of channel investment

5. Recent Campaigns: What They're Saying
   - [Campaign 1 summary]
   - [Campaign 2 summary]
   - Key themes: [Themes]
   Include: Campaign imagery or descriptions

6. Strategic Implications: What This Means for Us
   - Threats: [Key threats]
   - Opportunities: [White space]
   - Recommended responses: [Actions]
   Include: Strategic response framework

[Continue for all analysis sections]

Visual style: Professional, strategic, data-rich
Tone: Analytical, confident, action-oriented

═══════════════════════════════════════════════════════════════════════════"""

        user_message = f"""Analyze the competitive intelligence for {competitor_brand}{user_brand_text}{category_text}.

Provide comprehensive analysis including:
1. Brand positioning (with comparison to user's brand if provided)
2. Recent campaigns with specific examples
3. Rigorous media spend estimation:
   - Total spend with confidence level
   - US vs Global breakdown
   - Detailed channel breakdown for US
   - Methodology and assumptions
4. Strategic implications for the user's brand{focus_text}{comparative_instruction}{ai_prompt_instruction}

Be specific with numbers, show your reasoning, and indicate confidence levels."""

        return self._chat("competitive_intel", user_message, system_prompt)
    
    # ==================== MODULE 7: CREATIVE QUALITY REVIEW ====================
    
    def review_creative_asset(self, creative_description, objective, target_consumer, 
                            medium, brand_context=None, generate_ai_prompt=False):
        """
        Review creative asset quality using persona-based evaluation
        
        Args:
            creative_description: Description of the creative asset
            objective: Campaign objective
            target_consumer: Target audience description
            medium: Creative medium (TV, print, digital, social, etc.)
            brand_context: Additional brand context
            generate_ai_prompt: If True, also generate Gamma.ai/Beautiful.ai presentation prompt
        """
        system_prompt = """You are an expert creative strategist and consumer insights analyst specializing in creative effectiveness.

Your role is to:
1. Generate 100 diverse personas representing the target consumer
2. Evaluate creative from each persona's perspective
3. Assess brand recognition, appeal, and purchase intent
4. Identify creative strengths and improvement opportunities
5. Provide specific, actionable creative recommendations

**Persona Generation:**
Create 100 diverse personas within the target, varying by:
- Demographics (age, income, location)
- Psychographics (values, lifestyle, attitudes)
- Category relationship (heavy/light users, loyal/switchers)
- Media consumption habits
- Purchase drivers

**Evaluation Criteria (1-10 scale):**
1. Brand Recognition: How quickly/clearly is the brand identified?
2. Message Clarity: Is the key message understood?
3. Emotional Appeal: Does it resonate emotionally?
4. Relevance: Is it relevant to their life/needs?
5. Distinctiveness: Does it stand out from competition?
6. Purchase Intent: Does it drive intent to buy?

**Analysis Framework:**
1. Generate 100 persona profiles
2. Score creative on all 6 criteria for each persona
3. Calculate aggregate scores with distribution
4. Identify high-performing vs low-performing segments
5. Provide creative improvement recommendations

**Output Format:**
- Persona Summary (demographics, psychographics of the 100)
- Overall Scores (averages across all personas)
- Score Distribution (% scoring 1-3, 4-7, 8-10 on each metric)
- Segment Analysis (which personas love/hate it)
- Top 5 Creative Strengths
- Top 5 Improvement Opportunities
- Specific Creative Tweaks (copy, visual, format changes)"""

        brand_text = f"\n\nBrand Context: {brand_context}" if brand_context else ""
        
        ai_prompt_instruction = ""
        if generate_ai_prompt:
            ai_prompt_instruction = """

ADDITIONALLY: Create a Gamma.ai/Beautiful.ai presentation prompt for this creative review.

Format:

═══════════════════════════════════════════════════════════════════════════
GAMMA.AI / BEAUTIFUL.AI PROMPT (Copy and paste this)
═══════════════════════════════════════════════════════════════════════════

Create a 10-12 slide creative quality review presentation.

Objective: Review creative performance and recommend optimizations

Style: Creative, analytical, actionable
Color scheme: Modern with color-coded scores (green for high, yellow for medium, red for low)

Slide-by-slide content:

1. Creative Overview: [Creative name/description]
   - Medium: [Medium]
   - Objective: [Objective]
   - Target: [Target consumer]
   Include: The creative asset itself

2. Testing Methodology: 100 Consumer Personas
   - Persona diversity: [Demographics covered]
   - Evaluation criteria: 6 key metrics
   - Scoring: 1-10 scale
   Include: Persona diversity visualization

3. Overall Performance Scores
   - Brand Recognition: [Score]/10
   - Emotional Appeal: [Score]/10
   - Purchase Intent: [Score]/10
   - Message Clarity: [Score]/10
   - Distinctiveness: [Score]/10
   - Relevance: [Score]/10
   Include: Spider/radar chart of scores

4. Score Distribution: Who Loves It, Who Doesn't
   - High scorers (8-10): XX%
   - Medium scorers (4-7): XX%
   - Low scorers (1-3): XX%
   - Segment insights: [Which personas scored high/low]
   Include: Distribution histogram

5. Top 5 Creative Strengths
   - Strength 1: [What works well]
   - Strength 2: [What resonates]
   - [Continue...]
   Include: Supporting evidence from personas

6. Top 5 Improvement Opportunities
   - Opportunity 1: [Specific issue]
   - Opportunity 2: [What to fix]
   - [Continue...]
   Include: Persona feedback

7. Recommended Creative Tweaks: [Category - Copy]
   - Current: [Current copy]
   - Recommended: [Improved copy]
   - Rationale: [Why this is better]

8. Recommended Creative Tweaks: [Category - Visual]
   - Current: [Current visual approach]
   - Recommended: [Improved approach]
   - Rationale: [Why this is better]

[Continue for all recommendations]

Final Slide: Next Steps
   - [Priority improvements]
   - Testing plan
   - Timeline

Visual style: Clean, analytical, creative
Tone: Constructive, specific, actionable

═══════════════════════════════════════════════════════════════════════════"""
        
        user_message = f"""Review this creative asset:

**Creative Description:**
{creative_description}

**Campaign Objective:**
{objective}

**Target Consumer:**
{target_consumer}

**Medium:**
{medium}{brand_text}

Generate 100 diverse personas within this target and evaluate the creative from each perspective.

Provide:
1. Persona summary (the 100 consumers you generated)
2. Overall scores (1-10) on: Brand Recognition, Appeal, Purchase Intent
3. Score distributions
4. Creative strengths
5. Specific improvement recommendations with rationale

Be specific and actionable in your recommendations.{ai_prompt_instruction}"""

        return self._chat("creative_review", user_message, system_prompt)

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
