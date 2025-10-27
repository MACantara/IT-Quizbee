"""
Base Repository Pattern Implementation
Abstracts database operations for easier testing and migration
"""

from typing import TypeVar, Generic, List, Optional
from models import db

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository providing common CRUD operations
    Implements the Repository Pattern for database abstraction
    """
    
    def __init__(self, model_class):
        """
        Initialize repository with a model class
        
        Args:
            model_class: SQLAlchemy model class
        """
        self.model_class = model_class
    
    def get_by_id(self, id: str) -> Optional[T]:
        """
        Retrieve entity by ID
        
        Args:
            id: Entity identifier
            
        Returns:
            Entity instance or None
        """
        return self.model_class.query.get(id)
    
    def get_all(self, limit: Optional[int] = None) -> List[T]:
        """
        Retrieve all entities
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of entities
        """
        query = self.model_class.query
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def filter_by(self, **kwargs) -> List[T]:
        """
        Filter entities by criteria
        
        Args:
            **kwargs: Filter criteria
            
        Returns:
            List of matching entities
        """
        return self.model_class.query.filter_by(**kwargs).all()
    
    def create(self, **kwargs) -> T:
        """
        Create new entity
        
        Args:
            **kwargs: Entity attributes
            
        Returns:
            Created entity instance
        """
        try:
            entity = self.model_class(**kwargs)
            db.session.add(entity)
            db.session.commit()
            return entity
        except Exception:
            db.session.rollback()
            raise
    
    def update(self, entity: T) -> T:
        """
        Update existing entity
        
        Args:
            entity: Entity to update
            
        Returns:
            Updated entity
        """
        try:
            db.session.commit()
            return entity
        except Exception:
            db.session.rollback()
            raise
    
    def delete(self, entity: T) -> bool:
        """
        Delete entity
        
        Args:
            entity: Entity to delete
            
        Returns:
            True if successful
        """
        try:
            db.session.delete(entity)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def delete_by_id(self, id: str) -> bool:
        """
        Delete entity by ID
        
        Args:
            id: Entity identifier
            
        Returns:
            True if successful
        """
        entity = self.get_by_id(id)
        if entity:
            return self.delete(entity)
        return False
    
    def count(self) -> int:
        """
        Count total entities
        
        Returns:
            Total count
        """
        return self.model_class.query.count()
    
    def exists(self, id: str) -> bool:
        """
        Check if entity exists
        
        Args:
            id: Entity identifier
            
        Returns:
            True if exists
        """
        return self.get_by_id(id) is not None
