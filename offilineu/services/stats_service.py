"""
Statistics Service - Provides analytics and statistics from the database.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from offilineu.database import init_db
from offilineu.database.models.stats import DailyStatsModel
from offilineu.database.models.lesson import LessonProgressModel
from offilineu.database.models.session import StudySessionModel
from offilineu.database.models.library import LibraryModel

# Ensure database is initialized
_db_initialized = False


def _ensure_db():
    """Initialize database if not already done."""
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True


def get_dashboard_stats() -> Dict[str, Any]:
    """Get statistics for the dashboard."""
    _ensure_db()
    
    # Get totals
    total_stats = DailyStatsModel.get_total_stats()
    
    # Get streak
    streak = DailyStatsModel.get_streak()
    
    # Get today's stats
    today = DailyStatsModel.get_or_create_today()
    
    # Get library count
    library_count = LibraryModel.count()
    
    return {
        'total_lessons_completed': total_stats['total_lessons'],
        'total_time_spent_seconds': total_stats['total_time'],
        'active_days': total_stats['active_days'],
        'current_streak': streak,
        'today_lessons_completed': today['lessons_completed'],
        'today_time_spent_seconds': today['time_spent_seconds'],
        'total_courses': library_count,
    }


def get_weekly_stats() -> List[Dict[str, Any]]:
    """Get daily stats for the last 7 days."""
    _ensure_db()
    return DailyStatsModel.get_last_n_days(7)


def get_monthly_stats() -> List[Dict[str, Any]]:
    """Get daily stats for the last 30 days."""
    _ensure_db()
    return DailyStatsModel.get_last_n_days(30)


def get_completion_history(days: int = 30) -> List[Dict[str, Any]]:
    """Get lesson completion history."""
    _ensure_db()
    return LessonProgressModel.get_completion_history(days)


def get_study_sessions(days: int = 7) -> List[Dict[str, Any]]:
    """Get study sessions for the last N days."""
    _ensure_db()
    return StudySessionModel.get_weekly_summary()


def record_time_spent(seconds: int) -> None:
    """Record time spent studying today."""
    _ensure_db()
    DailyStatsModel.add_time_spent(seconds)


def record_lesson_completed() -> None:
    """Record that a lesson was completed today."""
    _ensure_db()
    DailyStatsModel.increment_lessons_completed()


def get_streak() -> int:
    """Get current study streak."""
    _ensure_db()
    return DailyStatsModel.get_streak()


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
