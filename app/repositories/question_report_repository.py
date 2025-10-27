"""
Question Report Repository
Handles database operations for question reports
"""
from models import db, QuestionReport
from sqlalchemy import desc, func


class QuestionReportRepository:
    """Repository for question report data access"""
    
    @staticmethod
    def create(question_id, report_type, reason=None, user_name=None,
               topic=None, subtopic=None, quiz_type=None, difficulty=None,
               question_text=None, question_data=None):
        """
        Create a new question report
        
        Args:
            question_id: ID of the question being reported
            report_type: Type of issue
            reason: Detailed explanation
            user_name: Name of the reporter
            topic: Topic name
            subtopic: Subtopic name
            quiz_type: Type of quiz
            difficulty: Difficulty level
            question_text: The question text
            question_data: Full question data
            
        Returns:
            QuestionReport: Created report object
        """
        report = QuestionReport(
            question_id=question_id,
            report_type=report_type,
            reason=reason,
            user_name=user_name,
            topic=topic,
            subtopic=subtopic,
            quiz_type=quiz_type,
            difficulty=difficulty,
            question_text=question_text,
            question_data=question_data
        )
        
        db.session.add(report)
        db.session.commit()
        
        return report
    
    @staticmethod
    def get_by_id(report_id):
        """Get report by ID"""
        return QuestionReport.query.filter_by(id=report_id).first()
    
    @staticmethod
    def get_all(status=None, limit=None):
        """
        Get all reports, optionally filtered by status
        
        Args:
            status: Filter by status (pending, reviewed, resolved, dismissed)
            limit: Maximum number of reports to return
            
        Returns:
            List of QuestionReport objects
        """
        query = QuestionReport.query
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(desc(QuestionReport.created_at))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_by_question_id(question_id):
        """Get all reports for a specific question"""
        return QuestionReport.query.filter_by(question_id=question_id)\
            .order_by(desc(QuestionReport.created_at))\
            .all()
    
    @staticmethod
    def get_pending_count():
        """Get count of pending reports"""
        return QuestionReport.query.filter_by(status='pending').count()
    
    @staticmethod
    def get_most_reported_questions(limit=10):
        """
        Get questions with the most reports
        
        Args:
            limit: Maximum number of questions to return
            
        Returns:
            List of tuples (question_id, count, latest_report)
        """
        # Group by question_id and count reports
        results = db.session.query(
            QuestionReport.question_id,
            QuestionReport.question_text,
            QuestionReport.topic,
            QuestionReport.subtopic,
            QuestionReport.difficulty,
            func.count(QuestionReport.id).label('report_count')
        ).group_by(
            QuestionReport.question_id,
            QuestionReport.question_text,
            QuestionReport.topic,
            QuestionReport.subtopic,
            QuestionReport.difficulty
        ).order_by(
            desc('report_count')
        ).limit(limit).all()
        
        return results
    
    @staticmethod
    def get_reports_by_type():
        """Get report count grouped by report type"""
        results = db.session.query(
            QuestionReport.report_type,
            func.count(QuestionReport.id).label('count')
        ).group_by(
            QuestionReport.report_type
        ).all()
        
        return {report_type: count for report_type, count in results}
    
    @staticmethod
    def update_status(report_id, status, admin_name=None, notes=None):
        """
        Update report status
        
        Args:
            report_id: ID of the report
            status: New status (reviewed, resolved, dismissed)
            admin_name: Name of admin making the update
            notes: Admin notes
            
        Returns:
            Updated QuestionReport or None if not found
        """
        report = QuestionReport.query.filter_by(id=report_id).first()
        
        if report:
            report.mark_reviewed(admin_name, notes, status)
            db.session.commit()
        
        return report
    
    @staticmethod
    def delete(report_id):
        """
        Delete a report
        
        Args:
            report_id: ID of the report to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        report = QuestionReport.query.filter_by(id=report_id).first()
        
        if report:
            db.session.delete(report)
            db.session.commit()
            return True
        
        return False
