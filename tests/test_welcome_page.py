"""
Tests for the IT Quizbee Welcome/Home Page

This module contains tests that verify the welcome page loads correctly
and displays all expected elements including the three game mode buttons.
"""

import pytest
from playwright.sync_api import Page, expect


class TestWelcomePage:
    """Tests for the welcome/home page"""
    
    def test_welcome_page_loads(self, page: Page):
        """Test that the welcome page loads successfully"""
        page.goto("http://localhost:5000")
        
        # Check page title
        expect(page).to_have_title("IT Quizbee - Welcome")
        
        # Check main heading
        heading = page.locator("h2:has-text('Welcome to IT Quizbee!')")
        expect(heading).to_be_visible()
    
    def test_welcome_page_features(self, page: Page):
        """Test that all feature cards are displayed"""
        page.goto("http://localhost:5000")
        
        # Check for feature cards - use more specific selectors
        expect(page.locator("h3:has-text('10 Topics')").first).to_be_visible()
        expect(page.locator("h3:has-text('Multiple Modes')")).to_be_visible()
        expect(page.locator("h3:has-text('Three Game Modes')")).to_be_visible()
        expect(page.locator("h3:has-text('Explanations')")).to_be_visible()
    
    def test_three_mode_cards_displayed(self, page: Page):
        """Test that all three game mode cards are displayed"""
        page.goto("http://localhost:5000")
        
        # Check Elimination Mode card - use heading selector for specificity
        expect(page.locator("h3:has-text('Elimination')")).to_be_visible()
        expect(page.locator("text=100 random questions")).to_be_visible()
        expect(page.locator("text=Start Elimination")).to_be_visible()
        
        # Check Finals Mode card
        expect(page.locator("h3:has-text('Finals')")).to_be_visible()
        expect(page.locator("text=30 identification questions")).to_be_visible()
        expect(page.locator("text=Start Finals")).to_be_visible()
        
        # Check Review Mode card
        expect(page.locator("h3:has-text('Review')")).to_be_visible()
        expect(page.locator("text=Choose any topic")).to_be_visible()
        expect(page.locator("text=Start Review")).to_be_visible()
    
    def test_elimination_mode_navigation(self, page: Page):
        """Test clicking elimination mode button navigates correctly"""
        page.goto("http://localhost:5000")
        
        # Click Start Elimination button
        page.click("text=Start Elimination")
        
        # Should navigate to elimination mode page
        page.wait_for_url("**/elimination")
        expect(page.locator("text=⚡ Elimination Mode")).to_be_visible()
    
    def test_finals_mode_navigation(self, page: Page):
        """Test clicking finals mode button navigates correctly"""
        page.goto("http://localhost:5000")
        
        # Click Start Finals button
        page.click("text=Start Finals")
        
        # Should navigate to finals mode page
        page.wait_for_url("**/finals")
        expect(page.locator("text=🏆 Finals Mode")).to_be_visible()
    
    def test_review_mode_navigation(self, page: Page):
        """Test clicking review mode button navigates to topics"""
        page.goto("http://localhost:5000")
        
        # Click Start Review button
        page.click("text=Start Review")
        
        # Should navigate to topics page
        page.wait_for_url("**/topics")
        expect(page.locator("text=Choose Your Topic")).to_be_visible()
