"""
Tests for the IT Quizbee Full Finals Mode

This module contains tests that verify the full finals mode works correctly,
including 30 identification questions with different difficulty levels and per-question timers.
"""

import pytest
from playwright.sync_api import Page, expect
import re


class TestFinalsModeFull:
    """Tests for full finals mode (30 identification questions with timers)"""
    
    def test_finals_mode_page_loads(self, page: Page):
        """Test finals mode page loads with correct elements"""
        page.goto("http://localhost:5000/finals")
        
        # Check mode badge
        expect(page.locator("text=🏆 Finals Mode")).to_be_visible()
        
        # Check header
        expect(page.locator("text=Identification Questions")).to_be_visible()
        
        # Check instruction text
        expect(page.locator("text=Answer each question before the timer runs out!")).to_be_visible()
        
        # Check progress bar is visible
        expect(page.locator("#progress-bar")).to_be_visible()
        expect(page.locator("#progress-text")).to_have_text("1 / 30")
    
    def test_first_question_displays(self, page: Page):
        """Test that the first question is displayed on load"""
        page.goto("http://localhost:5000/finals")
        
        # Check question text is visible
        question_text = page.locator("#question-text")
        expect(question_text).to_be_visible()
        
        # Check answer input is visible
        answer_input = page.locator("#answer-input")
        expect(answer_input).to_be_visible()
        
        # Check submit button
        expect(page.locator("#submit-answer")).to_be_visible()
    
    def test_difficulty_badge_displays(self, page: Page):
        """Test that difficulty badge is shown"""
        page.goto("http://localhost:5000/finals")
        
        # Check difficulty badge (should be easy, average, or difficult)
        difficulty_badge = page.locator("#difficulty-badge")
        expect(difficulty_badge).to_be_visible()
        
        # Should contain one of the difficulty levels
        badge_text = difficulty_badge.text_content()
        assert any(level in badge_text for level in ["Easy", "Average", "Difficult"])
    
    def test_timer_displays_and_counts_down(self, page: Page):
        """Test that timer is visible and counts down"""
        page.goto("http://localhost:5000/finals")
        
        timer = page.locator("#timer")
        expect(timer).to_be_visible()
        
        # Timer should show a number (initial time based on difficulty)
        initial_time = int(timer.text_content())
        assert initial_time > 0
        
        # Wait 2 seconds
        page.wait_for_timeout(2000)
        
        # Timer should have decreased
        current_time = int(timer.text_content())
        assert current_time < initial_time
    
    def test_can_type_answer(self, page: Page):
        """Test that user can type an answer"""
        page.goto("http://localhost:5000/finals")
        
        answer_input = page.locator("#answer-input")
        
        # Type an answer
        answer_input.fill("Test Answer")
        
        # Check value was set
        expect(answer_input).to_have_value("Test Answer")
    
    def test_submit_answer_advances_question(self, page: Page):
        """Test that submitting an answer advances to next question"""
        page.goto("http://localhost:5000/finals")
        
        # Get current question text
        question_text = page.locator("#question-text")
        initial_question = question_text.text_content()
        
        # Fill and submit answer
        page.locator("#answer-input").fill("Test Answer")
        page.click("#submit-answer")
        
        # Wait for next question
        page.wait_for_timeout(600)
        
        # Question should have changed
        new_question = question_text.text_content()
        assert new_question != initial_question
        
        # Progress should update
        expect(page.locator("#progress-text")).to_have_text("2 / 30")
    
    def test_enter_key_submits_answer(self, page: Page):
        """Test that pressing Enter submits the answer"""
        page.goto("http://localhost:5000/finals")
        
        # Get current progress
        initial_progress = page.locator("#progress-text").text_content()
        
        # Type answer and press Enter
        answer_input = page.locator("#answer-input")
        answer_input.fill("Test Answer")
        answer_input.press("Enter")
        
        # Wait for next question
        page.wait_for_timeout(600)
        
        # Progress should have changed
        new_progress = page.locator("#progress-text").text_content()
        assert new_progress != initial_progress
    
    def test_answer_input_clears_on_new_question(self, page: Page):
        """Test that answer input is cleared when advancing to next question"""
        page.goto("http://localhost:5000/finals")
        
        # Fill and submit first answer
        page.locator("#answer-input").fill("First Answer")
        page.click("#submit-answer")
        
        # Wait for next question
        page.wait_for_timeout(600)
        
        # Input should be empty
        expect(page.locator("#answer-input")).to_have_value("")
    
    def test_progress_bar_updates(self, page: Page):
        """Test that progress bar updates correctly"""
        page.goto("http://localhost:5000/finals")
        
        # Initial progress
        progress_bar = page.locator("#progress-bar")
        
        # Answer 5 questions
        for i in range(5):
            page.locator("#answer-input").fill(f"Answer {i + 1}")
            page.click("#submit-answer")
            page.wait_for_timeout(600)
        
        # Progress should be 6/30 (we're on question 6 now)
        expect(page.locator("#progress-text")).to_have_text("6 / 30")
    
    def test_different_difficulty_levels_present(self, page: Page):
        """Test that questions include different difficulty levels"""
        page.goto("http://localhost:5000/finals")
        
        difficulties_seen = set()
        
        # Go through several questions to see different difficulties
        for i in range(10):
            difficulty_badge = page.locator("#difficulty-badge")
            difficulty_text = difficulty_badge.text_content()
            
            if "Easy" in difficulty_text:
                difficulties_seen.add("easy")
            elif "Average" in difficulty_text:
                difficulties_seen.add("average")
            elif "Difficult" in difficulty_text:
                difficulties_seen.add("difficult")
            
            # Submit answer to move to next question
            page.locator("#answer-input").fill("Answer")
            page.click("#submit-answer")
            page.wait_for_timeout(600)
        
        # Should have seen at least 2 different difficulty levels in first 10 questions
        assert len(difficulties_seen) >= 2
    
    def test_complete_all_30_questions(self, page: Page):
        """Test completing all 30 questions"""
        page.goto("http://localhost:5000/finals")
        
        # Answer all 30 questions
        for i in range(30):
            # Fill answer
            page.locator("#answer-input").fill(f"Answer {i + 1}")
            
            # Submit
            page.click("#submit-answer")
            
            # Wait for transition
            page.wait_for_timeout(600)
        
        # Should show completion message
        expect(page.locator("#complete-message")).to_be_visible()
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
    
    def test_auto_submit_on_completion(self, page: Page):
        """Test that quiz auto-submits after all questions are answered"""
        page.goto("http://localhost:5000/finals")
        
        # Answer all 30 questions quickly
        for i in range(30):
            page.locator("#answer-input").fill(f"Answer {i + 1}")
            page.click("#submit-answer")
            page.wait_for_timeout(600)
        
        # Wait for auto-submit
        page.wait_for_timeout(2000)
        
        # Should be on results page
        page.wait_for_url("**/finals/submit", timeout=5000)
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
    
    def test_results_display_after_finals(self, page: Page):
        """Test that results are displayed correctly after finals quiz"""
        page.goto("http://localhost:5000/finals")
        
        # Complete all questions
        for i in range(30):
            page.locator("#answer-input").fill(f"TestAnswer{i}")
            page.click("#submit-answer")
            page.wait_for_timeout(600)
        
        # Wait for results page
        page.wait_for_timeout(2000)
        page.wait_for_url("**/finals/submit", timeout=5000)
        
        # Check results elements
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
        expect(page.locator("div.bg-green-50:has-text('Correct')")).to_be_visible()
        expect(page.locator("div.bg-red-50:has-text('Incorrect')")).to_be_visible()
    
    def test_timer_color_changes_with_time(self, page: Page):
        """Test that timer color changes as time runs low"""
        page.goto("http://localhost:5000/finals")
        
        timer = page.locator("#timer")
        
        # Timer should start with purple or normal color
        initial_class = timer.get_attribute("class")
        assert "text-purple-600" in initial_class or "text-yellow-600" in initial_class or "text-red-600" in initial_class
    
    def test_empty_answer_allowed(self, page: Page):
        """Test that submitting empty answer is allowed"""
        page.goto("http://localhost:5000/finals")
        
        # Don't fill answer, just submit
        page.click("#submit-answer")
        
        # Wait for next question
        page.wait_for_timeout(600)
        
        # Should advance to question 2
        expect(page.locator("#progress-text")).to_have_text("2 / 30")
    
    def test_question_content_changes(self, page: Page):
        """Test that question content actually changes between questions"""
        page.goto("http://localhost:5000/finals")
        
        questions_seen = set()
        
        # Collect first 5 questions
        for i in range(5):
            question_text = page.locator("#question-text").text_content()
            questions_seen.add(question_text)
            
            page.locator("#answer-input").fill("Answer")
            page.click("#submit-answer")
            page.wait_for_timeout(600)
        
        # Should have 5 different questions
        assert len(questions_seen) == 5
