"""
Lesson Notes model for managing markdown notes per lesson.
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any
from ..connection import execute, fetch_one, fetch_all


class LessonNotesModel:
    """Model for lesson_notes table operations."""
    
    @staticmethod
    def get_note(library_id: int, lesson_path: str) -> Optional[Dict[str, Any]]:
        """Get note for a specific lesson."""
        row = fetch_one("""
            SELECT id, library_id, lesson_path, content, created_at, updated_at
            FROM lesson_notes
            WHERE library_id = ? AND lesson_path = ?
        """, (library_id, lesson_path))
        return dict(row) if row else None
    
    @staticmethod
    def save_note(library_id: int, lesson_path: str, content: str) -> int:
        """Save or update a note for a lesson."""
        now = datetime.now().isoformat()
        cursor = execute("""
            INSERT INTO lesson_notes (library_id, lesson_path, content, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(library_id, lesson_path) DO UPDATE SET
                content = excluded.content,
                updated_at = excluded.updated_at
        """, (library_id, lesson_path, content, now, now))
        return cursor.lastrowid
    
    @staticmethod
    def delete_note(library_id: int, lesson_path: str) -> bool:
        """Delete a note for a lesson."""
        cursor = execute("""
            DELETE FROM lesson_notes
            WHERE library_id = ? AND lesson_path = ?
        """, (library_id, lesson_path))
        return cursor.rowcount > 0
    
    @staticmethod
    def get_all_notes_for_course(library_id: int) -> list[Dict[str, Any]]:
        """Get all notes for a specific course."""
        rows = fetch_all("""
            SELECT id, library_id, lesson_path, content, created_at, updated_at
            FROM lesson_notes
            WHERE library_id = ?
            ORDER BY updated_at DESC
        """, (library_id,))
        return [dict(row) for row in rows]
