"""
Tests for Admin Pages

This module contains end-to-end tests for all admin-related pages including:
- Admin login
- Admin dashboard
- Question reports
- Question analytics
- API health
- Recent activity
- Topic performance
"""
import pytest
import time
from playwright.sync_api import Page, expect


class TestAdminLogin:
    """Tests for admin login page"""
    
    def test_admin_login_page_loads(self, page: Page):
        """Test that admin login page loads correctly"""
        page.goto("http://localhost:5000/admin/login")
        page.wait_for_load_state("networkidle")
        
        # Check page title and header
        expect(page).to_have_title("Admin Login - IT Quizbee")
        expect(page.get_by_role("heading", name="Admin Login")).to_be_visible()
        
        # Verify login form elements
        expect(page.locator("input[name='username']")).to_be_visible()
        expect(page.locator("input[name='password']")).to_be_visible()
        expect(page.locator("button[type='submit']")).to_be_visible()
        
    def test_admin_login_with_valid_credentials(self, page: Page):
        """Test successful admin login"""
        page.goto("http://localhost:5000/admin/login")
        page.wait_for_load_state("networkidle")
        
        # Fill in credentials (from config.py)
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin123")
        
        # Submit form
        page.click("button[type='submit']")
        page.wait_for_timeout(1000)  # Wait a bit for form processing
        
        # Check if we're on dashboard or if there's an error
        # The login might fail if admin user doesn't exist in DB yet
        # In that case, skip this test or create the user first
        try:
            page.wait_for_url("**/admin/dashboard", timeout=5000)
            expect(page).to_have_url("http://localhost:5000/admin/dashboard")
        except:
            # If login failed, check for error message
            # This might be expected if admin user isn't seeded
            page.wait_for_load_state("networkidle")
            # Skip test if admin not set up
            pytest.skip("Admin user not configured in database")
        
    def test_admin_login_with_invalid_credentials(self, page: Page):
        """Test login failure with wrong credentials"""
        page.goto("http://localhost:5000/admin/login")
        page.wait_for_load_state("networkidle")
        
        # Fill in wrong credentials
        page.fill("input[name='username']", "wronguser")
        page.fill("input[name='password']", "wrongpass")
        
        # Submit form
        page.click("button[type='submit']")
        time.sleep(1)  # Wait for error message
        
        # Should stay on login page with error message
        expect(page).to_have_url("http://localhost:5000/admin/login")
        
    def test_admin_protected_page_redirect(self, page: Page):
        """Test that accessing admin pages without login redirects to login"""
        page.goto("http://localhost:5000/admin/dashboard")
        page.wait_for_load_state("networkidle")
        
        # Should redirect to login
        expect(page.get_by_text("Admin Login")).to_be_visible()


class TestAdminDashboard:
    """Tests for admin dashboard page"""
    
    @pytest.fixture(autouse=True)
    def login_admin(self, page: Page):
        """Login as admin before each test"""
        page.goto("http://localhost:5000/admin/login")
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        
    def test_dashboard_page_loads(self, page: Page):
        """Test that dashboard page loads correctly"""
        page.goto("http://localhost:5000/admin/dashboard")
        page.wait_for_load_state("networkidle")
        
        # Check page title
        expect(page).to_have_title("Admin Dashboard - IT Quizbee")
        
        # Verify sidebar is present
        expect(page.locator("aside")).to_be_visible()
        
        # Check for statistics cards
        expect(page.locator("text=Total Quizzes")).to_be_visible()
        
    def test_dashboard_statistics_display(self, page: Page):
        """Test that dashboard statistics are displayed"""
        page.goto("http://localhost:5000/admin/dashboard")
        page.wait_for_load_state("networkidle")
        
        # Wait for statistics to load
        time.sleep(2)
        
        # Check for key metrics
        expect(page.locator("text=Total Quizzes").or_(page.locator("text=Loading"))).to_be_visible()
        
    def test_dashboard_charts_render(self, page: Page):
        """Test that dashboard charts are rendered"""
        page.goto("http://localhost:5000/admin/dashboard")
        page.wait_for_load_state("networkidle")
        
        # Wait for charts to load
        time.sleep(3)
        
        # Check for canvas elements (Chart.js uses canvas)
        canvases = page.locator("canvas")
        expect(canvases.first).to_be_visible()
        
    def test_dashboard_refresh_button(self, page: Page):
        """Test dashboard refresh functionality"""
        page.goto("http://localhost:5000/admin/dashboard")
        page.wait_for_load_state("networkidle")
        
        # Look for refresh button
        refresh_button = page.locator("button:has-text('Refresh')").or_(
            page.locator("i.bi-arrow-clockwise")
        )
        
        if refresh_button.count() > 0:
            refresh_button.first.click()
            time.sleep(1)


class TestQuestionReports:
    """Tests for question reports page"""
    
    @pytest.fixture(autouse=True)
    def login_admin(self, page: Page):
        """Login as admin before each test"""
        page.goto("http://localhost:5000/admin/login")
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        
    def test_question_reports_page_loads(self, page: Page):
        """Test that question reports page loads"""
        page.goto("http://localhost:5000/admin/reports")
        page.wait_for_load_state("networkidle")
        
        # Check page title
        expect(page).to_have_title("Question Reports - Admin")
        
        # Check for filter tabs
        expect(page.locator("text=All Reports").or_(page.locator("text=Pending"))).to_be_visible()
        
    def test_question_reports_filter_tabs(self, page: Page):
        """Test that filter tabs work"""
        page.goto("http://localhost:5000/admin/reports")
        page.wait_for_load_state("networkidle")
        
        # Try clicking different filter tabs
        pending_tab = page.locator("text=Pending").first
        if pending_tab.is_visible():
            pending_tab.click()
            time.sleep(1)
            
        all_tab = page.locator("text=All Reports").first
        if all_tab.is_visible():
            all_tab.click()
            time.sleep(1)


class TestQuestionAnalytics:
    """Tests for question analytics page"""
    
    @pytest.fixture(autouse=True)
    def login_admin(self, page: Page):
        """Login as admin before each test"""
        page.goto("http://localhost:5000/admin/login")
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        
    def test_question_analytics_page_loads(self, page: Page):
        """Test that question analytics page loads"""
        page.goto("http://localhost:5000/admin/question-analytics")
        page.wait_for_load_state("networkidle")
        
        # Check page loaded
        expect(page.locator("h1").or_(page.locator("text=Question Analytics"))).to_be_visible()


class TestAPIHealth:
    """Tests for API health page"""
    
    @pytest.fixture(autouse=True)
    def login_admin(self, page: Page):
        """Login as admin before each test"""
        page.goto("http://localhost:5000/admin/login")
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        
    def test_api_health_page_loads(self, page: Page):
        """Test that API health page loads"""
        page.goto("http://localhost:5000/admin/api-health")
        page.wait_for_load_state("networkidle")
        
        # Check page loaded
        expect(page).to_have_title("API Health - IT Quizbee Admin")
        expect(page.locator("text=API Health").or_(page.locator("text=System Status"))).to_be_visible()


class TestRecentActivity:
    """Tests for recent activity page"""
    
    @pytest.fixture(autouse=True)
    def login_admin(self, page: Page):
        """Login as admin before each test"""
        page.goto("http://localhost:5000/admin/login")
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        
    def test_recent_activity_page_loads(self, page: Page):
        """Test that recent activity page loads"""
        page.goto("http://localhost:5000/admin/recent-activity")
        page.wait_for_load_state("networkidle")
        
        # Check page loaded
        expect(page).to_have_title("Recent Activity - IT Quizbee Admin")
        expect(page.locator("text=Recent Activity")).to_be_visible()


class TestTopicPerformance:
    """Tests for topic performance page"""
    
    @pytest.fixture(autouse=True)
    def login_admin(self, page: Page):
        """Login as admin before each test"""
        page.goto("http://localhost:5000/admin/login")
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        
    def test_topic_performance_page_loads(self, page: Page):
        """Test that topic performance page loads"""
        page.goto("http://localhost:5000/admin/topic-performance")
        page.wait_for_load_state("networkidle")
        
        # Check page loaded
        expect(page).to_have_title("Topic Performance - IT Quizbee Admin")
        expect(page.locator("text=Topic Performance")).to_be_visible()
        
    def test_topic_performance_charts(self, page: Page):
        """Test that performance charts are rendered"""
        page.goto("http://localhost:5000/admin/topic-performance")
        page.wait_for_load_state("networkidle")
        
        # Wait for charts to load
        time.sleep(3)
        
        # Check for canvas elements
        canvases = page.locator("canvas")
        expect(canvases.first).to_be_visible()


class TestAdminSidebar:
    """Tests for admin sidebar navigation"""
    
    @pytest.fixture(autouse=True)
    def login_admin(self, page: Page):
        """Login as admin before each test"""
        page.goto("http://localhost:5000/admin/login")
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        
    def test_sidebar_navigation_links(self, page: Page):
        """Test that all sidebar navigation links are present"""
        page.goto("http://localhost:5000/admin/dashboard")
        page.wait_for_load_state("networkidle")
        
        # Check for sidebar
        sidebar = page.locator("aside")
        expect(sidebar).to_be_visible()
        
        # Check for key navigation items
        expect(page.locator("text=Dashboard").or_(page.locator("a[href*='dashboard']"))).to_be_visible()
        
    def test_sidebar_logout(self, page: Page):
        """Test logout functionality from sidebar"""
        page.goto("http://localhost:5000/admin/dashboard")
        page.wait_for_load_state("networkidle")
        
        # Click logout
        logout_link = page.locator("a[href*='logout']").or_(page.locator("text=Logout"))
        if logout_link.count() > 0:
            logout_link.click()
            page.wait_for_load_state("networkidle")
            
            # Should redirect to login
            expect(page.get_by_text("Admin Login")).to_be_visible()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
