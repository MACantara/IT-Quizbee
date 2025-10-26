"""
Tests for the IT Quizbee Review Mode - Elimination Quiz (Multiple Choice)

This module contains tests that verify the Review Mode elimination quiz works correctly,
including loading questions, selecting radio button answers, and submitting.
This tests the topic → subtopic → elimination mode flow.
"""

import pytest
from playwright.sync_api import Page, expect


class TestReviewEliminationQuiz:
    """Tests for Review Mode elimination quiz (multiple choice)"""
    
    def test_elimination_quiz_loads(self, page: Page):
        """Test elimination quiz page loads with questions"""
        # Navigate through the proper flow
        page.goto("http://localhost:5000/topics")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.click("text=Start Elimination")
        page.wait_for_load_state("networkidle")
        
        # Check mode badge
        expect(page.locator("text=⚡ Elimination Mode")).to_be_visible()
        
        # Check questions are displayed
        questions = page.locator("h3:has-text('.')")
        expect(questions.first).to_be_visible()
        
        # Check radio buttons exist
        radio_buttons = page.locator("input[type='radio']")
        expect(radio_buttons.first).to_be_visible()
    
    def test_can_select_multiple_choice_answers(self, page: Page):
        """Test that user can select radio button answers"""
        # Navigate through the proper flow
        page.goto("http://localhost:5000/topics")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.click("text=Start Elimination")
        page.wait_for_load_state("networkidle")
        
        # Select first option of first question
        first_radio = page.locator("input[type='radio']").first
        first_radio.click()
        
        # Check it's selected
        expect(first_radio).to_be_checked()
    
    def test_only_one_option_per_question(self, page: Page):
        """Test that only one option can be selected per question"""
        # Navigate through the proper flow
        page.goto("http://localhost:5000/topics")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.click("text=Start Elimination")
        page.wait_for_load_state("networkidle")
        
        # Get all radio buttons for first question
        first_question_radios = page.locator("input[name='answer_0']")
        
        # Select first option
        first_question_radios.nth(0).click()
        expect(first_question_radios.nth(0)).to_be_checked()
        
        # Select second option
        first_question_radios.nth(1).click()
        expect(first_question_radios.nth(1)).to_be_checked()
        
        # First should now be unchecked
        expect(first_question_radios.nth(0)).not_to_be_checked()
    
    def test_submit_elimination_quiz(self, page: Page):
        """Test submitting an elimination quiz"""
        # Navigate through the proper flow
        page.goto("http://localhost:5000/topics")
        page.locator("a[href*='/topics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.locator("a[href*='/subtopics/']").first.click()
        page.wait_for_load_state("networkidle")
        page.click("text=Start Elimination")
        page.wait_for_load_state("networkidle")
        
        # Answer all questions (select first option for each)
        for i in range(10):
            radio = page.locator(f"input[name='answer_{i}']").first
            radio.click()
        
        # Submit quiz
        page.click("text=Submit Quiz")
        
        # Should navigate to results
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
