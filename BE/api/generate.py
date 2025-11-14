"""
Generate PPT API Endpoint
Handles presentation generation from topic/text/URLs/Wikipedia
"""
from flask import Blueprint, request, jsonify
import logging
import os
import uuid
from dotenv import load_dotenv
load_dotenv()

from auth import require_auth, optional_auth
# from services.claude_client import ClaudeClient
from services.groq import GroqClient
from services.pixabay import PixabayClient
from services.ppt_service import PPTService
from services.web_scraper import WebScraper
from services.wikipedia_service import WikipediaService
from services.firebase_service import FirebaseService
from storage import ppt_storage

logger = logging.getLogger(__name__)


logger.info('load_dotenv(): ', load_dotenv())

generate_bp = Blueprint('generate', __name__)


@generate_bp.route('/generate', methods=['POST'])
@optional_auth
def generate_ppt():
    """
    Generate a new PowerPoint presentation
    
    Request JSON:
    {
        "topic": "Presentation topic",
        "urls": ["https://example.com"],  // optional - URLs to scrape
        "theme": "modern",  // optional
        "num_slides": 5,   // optional
        "brand_colors": ["#1A73E8"],  // optional
        "source_text": "...",  // optional
        "ai_provider": "claude" or "groq"  // optional
    }
    
    Response:
    {
        "ppt_id": "uuid",
        "slides": [...],
        "download_url": "/api/v1/download/<uuid>"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided', 'code': 400}), 400
        
        topic = data.get('topic', '')
        urls = data.get('urls', [])
        source_text = data.get('source_text', '')
        theme = data.get('theme', 'modern')
        slide_count = data.get('num_slides', data.get('slide_count', 7))
        brand_colors = data.get('brand_colors', [])
        ai_provider = data.get('ai_provider', 'groq')
        
        if not topic:
            return jsonify({
                'error': 'Topic is required',
                'code': 400
            }), 400
        
        # logger.info(f"Generating PPT for topic: {topic} (user: {getattr(request, 'user_id', 'anonymous')})")
        
        # Step 1: Gather content from sources
        content_sources = []
        
        # 1a. Scrape URLs if provided
        if urls:
            logger.info(f"Scraping {len(urls)} URLs")
            scraper = WebScraper()
            scrape_results = scraper.scrape_urls(urls)
            
            # Check for successful scrapes
            successful_scrapes = [result for result in scrape_results.values() if result.get('success')]
            
            if successful_scrapes:
                scraped_text = scraper.get_combined_text(scrape_results)
                content_sources.append({
                    "type": "web_scraping",
                    "urls": urls,
                    "text": scraped_text,
                    "success_count": len(successful_scrapes),
                    "total_count": len(urls)
                })
                # logger.info(f"Successfully scraped {len(successful_scrapes)}/{len(urls)} URLs")
            else:
                logger.warning("All URL scraping attempts failed")
        
        # 1b. Use provided source text
        if source_text:
            content_sources.append({
                "type": "user_provided",
                "text": source_text
            })
            logger.info("Using user-provided source text")
        
        # 1c. Fallback to Wikipedia if no other sources
        if not content_sources:
            logger.info("No content sources provided, using Wikipedia as fallback")
            wiki_service = WikipediaService()
            wiki_result = wiki_service.get_content_for_query(topic, max_articles=3)
            
            if wiki_result.get('success'):
                content_sources.append({
                    "type": "wikipedia",
                    "text": wiki_result['combined_text'],
                    "articles": [article['title'] for article in wiki_result['articles']]
                })
                # logger.info(f"Retrieved content from {wiki_result['num_articles']} Wikipedia articles")
            else:
                logger.warning("Wikipedia fallback failed, using topic only")
        
        # Combine all content sources
        combined_content = "\n\n".join([source.get('text', '') for source in content_sources if source.get('text')])
        
        logger.info(f"Total content length: {len(combined_content)} characters")
        
        # Step 2: Choose AI service based on availability and preference
        ai_client = None
        try:
            # if ai_provider == 'claude' and os.getenv('CLAUDE_API_KEY'):
            #     ai_client = ClaudeClient()
            #     logger.info("Using Claude for content generation")
            if os.getenv('GROQ_API_KEY'):
                ai_client = GroqClient()
                logger.info("Using Groq for content generation")
            else:
                return jsonify({
                    'error': 'No AI API key configured (CLAUDE_API_KEY or GROQ_API_KEY required)',
                    'code': 500
                }), 500
        except Exception as e:
            logger.warning(f"Failed to initialize AI client: {e}")
            return jsonify({
                'error': f'Failed to initialize AI service: {str(e)}',
                'code': 500
            }), 500
        
        # Step 3: Generate presentation structure with AI
        # Pass combined content as context for better results
        if combined_content:
            # Truncate if too long (to avoid token limits)
            max_context_length = 10000
            if len(combined_content) > max_context_length:
                combined_content = combined_content[:max_context_length] + "..."
            
            context_topic = f"{topic}\n\nContext:\n{combined_content}"
        else:
            context_topic = topic
        
        presentation_data = ai_client.generate_presentation_structure(context_topic, slide_count)
        
        # Generate presentation ID before fetching images
        ppt_id = str(uuid.uuid4())
        user_id = getattr(request, 'user_id', 'anonymous')
        
        # Fetch images from Pixabay if API key available
        image_paths = {}
        image_firebase_urls = {}
        suggested_images_by_slide = {}
        firebase_service = FirebaseService()
        
        if os.getenv('PIXABAY_API_KEY'):
            try:
                pixabay = PixabayClient()
                
                for slide in presentation_data.get('slides', []):
                    slide_num = slide.get('slide_number', slide.get('index', 0) + 1)
                    keywords = slide.get('image_keywords', topic)
                    
                    # Get image suggestions
                    suggestions = pixabay.get_image_suggestions(keywords, count=5)
                    suggested_images_by_slide[slide_num] = suggestions
                    
                    # Download best image for actual PPT
                    if suggestions:
                        best_img = suggestions[0]
                        # img_path: stored in BE temp_images/ for backend/PPT download
                        img_path = f"temp_images/slide_{slide_num}.jpg"
                        # img_path2: frontend temp_images path for display purposes
                        img_path2 = f"../FE_jsx/temp_images/slide_{slide_num}.jpg"
                        
                        if pixabay.download_image(best_img['webformat_url'], img_path2):
                            # Store backend path for PPT generation
                            image_paths[slide_num] = img_path
                            
                            # Upload to Firebase Storage
                            try:
                                firebase_storage_path = f"presentations/{user_id}/{ppt_id}/slide_{slide_num}.jpg"
                                firebase_url = firebase_service.upload_image(img_path2, firebase_storage_path)
                                if firebase_url:
                                    image_firebase_urls[slide_num] = firebase_url
                                    logger.info(f"Uploaded slide {slide_num} to Firebase: {firebase_storage_path}")
                            except Exception as e:
                                logger.error(f"Failed to upload slide {slide_num} to Firebase: {e}")
                
                logger.info(f"Fetched images for {len(image_paths)} slides")
            except Exception as e:
                logger.error(f"Error fetching images: {e}")
        
        # Generate PowerPoint file
        ppt_service = PPTService(theme=theme, brand_colors=brand_colors)
        ppt_bytes = ppt_service.generate_from_data(presentation_data, image_paths)
        
        # Format slides for response
        slides_response = []
        for slide in presentation_data.get('slides', []):
            slide_num = slide.get('slide_number', slide.get('index', 0) + 1)
            
            # Use Firebase URL if available, otherwise fallback to local path
            image_firebase_url = image_firebase_urls.get(slide_num)
            image_url = f'/temp_images/slide_{slide_num}.jpg' if image_paths.get(slide_num) else None
            
            slides_response.append({
                'index': slide_num - 1,
                'title': slide.get('title', ''),
                'content': slide.get('content', []),
                'bullets': slide.get('content', []),
                'speaker_notes': slide.get('speaker_notes', ''),
                'layout': 'content',
                'suggested_images': suggested_images_by_slide.get(slide_num, []),
                'image_path': image_url,
                'image_firebase_url': image_firebase_url
            })
        
        # Update presentation data with formatted slides
        presentation_data['slides'] = slides_response
        
        # Store presentation metadata in storage
        ppt_metadata = {
            'topic': topic,
            'theme': theme,
            'slides': slides_response,
            'ppt_bytes': ppt_bytes,
            'image_paths': image_paths,
            'image_firebase_urls': image_firebase_urls,
            'content_sources': content_sources,
            'user_id': user_id
        }
        
        # Store in local storage
        ppt_storage.create(ppt_metadata)
        
        # Also store in Firestore with Firebase image URLs
        try:
            firebase_service.create_presentation(user_id, {
                'ppt_id': ppt_id,
                'topic': topic,
                'theme': theme,
                'slides': slides_response,  # Includes Firebase URLs
                'image_firebase_urls': image_firebase_urls,
                'content_sources': content_sources,
                'brand_colors': brand_colors
            })
            logger.info(f"Presentation stored in Firestore with ID: {ppt_id}")
        except Exception as e:
            logger.error(f"Failed to store presentation in Firestore: {e}")
        
        logger.info(f"PPT generated successfully with ID: {ppt_id}")
        
        return jsonify({
            'ppt_id': ppt_id,
            'slides': slides_response,
            'download_url': f'/api/v1/download/{ppt_id}',
            'content_sources': [
                {
                    'type': source['type'],
                    'details': source.get('urls') or source.get('articles', [])
                } for source in content_sources
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating PPT: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to generate presentation',
            'message': str(e),
            'code': 500
        }), 500
