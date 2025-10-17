"""
Tests for the IT Quizbee Topics Selection Page

This module contains tests that verify the topics page displays all 10 topics
correctly and that navigation to/from the page works as expected.
"""

import pytest
from playwright.sync_api import Page, expect


class TestTopicsPage:
    """Tests for the topics selection page"""
    
    def test_navigate_to_topics(self, page: Page):
        """Test navigation from welcome to topics page"""
        page.goto("http://localhost:5000")
        
        # Click Start Quiz button
        page.click("text=Start Quiz")
        
        # Wait for navigation
        page.wait_for_url("**/topics")
        
        # Check topics page loaded
        expect(page.locator("text=Choose Your Topic")).to_be_visible()
    
    def test_topics_displayed(self, page: Page):
        """Test that all 10 topics are displayed"""
        page.goto("http://localhost:5000/topics")
        
        # Check for topic cards (should be 10)
        topic_cards = page.locator("a[href*='/topics/']")
        expect(topic_cards).to_have_count(10)
    
    def test_topic_navigation(self, page: Page):
        """Test clicking on a topic navigates to subtopics"""
        page.goto("http://localhost:5000/topics")
        
        # Click first topic
        first_topic = page.locator("a[href*='/topics/']").first
        first_topic.click()
        
        # Check subtopics page loaded
        expect(page.locator("text=Back to Topics")).to_be_visible()
    
    def test_home_button_from_topics(self, page: Page):
        """Test home button returns to welcome page"""
        page.goto("http://localhost:5000/topics")
        
        # Click home button
        page.click("text=Home")
        
        # Should be back on welcome page
        expect(page.locator("text=Welcome to IT Quizbee!")).to_be_visible()
