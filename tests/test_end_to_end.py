"""
End-to-End Integration Tests for IT Quizbee

This module contains complete user journey tests that verify the entire
flow from welcome page to quiz completion for both game modes.
"""

import pytest
from playwright.sync_api import Page, expect


class TestEndToEndFlow:
    """End-to-end integration tests"""
    
    def test_complete_elimination_flow(self, page: Page):
        """Test complete flow: welcome -> topics -> subtopics -> mode -> elimination quiz -> results"""
        # Start at welcome
        page.goto("http://localhost:5000")
        expect(page.locator("text=Welcome to IT Quizbee!")).to_be_visible()
        
        # Go to topics
        page.click("text=Start Quiz")
        expect(page.locator("text=Choose Your Topic")).to_be_visible()
        
        # Select a topic
        page.locator("a[href*='/topics/']").first.click()
        expect(page.locator("text=Back to Topics")).to_be_visible()
        
        # Select a subtopic
        page.locator("a[href*='/mode']").first.click()
        expect(page.locator("text=Choose your game mode")).to_be_visible()
        
        # Select elimination mode
        page.click("text=Start Elimination")
        expect(page.locator("text=⚡ Elimination Mode")).to_be_visible()
        
        # Answer all questions
        for i in range(10):
            page.locator(f"input[name='answer_{i}']").first.click()
        
        # Submit
        page.click("text=Submit Quiz")
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
    
    def test_complete_finals_flow(self, page: Page):
        """Test complete flow: welcome -> topics -> subtopics -> mode -> finals quiz -> results"""
        # Start at welcome
        page.goto("http://localhost:5000")
        
        # Navigate to topics
        page.click("text=Start Quiz")
        
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
