"""
Course Library Service - Stores courses and learning paths in SQLite database.
Migrated from JSON file storage for better performance and analytics support.
"""

from typing import List, Dict, Any, Optional
from offilineu.database import init_db
from offilineu.database.models.library import LibraryModel

# Ensure database is initialized
_db_initialized = False


def _ensure_db():
    """Initialize database if not already done."""
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True


def get_library() -> List[Dict[str, Any]]:
    """Get the course library from database."""
    _ensure_db()
    return LibraryModel.get_all()


def add_to_library(name: str, path: str, load_mode: str = 'course', 
                   total_lessons: int = 0, completed_lessons: int = 0, tags: Optional[List[str]] = None) -> None:
    """Add a course to the library (or update if exists)."""
    _ensure_db()
    LibraryModel.add(name, path, load_mode, total_lessons, completed_lessons, tags)


def update_library_progress(path: str, completed_lessons: int, total_lessons: int) -> None:
    """Update progress for alibrary item."""
    _ensure_db()
    LibraryModel.update_progress(path, completed_lessons, total_lessons)


def remove_from_library(path: str) -> None:
    """Remove a course from the library."""
    _ensure_db()
    LibraryModel.remove(path)


def get_library_item(path: str) -> Optional[Dict[str, Any]]:
    """Get a specific library item by path."""
    _ensure_db()
    return LibraryModel.get_by_path(path)


def update_last_accessed(path: str) -> None:
    """Update the last accessed timestamp for a library item."""
    _ensure_db()
    LibraryModel.update_last_accessed(path)


def update_library_tags(path: str, tags: List[str]) -> None:
    """Update tags for a library item."""
    _ensure_db()
    LibraryModel.update_tags(path, tags)


def get_all_tags() -> List[str]:
    """Get all unique tags from the library."""
    _ensure_db()
    return LibraryModel.get_all_tags()
