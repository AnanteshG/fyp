"""
Test PPT Generation
Unit tests for presentation generation with mocked APIs
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from services.ppt_service import PPTService
from storage import PPTStorage


def test_ppt_service_initialization():
    """Test PPT service initialization"""
    ppt_service = PPTService(theme='modern')
    assert ppt_service.theme is not None
    assert ppt_service.prs is not None


def test_ppt_service_with_brand_colors():
    """Test PPT service with custom brand colors"""
    brand_colors = ['#1A73E8', '#FF6B6B']
    ppt_service = PPTService(theme='modern', brand_colors=brand_colors)
    assert ppt_service.theme is not None


def test_create_title_slide():
    """Test title slide creation"""
    ppt_service = PPTService()
    slide = ppt_service.create_title_slide("Test Title", "Test Subtitle")
    assert slide is not None
    assert len(ppt_service.prs.slides) == 1


def test_create_content_slide():
    """Test content slide creation"""
    ppt_service = PPTService()
    content = ["Point 1", "Point 2", "Point 3"]
    slide = ppt_service.create_content_slide("Test Slide", content)
    assert slide is not None
    assert len(ppt_service.prs.slides) == 1


def test_generate_from_data():
    """Test complete presentation generation"""
    ppt_service = PPTService()
    
    presentation_data = {
        'title': 'Test Presentation',
        'subtitle': 'Test Subtitle',
        'slides': [
            {
                'slide_number': 1,
                'title': 'Slide 1',
                'content': ['Point 1', 'Point 2'],
                'speaker_notes': 'Test notes'
            },
            {
                'slide_number': 2,
                'title': 'Slide 2',
                'content': ['Point A', 'Point B', 'Point C'],
                'speaker_notes': 'More notes'
            }
        ]
    }
    
    ppt_bytes = ppt_service.generate_from_data(presentation_data)
    
    assert ppt_bytes is not None
    assert len(ppt_bytes) > 0
    # Should have title slide + 2 content slides + thank you slide = 4 slides
    assert len(ppt_service.prs.slides) == 4


def test_storage_create():
    """Test creating a PPT entry in storage"""
    storage = PPTStorage()
    
    data = {
        'topic': 'Test Topic',
        'theme': 'modern',
        'slides': []
    }
    
    ppt_id = storage.create(data)
    
    assert ppt_id is not None
    assert len(ppt_id) > 0


def test_storage_get():
    """Test retrieving a PPT from storage"""
    storage = PPTStorage()
    
    data = {'topic': 'Test', 'slides': []}
    ppt_id = storage.create(data)
    
    retrieved = storage.get(ppt_id)
    
    assert retrieved is not None
    assert retrieved['ppt_id'] == ppt_id
    assert retrieved['topic'] == 'Test'


def test_storage_update():
    """Test updating a PPT in storage"""
    storage = PPTStorage()
    
    data = {'topic': 'Original', 'slides': []}
    ppt_id = storage.create(data)
    
    success = storage.update(ppt_id, {'topic': 'Updated'})
    
    assert success is True
    
    updated = storage.get(ppt_id)
    assert updated['topic'] == 'Updated'


def test_storage_delete():
    """Test deleting a PPT from storage"""
    storage = PPTStorage()
    
    data = {'topic': 'Test', 'slides': []}
    ppt_id = storage.create(data)
    
    deleted = storage.delete(ppt_id)
    
    assert deleted is True
    assert storage.get(ppt_id) is None


def test_storage_list_all():
    """Test listing all PPTs"""
    storage = PPTStorage()
    
    storage.create({'topic': 'Test 1', 'slides': []})
    storage.create({'topic': 'Test 2', 'slides': []})
    
    all_ppts = storage.list_all()
    
    assert len(all_ppts) >= 2


@patch('services.groq.Groq')
def test_groq_client_initialization(mock_groq):
    """Test Groq client initialization with mocked API"""
    from services.groq import GroqClient
    
    # Set environment variable for test
    import os
    os.environ['GROQ_API_KEY'] = 'test_key'
    
    client = GroqClient()
    assert client.api_key == 'test_key'
    
    del os.environ['GROQ_API_KEY']


@patch('services.pixabay.requests.get')
def test_pixabay_search(mock_get):
    """Test Pixabay image search with mocked API"""
    from services.pixabay import PixabayClient
    import os
    
    # Set environment variable
    os.environ['PIXABAY_API_KEY'] = 'test_key'
    
    # Mock response
    mock_response = Mock()
    mock_response.json.return_value = {
        'hits': [
            {'id': 1, 'previewURL': 'http://example.com/preview1.jpg'},
            {'id': 2, 'previewURL': 'http://example.com/preview2.jpg'}
        ]
    }
    mock_get.return_value = mock_response
    
    client = PixabayClient()
    results = client.search_images('test query')
    
    assert len(results) == 2
    assert results[0]['id'] == 1
    
    del os.environ['PIXABAY_API_KEY']
