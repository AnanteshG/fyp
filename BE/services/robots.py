"""
Robots.txt Checker Module
Checks if scraping is allowed for a given URL by parsing robots.txt
"""
import requests
import urllib.robotparser
from urllib.parse import urlparse, urljoin
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def get_robots_url(url: str) -> str:
    """
    Construct the robots.txt URL for a given URL
    
    Args:
        url: The URL to check
        
    Returns:
        URL of the robots.txt file
    """
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    return robots_url


def check_robots_txt(url: str, user_agent: str = '*') -> Tuple[bool, str]:
    """
    Check if scraping is allowed for a URL based on its robots.txt
    
    Args:
        url: The URL to check
        user_agent: The user agent to check against (default: '*')
        
    Returns:
        Tuple of (is_allowed: bool, message: str)
    """
    try:
        robots_url = get_robots_url(url)
        logger.info(f"Checking robots.txt at: {robots_url}")
        
        # Create a RobotFileParser
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        
        try:
            rp.read()
        except Exception as e:
            logger.warning(f"Could not read robots.txt from {robots_url}: {e}")
            # If we can't read robots.txt, assume scraping is disallowed (conservative approach)
            return False, f"Could not access robots.txt: {str(e)}"
        
        # Check if fetching is allowed
        can_fetch = rp.can_fetch(user_agent, url)
        
        if can_fetch:
            return True, "Scraping is allowed by robots.txt"
        else:
            return False, "Scraping is disallowed by robots.txt"
            
    except Exception as e:
        logger.error(f"Error checking robots.txt for {url}: {e}")
        # Fail safely by disallowing scraping
        return False, f"Error checking robots.txt: {str(e)}"


def fetch_robots_txt(url: str) -> Tuple[bool, str]:
    """
    Fetch and return the raw robots.txt content
    
    Args:
        url: The URL to get robots.txt for
        
    Returns:
        Tuple of (success: bool, content: str)
    """
    try:
        robots_url = get_robots_url(url)
        
        response = requests.get(robots_url, timeout=5)
        response.raise_for_status()
        
        return True, response.text
        
    except requests.RequestException as e:
        logger.error(f"Error fetching robots.txt: {e}")
        return False, f"Error: {str(e)}"
