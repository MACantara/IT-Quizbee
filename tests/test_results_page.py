"""
Tests for the IT Quizbee Results Page

This module contains tests that verify quiz results are displayed correctly
for both elimination and finals modes, and that all navigation buttons work.
"""

import pytest
from playwright.sync_api import Page, expect


class TestResultsPage:
    """Tests for quiz results page"""
    
    def test_elimination_results_display(self, page: Page):
        """Test results page displays after elimination quiz"""
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=elimination")
        
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
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=finals&difficulty=easy")
        
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
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=elimination")
        
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
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=elimination")
        
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
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=elimination")
        
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
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=elimination")
        
        # Complete and submit quiz
        for i in range(10):
            page.locator(f"input[name='answer_{i}']").first.click()
        page.click("text=Submit Quiz")
        
        # Click home
        page.click("text=Home")
        
        # Should be on welcome page
        expect(page.locator("text=Welcome to IT Quizbee!")).to_be_visible()
