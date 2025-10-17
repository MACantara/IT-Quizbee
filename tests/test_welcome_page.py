"""
Tests for the IT Quizbee Welcome/Home Page

This module contains tests that verify the welcome page loads correctly
and displays all expected elements including the start button and feature cards.
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
        
        # Check start button
        start_button = page.locator("text=Start Quiz")
        expect(start_button).to_be_visible()
    
    def test_welcome_page_features(self, page: Page):
        """Test that all feature cards are displayed"""
        page.goto("http://localhost:5000")
        
        # Check for feature cards
        expect(page.locator("text=10 Topics")).to_be_visible()
        expect(page.locator("text=Self-Paced")).to_be_visible()
        expect(page.locator("text=Two Game Modes")).to_be_visible()
        expect(page.locator("text=Explanations")).to_be_visible()
