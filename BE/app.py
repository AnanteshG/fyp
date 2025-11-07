"""
Flask Application - SlideX Backend
Main application entry point with CORS, logging, and error handling
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API blueprints
from api.generate import generate_bp
from api.ppt_management import ppt_mgmt_bp
from api.replace_image import replace_image_bp
from api.pixabay_proxy import pixabay_bp
from api.upload_and_robots import upload_robots_bp
from api.history import history_bp

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['JSON_SORT_KEYS'] = False

# Enable CORS
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('CORS_ORIGINS', '*'),
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Setup logging
def setup_logging():
    """Configure application logging"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s'
    ))
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # App logger
    app.logger.setLevel(logging.INFO)
    app.logger.info("Logging configured")

setup_logging()

# Register blueprints
app.register_blueprint(generate_bp, url_prefix='/api/v1')
app.register_blueprint(ppt_mgmt_bp, url_prefix='/api/v1')
app.register_blueprint(replace_image_bp, url_prefix='/api/v1')
app.register_blueprint(pixabay_bp, url_prefix='/api/v1')
app.register_blueprint(upload_robots_bp, url_prefix='/api/v1')
app.register_blueprint(history_bp, url_prefix='/api/v1')

# Serve static images from temp_images directory
@app.route('/temp_images/<path:filename>')
def serve_temp_image(filename):
    """Serve images from temp_images directory"""
    return send_from_directory('temp_images', filename)

# Global error handlers
@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors"""
    return jsonify({
        'error': 'Bad Request',
        'message': str(error),
        'code': 400
    }), 400

@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'code': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors"""
    app.logger.error(f'Internal error: {error}')
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'code': 500
    }), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all other exceptions"""
    app.logger.error(f'Unhandled exception: {error}', exc_info=True)
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'code': 500
    }), 500

# Health check endpoint
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'SlideX API',
        'version': '1.0.0'
    }), 200

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'service': 'SlideX API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/v1/health',
            'generate': '/api/v1/generate',
            'ppt': '/api/v1/ppt/<id>',
            'download': '/api/v1/download/<id>',
            'replace_image': '/api/v1/replace-image',
            'pixabay_search': '/api/v1/pixabay/search',
            'upload_source': '/api/v1/upload-source',
            'robots_check': '/api/v1/robots-check'
        }
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = True
    
    app.logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
