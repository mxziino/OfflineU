"""
Notes Service - Manages lesson notes with optional Obsidian vault integration.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from offilineu.database import init_db
from offilineu.database.models.lesson_notes import LessonNotesModel
from offilineu.database.models.library import LibraryModel

# Ensure database is initialized
_db_initialized = False


def _ensure_db():
    """Initialize database if not already done."""
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True


def get_note(course_path: str, lesson_path: str) -> Optional[Dict[str, Any]]:
    """Get note for a specific lesson."""
    _ensure_db()
    
    # Get library_id from course path
    library_item = LibraryModel.get_by_path(course_path)
    if not library_item:
        return None
    
    return LessonNotesModel.get_note(library_item['id'], lesson_path)


def save_note(course_path: str, lesson_path: str, content: str, obsidian_vault_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Save or update a note for a lesson.
    Optionally syncs to Obsidian vault if path is provided.
    """
    _ensure_db()
    
    # Get library_id from course path
    library_item = LibraryModel.get_by_path(course_path)
    if not library_item:
        raise ValueError(f"Course not found: {course_path}")
    
    # Save to database
    LessonNotesModel.save_note(library_item['id'], lesson_path, content)
    
    # Optionally sync to Obsidian vault
    if obsidian_vault_path:
        sync_to_obsidian(library_item['name'], lesson_path, content, obsidian_vault_path)
    
    return {'success': True, 'synced_to_vault': bool(obsidian_vault_path)}


def delete_note(course_path: str, lesson_path: str) -> bool:
    """Delete a note for a lesson."""
    _ensure_db()
    
    # Get library_id from course path
    library_item = LibraryModel.get_by_path(course_path)
    if not library_item:
        return False
    
    return LessonNotesModel.delete_note(library_item['id'], lesson_path)


def sync_to_obsidian(course_name: str, lesson_path: str, content: str, vault_path: str):
    """
    Write note to Obsidian vault as markdown file.
    
    File structure: {vault_path}/OfflineU/{course_name}/{lesson_title}.md
    """
    # Sanitize names for filesystem
    safe_course_name = _sanitize_filename(course_name)
    safe_lesson_name = _sanitize_filename(Path(lesson_path).stem)
    
    # Build file path
    notes_dir = Path(vault_path) / "OfflineU" / safe_course_name
    notes_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = notes_dir / f"{safe_lesson_name}.md"
    
    # Write markdown file
    with open(file_path, 'w', encoding='utf-8') as f:
        # Add frontmatter for Obsidian
        f.write(f"---\n")
        f.write(f"course: {course_name}\n")
        f.write(f"lesson: {lesson_path}\n")
        f.write(f"---\n\n")
        f.write(content)


def _sanitize_filename(name: str) -> str:
    """Sanitize a string to be safe for use as a filename."""
    # Remove or replace characters that are invalid in filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    # Remove leading/trailing spaces and dots
    name = name.strip('. ')
    return name or 'unnamed'
