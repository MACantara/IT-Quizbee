"""
Event Manager - Observer Pattern Implementation
Handles event subscription and notification for async event handling
"""

from typing import Dict, List, Callable, Any
from enum import Enum
import logging


class EventType(Enum):
    """Enumeration of available event types"""
    QUIZ_STARTED = "quiz_started"
    QUIZ_COMPLETED = "quiz_completed"
    QUIZ_SUBMITTED = "quiz_submitted"
    USER_LOGGED_IN = "user_logged_in"
    USER_LOGGED_OUT = "user_logged_out"
    HIGH_SCORE_ACHIEVED = "high_score_achieved"
    ANALYTICS_REQUESTED = "analytics_requested"


class Event:
    """
    Base Event class
    Contains event type and data
    """
    
    def __init__(self, event_type: EventType, data: Dict[str, Any] = None):
        """
        Initialize event
        
        Args:
            event_type: Type of event
            data: Event data payload
        """
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = None
    
    def __repr__(self):
        return f"Event(type={self.event_type.value}, data={self.data})"


class EventManager:
    """
    Event Manager - Singleton pattern
    Manages event subscriptions and notifications (Observer Pattern)
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._observers: Dict[EventType, List[Callable]] = {}
        self._logger = logging.getLogger(__name__)
        self._initialized = True
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """
        Subscribe to an event type
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is triggered
        """
        if event_type not in self._observers:
            self._observers[event_type] = []
        
        if callback not in self._observers[event_type]:
            self._observers[event_type].append(callback)
            self._logger.debug(f"Subscribed {callback.__name__} to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """
        Unsubscribe from an event type
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove
        """
        if event_type in self._observers and callback in self._observers[event_type]:
            self._observers[event_type].remove(callback)
            self._logger.debug(f"Unsubscribed {callback.__name__} from {event_type.value}")
    
    def notify(self, event: Event):
        """
        Notify all subscribers of an event
        
        Args:
            event: Event to broadcast
        """
        if event.event_type not in self._observers:
            self._logger.debug(f"No observers for {event.event_type.value}")
            return
        
        self._logger.info(f"Notifying {len(self._observers[event.event_type])} observers of {event.event_type.value}")
        
        for callback in self._observers[event.event_type]:
            try:
                callback(event)
            except Exception as e:
                self._logger.error(f"Error in observer {callback.__name__}: {e}")
    
    def clear_all(self):
        """Clear all subscriptions"""
        self._observers.clear()
        self._logger.info("Cleared all event subscriptions")
    
    def get_subscriber_count(self, event_type: EventType) -> int:
        """
        Get number of subscribers for an event type
        
        Args:
            event_type: Event type to check
            
        Returns:
            Number of subscribers
        """
        return len(self._observers.get(event_type, []))


# Global event manager instance
event_manager = EventManager()
