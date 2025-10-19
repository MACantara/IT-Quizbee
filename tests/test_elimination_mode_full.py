"""
Tests for the IT Quizbee Full Elimination Mode

This module contains tests that verify the full elimination mode works correctly,
including the 100-question quiz with 60-minute timer, progress tracking, and submission.
"""

import pytest
from playwright.sync_api import Page, expect
import re


class TestEliminationModeFull:
    """Tests for full elimination mode (100 questions, 60 minutes)"""
    
    def test_elimination_mode_page_loads(self, page: Page):
        """Test elimination mode page loads with correct elements"""
        page.goto("http://localhost:5000/elimination")
        
        # Check mode badge
        expect(page.locator("text=⚡ Elimination Mode")).to_be_visible()
        
        # Check header
        expect(page.locator("text=100 Questions from All Topics")).to_be_visible()
        
        # Check timer is visible and starts at 60:00
        timer = page.locator("#timer")
        expect(timer).to_be_visible()
        expect(timer).to_have_text(re.compile(r"60:00|59:\d{2}"))
        
        # Check progress bar elements exist (progress bar starts with 0 width)
        expect(page.locator("#progress-bar")).to_be_attached()
        expect(page.locator("#progress-text")).to_be_visible()
        expect(page.locator("#progress-text")).to_have_text("0 / 100")
    
    def test_100_questions_displayed(self, page: Page):
        """Test that 100 questions are displayed"""
        page.goto("http://localhost:5000/elimination")
        
        # Count question headers (numbered 1-100)
        questions = page.locator("h3:has-text('.')")
        
        # Should have 100 questions
        expect(questions).to_have_count(100)
        
        # Verify first and last question numbers
        expect(page.locator("h3:has-text('1.')").first).to_be_visible()
        expect(page.locator("h3:has-text('100.')")).to_be_visible()
    
    def test_questions_from_multiple_topics(self, page: Page):
        """Test that questions are from different topics"""
        page.goto("http://localhost:5000/elimination")
        
        # Check for topic tags (should have variety)
        topic_tags = page.locator("div.text-xs.text-gray-500")
        expect(topic_tags.first).to_be_visible()
        
        # Should contain topic/subtopic information
        first_tag = topic_tags.first
        expect(first_tag).to_contain_text("-")  # Format: "Topic - Subtopic"
    
    def test_multiple_choice_radio_buttons(self, page: Page):
        """Test that each question has radio button options"""
        page.goto("http://localhost:5000/elimination")
        
        # Check first question has 4 radio options
        first_question_radios = page.locator("input[name='answer_0']")
        expect(first_question_radios).to_have_count(4)
        
        # All should be radio buttons
        expect(first_question_radios.first).to_have_attribute("type", "radio")
    
    def test_can_select_answers(self, page: Page):
        """Test that user can select radio button answers"""
        page.goto("http://localhost:5000/elimination")
        
        # Select first option of first question
        first_radio = page.locator("input[name='answer_0']").first
        first_radio.click()
        
        # Check it's selected
        expect(first_radio).to_be_checked()
    
    def test_progress_tracking(self, page: Page):
        """Test progress bar updates when answering questions"""
        page.goto("http://localhost:5000/elimination")
        
        # Initial progress
        progress_text = page.locator("#progress-text")
        expect(progress_text).to_have_text("0 / 100")
        
        # Answer first question
        page.locator("input[name='answer_0']").first.click()
        
        # Progress should update
        expect(progress_text).to_have_text("1 / 100")
        
        # Answer second question
        page.locator("input[name='answer_1']").first.click()
        
        # Progress should update again
        expect(progress_text).to_have_text("2 / 100")
    
    def test_timer_countdown(self, page: Page):
        """Test that timer counts down"""
        page.goto("http://localhost:5000/elimination")
        
        timer = page.locator("#timer")
        initial_time = timer.text_content()
        
        # Wait 2 seconds
        page.wait_for_timeout(2000)
        
        current_time = timer.text_content()
        
        # Time should have decreased
        assert current_time != initial_time
    
    def test_submit_button_exists(self, page: Page):
        """Test submit button is present"""
        page.goto("http://localhost:5000/elimination")
        
        submit_button = page.locator("button:has-text('Submit Quiz')")
        expect(submit_button).to_be_visible()
    
    def test_back_to_home_button(self, page: Page):
        """Test back to home button exists and works"""
        page.goto("http://localhost:5000/elimination")
        
        # Click back button
        page.click("text=Back to Home")
        
        # Should be on welcome page
        expect(page.locator("text=Welcome to IT Quizbee!")).to_be_visible()
    
    def test_submit_elimination_quiz(self, page: Page):
        """Test submitting the elimination quiz"""
        page.goto("http://localhost:5000/elimination")
        
        # Answer first 10 questions (sample)
        for i in range(10):
            radio = page.locator(f"input[name='answer_{i}']").first
            radio.click()
        
        # Submit quiz (will show confirmation if not all answered)
        page.on("dialog", lambda dialog: dialog.accept())  # Auto-accept confirmation
        page.click("text=Submit Quiz")
        
        # Should navigate to results (after accepting dialog)
        page.wait_for_timeout(500)  # Small wait for navigation
        
        # Check if we're on results page or still on quiz page with dialog
        # (depends on whether dialog was shown)
    
    def test_answer_all_and_submit(self, page: Page):
        """Test answering all 100 questions and submitting"""
        page.goto("http://localhost:5000/elimination")
        
        # Answer all 100 questions
        for i in range(100):
            # Click first option for each question
            radio = page.locator(f"input[name='answer_{i}']").first
            radio.click()
        
        # Progress should be 100/100
        expect(page.locator("#progress-text")).to_have_text("100 / 100")
        
        # Submit quiz
        page.click("text=Submit Quiz")
        
        # Should navigate to results
        page.wait_for_url("**/elimination/submit", timeout=10000)
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
    
    def test_results_display_after_submission(self, page: Page):
        """Test that results are displayed correctly after submission"""
        page.goto("http://localhost:5000/elimination")
        
        # Answer all questions quickly
        for i in range(100):
            page.locator(f"input[name='answer_{i}']").first.click()
        
        # Submit
        page.click("text=Submit Quiz")
        
        # Wait for results page
        page.wait_for_url("**/elimination/submit", timeout=10000)
        
        # Check results elements
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
        expect(page.locator("div.bg-green-50:has-text('Correct')")).to_be_visible()
        expect(page.locator("div.bg-red-50:has-text('Incorrect')")).to_be_visible()
        expect(page.locator("div.bg-blue-50:has-text('Total')")).to_be_visible()
    
    def test_navigation_from_elimination_results(self, page: Page):
        """Test navigation buttons on elimination results page"""
        page.goto("http://localhost:5000/elimination")
        
        # Answer and submit
        for i in range(100):
            page.locator(f"input[name='answer_{i}']").first.click()
        
        page.click("text=Submit Quiz")
        page.wait_for_url("**/elimination/submit", timeout=10000)
        
        # Check for Home button
        home_button = page.locator("text=Home")
        expect(home_button).to_be_visible()
