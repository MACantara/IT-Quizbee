"""
Events Package
Exports event manager and observer classes
"""

from .event_manager import EventManager, Event, EventType, event_manager
from .observers import (
    LoggingObserver,
    AnalyticsObserver,
    NotificationObserver,
    PerformanceMonitor,
    register_all_observers
)

__all__ = [
    'EventManager',
    'Event',
    'EventType',
    'event_manager',
    'LoggingObserver',
    'AnalyticsObserver',
    'NotificationObserver',
    'PerformanceMonitor',
    'register_all_observers',
]
