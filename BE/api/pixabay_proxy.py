"""
Pixabay Proxy API Endpoint
Proxies image search requests to Pixabay API
"""
from flask import Blueprint, request, jsonify
import logging
import os

from services.pixabay import PixabayClient

logger = logging.getLogger(__name__)

pixabay_bp = Blueprint('pixabay', __name__)


@pixabay_bp.route('/pixabay/search', methods=['GET'])
def search_pixabay():
    """
    Search Pixabay for images
    
    Query params:
        q: Search query (required)
        page: Page number (default: 1)
        per_page: Results per page (default: 20, max: 200)
    
    Returns:
    {
        "images": [
            {
                "id": "12345",
                "preview_url": "...",
                "webformat_url": "...",
                "large_url": "...",
                "keywords": "...",
                "user": "..."
            }
        ],
        "total": 100,
        "page": 1,
        "per_page": 20
    }
    """
    try:
        query = request.args.get('q')
        
        if not query:
            return jsonify({
                'error': 'Query parameter "q" is required',
                'code': 400
            }), 400
        
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 200)
        
        if not os.getenv('PIXABAY_API_KEY'):
            return jsonify({
                'error': 'Pixabay API key not configured',
                'code': 500
            }), 500
        
        pixabay = PixabayClient()
        results = pixabay.search_images(query, per_page=per_page, page=page)
        
        # Format response
        images = []
        for img in results:
            images.append({
                'id': str(img.get('id')),
                'previewURL': img.get('previewURL'),
                'webformatURL': img.get('webformatURL'),
                'largeImageURL': img.get('largeImageURL'),
                'tags': img.get('tags', ''),
                'user': img.get('user', 'Unknown'),
                'pageURL': img.get('pageURL', '')
            })
        
        logger.info(f"Pixabay search for '{query}' returned {len(images)} results")
        
        return jsonify({
            'images': images,
            'total': len(images),
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching Pixabay: {e}")
        return jsonify({
            'error': 'Failed to search images',
            'message': str(e),
            'code': 500
        }), 500
