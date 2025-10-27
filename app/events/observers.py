"""
Event Observers - Concrete implementations of event handlers
Implements Observer Pattern for various system events
"""

import logging
from datetime import datetime
from flask import current_app
from .event_manager import Event, EventType


class LoggingObserver:
    """
    Observer that logs all events to the application log
    """
    
    def __init__(self):
        self.logger = logging.getLogger('quiz.events')
    
    def update(self, event: Event):
        """
        Main update method called by EventManager
        Routes to specific handler based on event type
        """
        handler_map = {
            EventType.QUIZ_STARTED: self.on_quiz_started,
            EventType.QUIZ_COMPLETED: self.on_quiz_completed,
            EventType.HIGH_SCORE_ACHIEVED: self.on_high_score,
            EventType.SYSTEM_ERROR: self.on_error,
        }
        
        handler = handler_map.get(event.event_type)
        if handler:
            handler(event)
        else:
            # Log unknown event types
            try:
                current_app.logger.info(f"Event: {event.event_type.value}, Data: {event.data}")
            except:
                self.logger.info(f"Event: {event.event_type.value}, Data: {event.data}")
    
    def on_quiz_started(self, event: Event):
        """Handle quiz started event"""
        data = event.data
        try:
            current_app.logger.info(
                f"Quiz Started - Mode: {data.get('mode')}, "
                f"User: {data.get('user_name', 'Anonymous')}, "
                f"Questions: {data.get('question_count')}"
            )
        except:
            self.logger.info(
                f"Quiz Started - Mode: {data.get('mode')}, "
                f"User: {data.get('user_name', 'Anonymous')}, "
                f"Questions: {data.get('question_count')}"
            )
    
    def on_quiz_completed(self, event: Event):
        """Handle quiz completed event"""
        data = event.data
        try:
            current_app.logger.info(
                f"Quiz Completed - Mode: {data.get('mode')}, "
                f"User: {data.get('user_name', 'Anonymous')}, "
                f"Score: {data.get('score')}%, "
                f"Correct: {data.get('correct')}/{data.get('total')}"
            )
        except:
            self.logger.info(
                f"Quiz Completed - Mode: {data.get('mode')}, "
                f"User: {data.get('user_name', 'Anonymous')}, "
                f"Score: {data.get('score')}%, "
                f"Correct: {data.get('correct')}/{data.get('total')}"
            )
    
    def on_high_score(self, event: Event):
        """Handle high score achievement"""
        data = event.data
        try:
            current_app.logger.info(
                f"🏆 High Score Achieved! User: {data.get('user_name')}, "
                f"Score: {data.get('score')}%"
            )
        except:
            self.logger.info(
                f"🏆 High Score Achieved! User: {data.get('user_name')}, "
                f"Score: {data.get('score')}%"
            )
    
    def on_error(self, event: Event):
        """Handle error events"""
        data = event.data
        try:
            current_app.logger.error(
                f"System Error: {data.get('error')}, Details: {data.get('details', 'N/A')}"
            )
        except:
            self.logger.error(
                f"System Error: {data.get('error')}, Details: {data.get('details', 'N/A')}"
            )


class AnalyticsObserver:
    """
    Observer that tracks analytics and statistics
    """
    
    def __init__(self):
        self.quiz_counts = {'elimination': 0, 'finals': 0, 'review': 0}
        self.total_attempts = 0
        self.logger = logging.getLogger('quiz.analytics')
    
    def update(self, event: Event):
        """
        Main update method called by EventManager
        Routes to specific handler based on event type
        """
        if event.event_type == EventType.QUIZ_COMPLETED:
            self.on_quiz_completed(event)
        elif event.event_type == EventType.QUIZ_STARTED:
            self.on_quiz_started(event)
    
    def on_quiz_started(self, event: Event):
        """Handle quiz start for analytics"""
        # Can track quiz starts if needed
        pass
    
    def on_quiz_completed(self, event: Event):
        """Track quiz completion for analytics"""
        data = event.data
        mode = data.get('mode', 'unknown')
        
        # Update counters
        self.total_attempts += 1
        if mode in self.quiz_counts:
            self.quiz_counts[mode] += 1
        
        self.logger.debug(
            f"Analytics Updated - Total: {self.total_attempts}, "
            f"Elimination: {self.quiz_counts['elimination']}, "
            f"Finals: {self.quiz_counts['finals']}, "
            f"Review: {self.quiz_counts['review']}"
        )
    
    def get_statistics(self):
        """Get current statistics"""
        return {
            'total_attempts': self.total_attempts,
            'by_mode': self.quiz_counts.copy()
        }


class NotificationObserver:
    """
    Observer that handles user notifications
    Could be extended to send emails, push notifications, etc.
    """
    
    def __init__(self):
        self.notifications = []
        self.logger = logging.getLogger('quiz.notifications')
    
    def update(self, event: Event):
        """
        Main update method called by EventManager
        Routes to specific handler based on event type
        """
        if event.event_type == EventType.HIGH_SCORE_ACHIEVED:
            self.on_high_score(event)
        elif event.event_type == EventType.QUIZ_COMPLETED:
            self.on_quiz_completed(event)
    
    def on_high_score(self, event: Event):
        """Send notification for high score"""
        data = event.data
        message = f"Congratulations {data.get('user_name')}! You achieved {data.get('score')}%!"
        
        self.notifications.append({
            'timestamp': datetime.utcnow(),
            'type': 'high_score',
            'message': message,
            'user': data.get('user_name')
        })
        
        try:
            current_app.logger.info(f"Notification queued: {message}")
        except:
            self.logger.info(f"Notification queued: {message}")
    
    def on_quiz_completed(self, event: Event):
        """Send completion notification"""
        data = event.data
        score = data.get('score', 0)
        
        # Different messages based on score
        if score >= 90:
            message = f"Excellent work, {data.get('user_name', 'Student')}! 🌟"
        elif score >= 70:
            message = f"Good job, {data.get('user_name', 'Student')}! Keep it up! 👍"
        else:
            message = f"Keep practicing, {data.get('user_name', 'Student')}! You'll improve! 💪"
        
        self.notifications.append({
            'timestamp': datetime.utcnow(),
            'type': 'completion',
            'message': message,
            'user': data.get('user_name'),
            'score': score
        })
        
        try:
            current_app.logger.info(message)
        except:
            self.logger.info(message)
    
    def get_notifications(self, user_name=None):
        """Get notifications, optionally filtered by user"""
        if user_name:
            return [n for n in self.notifications if n.get('user') == user_name]
        return self.notifications.copy()
    
    def clear_notifications(self):
        """Clear all notifications"""
        self.notifications.clear()


class PerformanceMonitor:
    """
    Observer that monitors system performance metrics
    """
    
    def __init__(self):
        self.quiz_durations = []
        self.logger = logging.getLogger('quiz.performance')
    
    def update(self, event: Event):
        """
        Main update method called by EventManager
        Routes to specific handler based on event type
        """
        if event.event_type == EventType.QUIZ_STARTED:
            self.on_quiz_started(event)
        elif event.event_type == EventType.QUIZ_COMPLETED:
            self.on_quiz_completed(event)
        elif event.event_type == EventType.SYSTEM_ERROR:
            self.on_error(event)
    
    def on_quiz_started(self, event: Event):
        """Track quiz start time"""
        data = event.data
        session_id = data.get('session_id')
        self.logger.debug(f"Performance tracking started for session {session_id}")
    
    def on_quiz_completed(self, event: Event):
        """Track quiz completion and duration"""
        data = event.data
        duration = data.get('duration_seconds', 0) or data.get('time_taken', 0)
        
        self.quiz_durations.append({
            'mode': data.get('mode'),
            'duration': duration,
            'timestamp': datetime.utcnow()
        })
        
        # Keep only recent records (last 100)
        if len(self.quiz_durations) > 100:
            self.quiz_durations = self.quiz_durations[-100:]
        
        # Log warnings for unusual durations
        try:
            if duration > 1000:  # Very slow (over 16 minutes)
                current_app.logger.warning(f"Slow quiz completion detected: {duration} seconds")
            elif duration < 60:  # Very fast (under 1 minute)
                current_app.logger.info(f"Fast quiz completion: {duration} seconds")
            else:
                current_app.logger.info(f"Quiz completed in {duration} seconds")
        except:
            if duration > 1000:
                self.logger.warning(f"Slow quiz completion detected: {duration} seconds")
            elif duration < 60:
                self.logger.info(f"Fast quiz completion: {duration} seconds")
            else:
                self.logger.info(f"Quiz completed in {duration} seconds")
    
    def on_error(self, event: Event):
        """Track error events"""
        data = event.data
        try:
            current_app.logger.error(f"Performance: Error tracked - {data.get('error')}")
        except:
            self.logger.error(f"Performance: Error tracked - {data.get('error')}")
    
    def get_average_duration(self, mode=None):
        """Calculate average quiz duration"""
        if mode:
            durations = [d['duration'] for d in self.quiz_durations if d['mode'] == mode]
        else:
            durations = [d['duration'] for d in self.quiz_durations]
        
        return sum(durations) / len(durations) if durations else 0


def register_all_observers(event_manager):
    """
    Register all observers with the event manager
    
    Args:
        event_manager: EventManager instance
    """
    # Create observer instances
    logging_observer = LoggingObserver()
    analytics_observer = AnalyticsObserver()
    notification_observer = NotificationObserver()
    performance_monitor = PerformanceMonitor()
    
    # Register logging observer
    event_manager.subscribe(EventType.QUIZ_STARTED, logging_observer.update)
    event_manager.subscribe(EventType.QUIZ_COMPLETED, logging_observer.update)
    event_manager.subscribe(EventType.HIGH_SCORE_ACHIEVED, logging_observer.update)
    event_manager.subscribe(EventType.SYSTEM_ERROR, logging_observer.update)
    
    # Register analytics observer
    event_manager.subscribe(EventType.QUIZ_COMPLETED, analytics_observer.update)
    event_manager.subscribe(EventType.QUIZ_STARTED, analytics_observer.update)
    
    # Register notification observer
    event_manager.subscribe(EventType.QUIZ_COMPLETED, notification_observer.update)
    event_manager.subscribe(EventType.HIGH_SCORE_ACHIEVED, notification_observer.update)
    
    # Register performance monitor
    event_manager.subscribe(EventType.QUIZ_STARTED, performance_monitor.update)
    event_manager.subscribe(EventType.QUIZ_COMPLETED, performance_monitor.update)
    event_manager.subscribe(EventType.SYSTEM_ERROR, performance_monitor.update)
    
    return {
        'logging': logging_observer,
        'analytics': analytics_observer,
        'notifications': notification_observer,
        'performance': performance_monitor
    }
