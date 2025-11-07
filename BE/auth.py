import logging
from functools import wraps
from flask import request, jsonify
from typing import Optional, Dict

import firebase_admin
from firebase_admin import credentials, auth

class FirebaseService:
    def __init__(self):
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)

    def verify_token(self, token: str) -> Optional[Dict]:
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            logging.error(f"Error verifying Firebase ID token: {e}")
            return None

firebase_service = FirebaseService()
from services.firebase_service import firebase_service


logger = logging.getLogger(__name__)


class FirebaseAuth:
    """Firebase authentication handler"""

    def __init__(self):
        self.firebase = firebase_service

    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify Firebase ID token

        Args:
            token: Firebase ID token from Authorization header

        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            # Verify token using Firebase Admin SDK
            decoded_token = self.firebase.verify_token(token)

            if not decoded_token:
                return None

            return {
                'user_id': decoded_token.get('uid'),
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False),
                'name': decoded_token.get('name')
            }

        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None


# Initialize auth
firebase_auth = FirebaseAuth()


def require_auth(f):
    """
    Decorator to require Firebase authentication for endpoint
    Extracts user info from token and adds to request object
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Missing or invalid authorization header',
                'code': 401
            }), 401

        token = auth_header.split(' ')[1]

        # Verify token
        user_info = firebase_auth.verify_token(token)

        if not user_info:
            return jsonify({
                'error': 'Invalid or expired token',
                'code': 401
            }), 401

        # Add user info to request
        request.user_id = user_info['user_id']
        request.user_email = user_info.get('email')
        request.user_info = user_info

        return f(*args, **kwargs)

    return decorated_function


def optional_auth(f):
    """
    Decorator for optional authentication
    If token is provided and valid, adds user info to request
    If token is missing or invalid, continues without auth
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user_info = firebase_auth.verify_token(token)

            if user_info:
                request.user_id = user_info['user_id']
                request.user_email = user_info.get('email')
                request.user_info = user_info
            else:
                request.user_id = None
                request.user_info = None
        else:
            request.user_id = None
            request.user_info = None

        return f(*args, **kwargs)

    return decorated_function