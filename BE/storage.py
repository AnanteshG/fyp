"""
In-Memory Storage Module
Stores generated PPT data temporarily using dictionaries keyed by UUID
This can be easily swapped with a database later
"""
import uuid
from datetime import datetime
from typing import Dict, Optional, Any
from threading import Lock


class PPTStorage:
    """In-memory storage for PPT sessions"""
    
    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
    
    def create(self, data: Dict[str, Any]) -> str:
        """
        Create a new PPT session
        
        Args:
            data: PPT metadata and content
            
        Returns:
            UUID string for the session
        """
        with self._lock:
            ppt_id = str(uuid.uuid4())
            self._storage[ppt_id] = {
                **data,
                'ppt_id': ppt_id,
                'generated_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
            }
            return ppt_id
    
    def get(self, ppt_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve PPT session by ID
        
        Args:
            ppt_id: Session UUID
            
        Returns:
            Session data or None if not found
        """
        with self._lock:
            return self._storage.get(ppt_id)
    
    def update(self, ppt_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update PPT session
        
        Args:
            ppt_id: Session UUID
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful, False if not found
        """
        with self._lock:
            if ppt_id in self._storage:
                self._storage[ppt_id].update(updates)
                self._storage[ppt_id]['updated_at'] = datetime.utcnow().isoformat()
                return True
            return False
    
    def delete(self, ppt_id: str) -> bool:
        """
        Delete PPT session
        
        Args:
            ppt_id: Session UUID
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if ppt_id in self._storage:
                del self._storage[ppt_id]
                return True
            return False
    
    def list_all(self) -> list:
        """
        List all PPT sessions
        
        Returns:
            List of all session metadata (without binary data)
        """
        with self._lock:
            return [
                {
                    'ppt_id': ppt_id,
                    'topic': data.get('topic', ''),
                    'theme': data.get('theme', ''),
                    'generated_at': data.get('generated_at', ''),
                    'slide_count': len(data.get('slides', []))
                }
                for ppt_id, data in self._storage.items()
            ]
    
    def clear_old_sessions(self, max_age_hours: int = 24):
        """
        Clear sessions older than specified hours
        
        Args:
            max_age_hours: Maximum age in hours
        """
        with self._lock:
            now = datetime.utcnow()
            to_delete = []
            
            for ppt_id, data in self._storage.items():
                generated_at = datetime.fromisoformat(data.get('generated_at', now.isoformat()))
                age_hours = (now - generated_at).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    to_delete.append(ppt_id)
            
            for ppt_id in to_delete:
                del self._storage[ppt_id]
            
            return len(to_delete)


# Global storage instance
ppt_storage = PPTStorage()
