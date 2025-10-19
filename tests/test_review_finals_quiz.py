"""
Tests for the IT Quizbee Review Mode - Finals Quiz (Identification/Type-in)

This module contains tests that verify the Review Mode finals quiz works correctly,
including loading text input fields, typing answers, and submitting for all
three difficulty levels. This tests the topic → subtopic → finals mode flow.
"""

import pytest
from playwright.sync_api import Page, expect


class TestReviewFinalsQuiz:
    """Tests for Review Mode finals quiz (identification/type-in)"""
    
    def test_finals_quiz_loads(self, page: Page):
        """Test finals quiz page loads with text inputs"""
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=finals&difficulty=easy")
        
        # Check mode badge
        expect(page.locator("text=🏆 Finals Mode")).to_be_visible()
        expect(page.locator("text=⭐ Easy")).to_be_visible()
        
        # Check text inputs exist
        text_inputs = page.locator("input[type='text']")
        expect(text_inputs.first).to_be_visible()
    
    def test_can_type_answers(self, page: Page):
        """Test that user can type answers in text fields"""
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=finals&difficulty=easy")
        
        # Type in first answer field
        first_input = page.locator("input[name='answer_0']")
        first_input.fill("Test Answer")
        
        # Check value was set
        expect(first_input).to_have_value("Test Answer")
    
    def test_submit_finals_quiz(self, page: Page):
        """Test submitting a finals quiz"""
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=finals&difficulty=easy")
        
        # Answer all questions
        for i in range(10):
            input_field = page.locator(f"input[name='answer_{i}']")
            input_field.fill(f"Answer {i + 1}")
        
        # Submit quiz
        page.click("text=Submit Quiz")
        
        # Should navigate to results
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
    
    def test_finals_different_difficulties(self, page: Page):
        """Test all three difficulty levels load correctly"""
        difficulties = [
            ("easy", "⭐ Easy"),
            ("average", "⭐⭐ Average"),
            ("difficult", "⭐⭐⭐ Difficult")
        ]
        
        for difficulty, badge_text in difficulties:
            page.goto(f"http://localhost:5000/quiz/computer_architecture/authentication?mode=finals&difficulty={difficulty}")
            
            # Check difficulty badge
            expect(page.locator(f"text={badge_text}")).to_be_visible()
            
            # Check text inputs exist
            expect(page.locator("input[type='text']").first).to_be_visible()
