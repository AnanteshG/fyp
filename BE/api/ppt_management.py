"""
PPT Management API Endpoints
Handles get, download, update, and delete operations for PPTs
"""
from flask import Blueprint, request, jsonify, send_file
import logging
import io

from storage import ppt_storage
from services.ppt_service import PPTService

logger = logging.getLogger(__name__)

ppt_mgmt_bp = Blueprint('ppt_management', __name__)


def format_slides_for_response(slides, image_paths):
    """Convert slides with local image paths to URLs for frontend"""
    formatted_slides = []
    for slide in slides:
        slide_copy = slide.copy()
        slide_num = slide['index'] + 1
        
        # Convert local image path to URL if exists
        if image_paths and slide_num in image_paths:
            slide_copy['image_path'] = f'/temp_images/slide_{slide_num}.jpg'
        
        formatted_slides.append(slide_copy)
    
    return formatted_slides


@ppt_mgmt_bp.route('/ppt/<ppt_id>', methods=['GET'])
def get_ppt(ppt_id):
    """
    Get PPT metadata (without binary data)
    
    Returns:
    {
        "ppt_id": "uuid",
        "topic": "...",
        "theme": "...",
        "slides": [...],
        "generated_at": "...",
        "download_url": "..."
    }
    """
    try:
        ppt_data = ppt_storage.get(ppt_id)
        
        if not ppt_data:
            return jsonify({
                'error': 'Presentation not found',
                'code': 404
            }), 404
        
        # Format slides with proper image URLs
        slides = format_slides_for_response(
            ppt_data.get('slides', []),
            ppt_data.get('image_paths', {})
        )
        
        # Return metadata without binary data
        response_data = {
            'ppt_id': ppt_data['ppt_id'],
            'topic': ppt_data.get('topic', ''),
            'theme': ppt_data.get('theme', 'modern'),
            'slides': slides,
            'generated_at': ppt_data.get('generated_at', ''),
            'download_url': f'/api/v1/download/{ppt_id}'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error retrieving PPT {ppt_id}: {e}")
        return jsonify({
            'error': 'Failed to retrieve presentation',
            'message': str(e),
            'code': 500
        }), 500


@ppt_mgmt_bp.route('/download/<ppt_id>', methods=['GET'])
def download_ppt(ppt_id):
    """
    Download PPT file as PPTX
    
    Returns binary PPTX file
    """
    try:
        ppt_data = ppt_storage.get(ppt_id)
        
        if not ppt_data:
            return jsonify({
                'error': 'Presentation not found',
                'code': 404
            }), 404
        
        ppt_bytes = ppt_data.get('ppt_bytes')
        
        if not ppt_bytes:
            return jsonify({
                'error': 'Presentation file not available',
                'code': 404
            }), 404
        
        # Create filename from topic
        topic = ppt_data.get('topic', 'presentation')
        filename = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = filename.replace(' ', '_') + '.pptx'
        
        logger.info(f"Downloading PPT {ppt_id} as {filename}")
        
        return send_file(
            io.BytesIO(ppt_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error downloading PPT {ppt_id}: {e}")
        return jsonify({
            'error': 'Failed to download presentation',
            'message': str(e),
            'code': 500
        }), 500


@ppt_mgmt_bp.route('/ppt/<ppt_id>', methods=['DELETE'])
def delete_ppt(ppt_id):
    """
    Delete a PPT from storage
    
    Returns:
    {
        "success": true,
        "message": "Presentation deleted"
    }
    """
    try:
        deleted = ppt_storage.delete(ppt_id)
        
        if not deleted:
            return jsonify({
                'error': 'Presentation not found',
                'code': 404
            }), 404
        
        logger.info(f"Deleted PPT {ppt_id}")
        
        return jsonify({
            'success': True,
            'message': 'Presentation deleted'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting PPT {ppt_id}: {e}")
        return jsonify({
            'error': 'Failed to delete presentation',
            'message': str(e),
            'code': 500
        }), 500


@ppt_mgmt_bp.route('/ppt/<ppt_id>/slide/<int:slide_index>', methods=['PATCH'])
def update_slide(ppt_id, slide_index):
    """
    Update slide content
    
    Request JSON:
    {
        "title": "New title",  // optional
        "bullets": ["New bullet 1", ...],  // optional
        "speaker_notes": "..."  // optional
    }
    
    Returns updated PPT metadata
    """
    try:
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
        
        updates = request.get_json()
        
        if not updates:
            return jsonify({
                'error': 'No updates provided',
                'code': 400
            }), 400
        
        # Update slide data
        if 'title' in updates:
            slides[slide_index]['title'] = updates['title']
        if 'bullets' in updates:
            slides[slide_index]['bullets'] = updates['bullets']
        if 'speaker_notes' in updates:
            slides[slide_index]['speaker_notes'] = updates['speaker_notes']
        
        # Regenerate PPT with updated content
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
        
        ppt_bytes = ppt_service.generate_from_data(
            presentation_data,
            ppt_data.get('image_paths', {})
        )
        
        # Update storage
        ppt_storage.update(ppt_id, {
            'slides': slides,
            'ppt_bytes': ppt_bytes
        })
        
        logger.info(f"Updated slide {slide_index} in PPT {ppt_id}")
        
        # Return updated metadata
        updated_data = ppt_storage.get(ppt_id)
        
        # Format slides with proper image URLs
        slides = format_slides_for_response(
            updated_data.get('slides', []),
            updated_data.get('image_paths', {})
        )
        
        return jsonify({
            'ppt_id': updated_data['ppt_id'],
            'topic': updated_data.get('topic', ''),
            'theme': updated_data.get('theme', 'modern'),
            'slides': slides,
            'generated_at': updated_data.get('generated_at', ''),
            'download_url': f'/api/v1/download/{ppt_id}'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating slide in PPT {ppt_id}: {e}")
        return jsonify({
            'error': 'Failed to update slide',
            'message': str(e),
            'code': 500
        }), 500
