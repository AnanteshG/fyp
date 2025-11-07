"""
Test Robots.txt Checker
Unit tests for robots.py module with mocked HTTP requests
"""
import pytest
from unittest.mock import Mock, patch
from services.robots import check_robots_txt, get_robots_url


def test_get_robots_url():
    """Test robots.txt URL construction"""
    url = "https://example.com/path/to/page"
    expected = "https://example.com/robots.txt"
    assert get_robots_url(url) == expected


def test_get_robots_url_with_port():
    """Test robots.txt URL with port"""
    url = "http://example.com:8080/path"
    expected = "http://example.com:8080/robots.txt"
    assert get_robots_url(url) == expected


@patch('services.robots.urllib.robotparser.RobotFileParser')
def test_check_robots_allowed(mock_robot_parser):
    """Test when scraping is allowed"""
    mock_instance = Mock()
    mock_instance.can_fetch.return_value = True
    mock_robot_parser.return_value = mock_instance
    
    allowed, message = check_robots_txt("https://example.com/page")
    
    assert allowed is True
    assert "allowed" in message.lower()


@patch('services.robots.urllib.robotparser.RobotFileParser')
def test_check_robots_disallowed(mock_robot_parser):
    """Test when scraping is disallowed"""
    mock_instance = Mock()
    mock_instance.can_fetch.return_value = False
    mock_robot_parser.return_value = mock_instance
    
    allowed, message = check_robots_txt("https://example.com/page")
    
    assert allowed is False
    assert "disallowed" in message.lower()


@patch('services.robots.urllib.robotparser.RobotFileParser')
def test_check_robots_error_handling(mock_robot_parser):
    """Test error handling when robots.txt cannot be read"""
    mock_instance = Mock()
    mock_instance.read.side_effect = Exception("Network error")
    mock_robot_parser.return_value = mock_instance
    
    allowed, message = check_robots_txt("https://example.com/page")
    
    # Should fail safely by disallowing scraping
    assert allowed is False
    assert "error" in message.lower() or "could not" in message.lower()
