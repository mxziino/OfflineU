"""
Daily statistics model for aggregated analytics.
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from ..connection import execute, fetch_one, fetch_all


class DailyStatsModel:
    """Model for daily_stats table operations."""
    
    @staticmethod
    def get_or_create_today() -> Dict[str, Any]:
        """Get or create today's stats entry."""
        today = date.today().isoformat()
        
        row = fetch_one("SELECT * FROM daily_stats WHERE date = ?", (today,))
        if row:
            return dict(row)
        
        # Create new entry
        execute("""
            INSERT INTO daily_stats (date, lessons_completed, time_spent_seconds, courses_accessed)
            VALUES (?, 0, 0, 0)
        """, (today,))
        
        row = fetch_one("SELECT * FROM daily_stats WHERE date = ?", (today,))
        return dict(row)
    
    @staticmethod
    def increment_lessons_completed(count: int = 1) -> bool:
        """Increment today's completed lessons count."""
        today = date.today().isoformat()
        DailyStatsModel.get_or_create_today()  # Ensure today exists
        
        cursor = execute("""
            UPDATE daily_stats 
            SET lessons_completed = lessons_completed + ?
            WHERE date = ?
        """, (count, today))
        return cursor.rowcount > 0
    
    @staticmethod
    def add_time_spent(seconds: int) -> bool:
        """Add time to today's time spent."""
        today = date.today().isoformat()
        DailyStatsModel.get_or_create_today()
        
        cursor = execute("""
            UPDATE daily_stats 
            SET time_spent_seconds = time_spent_seconds + ?
            WHERE date = ?
        """, (seconds, today))
        return cursor.rowcount > 0
    
    @staticmethod
    def increment_courses_accessed() -> bool:
        """Increment today's courses accessed count."""
        today = date.today().isoformat()
        DailyStatsModel.get_or_create_today()
        
        cursor = execute("""
            UPDATE daily_stats 
            SET courses_accessed = courses_accessed + 1
            WHERE date = ?
        """, (today,))
        return cursor.rowcount > 0
    
    @staticmethod
    def get_last_n_days(days: int = 30) -> List[Dict[str, Any]]:
        """Get stats for the last N days."""
        rows = fetch_all("""
            SELECT * FROM daily_stats
            WHERE date >= DATE('now', '-' || ? || ' days')
            ORDER BY date DESC
        """, (days,))
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_streak() -> int:
        """Calculate current study streak (consecutive days with activity)."""
        rows = fetch_all("""
            SELECT date FROM daily_stats
            WHERE lessons_completed > 0 OR time_spent_seconds > 0
            ORDER BY date DESC
        """)
        
        if not rows:
            return 0
        
        streak = 0
        expected_date = date.today()
        
        for row in rows:
            row_date = date.fromisoformat(row['date'])
            if row_date == expected_date:
                streak += 1
                expected_date = date.fromordinal(expected_date.toordinal() - 1)
            elif row_date < expected_date:
                break
        
        return streak
    
    @staticmethod
    def get_total_stats() -> Dict[str, Any]:
        """Get all-time statistics."""
        row = fetch_one("""
            SELECT 
                COALESCE(SUM(lessons_completed), 0) as total_lessons,
                COALESCE(SUM(time_spent_seconds), 0) as total_time,
                COUNT(*) as active_days
            FROM daily_stats
            WHERE lessons_completed > 0 OR time_spent_seconds > 0
        """)
        return dict(row) if row else {'total_lessons': 0, 'total_time': 0, 'active_days': 0}
