"""
End-to-End Integration Tests for IT Quizbee

This module contains complete user journey tests that verify the entire
flow for all three game modes: Elimination, Finals, and Review Mode.
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



class TestEndToEndFlow:
    """End-to-end integration tests for all modes"""
    
    def test_complete_elimination_full_flow(self, page: Page):
        """Test complete flow: welcome -> full elimination mode -> results"""
        # Start at welcome
        page.goto("http://localhost:5000")
        expect(page.locator("text=Welcome to IT Quizbee!")).to_be_visible()
        
        # Click Elimination Mode
        page.click("text=Start Elimination")
        
        # Fill name modal if present
        fill_name_modal_if_present(page)
        expect(page.locator("text=⚡ Elimination Mode")).to_be_visible()
        expect(page.locator("text=100 Questions from All Topics")).to_be_visible()
        
        # Answer all 100 questions
        for i in range(100):
            page.locator(f"input[name='answer_{i}']").first.click()
        
        # Submit
        page.click("text=Submit Quiz")
        
        # Check results
        page.wait_for_load_state("networkidle")
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
    
    def test_complete_finals_full_flow(self, page: Page):
        """Test complete flow: welcome -> full finals mode -> results"""
        # Start at welcome
        page.goto("http://localhost:5000")
        
        # Click Finals Mode
        page.click("text=Start Finals")
        
        # Fill name modal if present
        fill_name_modal_if_present(page)
        expect(page.locator("text=🏆 Finals Mode")).to_be_visible()
        
        # Answer all 30 questions
        for i in range(30):
            page.locator("#answer-input").fill(f"Answer {i + 1}")
            page.click("#submit-answer")
            page.wait_for_timeout(600)
        
        # Wait for auto-submit to results
        page.wait_for_timeout(2000)
        page.wait_for_url("**/quiz/finals/submit", timeout=5000)
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
    
    def test_complete_review_elimination_flow(self, page: Page):
        """Test complete flow: welcome -> topics -> subtopics -> mode -> elimination quiz -> results"""
        # Start at welcome
        page.goto("http://localhost:5000")
        expect(page.locator("text=Welcome to IT Quizbee!")).to_be_visible()
        
        # Go to Review Mode
        page.click("text=Start Review")
        expect(page.locator("text=Choose Your Topic")).to_be_visible()
        
        # Select a topic
        page.locator("a[href*='/topics/']").first.click()
        expect(page.locator("text=Back to Topics")).to_be_visible()
        
        # Select a subtopic
        page.locator("a[href*='/mode']").first.click()
        expect(page.locator("text=Choose your game mode")).to_be_visible()
        
        # Select elimination mode
        page.click("text=Start Elimination")
        
        # Fill name modal if present
        fill_name_modal_if_present(page)
        expect(page.locator("text=⚡ Elimination Mode")).to_be_visible()
        
        # Answer all questions
        for i in range(10):
            page.locator(f"input[name='answer_{i}']").first.click()
        
        # Submit
        page.click("text=Submit Quiz")
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
    
    def test_complete_review_finals_flow(self, page: Page):
        """Test complete flow: welcome -> topics -> subtopics -> mode -> finals quiz -> results"""
        # Start at welcome
        page.goto("http://localhost:5000")
        
        # Navigate to Review Mode
        page.click("text=Start Review")
        
        # Select first topic
        page.locator("a[href*='/topics/']").first.click()
        
        # Select first subtopic
        page.locator("a[href*='/mode']").first.click()
        
        # Select finals easy
        page.locator("text=⭐ Easy").click()
        expect(page.locator("text=🏆 Finals Mode")).to_be_visible()
        
        # Answer all questions
        for i in range(10):
            page.locator(f"input[name='answer_{i}']").fill(f"Answer {i}")
        
        # Submit
        page.click("text=Submit Quiz")
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
    
    def test_navigation_between_modes(self, page: Page):
        """Test that user can navigate between different modes from home"""
        page.goto("http://localhost:5000")
        
        # Test Elimination navigation
        page.click("text=Start Elimination")
        
        # Fill name modal if present
        fill_name_modal_if_present(page)
        expect(page.locator("text=⚡ Elimination Mode")).to_be_visible()
        
        # Go back home
        page.click("text=Back to Home")
        expect(page.locator("text=Welcome to IT Quizbee!")).to_be_visible()
        
        # Test Finals navigation
        page.click("text=Start Finals")
        
        # Fill name modal if present
        fill_name_modal_if_present(page)
        expect(page.locator("text=🏆 Finals Mode")).to_be_visible()
        
        # Note: Finals doesn't have a back button, so we navigate directly
        page.goto("http://localhost:5000")
        
        # Test Review navigation
        page.click("text=Start Review")
        expect(page.locator("text=Choose Your Topic")).to_be_visible()
        
        # Go back home
        page.click("text=Home")
        expect(page.locator("text=Welcome to IT Quizbee!")).to_be_visible()
