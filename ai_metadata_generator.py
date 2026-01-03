"""
AI Metadata Generator for YouTube Videos.
Uses Google Generative AI (gemini-2.5-flash) to generate optimized titles and descriptions.
"""

import logging
import os
from typing import Dict, Optional

import google.generativeai as genai

import config

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AIMetadataGenerator:
    """
    Generates YouTube-optimized metadata using Google Generative AI.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI Metadata Generator.
        
        Args:
            api_key: Google AI API key. If not provided, uses GEMINI_API_KEY from config
        """
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the Gemini AI model."""
        try:
            if not self.api_key:
                raise ValueError("Google AI API key is not configured")
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("AI Metadata Generator initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize AI model: {str(e)}")
            raise
    
    def generate_metadata(
        self,
        video_context: str,
        video_language: str = "Thai",
        category: str = "Education",
        tags: str = ""
    ) -> Dict[str, str]:
        """
        Generate YouTube-optimized title and description.
        
        Args:
            video_context: Description of the video content or topic
            video_language: Primary language of the video
            category: YouTube category
            tags: Existing tags to incorporate
            
        Returns:
            Dictionary with 'title' and 'description' keys
        """
        if not self.model:
            raise RuntimeError("AI model not initialized")
        
        prompt = self._build_prompt(video_context, video_language, category, tags)
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            
            logger.info("AI metadata generated successfully")
            return result
        
        except Exception as e:
            logger.error(f"Failed to generate AI metadata: {str(e)}")
            raise
    
    def _build_prompt(
        self,
        video_context: str,
        video_language: str,
        category: str,
        tags: str
    ) -> str:
        """
        Build the prompt for AI generation.
        
        Args:
            video_context: Video content description
            video_language: Video language
            category: YouTube category
            tags: Existing tags
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a YouTube SEO expert. Generate an optimized title and description for a YouTube video based on the following information:

Video Content: {video_context}
Language: {video_language}
Category: {category}
Existing Tags: {tags if tags else "None"}

Requirements:
1. Title (max 100 characters):
   - Create a catchy, attention-grabbing title
   - Include relevant keywords for SEO
   - Use power words to increase click-through rate
   - Make it compelling and click-worthy
   - Avoid clickbait - be authentic

2. Description (500-1000 characters):
   - Start with a strong hook to engage viewers
   - Include relevant keywords naturally
   - Provide value and set expectations
   - Include a call-to-action
   - Add relevant hashtags (3-5)
   - Format with paragraphs for readability
   - Mention key topics covered

3. Generate 5-7 additional relevant tags (comma-separated)

Format your response exactly like this:

TITLE: [Your title here]

DESCRIPTION: [Your description here]

TAGS: [tag1, tag2, tag3, tag4, tag5]"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """
        Parse the AI response to extract title, description, and tags.
        
        Args:
            response_text: Raw response from AI model
            
        Returns:
            Dictionary with 'title', 'description', and 'tags' keys
        """
        result = {
            'title': '',
            'description': '',
            'tags': ''
        }
        
        try:
            # Split response into sections
            sections = response_text.split('\n\n')
            
            for section in sections:
                section = section.strip()
                if section.startswith('TITLE:'):
                    result['title'] = section.replace('TITLE:', '').strip()
                elif section.startswith('DESCRIPTION:'):
                    result['description'] = section.replace('DESCRIPTION:', '').strip()
                elif section.startswith('TAGS:'):
                    result['tags'] = section.replace('TAGS:', '').strip()
            
            # Validate that we got all required fields
            if not result['title']:
                result['title'] = "Generated Title"
            if not result['description']:
                result['description'] = "Generated description"
            
            logger.debug(f"Parsed AI response - Title length: {len(result['title'])}, Description length: {len(result['description'])}")
            
            return result
        
        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            # Return default values if parsing fails
            return {
                'title': 'AI Generated Title',
                'description': 'AI generated description',
                'tags': 'AI, generated'
            }
    
    def is_available(self) -> bool:
        """
        Check if the AI service is available.
        
        Returns:
            True if available, False otherwise
        """
        return self.model is not None and self.api_key is not None


def generate_metadata_from_context(
    video_context: str,
    video_language: str = "Thai",
    category: str = "Education",
    tags: str = "",
    api_key: Optional[str] = None
) -> Dict[str, str]:
    """
    Convenience function to generate metadata.
    
    Args:
        video_context: Description of the video content
        video_language: Primary language of the video
        category: YouTube category
        tags: Existing tags
        api_key: Optional API key
        
    Returns:
        Dictionary with 'title', 'description', and 'tags'
    """
    generator = AIMetadataGenerator(api_key)
    return generator.generate_metadata(video_context, video_language, category, tags)
