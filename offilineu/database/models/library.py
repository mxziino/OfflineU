"""
Library model for managing courses and learning paths.
"""
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from ..connection import execute, fetch_one, fetch_all


class LibraryModel:
    """Model for library table operations."""
    
    @staticmethod
    def add(name: str, path: str, load_mode: str = 'course',
            total_lessons: int = 0, completed_lessons: int = 0, tags: Optional[List[str]] = None) -> int:
        """Add a new course/learning path to the library."""
        now = datetime.now().isoformat()
        tags_json = json.dumps(tags if tags else [])
        cursor = execute("""
            INSERT INTO library (name, path, load_mode, total_lessons, completed_lessons, tags, last_accessed, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                name = excluded.name,
                load_mode = excluded.load_mode,
                total_lessons = excluded.total_lessons,
                completed_lessons = excluded.completed_lessons,
                tags = excluded.tags,
                last_accessed = excluded.last_accessed,
                updated_at = excluded.updated_at
        """, (name, path, load_mode, total_lessons, completed_lessons, tags_json, now, now, now))
        return cursor.lastrowid
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all library items."""
        rows = fetch_all("""
            SELECT id, name, path, load_mode, total_lessons, completed_lessons, 
                   tags, last_accessed, created_at, updated_at
            FROM library
            ORDER BY last_accessed DESC NULLS LAST
        """)
        result = []
        for row in rows:
            item = dict(row)
            # Parse tags JSON
            try:
                item['tags'] = json.loads(item.get('tags', '[]'))
            except (json.JSONDecodeError, TypeError):
                item['tags'] = []
            result.append(item)
        return result
    
    @staticmethod
    def get_by_path(path: str) -> Optional[Dict[str, Any]]:
        """Get a library item by path."""
        row = fetch_one("SELECT * FROM library WHERE path = ?", (path,))
        return dict(row) if row else None
    
    @staticmethod
    def get_by_id(library_id: int) -> Optional[Dict[str, Any]]:
        """Get a library item by ID."""
        row = fetch_one("SELECT * FROM library WHERE id = ?", (library_id,))
        return dict(row) if row else None
    
    @staticmethod
    def remove(path: str) -> bool:
        """Remove a course from the library."""
        cursor = execute("DELETE FROM library WHERE path = ?", (path,))
        return cursor.rowcount > 0
    
    @staticmethod
    def update_progress(path: str, completed_lessons: int, total_lessons: int) -> bool:
        """Update the progress of a library item."""
        now = datetime.now().isoformat()
        cursor = execute("""
            UPDATE library 
            SET completed_lessons = ?, total_lessons = ?, updated_at = ?
            WHERE path = ?
        """, (completed_lessons, total_lessons, now, path))
        return cursor.rowcount > 0
    
    @staticmethod
    def update_last_accessed(path: str) -> bool:
        """Update the last accessed timestamp."""
        now = datetime.now().isoformat()
        cursor = execute("""
            UPDATE library SET last_accessed = ?, updated_at = ? WHERE path = ?
        """, (now, now, path))
        return cursor.rowcount > 0
    
    @staticmethod
    def update_tags(path: str, tags: List[str]) -> bool:
        """Update tags for a library item."""
        now = datetime.now().isoformat()
        tags_json = json.dumps(tags)
        cursor = execute("""
            UPDATE library SET tags = ?, updated_at = ? WHERE path = ?
        """, (tags_json, now, path))
        return cursor.rowcount > 0
    
    @staticmethod
    def get_all_tags() -> List[str]:
        """Get all unique tags from the library."""
        rows = fetch_all("SELECT tags FROM library WHERE tags IS NOT NULL AND tags != '[]'")
        all_tags = set()
        for row in rows:
            try:
                tags = json.loads(row['tags'])
                all_tags.update(tags)
            except (json.JSONDecodeError, TypeError):
                continue
        return sorted(list(all_tags))
    
    @staticmethod
    def count() -> int:
        """Get total count of library items."""
        row = fetch_one("SELECT COUNT(*) as count FROM library")
        return row['count'] if row else 0
