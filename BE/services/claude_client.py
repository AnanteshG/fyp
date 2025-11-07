"""
Claude API Client Wrapper
Handles communication with Anthropic's Claude API for content generation
"""
import os
from anthropic import Anthropic
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for Claude API interactions"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client
        
        Args:
            api_key: Anthropic API key (defaults to CLAUDE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY')
        
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY is required. Set it in environment or pass as parameter.")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
    
    def generate_outline(self, topic: str, max_slides: int = 5) -> Dict:
        """
        Generate presentation outline from topic
        
        Args:
            topic: Presentation topic
            max_slides: Maximum number of slides to generate
            
        Returns:
            Dictionary with presentation structure
        """
        # Load prompt template
        prompt = self._load_prompt('outline_generation.txt').format(
            topic=topic,
            max_slides=max_slides
        )
        
        try:
            logger.info(f"Generating outline for topic: {topic}")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            content = response.content[0].text
            
            # Parse JSON response
            outline = self._parse_json_response(content)
            logger.info(f"Successfully generated outline with {len(outline.get('slides', []))} slides")
            
            return outline
            
        except Exception as e:
            logger.error(f"Error generating outline: {e}")
            # Return fallback outline
            return self._get_fallback_outline(topic, max_slides)
    
    def generate_slide_content(self, slide_title: str, context: str = "") -> Dict:
        """
        Generate detailed content for a single slide
        
        Args:
            slide_title: Title of the slide
            context: Additional context about the presentation
            
        Returns:
            Dictionary with slide content (bullets, speaker notes)
        """
        prompt = self._load_prompt('slide_content.txt').format(
            slide_title=slide_title,
            context=context
        )
        
        try:
            logger.info(f"Generating content for slide: {slide_title}")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            content = response.content[0].text
            slide_content = self._parse_json_response(content)
            
            return slide_content
            
        except Exception as e:
            logger.error(f"Error generating slide content: {e}")
            return {
                "bullets": [
                    f"Key point about {slide_title}",
                    "Supporting information",
                    "Additional details"
                ],
                "speaker_notes": f"Discuss {slide_title} in detail."
            }
    
    def summarize_text(self, text: str, max_length: int = 500) -> str:
        """
        Summarize long text into concise content
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary in words
            
        Returns:
            Summarized text
        """
        prompt = self._load_prompt('text_summarization.txt').format(
            text=text,
            max_length=max_length
        )
        
        try:
            logger.info("Summarizing text")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.5,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            summary = response.content[0].text
            logger.info("Successfully summarized text")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            # Return truncated text as fallback
            words = text.split()
            return ' '.join(words[:max_length]) + ('...' if len(words) > max_length else '')
    
    def _load_prompt(self, filename: str) -> str:
        """Load prompt template from prompts folder"""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', filename)
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt file {filename} not found, using default")
            return self._get_default_prompt(filename)
    
    def _get_default_prompt(self, filename: str) -> str:
        """Get default prompt if file doesn't exist"""
        defaults = {
            'outline_generation.txt': """Create a detailed presentation outline for: "{topic}"

Generate exactly {max_slides} slides with this JSON format:
{{
    "title": "Presentation Title",
    "slides": [
        {{
            "slide_number": 1,
            "title": "Slide Title",
            "content": ["Bullet 1", "Bullet 2", "Bullet 3"],
            "image_keywords": "keywords for image search",
            "speaker_notes": "What to say about this slide"
        }}
    ]
}}

Return ONLY valid JSON, no additional text.""",
            
            'slide_content.txt': """Generate detailed content for a slide titled: "{slide_title}"

Context: {context}

Return JSON format:
{{
    "bullets": ["Point 1", "Point 2", "Point 3"],
    "speaker_notes": "Detailed notes for the presenter"
}}

Return ONLY valid JSON.""",
            
            'text_summarization.txt': """Summarize the following text in approximately {max_length} words:

{text}

Provide a clear, concise summary suitable for presentation slides."""
        }
        return defaults.get(filename, "")
    
    def _parse_json_response(self, content: str) -> Dict:
        """Parse JSON from Claude's response"""
        # Remove markdown code blocks if present
        if content.startswith('```'):
            lines = content.split('\n')
            # Remove first and last lines (```json and ```)
            content = '\n'.join(lines[1:-1])
            if content.startswith('json'):
                content = content[4:].strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Raw content: {content}")
            raise
    
    def _get_fallback_outline(self, topic: str, max_slides: int) -> Dict:
        """Generate basic fallback outline"""
        return {
            "title": topic,
            "slides": [
                {
                    "slide_number": i,
                    "title": f"Section {i}: {topic}",
                    "content": [
                        f"Key point {i}.1",
                        f"Key point {i}.2",
                        f"Key point {i}.3"
                    ],
                    "image_keywords": topic,
                    "speaker_notes": f"Discuss section {i} of {topic}"
                }
                for i in range(1, max_slides + 1)
            ]
        }
