#!/usr/bin/env python3
"""Test Firebase initialization"""
import sys
import os
import logging

# Add BE to path
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging to see errors
logging.basicConfig(level=logging.DEBUG)

try:
    print("Testing Firebase import...")
    from services.firebase_service import firebase_service
    print("[OK] Firebase imported successfully!")
    print(f"Firebase service instance: {firebase_service}")
except Exception as e:
    print(f"[ERROR] Firebase import failed: {e}")
    import traceback
    traceback.print_exc()
