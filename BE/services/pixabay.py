"""
Pixabay Image Scraper Module
Adapted from final_year_project-main/pixabay_scraper.py
Fetches relevant royalty-free images from Pixabay API
"""
import os
import requests
from typing import List, Optional, Dict
from urllib.parse import urlencode
import time
import logging

logger = logging.getLogger(__name__)


class PixabayClient:
    """Client for Pixabay API interactions"""
    
    BASE_URL = "https://pixabay.com/api/"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Pixabay API client
        
        Args:
            api_key: Pixabay API key (defaults to PIXABAY_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('PIXABAY_API_KEY')
        
        if not self.api_key:
            raise ValueError("PIXABAY_API_KEY is required. Set it in environment or pass as parameter.")
    
    def search_images(
        self, 
        query: str, 
        per_page: int = 5,
        page: int = 1,
        image_type: str = "photo",
        orientation: str = "horizontal",
        safesearch: bool = True
    ) -> List[Dict]:
        """
        Search for images on Pixabay
        
        Args:
            query: Search keywords
            per_page: Number of results to return (default: 5, max: 200)
            page: Page number for pagination
            image_type: Type of image (photo, illustration, vector)
            orientation: Image orientation (horizontal, vertical, all)
            safesearch: Enable safe search
        
        Returns:
            List of image data dictionaries
        """
        params = {
            'key': self.api_key,
            'q': query,
            'per_page': min(per_page, 200),  # Pixabay max is 200
            'page': page,
            'image_type': image_type,
            'orientation': orientation,
            'safesearch': str(safesearch).lower()
        }
        
        try:
            logger.info(f"Searching Pixabay for: {query}")
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('hits'):
                logger.info(f"Found {len(data['hits'])} images for query: {query}")
                return data['hits']
            else:
                logger.warning(f"No images found for query: {query}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching images from Pixabay: {e}")
            return []
    
    def download_image(self, image_url: str, save_path: str) -> bool:
        """
        Download an image from URL to local path
        
        Args:
            image_url: URL of the image to download
            save_path: Local path to save the image
        
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(image_url, timeout=15, stream=True)
            response.raise_for_status()
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded image to: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return False
    
    def get_best_image(self, query: str, orientation: str = "horizontal") -> Optional[Dict]:
        """
        Get the best (highest quality) image for a query
        
        Args:
            query: Search keywords
            orientation: Image orientation preference
        
        Returns:
            Image data dictionary or None
        """
        images = self.search_images(query, per_page=3, orientation=orientation)
        
        if not images:
            return None
        
        # Sort by quality metrics (likes, views, etc.)
        best_image = max(images, key=lambda x: x.get('likes', 0) + x.get('views', 0) / 1000)
        
        logger.info(f"Selected best image for '{query}': ID {best_image.get('id')}")
        return best_image
    
    def download_slide_image(
        self, 
        keywords: str, 
        slide_number: int, 
        output_dir: str = "images"
    ) -> Optional[str]:
        """
        Download an image for a specific slide
        
        Args:
            keywords: Search keywords
            slide_number: Slide number for filename
            output_dir: Directory to save images
        
        Returns:
            Path to downloaded image or None
        """
        image_data = self.get_best_image(keywords)
        
        if not image_data:
            logger.warning(f"No image found for slide {slide_number} with keywords: {keywords}")
            return None
        
        # Use webformatURL for good quality
        image_url = image_data.get('webformatURL') or image_data.get('largeImageURL')
        
        if not image_url:
            return None
        
        # Generate filename
        filename = f"slide_{slide_number}.jpg"
        filepath = os.path.join(output_dir, filename)
        
        # Download the image
        if self.download_image(image_url, filepath):
            logger.info(f"Downloaded image for slide {slide_number}: {keywords}")
            return filepath
        else:
            return None
    
    def download_all_slide_images(
        self, 
        slides_data: List[Dict], 
        output_dir: str = "images"
    ) -> Dict[int, str]:
        """
        Download images for all slides
        
        Args:
            slides_data: List of slide dictionaries with image_keywords
            output_dir: Directory to save images
        
        Returns:
            Dictionary mapping slide numbers to image paths
        """
        image_paths = {}
        
        for slide in slides_data:
            slide_num = slide.get('slide_number')
            keywords = slide.get('image_keywords', '')
            
            if not keywords:
                continue
            
            path = self.download_slide_image(keywords, slide_num, output_dir)
            
            if path:
                image_paths[slide_num] = path
            
            # Small delay to be respectful to the API
            time.sleep(0.5)
        
        logger.info(f"Downloaded {len(image_paths)} images total")
        return image_paths
    
    def get_image_suggestions(self, query: str, count: int = 5) -> List[Dict]:
        """
        Get image suggestions with metadata for frontend display
        
        Args:
            query: Search query
            count: Number of suggestions to return
            
        Returns:
            List of image metadata dictionaries
        """
        images = self.search_images(query, per_page=count)
        
        suggestions = []
        for img in images:
            suggestions.append({
                'id': str(img.get('id')),
                'preview_url': img.get('previewURL'),
                'webformat_url': img.get('webformatURL'),
                'large_url': img.get('largeImageURL'),
                'keywords': img.get('tags', query),
                'user': img.get('user', 'Unknown'),
                'page_url': img.get('pageURL')
            })
        
        return suggestions
