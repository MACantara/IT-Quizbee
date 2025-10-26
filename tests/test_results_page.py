"""
Tests for the IT Quizbee Results Page

This module contains tests that verify quiz results are displayed correctly
for both elimination and finals modes, and that all navigation buttons work.
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



class TestResultsPage:
    """Tests for quiz results page"""
    
    def test_elimination_results_display(self, page: Page):
        """Test results page displays after elimination quiz"""
        # Navigate through the review mode flow
        page.goto("http://localhost:5000/topics")
        
        # Click first topic
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        
        # Click first subtopic to get to mode selection
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        
        # Click elimination mode
        page.click("text=Start Elimination")
        
        # Fill name modal if present
        fill_name_modal_if_present(page)
        page.wait_for_load_state("networkidle")
        
        # Answer all questions
        for i in range(10):
            page.locator(f"input[name='answer_{i}']").first.click()
        
        # Submit
        page.click("text=Submit Quiz")
        
        # Check results elements - use more specific locators
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
        expect(page.locator("div.bg-green-50:has-text('Correct')")).to_be_visible()
        expect(page.locator("div.bg-red-50:has-text('Incorrect')")).to_be_visible()
        expect(page.locator("div.bg-blue-50:has-text('Total')")).to_be_visible()
        expect(page.locator("text=Detailed Results")).to_be_visible()
    
    def test_finals_results_display(self, page: Page):
        """Test results page displays after finals quiz"""
        # Navigate through the review mode flow
        page.goto("http://localhost:5000/topics")
        
        # Click first topic
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        
        # Click first subtopic to get to mode selection
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        
        # Click finals easy difficulty
        page.locator("text=⭐ Easy").click()
        page.wait_for_load_state("networkidle")
        
        # Answer all questions
        for i in range(10):
            page.locator(f"input[name='answer_{i}']").fill("test answer")
        
        # Submit
        page.click("text=Submit Quiz")
        
        # Check results elements
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
        expect(page.locator("text=Detailed Results")).to_be_visible()
    
    def test_retake_quiz_button(self, page: Page):
        """Test retake quiz button returns to same quiz"""
        # Navigate through the review mode flow
        page.goto("http://localhost:5000/topics")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.click("text=Start Elimination")
        
        # Fill name modal if present
        fill_name_modal_if_present(page)
        page.wait_for_load_state("networkidle")
        
        # Complete and submit quiz
        for i in range(10):
            page.locator(f"input[name='answer_{i}']").first.click()
        page.click("text=Submit Quiz")
        
        # Click retake button
        page.click("text=Retake Quiz")
        
        # Should be back on quiz page
        expect(page.locator("text=⚡ Elimination Mode")).to_be_visible()
    
    def test_try_different_mode_button(self, page: Page):
        """Test try different mode returns to mode selection"""
        # Navigate through the review mode flow
        page.goto("http://localhost:5000/topics")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.click("text=Start Elimination")
        
        # Fill name modal if present
        fill_name_modal_if_present(page)
        page.wait_for_load_state("networkidle")
        
        # Complete and submit quiz
        for i in range(10):
            page.locator(f"input[name='answer_{i}']").first.click()
        page.click("text=Submit Quiz")
        
        # Click try different mode
        page.click("text=Try Different Mode")
        
        # Should be on mode selection
        expect(page.locator("text=Choose your game mode")).to_be_visible()
    
    def test_back_to_subtopics_from_results(self, page: Page):
        """Test back to subtopics from results"""
        # Navigate through the review mode flow
        page.goto("http://localhost:5000/topics")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.click("text=Start Elimination")
        
        # Fill name modal if present
        fill_name_modal_if_present(page)
        page.wait_for_load_state("networkidle")
        
        # Complete and submit quiz
        for i in range(10):
            page.locator(f"input[name='answer_{i}']").first.click()
        page.click("text=Submit Quiz")
        
        # Click back to subtopics
        page.click("text=Back to Subtopics")
        
        # Should be on subtopics page
        page.wait_for_url("**/subtopics")
    
    def test_home_from_results(self, page: Page):
        """Test home button from results"""
        # Navigate through the review mode flow
        page.goto("http://localhost:5000/topics")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.click("text=Start Elimination")
        
        # Fill name modal if present
        fill_name_modal_if_present(page)
        page.wait_for_load_state("networkidle")
        
        # Complete and submit quiz
        for i in range(10):
            page.locator(f"input[name='answer_{i}']").first.click()
        page.click("text=Submit Quiz")
        
        # Click home
        page.click("text=Home")
        
        # Should be on welcome page
        expect(page.locator("text=Welcome to IT Quizbee!")).to_be_visible()
