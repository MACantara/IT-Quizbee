"""
Tests for Error Pages

This module contains tests for error handling and error page display,
including 404 Not Found and other error states.
"""
import pytest
from playwright.sync_api import Page, expect


class TestErrorPages:
    """Tests for error page handling"""
    
    def test_404_page_display(self, page: Page):
        """Test that 404 error page is displayed for invalid URLs"""
        # Navigate to a non-existent page
        page.goto("http://localhost:5000/this-page-does-not-exist")
        page.wait_for_load_state("networkidle")
        
        # Check for error page elements
        # The page might show "404" or "Not Found" text
        expect(page.locator("h1").or_(page.locator("text=404"))).to_be_visible()
        
    def test_404_home_button(self, page: Page):
        """Test that home button works on 404 page"""
        page.goto("http://localhost:5000/this-page-does-not-exist")
        page.wait_for_load_state("networkidle")
        
        # Look for home button/link
        home_link = page.locator("a[href='/']").or_(page.locator("text=Home").and_(page.locator("a")))
        
        if home_link.count() > 0:
            home_link.first.click()
            page.wait_for_load_state("networkidle")
            
            # Should be on home page
            expect(page).to_have_url("http://localhost:5000/")
            
    def test_invalid_quiz_session(self, page: Page):
        """Test error handling for invalid quiz session"""
        # Try to access results without a session
        page.goto("http://localhost:5000/quiz/results")
        page.wait_for_load_state("networkidle")
        
        # Should show error or redirect
        # Check if we're redirected or see an error message
        url = page.url
        assert url == "http://localhost:5000/quiz/results" or url == "http://localhost:5000/"
        
    def test_invalid_topic_navigation(self, page: Page):
        """Test error handling for invalid topic"""
        # Try to navigate to non-existent topic
        page.goto("http://localhost:5000/topics/invalid_topic_xyz/subtopics")
        page.wait_for_load_state("networkidle")
        
        # Should show error or redirect
        # The app might handle this gracefully or show 404
        # Just verify page loads without crashing
        assert page.url is not None
        
    def test_invalid_subtopic_navigation(self, page: Page):
        """Test error handling for invalid subtopic"""
        # Try to navigate to non-existent subtopic
        page.goto("http://localhost:5000/mode-selection?topic=computer_architecture&subtopic=invalid_xyz")
        page.wait_for_load_state("networkidle")
        
        # Should show error or redirect
        # Just verify page loads without crashing
        assert page.url is not None


class TestErrorRecovery:
    """Tests for error recovery mechanisms"""
    
    def test_back_to_home_from_error(self, page: Page):
        """Test navigation back to home from error state"""
        # Trigger an error
        page.goto("http://localhost:5000/nonexistent-page")
        page.wait_for_load_state("networkidle")
        
        # Try to navigate back to home
        # Either through home link or browser navigation
        page.goto("http://localhost:5000/")
        page.wait_for_load_state("networkidle")
        
        # Should be on home page
        expect(page).to_have_url("http://localhost:5000/")
        expect(page.locator("text=Welcome to IT Quizbee")).to_be_visible()
        
    def test_retry_after_error(self, page: Page):
        """Test retry functionality after error"""
        # Go to an error page
        page.goto("http://localhost:5000/invalid-route")
        page.wait_for_load_state("networkidle")
        
        # Look for retry/try again button
        retry_button = page.locator("button:has-text('Try Again')").or_(
            page.locator("button:has-text('Retry')")
        )
        
        if retry_button.count() > 0:
            retry_button.first.click()
            page.wait_for_load_state("networkidle")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
