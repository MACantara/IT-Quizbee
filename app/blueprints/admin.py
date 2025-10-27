"""
Admin Blueprint
Handles admin authentication and dashboard routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services import AuthService, AnalyticsService
from app.services.question_analytics_service import QuestionAnalyticsService
from app.repositories import QuizAttemptRepository
from app.repositories.question_report_repository import QuestionReportRepository
from app.decorators.auth import admin_required
from app.decorators.logging import log_request
from app.services import AuthService, AnalyticsService
from app.repositories import QuizAttemptRepository
from app.decorators.auth import admin_required
from app.decorators.logging import log_request, audit_log
from app.decorators.rate_limit import rate_limit
from app.utils import handle_error, AuthenticationError, ValidationError

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Initialize services
auth_service = AuthService()
analytics_service = None
question_analytics_service = None
question_report_repo = None  # Will be initialized with repository


@admin_bp.route('/login', methods=['GET', 'POST'])
@rate_limit(max_requests=60, window_seconds=60)
@log_request
def login():
    """Admin login page"""
    try:
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            success, error = auth_service.authenticate_admin(username, password)
            
            if success:
                flash('Login successful!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                raise AuthenticationError(error)
        
        return render_template('admin/admin_login.html')
    except AuthenticationError as e:
        flash(str(e), 'error')
        return render_template('admin/admin_login.html'), 401


@admin_bp.route('/logout')
@admin_required
@audit_log("Admin logout")
def logout():
    """Admin logout"""
    auth_service.logout_admin()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
@admin_required
@log_request
def dashboard():
    """Admin dashboard with analytics"""
    try:
        global analytics_service, question_analytics_service, question_report_repo
        
        # Initialize services if not already done
        if analytics_service is None:
            attempt_repo = QuizAttemptRepository()
            analytics_service = AnalyticsService(attempt_repo)
        
        if question_analytics_service is None:
            question_analytics_service = QuestionAnalyticsService()
        
        if question_report_repo is None:
            question_report_repo = QuestionReportRepository()
        
        # Get statistics
        stats = analytics_service.get_dashboard_statistics(days=30)
        admin_info = auth_service.get_admin_info()
        
        # Get question analytics
        question_stats = question_analytics_service.get_question_statistics(limit=10)
        
        # Get pending reports count
        pending_reports_count = question_report_repo.get_pending_count()
        
        # Get recent reports
        recent_reports = question_report_repo.get_all(status='pending', limit=5)
        
        return render_template(
            'admin/admin_dashboard.html',
            statistics=stats,
            admin_info=admin_info,
            question_analytics=question_stats,
            pending_reports_count=pending_reports_count,
            recent_reports=[report.to_dict() for report in recent_reports]
        )
    except Exception as e:
        return handle_error(e, "Error loading dashboard")


@admin_bp.route('/analytics')
@admin_required
@log_request
def analytics():
    """Detailed analytics page"""
    try:
        global analytics_service
        
        if analytics_service is None:
            attempt_repo = QuizAttemptRepository()
            analytics_service = AnalyticsService(attempt_repo)
        
        # Get comprehensive statistics
        days = request.args.get('days', 30, type=int)
        stats = analytics_service.get_dashboard_statistics(days=days)
        mode_comparison = analytics_service.get_mode_comparison()
        difficulty_analysis = analytics_service.get_difficulty_analysis()
        
        return render_template(
            'admin/analytics.html',
            statistics=stats,
            mode_comparison=mode_comparison,
            difficulty_analysis=difficulty_analysis,
            days=days
        )
    except Exception as e:
        return handle_error(e, "Error loading analytics")


@admin_bp.route('/users')
@admin_required
@log_request
def users():
    """User management page"""
    try:
        admins = auth_service.get_all_admins()
        
        return render_template(
            'admin/users.html',
            admins=admins
        )
    except Exception as e:
        return handle_error(e, "Error loading users")


@admin_bp.route('/users/add', methods=['POST'])
@admin_required
@rate_limit(max_requests=60, window_seconds=60)
@audit_log("Add admin user")
def add_user():
    """Add new admin user"""
    try:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        success, error = auth_service.add_admin_user(username, password)
        
        if success:
            flash(f'Admin user "{username}" created successfully!', 'success')
        else:
            raise ValidationError(error)
        
        return redirect(url_for('admin.users'))
    except ValidationError as e:
        flash(str(e), 'error')
        return redirect(url_for('admin.users'))


@admin_bp.route('/users/remove/<username>', methods=['POST'])
@admin_required
@audit_log("Remove admin user")
def remove_user(username):
    """Remove admin user"""
    try:
        success, error = auth_service.remove_admin_user(username)
        
        if success:
            flash(f'Admin user "{username}" removed successfully!', 'success')
        else:
            raise ValidationError(error)
        
        return redirect(url_for('admin.users'))
    except ValidationError as e:
        flash(str(e), 'error')
        return redirect(url_for('admin.users'))


@admin_bp.route('/question-reports')
@admin_required
@log_request
def question_reports():
    """View all question reports"""
    try:
        global question_report_repo, question_analytics_service
        
        if question_report_repo is None:
            question_report_repo = QuestionReportRepository()
        
        if question_analytics_service is None:
            question_analytics_service = QuestionAnalyticsService()
        
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        
        # Get reports
        if status_filter == 'all':
            reports = question_report_repo.get_all()
        else:
            reports = question_report_repo.get_all(status=status_filter)
        
        # Get question analytics
        question_stats = question_analytics_service.get_question_statistics(limit=20)
        
        return render_template(
            'admin/question_reports.html',
            reports=[report.to_dict() for report in reports],
            status_filter=status_filter,
            question_analytics=question_stats
        )
    except Exception as e:
        return handle_error(e, "Error loading question reports")


@admin_bp.route('/question-analytics')
@admin_required
@log_request
def question_analytics():
    """Question analytics page"""
    try:
        global question_report_repo, question_analytics_service
        
        if question_report_repo is None:
            question_report_repo = QuestionReportRepository()
        
        if question_analytics_service is None:
            question_analytics_service = QuestionAnalyticsService()
        
        # Get question analytics
        question_stats = question_analytics_service.get_question_statistics(limit=20)
        
        # Get pending reports count
        pending_reports_count = question_report_repo.get_pending_count()
        
        # Get recent reports
        recent_reports = question_report_repo.get_all(status='pending', limit=10)
        
        return render_template(
            'admin/question_analytics.html',
            question_analytics=question_stats,
            pending_reports_count=pending_reports_count,
            recent_reports=[report.to_dict() for report in recent_reports]
        )
    except Exception as e:
        return handle_error(e, "Error loading question analytics")


@admin_bp.route('/topic-performance')
@admin_required
@log_request
def topic_performance():
    """Topic performance analytics page"""
    try:
        global analytics_service
        
        if analytics_service is None:
            attempt_repo = QuizAttemptRepository()
            analytics_service = AnalyticsService(attempt_repo)
        
        # Get statistics
        stats = analytics_service.get_dashboard_statistics(days=30)
        
        return render_template(
            'admin/topic_performance.html',
            statistics=stats
        )
    except Exception as e:
        return handle_error(e, "Error loading topic performance")


@admin_bp.route('/recent-activity')
@admin_required
@log_request
def recent_activity():
    """Recent activity page"""
    try:
        global analytics_service
        
        if analytics_service is None:
            attempt_repo = QuizAttemptRepository()
            analytics_service = AnalyticsService(attempt_repo)
        
        # Get statistics with more recent activity
        stats = analytics_service.get_dashboard_statistics(days=7)
        
        return render_template(
            'admin/recent_activity.html',
            statistics=stats
        )
    except Exception as e:
        return handle_error(e, "Error loading recent activity")


@admin_bp.route('/api-health')
@admin_required
@log_request
def api_health():
    """API health monitoring page"""
    return render_template('admin/api_health.html')


@admin_bp.route('/change-password', methods=['POST'])
@admin_required
@rate_limit(max_requests=60, window_seconds=60)
@audit_log("Change password")
def change_password():
    """Change admin password"""
    try:
        username = session.get('admin_username')
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if new_password != confirm_password:
            raise ValidationError('New passwords do not match!')
        
        success, error = auth_service.change_admin_password(
            username, old_password, new_password
        )
        
        if success:
            flash('Password changed successfully!', 'success')
        else:
            raise ValidationError(error)
        
        return redirect(url_for('admin.dashboard'))
    except ValidationError as e:
        flash(str(e), 'error')
        return redirect(url_for('admin.dashboard'))
