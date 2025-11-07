"""
Wikipedia Search and Content Extraction Service
Fallback content source when no URLs are provided
"""
import logging
import wikipedia
import re
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class WikipediaService:
    """Wikipedia content extraction service"""
    
    def __init__(self, lang: str = 'en'):
        """
        Initialize Wikipedia service
        
        Args:
            lang: Language code (default: 'en')
        """
        wikipedia.set_lang(lang)
        self.lang = lang
    
    def extract_keywords(self, query: str) -> List[str]:
        """
        Extract keywords from search query
        
        Args:
            query: Search query string
            
        Returns:
            List of extracted keywords
        """
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'about', 'as', 'into', 'through', 'during',
            'including', 'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'presentation', 'ppt', 'powerpoint', 'slides'
        }
        
        # Clean and split query
        words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        
        # Filter keywords
        keywords = [word for word in words if word not in stop_words]
        
        return keywords
    
    def search_wikipedia(self, query: str, num_results: int = 5) -> List[str]:
        """
        Search Wikipedia for relevant articles
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of article titles
        """
        try:
            # Extract keywords
            keywords = self.extract_keywords(query)
            
            # If no keywords, use original query
            search_query = ' '.join(keywords) if keywords else query
            
            logger.info(f"Searching Wikipedia for: {search_query}")
            
            # Search Wikipedia
            results = wikipedia.search(search_query, results=num_results)
            
            logger.info(f"Found {len(results)} Wikipedia articles")
            
            return results
            
        except Exception as e:
            logger.error(f"Wikipedia search error: {str(e)}")
            return []
    
    def get_article_content(self, title: str) -> Optional[Dict]:
        """
        Get content from a Wikipedia article
        
        Args:
            title: Article title
            
        Returns:
            Dict with article content or None
        """
        try:
            # Get page
            page = wikipedia.page(title, auto_suggest=False)
            
            # Extract sections
            sections = self._extract_sections(page.content)
            
            return {
                "title": page.title,
                "url": page.url,
                "summary": page.summary,
                "content": page.content,
                "sections": sections,
                "categories": page.categories if hasattr(page, 'categories') else []
            }
            
        except wikipedia.exceptions.DisambiguationError as e:
            logger.warning(f"Disambiguation page for '{title}', trying first option")
            # Try first option
            if e.options:
                return self.get_article_content(e.options[0])
            return None
            
        except wikipedia.exceptions.PageError:
            logger.error(f"Wikipedia page not found: {title}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting Wikipedia article '{title}': {str(e)}")
            return None
    
    def get_content_for_query(self, query: str, max_articles: int = 3) -> Dict:
        """
        Get Wikipedia content for a search query
        
        Args:
            query: Search query
            max_articles: Maximum number of articles to fetch
            
        Returns:
            Dict with combined content from multiple articles
        """
        # Search for articles
        article_titles = self.search_wikipedia(query, num_results=max_articles * 2)
        
        if not article_titles:
            return {
                "success": False,
                "error": "No Wikipedia articles found for query"
            }
        
        # Fetch article content
        articles = []
        for title in article_titles[:max_articles]:
            content = self.get_article_content(title)
            if content:
                articles.append(content)
        
        if not articles:
            return {
                "success": False,
                "error": "Failed to fetch Wikipedia article content"
            }
        
        # Combine content
        combined_text = self._combine_articles(articles)
        
        return {
            "success": True,
            "source": "wikipedia",
            "query": query,
            "articles": articles,
            "combined_text": combined_text,
            "num_articles": len(articles)
        }
    
    def _extract_sections(self, content: str) -> List[Dict]:
        """
        Extract sections from Wikipedia content
        
        Args:
            content: Raw content text
            
        Returns:
            List of sections with titles and content
        """
        sections = []
        
        # Split by section headers (== Title ==)
        parts = re.split(r'\n==(.*?)==\n', content)
        
        if len(parts) > 1:
            # First part is intro
            if parts[0].strip():
                sections.append({
                    "title": "Introduction",
                    "content": parts[0].strip()
                })
            
            # Process remaining sections
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    title = parts[i].strip()
                    content = parts[i + 1].strip()
                    
                    if content:
                        sections.append({
                            "title": title,
                            "content": content
                        })
        else:
            # No sections, just content
            sections.append({
                "title": "Content",
                "content": content.strip()
            })
        
        return sections
    
    def _combine_articles(self, articles: List[Dict]) -> str:
        """
        Combine content from multiple Wikipedia articles
        
        Args:
            articles: List of article dicts
            
        Returns:
            Combined text content
        """
        combined = []
        
        for article in articles:
            combined.append(f"# {article['title']}\n")
            combined.append(f"Source: {article['url']}\n")
            
            # Add summary
            if article.get('summary'):
                combined.append(f"## Summary\n{article['summary']}\n")
            
            # Add key sections (limit to avoid too much content)
            if article.get('sections'):
                combined.append("## Key Information\n")
                for section in article['sections'][:5]:  # First 5 sections
                    combined.append(f"### {section['title']}")
                    # Limit section content
                    content = section['content']
                    if len(content) > 1000:
                        content = content[:1000] + "..."
                    combined.append(f"{content}\n")
            
            combined.append("\n" + "="*80 + "\n")
        
        return "\n".join(combined)
