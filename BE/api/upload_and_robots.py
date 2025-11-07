"""
Upload and Robots.txt Check API Endpoints
Handles document uploads and robots.txt checking
"""
from flask import Blueprint, request, jsonify
import logging
import os
import tempfile
from werkzeug.utils import secure_filename

from services.robots import check_robots_txt, fetch_robots_txt

logger = logging.getLogger(__name__)

upload_robots_bp = Blueprint('upload_robots', __name__)


@upload_robots_bp.route('/upload-source', methods=['POST'])
def upload_source():
    """
    Upload PDF or DOCX file and extract text
    
    Form data:
        file: PDF or DOCX file
    
    Returns:
    {
        "source_id": "uuid",
        "text": "Extracted text content",
        "filename": "original_filename.pdf"
    }
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'code': 400
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'code': 400
            }), 400
        
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in ['.pdf', '.docx']:
            return jsonify({
                'error': 'Only PDF and DOCX files are supported',
                'code': 400
            }), 400
        
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        # Extract text based on file type
        extracted_text = ""
        
        try:
            if file_ext == '.pdf':
                extracted_text = extract_text_from_pdf(temp_path)
            elif file_ext == '.docx':
                extracted_text = extract_text_from_docx(temp_path)
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        if not extracted_text:
            return jsonify({
                'error': 'Failed to extract text from document',
                'code': 500
            }), 500
        
        # Generate source ID (in a real app, you might store this)
        import uuid
        source_id = str(uuid.uuid4())
        
        logger.info(f"Extracted {len(extracted_text)} characters from {filename}")
        
        return jsonify({
            'source_id': source_id,
            'text': extracted_text,
            'filename': filename
        }), 200
        
    except Exception as e:
        logger.error(f"Error uploading source: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to process uploaded file',
            'message': str(e),
            'code': 500
        }), 500


@upload_robots_bp.route('/robots-check', methods=['GET'])
def robots_check():
    """
    Check if a URL allows scraping based on robots.txt
    
    Query params:
        url: URL to check (required)
    
    Returns:
    {
        "url": "https://example.com",
        "allowed": true,
        "message": "Scraping is allowed by robots.txt"
    }
    """
    try:
        url = request.args.get('url')
        
        if not url:
            return jsonify({
                'error': 'URL parameter is required',
                'code': 400
            }), 400
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return jsonify({
                'error': 'Invalid URL format. Must start with http:// or https://',
                'code': 400
            }), 400
        
        allowed, message = check_robots_txt(url)
        
        logger.info(f"Robots.txt check for {url}: allowed={allowed}")
        
        return jsonify({
            'url': url,
            'allowed': allowed,
            'message': message
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking robots.txt: {e}")
        return jsonify({
            'error': 'Failed to check robots.txt',
            'message': str(e),
            'code': 500
        }), 500


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    try:
        from PyPDF2 import PdfReader
        
        reader = PdfReader(pdf_path)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise


def extract_text_from_docx(docx_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        from docx import Document
        
        doc = Document(docx_path)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        raise
