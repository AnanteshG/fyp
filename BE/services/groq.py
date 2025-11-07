"""
Groq API Integration Module
Adapted from final_year_project-main/groq_api.py
Handles communication with Groq API for AI content generation
"""
import os
from groq import Groq
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class GroqClient:
    """Client for Groq API interactions"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq API client
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is required. Set it in environment or pass as parameter.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    
    def generate_presentation_structure(self, topic: str, num_slides: int = 5) -> Dict:
        """
        Generate presentation structure using Groq API
        
        Args:
            topic: The main topic of the presentation
            num_slides: Number of slides to generate (default: 5)
        
        Returns:
            Dictionary containing presentation structure
        """
        prompt = f"""Create a detailed presentation structure for the topic: "{topic}"

Generate exactly {num_slides} slides with the following JSON format:
{{
    "title": "Presentation Title",
    "slides": [
        {{
            "slide_number": 1,
            "title": "Slide Title",
            "content": ["Bullet point 1", "Bullet point 2", "Bullet point 3"],
            "image_keywords": "relevant keywords for image search",
            "speaker_notes": "Detailed notes for the presenter"
        }}
    ]
}}

Make the content engaging, informative, and well-structured. Each slide should have 3-5 bullet points.
Return ONLY the JSON, no additional text."""

        try:
            logger.info(f"Generating presentation structure for: {topic}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert presentation designer. Generate well-structured, engaging presentation content in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON if there's extra text
            if content.startswith('```'):
                # Remove markdown code blocks
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()
            
            presentation_data = json.loads(content)
            logger.info(f"Successfully generated {len(presentation_data.get('slides', []))} slides")
            
            return presentation_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            logger.debug(f"Raw content: {content}")
            # Return a fallback structure
            return self._get_fallback_structure(topic, num_slides)
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return self._get_fallback_structure(topic, num_slides)
    
    def expand_bullet_point(self, bullet: str, context: str = "") -> str:
        """
        Expand a bullet point into more detailed content
        
        Args:
            bullet: The bullet point to expand
            context: Additional context
            
        Returns:
            Expanded text
        """
        prompt = f"""Expand this bullet point into 2-3 sentences of detailed, informative content:

Bullet: {bullet}
Context: {context}

Provide clear, professional content suitable for a presentation."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a presentation content expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error expanding bullet point: {e}")
            return bullet
    
    def _get_fallback_structure(self, topic: str, num_slides: int) -> Dict:
        """Generate a basic fallback structure if API call fails"""
        logger.warning("Using fallback presentation structure")
        return {
            "title": topic,
            "slides": [
                {
                    "slide_number": i,
                    "title": f"Slide {i}: {topic}",
                    "content": [
                        f"Point 1 about {topic}",
                        f"Point 2 about {topic}",
                        f"Point 3 about {topic}"
                    ],
                    "image_keywords": topic,
                    "speaker_notes": f"Discuss slide {i} about {topic}"
                }
                for i in range(1, num_slides + 1)
            ]
        }
