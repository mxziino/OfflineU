"""
Lesson progress model for tracking individual lesson completion.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from ..connection import execute, fetch_one, fetch_all


class LessonProgressModel:
    """Model for lesson_progress table operations."""
    
    @staticmethod
    def get_or_create(library_id: int, lesson_path: str) -> Dict[str, Any]:
        """Get existing progress or create new entry."""
        row = fetch_one("""
            SELECT * FROM lesson_progress 
            WHERE library_id = ? AND lesson_path = ?
        """, (library_id, lesson_path))
        
        if row:
            return dict(row)
        
        # Create new entry
        now = datetime.now().isoformat()
        execute("""
            INSERT INTO lesson_progress (library_id, lesson_path, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (library_id, lesson_path, now, now))
        
        row = fetch_one("""
            SELECT * FROM lesson_progress 
            WHERE library_id = ? AND lesson_path = ?
        """, (library_id, lesson_path))
        return dict(row)
    
    @staticmethod
    def update_progress(library_id: int, lesson_path: str, 
                        completed: bool, progress_seconds: int = 0) -> bool:
        """Update lesson progress."""
        now = datetime.now().isoformat()
        completed_at = now if completed else None
        
        cursor = execute("""
            INSERT INTO lesson_progress (library_id, lesson_path, completed, progress_seconds, completed_at, last_accessed, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(library_id, lesson_path) DO UPDATE SET
                completed = excluded.completed,
                progress_seconds = excluded.progress_seconds,
                completed_at = CASE WHEN excluded.completed THEN COALESCE(lesson_progress.completed_at, excluded.completed_at) ELSE NULL END,
                last_accessed = excluded.last_accessed,
                updated_at = excluded.updated_at
        """, (library_id, lesson_path, completed, progress_seconds, completed_at, now, now, now))
        return cursor.rowcount > 0
    
    @staticmethod
    def mark_complete(library_id: int, lesson_path: str) -> bool:
        """Mark a lesson as complete."""
        return LessonProgressModel.update_progress(library_id, lesson_path, True)
    
    @staticmethod
    def mark_incomplete(library_id: int, lesson_path: str) -> bool:
        """Mark a lesson as incomplete."""
        return LessonProgressModel.update_progress(library_id, lesson_path, False)
    
    @staticmethod
    def get_by_library(library_id: int) -> List[Dict[str, Any]]:
        """Get all lesson progress for a library item."""
        rows = fetch_all("""
            SELECT * FROM lesson_progress 
            WHERE library_id = ?
            ORDER BY lesson_path
        """, (library_id,))
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_completed_count(library_id: int) -> int:
        """Get count of completed lessons for a library item."""
        row = fetch_one("""
            SELECT COUNT(*) as count FROM lesson_progress 
            WHERE library_id = ? AND completed = TRUE
        """, (library_id,))
        return row['count'] if row else 0
    
    @staticmethod
    def get_completion_history(days: int = 30) -> List[Dict[str, Any]]:
        """Get lesson completion history for the last N days."""
        rows = fetch_all("""
            SELECT DATE(completed_at) as date, COUNT(*) as count
            FROM lesson_progress
            WHERE completed = TRUE 
              AND completed_at >= DATE('now', '-' || ? || ' days')
            GROUP BY DATE(completed_at)
            ORDER BY date DESC
        """, (days,))
        return [dict(row) for row in rows]
    
    @staticmethod
    def is_completed(library_id: int, lesson_path: str) -> bool:
        """Check if a lesson is completed."""
        row = fetch_one("""
            SELECT completed FROM lesson_progress 
            WHERE library_id = ? AND lesson_path = ?
        """, (library_id, lesson_path))
        return row['completed'] if row else False
    
    @staticmethod
    def get_progress(library_id: int, lesson_path: str) -> Optional[Dict[str, Any]]:
        """Get progress for a specific lesson."""
        row = fetch_one("""
            SELECT * FROM lesson_progress 
            WHERE library_id = ? AND lesson_path = ?
        """, (library_id, lesson_path))
        return dict(row) if row else None
