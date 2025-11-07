"""
Auth and History API Endpoints
Handles user presentations history
"""
from flask import Blueprint, request, jsonify
import logging
from auth import require_auth
from services.firebase_service import firebase_service

logger = logging.getLogger(__name__)

history_bp = Blueprint('history', __name__)


@history_bp.route('/history', methods=['GET'])
@require_auth
def get_history():
    """
    Get user's presentation history
    
    Returns:
    {
        "presentations": [
            {
                "ppt_id": "uuid",
                "topic": "...",
                "theme": "modern",
                "slide_count": 5,
                "created_at": "...",
                "updated_at": "...",
                "thumbnail": "https://..."
            }
        ]
    }
    """
    try:
        user_id = request.user_id
        limit = request.args.get('limit', 50, type=int)
        
        presentations = firebase_service.get_user_presentations(user_id, limit=limit)
        
        return jsonify({
            'presentations': presentations,
            'count': len(presentations)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return jsonify({
            'error': 'Failed to fetch presentation history',
            'message': str(e),
            'code': 500
        }), 500


@history_bp.route('/user/info', methods=['GET'])
@require_auth
def get_user_info():
    """Get current user information"""
    try:
        user_info = request.user_info
        
        return jsonify({
            'user_id': user_info.get('user_id'),
            'email': user_info.get('email'),
            'email_verified': user_info.get('email_verified'),
            'name': user_info.get('name')
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching user info: {e}")
        return jsonify({
            'error': 'Failed to fetch user info',
            'message': str(e),
            'code': 500
        }), 500
