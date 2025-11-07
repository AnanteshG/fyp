"""
Web Scraping Service
Scrapes content from URLs with robots.txt validation
"""
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse, urljoin
from services.robots import check_robots_txt

logger = logging.getLogger(__name__)

class WebScraper:
    """Web scraping service with robots.txt compliance"""
    
    def __init__(self, user_agent: str = "AI-PPT-Generator-Bot/1.0"):
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent
        })
    
    def scrape_urls(self, urls: List[str]) -> Dict[str, Dict]:
        """
        Scrape multiple URLs with robots.txt validation
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            Dict mapping URL to scraped data or error
        """
        results = {}
        
        for url in urls:
            try:
                result = self.scrape_single_url(url)
                results[url] = result
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                results[url] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def scrape_single_url(self, url: str) -> Dict:
        """
        Scrape a single URL with robots.txt validation
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict with scraped content or error
        """
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Check robots.txt
        allowed, message = check_robots_txt(url, self.user_agent)
        
        if not allowed:
            return {
                "success": False,
                "error": f"Scraping not allowed: {message}",
                "robots_txt_blocked": True
            }
        
        # Scrape the URL
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract content
            content = self._extract_content(soup, url)
            
            return {
                "success": True,
                "url": url,
                "title": content["title"],
                "text": content["text"],
                "headings": content["headings"],
                "metadata": content["metadata"]
            }
            
        except requests.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to fetch URL: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Parsing error for {url}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to parse content: {str(e)}"
            }
    
    def _extract_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extract meaningful content from HTML
        
        Args:
            soup: BeautifulSoup object
            url: Original URL
            
        Returns:
            Dict with extracted content
        """
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract title
        title = ""
        if soup.title:
            title = soup.title.string
        elif soup.find('h1'):
            title = soup.find('h1').get_text(strip=True)
        
        # Extract headings
        headings = []
        for heading_tag in ['h1', 'h2', 'h3']:
            for heading in soup.find_all(heading_tag):
                text = heading.get_text(strip=True)
                if text and len(text) > 3:
                    headings.append({
                        "level": heading_tag,
                        "text": text
                    })
        
        # Extract main content
        text_content = []
        
        # Try to find main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            paragraphs = main_content.find_all('p')
        else:
            paragraphs = soup.find_all('p')
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 20:  # Filter out short snippets
                text_content.append(text)
        
        # Extract metadata
        metadata = {}
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            metadata['description'] = meta_desc['content']
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            metadata['keywords'] = meta_keywords['content']
        
        # Open Graph tags
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            metadata['og_title'] = og_title['content']
        
        return {
            "title": title,
            "text": "\n\n".join(text_content),
            "headings": headings,
            "metadata": metadata
        }
    
    def get_combined_text(self, scrape_results: Dict[str, Dict]) -> str:
        """
        Combine text from multiple scrape results
        
        Args:
            scrape_results: Dict of scrape results from scrape_urls
            
        Returns:
            Combined text from all successful scrapes
        """
        combined = []
        
        for url, result in scrape_results.items():
            if result.get("success"):
                # Add title
                if result.get("title"):
                    combined.append(f"# {result['title']}\n")
                
                # Add URL
                combined.append(f"Source: {url}\n")
                
                # Add headings
                if result.get("headings"):
                    combined.append("## Key Topics:")
                    for heading in result["headings"][:10]:  # Limit to top 10
                        combined.append(f"- {heading['text']}")
                    combined.append("")
                
                # Add text content
                if result.get("text"):
                    combined.append(result["text"])
                
                combined.append("\n" + "="*80 + "\n")
        
        return "\n".join(combined)
