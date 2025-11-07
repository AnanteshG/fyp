"""
Replace Image API Endpoint
Handles replacing images on slides
"""
from flask import Blueprint, request, jsonify
import logging
import os

from auth import require_auth
from storage import ppt_storage
from services.pixabay import PixabayClient
from services.ppt_service import PPTService
from services.firebase_service import firebase_service

logger = logging.getLogger(__name__)

replace_image_bp = Blueprint('replace_image', __name__)


@replace_image_bp.route('/replace-image', methods=['POST'])
@require_auth
def replace_image():
    """
    Replace an image on a slide
    
    Request JSON:
    {
        "ppt_id": "uuid",
        "slide_index": 0,
        "pixabay_image_id": "12345"
    }
    
    Returns updated PPT metadata
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided', 'code': 400}), 400
        
        ppt_id = data.get('ppt_id')
        slide_index = data.get('slide_index')
        image_id = data.get('pixabay_image_id')
        
        if not all([ppt_id, slide_index is not None, image_id]):
            return jsonify({
                'error': 'ppt_id, slide_index, and pixabay_image_id are required',
                'code': 400
            }), 400
        
        # Get PPT data
        ppt_data = ppt_storage.get(ppt_id)
        
        if not ppt_data:
            return jsonify({
                'error': 'Presentation not found',
                'code': 404
            }), 404
        
        slides = ppt_data.get('slides', [])
        
        if slide_index < 0 or slide_index >= len(slides):
            return jsonify({
                'error': 'Slide index out of range',
                'code': 400
            }), 400
        
        # Find the image in suggested images or search for it
        slide = slides[slide_index]
        image_url = None
        
        # Check suggested images first
        for img in slide.get('suggested_images', []):
            if img.get('id') == image_id:
                image_url = img.get('webformat_url')
                break
        
        # If not found, search Pixabay
        if not image_url and os.getenv('PIXABAY_API_KEY'):
            pixabay = PixabayClient()
            # Try to get the specific image (Pixabay API doesn't support this directly,
            # so we search and find the matching ID)
            keywords = slide.get('suggested_images', [{}])[0].get('keywords', ppt_data.get('topic', ''))
            images = pixabay.search_images(keywords, per_page=20)
            
            for img in images:
                if str(img.get('id')) == str(image_id):
                    image_url = img.get('webformatURL')
                    break
        
        if not image_url:
            return jsonify({
                'error': 'Image not found',
                'code': 404
            }), 404
        
        # Download new image
        pixabay = PixabayClient()
        slide_num = slide_index + 1
        img_path = f"temp_images/slide_{slide_num}_updated.jpg"
        
        if not pixabay.download_image(image_url, img_path):
            return jsonify({
                'error': 'Failed to download image',
                'code': 500
            }), 500
        
        # Upload to Firebase Storage
        user_id = getattr(request, 'user_id', 'anonymous')
        ppt_id_val = ppt_id  # Use the ppt_id from the request
        storage_path = f"users/{user_id}/presentations/{ppt_data.get('topic', 'presentation').replace(' ', '_')}/slide_{slide_num}.jpg"
        firebase_url = firebase_service.upload_image(img_path, storage_path)
        
        # Update image paths
        image_paths = ppt_data.get('image_paths', {})
        image_paths[slide_num] = img_path
        image_storage_paths = ppt_data.get('image_storage_paths', {})
        if firebase_url:
            image_storage_paths[slide_num] = storage_path
        
        # Regenerate PPT with new image
        ppt_service = PPTService(theme=ppt_data.get('theme', 'modern'))
        
        presentation_data = {
            'title': ppt_data.get('topic', 'Presentation'),
            'slides': [
                {
                    'slide_number': s['index'] + 1,
                    'title': s['title'],
                    'content': s['bullets'],
                    'speaker_notes': s.get('speaker_notes', '')
                }
                for s in slides
            ]
        }
        
        ppt_bytes = ppt_service.generate_from_data(presentation_data, image_paths)
        
        # Update storage
        ppt_storage.update(ppt_id, {
            'image_paths': image_paths,
            'image_storage_paths': image_storage_paths,
            'image_urls': {slide_num: firebase_url} if firebase_url else {},
            'ppt_bytes': ppt_bytes
        })
        
        logger.info(f"Replaced image on slide {slide_index} in PPT {ppt_id}")
        
        # Return updated metadata
        updated_data = ppt_storage.get(ppt_id)
        
        # Format slides with proper image URLs
        slides = []
        image_paths = updated_data.get('image_paths', {})
        image_urls = updated_data.get('image_urls', {})
        for slide in updated_data.get('slides', []):
            slide_copy = slide.copy()
            slide_num = slide['index'] + 1
            
            # Use Firebase URL if available, otherwise use local path
            firebase_url = image_urls.get(slide_num)
            local_path = image_paths.get(slide_num)
            
            if firebase_url:
                slide_copy['image_path'] = firebase_url
                slide_copy['image_firebase_url'] = firebase_url
            elif local_path:
                slide_copy['image_path'] = f'/temp_images/slide_{slide_num}_updated.jpg' if 'updated' in local_path else f'/temp_images/slide_{slide_num}.jpg'
        
            slides.append(slide_copy)
        
        return jsonify({
            'ppt_id': updated_data['ppt_id'],
            'topic': updated_data.get('topic', ''),
            'theme': updated_data.get('theme', 'modern'),
            'slides': slides,
            'generated_at': updated_data.get('generated_at', ''),
            'download_url': f'/api/v1/download/{ppt_id}'
        }), 200
        
    except Exception as e:
        logger.error(f"Error replacing image: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to replace image',
            'message': str(e),
            'code': 500
        }), 500
