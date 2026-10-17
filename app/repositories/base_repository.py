"""
Base Repository Pattern Implementation
JSON-file-backed CRUD for persisted entities
"""

from typing import TypeVar, Generic, List, Optional
from .json_store import JsonStore

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository providing common CRUD operations over a JsonStore.
    Entities must expose to_dict() and from_dict().
    """

    def __init__(self, filename: str, entity_class):
        """
        Initialize repository with a JSON store file and entity class

        Args:
            filename: Store filename (e.g. 'attempts.json')
            entity_class: Entity class with to_dict()/from_dict()
        """
        self.store = JsonStore(filename)
        self.entity_class = entity_class

    def _to_entity(self, record: dict) -> Optional[T]:
        return self.entity_class.from_dict(record) if record else None

    def _to_entities(self, records: List[dict]) -> List[T]:
        return [self.entity_class.from_dict(r) for r in records]

    def get_by_id(self, id: str) -> Optional[T]:
        """Retrieve entity by ID"""
        return self._to_entity(self.store.get(id))

    def get_all(self, limit: Optional[int] = None) -> List[T]:
        """Retrieve all entities"""
        records = self.store.all()
        if limit:
            records = records[:limit]
        return self._to_entities(records)

    def filter_by(self, **kwargs) -> List[T]:
        """Filter entities by attribute equality"""
        def matches(record):
            return all(record.get(k) == v for k, v in kwargs.items())
        return self._to_entities([r for r in self.store.all() if matches(r)])

    def create(self, **kwargs) -> T:
        """Create new entity"""
        entity = self.entity_class(**kwargs)
        self.store.upsert(entity.to_dict())
        return entity

    def update(self, entity: T) -> T:
        """Persist an entity's current state (upsert by id)"""
        self.store.upsert(entity.to_dict())
        return entity

    def delete(self, entity: T) -> bool:
        """Delete entity"""
        return self.store.delete(entity.id)

    def delete_by_id(self, id: str) -> bool:
        """Delete entity by ID"""
        return self.store.delete(id)

    def count(self) -> int:
        """Count total entities"""
        return len(self.store.all())

    def exists(self, id: str) -> bool:
        """Check if entity exists"""
        return self.store.get(id) is not None
