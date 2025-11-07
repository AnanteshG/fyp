"""
Firebase Service
Handles Firebase Admin SDK initialization, authentication, Firestore, and Storage
"""
import os
import logging
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from typing import Optional, Dict, List, Any
import uuid

logger = logging.getLogger(__name__)


class FirebaseService:
    """Firebase service for authentication, storage, and database operations"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not FirebaseService._initialized:
            self._initialize_firebase()
            FirebaseService._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if already initialized
            if len(firebase_admin._apps) > 0:
                logger.info("Firebase already initialized")
                self.db = firestore.client()
                self.bucket = storage.bucket('fy-project-518d9.appspot.com')
                return
            
            service_key_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'service-key.json'
            )
            
            if not os.path.exists(service_key_path):
                raise FileNotFoundError(f"Service key not found at {service_key_path}")
            
            cred = credentials.Certificate(service_key_path)
            
            # Initialize with storage bucket
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'fy-project-518d9.appspot.com'
            })
            
            # Initialize Firestore and Storage clients AFTER firebase_admin.initialize_app()
            self.db = firestore.client()
            self.bucket = storage.bucket('fy-project-518d9.appspot.com')
            self.bucket = storage.bucket('fy-project-518d9.appspot.com')
            
            logger.info("Firebase initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    # ==================== Authentication ====================
    
    def verify_token(self, id_token: str) -> Optional[Dict]:
        """
        Verify Firebase ID token
        
        Args:
            id_token: Firebase ID token from client
            
        Returns:
            Decoded token with user info or None if invalid
        """
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def get_user(self, uid: str) -> Optional[Dict]:
        """Get user by UID"""
        try:
            user = auth.get_user(uid)
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'photo_url': user.photo_url,
                'email_verified': user.email_verified
            }
        except Exception as e:
            logger.error(f"Failed to get user {uid}: {e}")
            return None
    
    def create_custom_token(self, uid: str) -> Optional[str]:
        """Create custom token for user"""
        try:
            return auth.create_custom_token(uid)
        except Exception as e:
            logger.error(f"Failed to create custom token: {e}")
            return None
    
    # ==================== Storage ====================
    
    def upload_image(self, image_path: str, destination_path: str) -> Optional[str]:
        """
        Upload image to Firebase Storage
        
        Args:
            image_path: Local path to image file
            destination_path: Path in Firebase Storage (e.g., 'users/uid/images/slide_1.jpg')
            
        Returns:
            Public URL of uploaded image or None if failed
        """
        try:
            blob = self.bucket.blob(destination_path)
            blob.upload_from_filename(image_path)
            
            # Make public and get URL
            blob.make_public()
            public_url = blob.public_url
            
            logger.info(f"Uploaded image to {destination_path}")
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return None
    
    def upload_image_from_bytes(self, image_bytes: bytes, destination_path: str, content_type: str = 'image/jpeg') -> Optional[str]:
        """
        Upload image from bytes to Firebase Storage
        
        Args:
            image_bytes: Image data as bytes
            destination_path: Path in Firebase Storage
            content_type: MIME type of image
            
        Returns:
            Public URL of uploaded image or None if failed
        """
        try:
            blob = self.bucket.blob(destination_path)
            blob.upload_from_string(image_bytes, content_type=content_type)
            
            # Make public and get URL
            blob.make_public()
            public_url = blob.public_url
            
            logger.info(f"Uploaded image bytes to {destination_path}")
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to upload image bytes: {e}")
            return None
    
    def delete_image(self, storage_path: str) -> bool:
        """Delete image from Firebase Storage"""
        try:
            blob = self.bucket.blob(storage_path)
            blob.delete()
            logger.info(f"Deleted image at {storage_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete image: {e}")
            return False
    
    # ==================== Firestore - Presentations ====================
    
    def create_presentation(self, user_id: str, presentation_data: Dict) -> str:
        """
        Create a new presentation in Firestore
        
        Args:
            user_id: User's Firebase UID
            presentation_data: Presentation metadata and content
            
        Returns:
            Presentation ID
        """
        try:
            ppt_id = str(uuid.uuid4())
            
            doc_data = {
                'ppt_id': ppt_id,
                'user_id': user_id,
                'topic': presentation_data.get('topic', ''),
                'theme': presentation_data.get('theme', 'modern'),
                'slides': presentation_data.get('slides', []),
                'slide_count': len(presentation_data.get('slides', [])),
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'content_sources': presentation_data.get('content_sources', []),
                'brand_colors': presentation_data.get('brand_colors')
            }
            
            # Add to Firestore
            self.db.collection('presentations').document(ppt_id).set(doc_data)
            
            logger.info(f"Created presentation {ppt_id} for user {user_id}")
            return ppt_id
            
        except Exception as e:
            logger.error(f"Failed to create presentation: {e}")
            raise
    
    def get_presentation(self, ppt_id: str, user_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get presentation by ID
        
        Args:
            ppt_id: Presentation ID
            user_id: Optional user ID for authorization check
            
        Returns:
            Presentation data or None if not found
        """
        try:
            doc = self.db.collection('presentations').document(ppt_id).get()
            
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            
            # Check authorization if user_id provided
            if user_id and data.get('user_id') != user_id:
                logger.warning(f"User {user_id} attempted to access presentation {ppt_id}")
                return None
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get presentation {ppt_id}: {e}")
            return None
    
    def update_presentation(self, ppt_id: str, user_id: str, updates: Dict) -> bool:
        """
        Update presentation
        
        Args:
            ppt_id: Presentation ID
            user_id: User ID for authorization
            updates: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection('presentations').document(ppt_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
            
            data = doc.to_dict()
            
            # Check authorization
            if data.get('user_id') != user_id:
                logger.warning(f"User {user_id} attempted to update presentation {ppt_id}")
                return False
            
            # Update with timestamp
            updates['updated_at'] = firestore.SERVER_TIMESTAMP
            doc_ref.update(updates)
            
            logger.info(f"Updated presentation {ppt_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update presentation: {e}")
            return False
    
    def delete_presentation(self, ppt_id: str, user_id: str) -> bool:
        """Delete presentation and associated images"""
        try:
            doc_ref = self.db.collection('presentations').document(ppt_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
            
            data = doc.to_dict()
            
            # Check authorization
            if data.get('user_id') != user_id:
                logger.warning(f"User {user_id} attempted to delete presentation {ppt_id}")
                return False
            
            # Delete images from storage
            for slide in data.get('slides', []):
                if slide.get('image_storage_path'):
                    self.delete_image(slide['image_storage_path'])
            
            # Delete document
            doc_ref.delete()
            
            logger.info(f"Deleted presentation {ppt_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete presentation: {e}")
            return False
    
    def get_user_presentations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get all presentations for a user
        
        Args:
            user_id: User's Firebase UID
            limit: Maximum number of presentations to return
            
        Returns:
            List of presentation metadata
        """
        try:
            query = (self.db.collection('presentations')
                    .where('user_id', '==', user_id)
                    .order_by('created_at', direction=firestore.Query.DESCENDING)
                    .limit(limit))
            
            docs = query.stream()
            
            presentations = []
            for doc in docs:
                data = doc.to_dict()
                # Return summary without full slide content
                presentations.append({
                    'ppt_id': data.get('ppt_id'),
                    'topic': data.get('topic'),
                    'theme': data.get('theme'),
                    'slide_count': data.get('slide_count', 0),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at'),
                    'thumbnail': data.get('slides', [{}])[0].get('image_url') if data.get('slides') else None
                })
            
            return presentations
            
        except Exception as e:
            logger.error(f"Failed to get user presentations: {e}")
            return []


# Singleton instance
firebase_service = FirebaseService()
