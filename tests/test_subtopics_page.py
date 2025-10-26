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
        # Navigate through topics first
        page.goto("http://localhost:5000/topics")
        page.wait_for_load_state("networkidle")
        
        # Click first topic to go to its subtopics
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        
        # Check subtopic cards exist (they should be links)
        subtopic_cards = page.locator("a").filter(has_text="Questions per mode")
        expect(subtopic_cards.first).to_be_visible()
    
    def test_back_to_topics_button(self, page: Page):
        """Test back to topics navigation"""
        # Navigate through topics first
        page.goto("http://localhost:5000/topics")
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        
        # Click back button
        page.click("text=Back to Topics")
        
        # Should be on topics page
        page.wait_for_url("**/topics")
        expect(page.locator("text=Choose Your Topic")).to_be_visible()
    
    def test_subtopic_click_navigates_to_mode_selection(self, page: Page):
        """Test clicking subtopic goes to mode selection"""
        # Navigate through topics first
        page.goto("http://localhost:5000/topics")
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        
        # Click first subtopic
        first_subtopic = page.locator("a").filter(has_text="Questions per mode").first
        first_subtopic.click()
        page.wait_for_load_state("networkidle")
        
        # Should be on mode selection page
        expect(page.locator("text=Choose your game mode")).to_be_visible()
