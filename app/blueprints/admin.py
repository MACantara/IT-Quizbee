"""
Admin Blueprint
Handles admin authentication and dashboard routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services import AuthService, AnalyticsService
from app.repositories import QuizAttemptRepository
from app.decorators.auth import admin_required
from app.decorators.logging import log_request, audit_log
from app.decorators.rate_limit import rate_limit
from app.utils import handle_error, AuthenticationError, ValidationError

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Initialize services
auth_service = AuthService()
analytics_service = None  # Will be initialized with repository


@admin_bp.route('/login', methods=['GET', 'POST'])
@rate_limit(max_requests=5, window_seconds=60)
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
        global analytics_service
        
        # Initialize analytics service if not already done
        if analytics_service is None:
            attempt_repo = QuizAttemptRepository()
            analytics_service = AnalyticsService(attempt_repo)
        
        # Get statistics
        stats = analytics_service.get_dashboard_statistics(days=30)
        admin_info = auth_service.get_admin_info()
        
        return render_template(
            'admin/admin_dashboard.html',
            statistics=stats,
            admin_info=admin_info
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
@rate_limit(max_requests=10, window_seconds=300)
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


@admin_bp.route('/change-password', methods=['POST'])
@admin_required
@rate_limit(max_requests=3, window_seconds=300)
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
