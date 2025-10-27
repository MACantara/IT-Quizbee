"""
Tests for Event System (Observer Pattern)

This module tests the Observer pattern implementation.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from app.events.event_manager import EventManager, Event, EventType
from app.events.observers import (
    LoggingObserver,
    AnalyticsObserver,
    NotificationObserver,
    PerformanceMonitor
)
from config import TestingConfig


class TestEventManager:
    """Tests for EventManager singleton"""
    
    def test_singleton_pattern(self):
        """Test that EventManager follows singleton pattern"""
        manager1 = EventManager()
        manager2 = EventManager()
        
        assert manager1 is manager2
    
    def test_subscribe_observer(self):
        """Test subscribing an observer to an event"""
        manager = EventManager()
        observer = Mock()
        
        manager.subscribe(EventType.QUIZ_STARTED, observer)
        
        assert EventType.QUIZ_STARTED in manager._observers
        assert observer in manager._observers[EventType.QUIZ_STARTED]
    
    def test_subscribe_multiple_observers(self):
        """Test subscribing multiple observers to same event"""
        manager = EventManager()
        observer1 = Mock()
        observer2 = Mock()
        
        manager.subscribe(EventType.QUIZ_STARTED, observer1)
        manager.subscribe(EventType.QUIZ_STARTED, observer2)
        
        assert len(manager._observers[EventType.QUIZ_STARTED]) == 2
    
    def test_subscribe_observer_to_multiple_events(self):
        """Test subscribing same observer to multiple events"""
        manager = EventManager()
        observer = Mock()
        
        manager.subscribe(EventType.QUIZ_STARTED, observer)
        manager.subscribe(EventType.QUIZ_COMPLETED, observer)
        
        assert observer in manager._observers[EventType.QUIZ_STARTED]
        assert observer in manager._observers[EventType.QUIZ_COMPLETED]
    
    def test_unsubscribe_observer(self):
        """Test unsubscribing an observer"""
        manager = EventManager()
        observer = Mock()
        
        manager.subscribe(EventType.QUIZ_STARTED, observer)
        manager.unsubscribe(EventType.QUIZ_STARTED, observer)
        
        assert observer not in manager._observers.get(EventType.QUIZ_STARTED, [])
    
    def test_notify_single_observer(self):
        """Test notifying a single observer"""
        manager = EventManager()
        observer = Mock()
        observer.update = Mock()
        
        manager.subscribe(EventType.QUIZ_STARTED, observer)
        
        event = Event(EventType.QUIZ_STARTED, {'session_id': '123'})
        manager.notify(event)
        
        observer.update.assert_called_once_with(event)
    
    def test_notify_multiple_observers(self):
        """Test notifying multiple observers"""
        manager = EventManager()
        observer1 = Mock()
        observer2 = Mock()
        observer1.update = Mock()
        observer2.update = Mock()
        
        manager.subscribe(EventType.QUIZ_STARTED, observer1)
        manager.subscribe(EventType.QUIZ_STARTED, observer2)
        
        event = Event(EventType.QUIZ_STARTED, {'session_id': '123'})
        manager.notify(event)
        
        observer1.update.assert_called_once_with(event)
        observer2.update.assert_called_once_with(event)
    
    def test_notify_no_observers(self):
        """Test notifying with no observers doesn't crash"""
        manager = EventManager()
        
        event = Event(EventType.QUIZ_STARTED, {})
        manager.notify(event)  # Should not raise
    
    def test_notify_observer_exception_handling(self):
        """Test that observer exceptions don't stop other notifications"""
        manager = EventManager()
        
        failing_observer = Mock()
        failing_observer.update = Mock(side_effect=Exception("Observer error"))
        
        working_observer = Mock()
        working_observer.update = Mock()
        
        manager.subscribe(EventType.QUIZ_STARTED, failing_observer)
        manager.subscribe(EventType.QUIZ_STARTED, working_observer)
        
        event = Event(EventType.QUIZ_STARTED, {})
        manager.notify(event)
        
        # Working observer should still be called
        working_observer.update.assert_called_once()
    
    def test_clear_observers(self):
        """Test clearing all observers"""
        manager = EventManager()
        observer = Mock()
        
        manager.subscribe(EventType.QUIZ_STARTED, observer)
        manager.subscribe(EventType.QUIZ_COMPLETED, observer)
        
        manager.clear()
        
        assert len(manager._observers) == 0


class TestEvent:
    """Tests for Event class"""
    
    def test_event_creation(self):
        """Test creating an event"""
        event = Event(EventType.QUIZ_STARTED, {'session_id': '123'})
        
        assert event.event_type == EventType.QUIZ_STARTED
        assert event.data == {'session_id': '123'}
        assert event.timestamp is not None
    
    def test_event_with_empty_data(self):
        """Test creating event with no data"""
        event = Event(EventType.SYSTEM_ERROR)
        
        assert event.event_type == EventType.SYSTEM_ERROR
        assert event.data == {}
    
    def test_event_representation(self):
        """Test event string representation"""
        event = Event(EventType.QUIZ_STARTED, {'session_id': '123'})
        
        event_str = str(event)
        assert 'QUIZ_STARTED' in event_str
        assert 'session_id' in event_str


class TestLoggingObserver:
    """Tests for LoggingObserver"""
    
    @patch('app.events.observers.current_app')
    def test_quiz_started_logging(self, mock_app):
        """Test logging when quiz starts"""
        mock_logger = Mock()
        mock_app.logger = mock_logger
        
        observer = LoggingObserver()
        event = Event(EventType.QUIZ_STARTED, {
            'session_id': '123',
            'quiz_type': 'elimination',
            'topic': 'python'
        })
        
        observer.update(event)
        
        mock_logger.info.assert_called()
        call_args = str(mock_logger.info.call_args)
        assert 'QUIZ_STARTED' in call_args
    
    @patch('app.events.observers.current_app')
    def test_quiz_completed_logging(self, mock_app):
        """Test logging when quiz completes"""
        mock_logger = Mock()
        mock_app.logger = mock_logger
        
        observer = LoggingObserver()
        event = Event(EventType.QUIZ_COMPLETED, {
            'session_id': '123',
            'score': 85.0,
            'passed': True
        })
        
        observer.update(event)
        
        mock_logger.info.assert_called()
    
    @patch('app.events.observers.current_app')
    def test_error_logging(self, mock_app):
        """Test logging errors"""
        mock_logger = Mock()
        mock_app.logger = mock_logger
        
        observer = LoggingObserver()
        event = Event(EventType.SYSTEM_ERROR, {
            'error': 'Test error',
            'details': 'Error details'
        })
        
        observer.update(event)
        
        mock_logger.error.assert_called()


class TestAnalyticsObserver:
    """Tests for AnalyticsObserver"""
    
    @patch('app.events.observers.db')
    def test_quiz_completed_analytics(self, mock_db):
        """Test analytics tracking on quiz completion"""
        observer = AnalyticsObserver()
        event = Event(EventType.QUIZ_COMPLETED, {
            'session_id': '123',
            'user_name': 'Test User',
            'score': 85.0,
            'time_taken': 300,
            'quiz_type': 'elimination'
        })
        
        observer.update(event)
        
        # Analytics should be recorded (implementation specific)
        # This test verifies the method is called without errors
    
    def test_quiz_started_analytics(self):
        """Test analytics tracking on quiz start"""
        observer = AnalyticsObserver()
        event = Event(EventType.QUIZ_STARTED, {
            'session_id': '123',
            'quiz_type': 'finals'
        })
        
        # Should handle without errors
        observer.update(event)


class TestNotificationObserver:
    """Tests for NotificationObserver"""
    
    @patch('app.events.observers.current_app')
    def test_high_score_notification(self, mock_app):
        """Test notification for high scores"""
        mock_logger = Mock()
        mock_app.logger = mock_logger
        
        observer = NotificationObserver()
        event = Event(EventType.QUIZ_COMPLETED, {
            'score': 95.0,
            'user_name': 'Test User',
            'quiz_type': 'finals'
        })
        
        observer.update(event)
        
        # Should log notification for high score
        mock_logger.info.assert_called()
    
    @patch('app.events.observers.current_app')
    def test_low_score_notification(self, mock_app):
        """Test notification for low scores"""
        mock_logger = Mock()
        mock_app.logger = mock_logger
        
        observer = NotificationObserver()
        event = Event(EventType.QUIZ_COMPLETED, {
            'score': 45.0,
            'user_name': 'Test User',
            'passed': False
        })
        
        observer.update(event)
        
        mock_logger.info.assert_called()


class TestPerformanceMonitor:
    """Tests for PerformanceMonitor"""
    
    @patch('app.events.observers.current_app')
    def test_slow_quiz_detection(self, mock_app):
        """Test detection of slow quiz submissions"""
        mock_logger = Mock()
        mock_app.logger = mock_logger
        
        observer = PerformanceMonitor()
        event = Event(EventType.QUIZ_COMPLETED, {
            'time_taken': 1200,  # 20 minutes (very slow)
            'session_id': '123'
        })
        
        observer.update(event)
        
        # Should log warning for slow completion
        assert mock_logger.warning.called or mock_logger.info.called
    
    @patch('app.events.observers.current_app')
    def test_fast_quiz_detection(self, mock_app):
        """Test detection of unusually fast quiz submissions"""
        mock_logger = Mock()
        mock_app.logger = mock_logger
        
        observer = PerformanceMonitor()
        event = Event(EventType.QUIZ_COMPLETED, {
            'time_taken': 30,  # 30 seconds (suspiciously fast)
            'session_id': '123'
        })
        
        observer.update(event)
        
        # Should log info about fast completion
        mock_logger.info.assert_called()
    
    @patch('app.events.observers.current_app')
    def test_error_performance_tracking(self, mock_app):
        """Test performance tracking of errors"""
        mock_logger = Mock()
        mock_app.logger = mock_logger
        
        observer = PerformanceMonitor()
        event = Event(EventType.SYSTEM_ERROR, {
            'error': 'Database timeout',
            'duration': 5.5
        })
        
        observer.update(event)
        
        mock_logger.error.assert_called()


class TestEventSystemIntegration:
    """Integration tests for the event system"""
    
    def test_full_event_flow(self):
        """Test complete event flow from trigger to observer notification"""
        manager = EventManager()
        manager.clear()  # Clear any existing observers
        
        # Create observers
        logging_observer = Mock()
        analytics_observer = Mock()
        logging_observer.update = Mock()
        analytics_observer.update = Mock()
        
        # Subscribe observers
        manager.subscribe(EventType.QUIZ_STARTED, logging_observer)
        manager.subscribe(EventType.QUIZ_STARTED, analytics_observer)
        manager.subscribe(EventType.QUIZ_COMPLETED, logging_observer)
        
        # Trigger quiz started event
        start_event = Event(EventType.QUIZ_STARTED, {'session_id': '123'})
        manager.notify(start_event)
        
        # Both observers should be notified
        logging_observer.update.assert_called_with(start_event)
        analytics_observer.update.assert_called_with(start_event)
        
        # Trigger quiz completed event
        complete_event = Event(EventType.QUIZ_COMPLETED, {
            'session_id': '123',
            'score': 85.0
        })
        manager.notify(complete_event)
        
        # Only logging observer should be notified (analytics not subscribed to completed)
        assert logging_observer.update.call_count == 2
        assert analytics_observer.update.call_count == 1
    
    def test_multiple_event_types(self):
        """Test handling multiple event types"""
        manager = EventManager()
        manager.clear()
        
        observer = Mock()
        observer.update = Mock()
        
        # Subscribe to multiple event types
        event_types = [
            EventType.QUIZ_STARTED,
            EventType.QUIZ_COMPLETED,
            EventType.USER_LOGIN,
            EventType.USER_LOGOUT
        ]
        
        for event_type in event_types:
            manager.subscribe(event_type, observer)
        
        # Trigger each event type
        for event_type in event_types:
            event = Event(event_type, {})
            manager.notify(event)
        
        # Observer should be called for each event
        assert observer.update.call_count == len(event_types)
