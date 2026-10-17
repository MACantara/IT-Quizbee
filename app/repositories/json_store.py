"""
JSON File Store
Persists a list of dict records to a single JSON file.
"""

import json
import os
import threading
from pathlib import Path
from typing import Callable, List, Optional


DEFAULT_STORE_DIR = Path(__file__).parent.parent.parent / 'instance'


class JsonStore:
    """
    Whole-collection JSON file store.

    shortcut: reads and rewrites the entire file on every write. Fine at
    classroom scale (hundreds of records); if attempts grow into the tens
    of thousands, switch to one file per record or SQLite.
    """

    _locks = {}
    _locks_guard = threading.Lock()

    def __init__(self, filename: str, store_dir: Optional[Path] = None):
        store_dir = store_dir or Path(
            os.getenv('QUIZBEE_STORE_DIR', DEFAULT_STORE_DIR)
        )
        self.path = Path(store_dir) / filename
        with self._locks_guard:
            self._lock = self._locks.setdefault(str(self.path), threading.Lock())

    def all(self) -> List[dict]:
        """Return every record, or [] if the file is missing/corrupt."""
        if not self.path.exists():
            return []
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def get(self, record_id: str) -> Optional[dict]:
        """Return the record with the given id, or None."""
        for record in self.all():
            if record.get('id') == record_id:
                return record
        return None

    def upsert(self, record: dict) -> dict:
        """Insert or replace a record matched by 'id'. Idempotent."""
        with self._lock:
            records = self.all()
            record_id = record.get('id')
            for i, existing in enumerate(records):
                if existing.get('id') == record_id:
                    records[i] = record
                    break
            else:
                records.append(record)
            self._write(records)
        return record

    def delete(self, record_id: str) -> bool:
        """Delete the record with the given id. True if something was removed."""
        with self._lock:
            records = self.all()
            remaining = [r for r in records if r.get('id') != record_id]
            if len(remaining) == len(records):
                return False
            self._write(remaining)
            return True

    def delete_where(self, predicate: Callable[[dict], bool]) -> int:
        """Delete every record matching predicate. Returns count removed."""
        with self._lock:
            records = self.all()
            remaining = [r for r in records if not predicate(r)]
            removed = len(records) - len(remaining)
            if removed:
                self._write(remaining)
            return removed

    def _write(self, records: List[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + '.tmp')
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)
