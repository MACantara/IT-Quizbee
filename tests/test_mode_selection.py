"""
Tests for the IT Quizbee Mode Selection Page

This module contains tests that verify users can select between Elimination
and Finals modes, and that all three difficulty levels work for Finals mode.
"""

import pytest
from playwright.sync_api import Page, expect


def fill_name_modal_if_present(page: Page, name: str = "Test User"):
    """
    Helper function to fill the name modal if it's present on the page
    
    Args:
        page: Playwright page object
        name: Name to enter in the modal (default: "Test User")
    """
    try:
        # Check if name modal is visible (with short timeout)
        name_modal = page.locator("#nameModal")
        if name_modal.is_visible(timeout=2000):
            # Fill in the name
            page.locator("#userName").fill(name)
            # Click the start button
            page.locator("#nameForm button[type='submit']").click()
            # Wait for modal to be hidden
            expect(name_modal).to_be_hidden(timeout=5000)
    except:
        # Modal not present, continue
        pass



class TestModeSelection:
    """Tests for mode selection page"""
    
    def test_mode_selection_page_loads(self, page: Page):
        """Test mode selection page displays correctly"""
        # Navigate via topics -> subtopics first for better stability
        page.goto("http://localhost:5000/topics")
        page.wait_for_load_state("networkidle")
        
        # Click first topic
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        
        # Click first subtopic
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        
        # Check both mode cards are visible
        expect(page.locator("text=Elimination Mode")).to_be_visible()
        expect(page.locator("text=Finals Mode")).to_be_visible()
    
    def test_elimination_mode_navigation(self, page: Page):
        """Test clicking elimination mode starts quiz"""
        # Navigate through proper flow
        page.goto("http://localhost:5000/topics")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        
        # Click elimination mode
        page.click("text=Start Elimination")
        
        # Fill name modal if present
        fill_name_modal_if_present(page)
        
        # Should navigate to quiz - verify by checking the mode badge is visible
        expect(page.locator("text=⚡ Elimination Mode")).to_be_visible()
    
    def test_finals_easy_navigation(self, page: Page):
        """Test clicking finals easy difficulty starts quiz"""
        # Navigate through proper flow
        page.goto("http://localhost:5000/topics")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        
        # Click easy difficulty
        page.locator("text=⭐ Easy").click()
        
        # Should navigate to quiz - verify by checking badges are visible
        expect(page.locator("text=🏆 Finals Mode")).to_be_visible()
        expect(page.locator("text=⭐ Easy")).to_be_visible()
    
    def test_finals_average_navigation(self, page: Page):
        """Test clicking finals average difficulty starts quiz"""
        # Navigate through proper flow
        page.goto("http://localhost:5000/topics")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        
        # Click average difficulty
        page.locator("text=⭐⭐ Average").click()
        
        # Should navigate to quiz - verify by checking badge is visible
        expect(page.locator("text=⭐⭐ Average")).to_be_visible()
    
    def test_finals_difficult_navigation(self, page: Page):
        """Test clicking finals difficult difficulty starts quiz"""
        # Navigate through proper flow
        page.goto("http://localhost:5000/topics")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        
        # Click difficult difficulty
        page.locator("text=⭐⭐⭐ Difficult").click()
        
        # Should navigate to quiz - verify by checking badge is visible
        expect(page.locator("text=⭐⭐⭐ Difficult")).to_be_visible()
    
    def test_back_to_subtopics_button(self, page: Page):
        """Test back to subtopics navigation"""
        # Navigate through proper flow to get to mode selection
        page.goto("http://localhost:5000/topics")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        
        # Click back button
        page.click("text=Back to Subtopics")
        
        # Should be on subtopics page
        page.wait_for_url("**/subtopics")
        expect(page.locator("text=Back to Topics")).to_be_visible()
