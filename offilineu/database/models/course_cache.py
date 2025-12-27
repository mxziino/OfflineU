"""
Course cache model for storing and retrieving cached course structures.
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any
from ..connection import execute, fetch_one


class CourseCacheModel:
    """Model for course_cache table operations."""
    
    @staticmethod
    def get_cached(library_id: int) -> Optional[Dict[str, Any]]:
        """Get cached course data by library ID."""
        row = fetch_one("""
            SELECT * FROM course_cache WHERE library_id = ?
        """, (library_id,))
        
        if row:
            return {
                'id': row['id'],
                'library_id': row['library_id'],
                'course_name': row['course_name'],
                'course_path': row['course_path'],
                'root_node': json.loads(row['root_node_json']),
                'total_lessons': row['total_lessons'],
                'cached_at': row['cached_at'],
                'file_count': row['file_count']
            }
        return None
    
    @staticmethod
    def save_cache(library_id: int, course_name: str, course_path: str, 
                   root_node: Dict[str, Any], total_lessons: int, file_count: int = 0) -> int:
        """Save course structure to cache."""
        now = datetime.now().isoformat()
        root_node_json = json.dumps(root_node, ensure_ascii=False)
        
        cursor = execute("""
            INSERT INTO course_cache (library_id, course_name, course_path, root_node_json, total_lessons, cached_at, file_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(library_id) DO UPDATE SET
                course_name = excluded.course_name,
                course_path = excluded.course_path,
                root_node_json = excluded.root_node_json,
                total_lessons = excluded.total_lessons,
                cached_at = excluded.cached_at,
                file_count = excluded.file_count
        """, (library_id, course_name, course_path, root_node_json, total_lessons, now, file_count))
        return cursor.lastrowid
    
    @staticmethod
    def invalidate(library_id: int) -> bool:
        """Remove cache for a library item."""
        cursor = execute("DELETE FROM course_cache WHERE library_id = ?", (library_id,))
        return cursor.rowcount > 0
    
    @staticmethod
    def is_stale(library_id: int, max_age_hours: int = 24) -> bool:
        """Check if cache is older than max_age_hours."""
        row = fetch_one("""
            SELECT cached_at FROM course_cache WHERE library_id = ?
        """, (library_id,))
        
        if not row:
            return True
        
        cached_at = datetime.fromisoformat(row['cached_at'])
        age = datetime.now() - cached_at
        return age.total_seconds() > (max_age_hours * 3600)
