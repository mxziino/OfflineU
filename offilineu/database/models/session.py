"""
Study session model for tracking study time.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from ..connection import execute, fetch_one, fetch_all


class StudySessionModel:
    """Model for study_sessions table operations."""
    
    @staticmethod
    def start_session(library_id: int, lesson_path: str = None) -> int:
        """Start a new study session."""
        now = datetime.now().isoformat()
        cursor = execute("""
            INSERT INTO study_sessions (library_id, lesson_path, started_at)
            VALUES (?, ?, ?)
        """, (library_id, lesson_path, now))
        return cursor.lastrowid
    
    @staticmethod
    def end_session(session_id: int) -> bool:
        """End a study session and calculate duration."""
        now = datetime.now()
        
        # Get session start time
        row = fetch_one("SELECT started_at FROM study_sessions WHERE id = ?", (session_id,))
        if not row:
            return False
        
        started_at = datetime.fromisoformat(row['started_at'])
        duration = int((now - started_at).total_seconds())
        
        cursor = execute("""
            UPDATE study_sessions 
            SET ended_at = ?, duration_seconds = ?
            WHERE id = ?
        """, (now.isoformat(), duration, session_id))
        return cursor.rowcount > 0
    
    @staticmethod
    def get_today_duration() -> int:
        """Get total study duration for today in seconds."""
        row = fetch_one("""
            SELECT COALESCE(SUM(duration_seconds), 0) as total
            FROM study_sessions
            WHERE DATE(started_at) = DATE('now')
        """)
        return row['total'] if row else 0
    
    @staticmethod
    def get_duration_by_date(date: str) -> int:
        """Get total study duration for a specific date."""
        row = fetch_one("""
            SELECT COALESCE(SUM(duration_seconds), 0) as total
            FROM study_sessions
            WHERE DATE(started_at) = ?
        """, (date,))
        return row['total'] if row else 0
    
    @staticmethod
    def get_weekly_summary() -> List[Dict[str, Any]]:
        """Get study summary for the last 7 days."""
        rows = fetch_all("""
            SELECT DATE(started_at) as date, 
                   COALESCE(SUM(duration_seconds), 0) as total_seconds,
                   COUNT(*) as session_count
            FROM study_sessions
            WHERE started_at >= DATE('now', '-7 days')
            GROUP BY DATE(started_at)
            ORDER BY date DESC
        """)
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_active_session(library_id: int) -> Optional[Dict[str, Any]]:
        """Get an active (not ended) session for a library item."""
        row = fetch_one("""
            SELECT * FROM study_sessions 
            WHERE library_id = ? AND ended_at IS NULL
            ORDER BY started_at DESC
            LIMIT 1
        """, (library_id,))
        return dict(row) if row else None
