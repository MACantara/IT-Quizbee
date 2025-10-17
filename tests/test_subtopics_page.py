"""
Tests for the IT Quizbee Subtopics Selection Page

This module contains tests that verify subtopics are displayed correctly
for a given topic and that navigation works as expected.
"""

import pytest
from playwright.sync_api import Page, expect


class TestSubtopicsPage:
    """Tests for the subtopics selection page"""
    
    def test_subtopics_displayed(self, page: Page):
        """Test that subtopics are displayed for a topic"""
        # Navigate to a known topic (computer_architecture)
        page.goto("http://localhost:5000/topics/computer_architecture/subtopics")
        
        # Check subtopic cards exist
        subtopic_cards = page.locator("a[href*='/mode']")
        expect(subtopic_cards.first).to_be_visible()
    
    def test_back_to_topics_button(self, page: Page):
        """Test back to topics navigation"""
        page.goto("http://localhost:5000/topics/computer_architecture/subtopics")
        
        # Click back button
        page.click("text=Back to Topics")
        
        # Should be on topics page
        page.wait_for_url("**/topics")
        expect(page.locator("text=Choose Your Topic")).to_be_visible()
    
    def test_subtopic_click_navigates_to_mode_selection(self, page: Page):
        """Test clicking subtopic goes to mode selection"""
        page.goto("http://localhost:5000/topics/computer_architecture/subtopics")
        
        # Click first subtopic
        first_subtopic = page.locator("a[href*='/mode']").first
        first_subtopic.click()
        
        # Should be on mode selection page
        expect(page.locator("text=Choose your game mode")).to_be_visible()
