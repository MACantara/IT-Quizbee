"""
Playwright Automated Tests for IT Quizbee Web Application

This module contains end-to-end tests for the quiz application using Playwright.
Tests cover navigation, quiz taking, answer submission, and results display
for both Elimination and Finals modes.

Author: IT Quizbee Team
Date: 2025
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


class TestTopicsPage:
    """Tests for the topics selection page"""
    
    def test_navigate_to_topics(self, page: Page):
        """Test navigation from welcome to topics page"""
        page.goto("http://localhost:5000")
        
        # Click Start Quiz button
        page.click("text=Start Quiz")
        
        # Wait for navigation
        page.wait_for_url("**/topics")
        
        # Check topics page loaded
        expect(page.locator("text=Choose Your Topic")).to_be_visible()
    
    def test_topics_displayed(self, page: Page):
        """Test that all 10 topics are displayed"""
        page.goto("http://localhost:5000/topics")
        
        # Check for topic cards (should be 10)
        topic_cards = page.locator("a[href*='/topics/']")
        expect(topic_cards).to_have_count(10)
    
    def test_topic_navigation(self, page: Page):
        """Test clicking on a topic navigates to subtopics"""
        page.goto("http://localhost:5000/topics")
        
        # Click first topic
        first_topic = page.locator("a[href*='/topics/']").first
        first_topic.click()
        
        # Check subtopics page loaded
        expect(page.locator("text=Back to Topics")).to_be_visible()
    
    def test_home_button_from_topics(self, page: Page):
        """Test home button returns to welcome page"""
        page.goto("http://localhost:5000/topics")
        
        # Click home button
        page.click("text=Home")
        
        # Should be back on welcome page
        expect(page.locator("text=Welcome to IT Quizbee!")).to_be_visible()


class TestSubtopicsPage:
    """Tests for the subtopics selection page"""
    
    def test_subtopics_displayed(self, page: Page):
        """Test that subtopics are displayed for a topic"""
        # Navigate to a known topic (computer_architecture)
        page.goto("http://localhost:5000/topics/computer_architecture/subtopics")
        
        # Check subtopic cards exist
        subtopic_cards = page.locator("a[href*='/mode']")
        expect(subtopic_cards.first).to_be_visible()
    
    def test_back_to_topics_button(self, page: Page):
        """Test back to topics navigation"""
        page.goto("http://localhost:5000/topics/computer_architecture/subtopics")
        
        # Click back button
        page.click("text=Back to Topics")
        
        # Should be on topics page
        page.wait_for_url("**/topics")
        expect(page.locator("text=Choose Your Topic")).to_be_visible()
    
    def test_subtopic_click_navigates_to_mode_selection(self, page: Page):
        """Test clicking subtopic goes to mode selection"""
        page.goto("http://localhost:5000/topics/computer_architecture/subtopics")
        
        # Click first subtopic
        first_subtopic = page.locator("a[href*='/mode']").first
        first_subtopic.click()
        
        # Should be on mode selection page
        expect(page.locator("text=Choose your game mode")).to_be_visible()


class TestModeSelection:
    """Tests for mode selection page"""
    
    def test_mode_selection_page_loads(self, page: Page):
        """Test mode selection page displays correctly"""
        page.goto("http://localhost:5000/topics/computer_architecture/subtopics/authentication/mode")
        
        # Check both mode cards are visible
        expect(page.locator("text=Elimination Mode")).to_be_visible()
        expect(page.locator("text=Finals Mode")).to_be_visible()
    
    def test_elimination_mode_navigation(self, page: Page):
        """Test clicking elimination mode starts quiz"""
        page.goto("http://localhost:5000/topics/computer_architecture/subtopics/authentication/mode")
        
        # Click elimination mode
        page.click("text=Start Elimination")
        
        # Should navigate to quiz
        page.wait_for_url("**/quiz/**mode=elimination")
        expect(page.locator("text=⚡ Elimination Mode")).to_be_visible()
    
    def test_finals_easy_navigation(self, page: Page):
        """Test clicking finals easy difficulty starts quiz"""
        page.goto("http://localhost:5000/topics/computer_architecture/subtopics/authentication/mode")
        
        # Click easy difficulty
        page.locator("text=⭐ Easy").click()
        
        # Should navigate to quiz with difficulty
        page.wait_for_url("**/quiz/**mode=finals**difficulty=easy**")
        expect(page.locator("text=🏆 Finals Mode")).to_be_visible()
        expect(page.locator("text=⭐ Easy")).to_be_visible()
    
    def test_finals_average_navigation(self, page: Page):
        """Test clicking finals average difficulty starts quiz"""
        page.goto("http://localhost:5000/topics/computer_architecture/subtopics/authentication/mode")
        
        # Click average difficulty
        page.locator("text=⭐⭐ Average").click()
        
        # Should navigate to quiz
        page.wait_for_url("**/quiz/**mode=finals**difficulty=average**")
        expect(page.locator("text=⭐⭐ Average")).to_be_visible()
    
    def test_finals_difficult_navigation(self, page: Page):
        """Test clicking finals difficult difficulty starts quiz"""
        page.goto("http://localhost:5000/topics/computer_architecture/subtopics/authentication/mode")
        
        # Click difficult difficulty
        page.locator("text=⭐⭐⭐ Difficult").click()
        
        # Should navigate to quiz
        page.wait_for_url("**/quiz/**mode=finals**difficulty=difficult**")
        expect(page.locator("text=⭐⭐⭐ Difficult")).to_be_visible()
    
    def test_back_to_subtopics_button(self, page: Page):
        """Test back to subtopics navigation"""
        page.goto("http://localhost:5000/topics/computer_architecture/subtopics/authentication/mode")
        
        # Click back button
        page.click("text=Back to Subtopics")
        
        # Should be on subtopics page
        page.wait_for_url("**/subtopics")
        expect(page.locator("text=Back to Topics")).to_be_visible()


class TestEliminationQuiz:
    """Tests for elimination mode quiz (multiple choice)"""
    
    def test_elimination_quiz_loads(self, page: Page):
        """Test elimination quiz page loads with questions"""
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=elimination")
        
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
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=elimination")
        
        # Select first option of first question
        first_radio = page.locator("input[type='radio']").first
        first_radio.click()
        
        # Check it's selected
        expect(first_radio).to_be_checked()
    
    def test_only_one_option_per_question(self, page: Page):
        """Test that only one option can be selected per question"""
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=elimination")
        
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
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=elimination")
        
        # Answer all questions (select first option for each)
        for i in range(10):
            radio = page.locator(f"input[name='answer_{i}']").first
            radio.click()
        
        # Submit quiz
        page.click("text=Submit Quiz")
        
        # Should navigate to results
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
    
    def test_back_button_from_quiz(self, page: Page):
        """Test back button returns to mode selection"""
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=elimination")
        
        # Click back button
        page.click("text=Back")
        
        # Should be on mode selection page
        expect(page.locator("text=Choose your game mode")).to_be_visible()


class TestFinalsQuiz:
    """Tests for finals mode quiz (identification/type-in)"""
    
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
        
        # Check results elements
        expect(page.locator("text=Quiz Complete!")).to_be_visible()
        expect(page.locator("text=Correct")).to_be_visible()
        expect(page.locator("text=Incorrect")).to_be_visible()
        expect(page.locator("text=Total")).to_be_visible()
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
    
    def test_navigation_breadcrumb(self, page: Page):
        """Test navigation using back buttons at each level"""
        # Start deep in the app
        page.goto("http://localhost:5000/quiz/computer_architecture/authentication?mode=elimination")
        
        # Go back to mode selection
        page.click("text=Back")
        expect(page.locator("text=Choose your game mode")).to_be_visible()
        
        # Go back to subtopics
        page.click("text=Back to Subtopics")
        expect(page.locator("text=Back to Topics")).to_be_visible()
        
        # Go back to topics
        page.click("text=Back to Topics")
        expect(page.locator("text=Choose Your Topic")).to_be_visible()
        
        # Go home
        page.click("text=Home")
        expect(page.locator("text=Welcome to IT Quizbee!")).to_be_visible()

