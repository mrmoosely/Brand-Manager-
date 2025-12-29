#!/usr/bin/env python3
"""
PowerPoint Deck Generator
Creates actual .pptx files with AI-generated content
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import json
from datetime import datetime

class PowerPointGenerator:
    def __init__(self, template_path=None):
        """Initialize with optional template file"""
        if template_path:
            self.prs = Presentation(template_path)
        else:
            self.prs = Presentation()
        
        # Default styling
        self.title_font_size = Pt(44)
        self.heading_font_size = Pt(32)
        self.body_font_size = Pt(18)
        self.title_color = RGBColor(0, 0, 0)
        self.body_color = RGBColor(64, 64, 64)
    
    def add_title_slide(self, title, subtitle=None):
        """Add title slide"""
        slide_layout = self.prs.slide_layouts[0]  # Title slide layout
        slide = self.prs.slides.add_slide(slide_layout)
        
        title_shape = slide.shapes.title
        title_shape.text = title
        
        if subtitle and len(slide.placeholders) > 1:
            subtitle_shape = slide.placeholders[1]
            subtitle_shape.text = subtitle
        
        return slide
    
    def add_section_header(self, title):
        """Add section divider slide"""
        slide_layout = self.prs.slide_layouts[2]  # Section header layout
        slide = self.prs.slides.add_slide(slide_layout)
        
        title_shape = slide.shapes.title
        title_shape.text = title
        
        return slide
    
    def add_content_slide(self, title, content_items, bullet_level=0):
        """Add content slide with bullet points"""
        slide_layout = self.prs.slide_layouts[1]  # Title and content layout
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Title
        title_shape = slide.shapes.title
        title_shape.text = title
        
        # Content
        content_shape = slide.placeholders[1]
        text_frame = content_shape.text_frame
        text_frame.clear()
        
        for item in content_items:
            if isinstance(item, dict):
                # Handle nested structure
                p = text_frame.add_paragraph()
                p.text = item.get('text', '')
                p.level = item.get('level', bullet_level)
                p.font.size = Pt(item.get('font_size', 18))
            else:
                # Simple text
                p = text_frame.add_paragraph()
                p.text = str(item)
                p.level = bullet_level
                p.font.size = self.body_font_size
        
        return slide
    
    def add_two_column_slide(self, title, left_content, right_content):
        """Add two-column comparison slide"""
        slide_layout = self.prs.slide_layouts[3]  # Two content layout
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Title
        title_shape = slide.shapes.title
        title_shape.text = title
        
        # Left column
        left_shape = slide.placeholders[1]
        left_frame = left_shape.text_frame
        left_frame.clear()
        for item in left_content:
            p = left_frame.add_paragraph()
            p.text = str(item)
            p.font.size = self.body_font_size
        
        # Right column
        right_shape = slide.placeholders[2]
        right_frame = right_shape.text_frame
        right_frame.clear()
        for item in right_content:
            p = right_frame.add_paragraph()
            p.text = str(item)
            p.font.size = self.body_font_size
        
        return slide
    
    def add_data_slide(self, title, data_dict):
        """Add slide with key metrics"""
        slide_layout = self.prs.slide_layouts[6]  # Blank layout
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Add title
        title_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(0.5),
            Inches(9), Inches(1)
        )
        title_frame = title_box.text_frame
        title_frame.text = title
        p = title_frame.paragraphs[0]
        p.font.size = self.heading_font_size
        p.font.bold = True
        
        # Add metrics in grid
        num_metrics = len(data_dict)
        cols = min(3, num_metrics)
        rows = (num_metrics + cols - 1) // cols
        
        metric_width = 9 / cols
        metric_height = 5 / rows
        
        for idx, (key, value) in enumerate(data_dict.items()):
            col = idx % cols
            row = idx // cols
            
            left = 0.5 + (col * metric_width)
            top = 2 + (row * metric_height)
            
            # Metric box
            metric_box = slide.shapes.add_textbox(
                Inches(left), Inches(top),
                Inches(metric_width - 0.2), Inches(metric_height - 0.2)
            )
            
            frame = metric_box.text_frame
            frame.word_wrap = True
            
            # Value (big)
            p = frame.paragraphs[0]
            p.text = str(value)
            p.font.size = Pt(36)
            p.font.bold = True
            p.alignment = PP_ALIGN.CENTER
            
            # Label (smaller)
            p = frame.add_paragraph()
            p.text = key
            p.font.size = Pt(14)
            p.alignment = PP_ALIGN.CENTER
        
        return slide
    
    def save(self, filename):
        """Save presentation to file"""
        if not filename.endswith('.pptx'):
            filename += '.pptx'
        
        self.prs.save(filename)
        return filename


def create_deck_from_outline(outline_text, template_path=None, output_filename=None):
    """
    Parse AI-generated outline and create PowerPoint deck
    
    Expected outline format:
    SLIDE 1: Title
    - Bullet point 1
    - Bullet point 2
    
    SLIDE 2: Another Title
    - Content here
    """
    generator = PowerPointGenerator(template_path)
    
    # Parse outline
    slides_data = []
    current_slide = None
    
    for line in outline_text.split('\n'):
        line = line.strip()
        
        if line.startswith('SLIDE') or line.startswith('Slide'):
            # New slide
            if current_slide:
                slides_data.append(current_slide)
            
            # Extract title (everything after the colon)
            title = line.split(':', 1)[1].strip() if ':' in line else line
            current_slide = {
                'title': title,
                'content': []
            }
        elif line.startswith('-') or line.startswith('•'):
            # Bullet point
            if current_slide:
                current_slide['content'].append(line.lstrip('-•').strip())
        elif line and current_slide and not line.startswith('**'):
            # Regular text line
            current_slide['content'].append(line)
    
    # Add last slide
    if current_slide:
        slides_data.append(current_slide)
    
    # Create slides
    for idx, slide_data in enumerate(slides_data):
        if idx == 0:
            # First slide is title slide
            generator.add_title_slide(
                slide_data['title'],
                slide_data['content'][0] if slide_data['content'] else None
            )
        elif 'section' in slide_data['title'].lower() or 'agenda' in slide_data['title'].lower():
            # Section header
            generator.add_section_header(slide_data['title'])
        elif not slide_data['content']:
            # Section header if no content
            generator.add_section_header(slide_data['title'])
        else:
            # Regular content slide
            generator.add_content_slide(
                slide_data['title'],
                slide_data['content']
            )
    
    # Save
    if not output_filename:
        output_filename = f"presentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
    
    saved_path = generator.save(output_filename)
    return saved_path


# Example usage
if __name__ == "__main__":
    # Example: Create a simple deck
    gen = PowerPointGenerator()
    
    # Title slide
    gen.add_title_slide(
        "Q4 Brand Performance Review",
        "Traveller Whiskey"
    )
    
    # Section header
    gen.add_section_header("Market Overview")
    
    # Content slide
    gen.add_content_slide(
        "Key Performance Highlights",
        [
            "Market share grew 1.2 points YOY to 12.3%",
            "Distribution increased 5 points to 72% ACV",
            "Dollar sales up 15.3% vs year ago",
            "Volume growth outpacing category at +8.7%"
        ]
    )
    
    # Data slide
    gen.add_data_slide(
        "Performance Metrics",
        {
            "Market Share": "12.3%",
            "YOY Growth": "+15.3%",
            "Distribution": "72% ACV",
            "Velocity": "+8.7%"
        }
    )
    
    # Two column slide
    gen.add_two_column_slide(
        "Strengths vs Opportunities",
        [
            "Strong distribution gains",
            "Premium positioning resonating",
            "Marketing effectiveness high"
        ],
        [
            "Price gaps vs competition",
            "Limited SKU variety",
            "Need digital investment"
        ]
    )
    
    # Save
    filename = gen.save("example_deck.pptx")
    print(f"Created: {filename}")
