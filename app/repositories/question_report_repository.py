"""
Question Report Repository
Handles persistence for question reports via the JSON store
"""
from collections import Counter
from models import QuestionReport
from .json_store import JsonStore


class QuestionReportRepository:
    """Repository for question report data access"""

    _store = None

    @classmethod
    def _get_store(cls) -> JsonStore:
        if cls._store is None:
            cls._store = JsonStore('reports.json')
        return cls._store

    @staticmethod
    def create(question_id, report_type, reason=None, user_name=None,
               topic=None, subtopic=None, quiz_type=None, difficulty=None,
               question_text=None, question_data=None):
        """
        Create a new question report

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

        QuestionReportRepository._get_store().upsert(report.to_dict())
        return report

    @staticmethod
    def get_by_id(report_id):
        """Get report by ID"""
        record = QuestionReportRepository._get_store().get(report_id)
        return QuestionReport.from_dict(record) if record else None

    @staticmethod
    def get_all(status=None, limit=None):
        """
        Get all reports, newest first, optionally filtered by status
        """
        records = QuestionReportRepository._get_store().all()
        reports = [QuestionReport.from_dict(r) for r in records]

        if status:
            reports = [r for r in reports if r.status == status]

        reports.sort(key=lambda r: r.created_at, reverse=True)

        if limit:
            reports = reports[:limit]

        return reports

    @staticmethod
    def get_by_question_id(question_id):
        """Get all reports for a specific question, newest first"""
        records = QuestionReportRepository._get_store().all()
        reports = [
            QuestionReport.from_dict(r) for r in records
            if r.get('question_id') == question_id
        ]
        reports.sort(key=lambda r: r.created_at, reverse=True)
        return reports

    @staticmethod
    def get_pending_count():
        """Get count of pending reports"""
        return sum(
            1 for r in QuestionReportRepository._get_store().all()
            if r.get('status') == 'pending'
        )

    @staticmethod
    def get_most_reported_questions(limit=10):
        """
        Get questions with the most reports

        Returns:
            List of tuples (question_id, question_text, topic, subtopic, difficulty, count)
        """
        records = QuestionReportRepository._get_store().all()
        counts = Counter(r.get('question_id') for r in records)

        latest = {}
        for r in records:
            q_id = r.get('question_id')
            if q_id and (q_id not in latest or r.get('created_at', '') > latest[q_id].get('created_at', '')):
                latest[q_id] = r

        rows = [
            (
                q_id,
                latest[q_id].get('question_text'),
                latest[q_id].get('topic'),
                latest[q_id].get('subtopic'),
                latest[q_id].get('difficulty'),
                count
            )
            for q_id, count in counts.items() if q_id
        ]
        rows.sort(key=lambda row: row[5], reverse=True)
        return rows[:limit]

    @staticmethod
    def get_reports_by_type():
        """Get report count grouped by report type"""
        return dict(Counter(
            r.get('report_type')
            for r in QuestionReportRepository._get_store().all()
            if r.get('report_type')
        ))

    @staticmethod
    def update_status(report_id, status, admin_name=None, notes=None):
        """
        Update report status

        Returns:
            Updated QuestionReport or None if not found
        """
        report = QuestionReportRepository.get_by_id(report_id)

        if report:
            report.mark_reviewed(admin_name, notes, status)
            QuestionReportRepository._get_store().upsert(report.to_dict())

        return report

    @staticmethod
    def delete(report_id):
        """
        Delete a report

        Returns:
            bool: True if deleted, False if not found
        """
        return QuestionReportRepository._get_store().delete(report_id)
