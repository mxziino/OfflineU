"""
Progress Tracker - Handles progress tracking and persistence.
Now uses SQLite database with JSON file fallback for backward compatibility.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from offilineu.models.course import Course
from offilineu.models.directory_node import DirectoryNode
from offilineu.services.dynamic_course_parser import DynamicCourseParser
from offilineu.database import init_db
from offilineu.database.models.library import LibraryModel
from offilineu.database.models.lesson import LessonProgressModel
from offilineu.database.models.stats import DailyStatsModel

# Ensure database is initialized
_db_initialized = False


def _ensure_db():
    """Initialize database if not already done."""
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True


class ProgressTracker:
    """Handles progress tracking and persistence with database storage."""

    @staticmethod
    def _get_library_id(course_path: str) -> Optional[int]:
        """Get the library ID for a course path."""
        _ensure_db()
        item = LibraryModel.get_by_path(course_path)
        return item['id'] if item else None

    @staticmethod
    def load_progress(course: Course) -> Dict[str, Any]:
        """Load progress from database (with JSON fallback)."""
        _ensure_db()
        library_id = ProgressTracker._get_library_id(course.path)
        
        if library_id:
            # Load from database
            progress = {}
            rows = LessonProgressModel.get_by_library(library_id)
            for row in rows:
                progress[row['lesson_path']] = {
                    'completed': bool(row['completed']),
                    'progress_seconds': row['progress_seconds'],
                    'last_accessed': row['last_accessed']
                }
            
            # Get last accessed path from library
            item = LibraryModel.get_by_id(library_id)
            if item:
                # Find the most recently accessed lesson
                most_recent = None
                for row in rows:
                    if row['last_accessed']:
                        if most_recent is None or row['last_accessed'] > most_recent['last_accessed']:
                            most_recent = row
                if most_recent:
                    progress['last_accessed_path'] = most_recent['lesson_path']
            
            return progress
        
        # Fallback to JSON file
        try:
            with open(course.progress_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def save_progress(course: Course, progress_data: Dict[str, Any]):
        """Save progress to database (and JSON for backward compatibility)."""
        _ensure_db()
        library_id = ProgressTracker._get_library_id(course.path)
        
        if library_id:
            # Save each lesson to database
            for lesson_path, data in progress_data.items():
                if lesson_path == 'last_accessed_path':
                    continue
                if isinstance(data, dict):
                    LessonProgressModel.update_progress(
                        library_id=library_id,
                        lesson_path=lesson_path,
                        completed=data.get('completed', False),
                        progress_seconds=data.get('progress_seconds', 0)
                    )
        
        # Also save to JSON for backward compatibility
        try:
            with open(course.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            print(f"Error saving progress to JSON: {e}")

    @staticmethod
    def update_lesson_progress(course: Course, lesson_path: str, completed: bool = False, progress_seconds: int = 0):
        """Update progress for specific lesson."""
        _ensure_db()
        library_id = ProgressTracker._get_library_id(course.path)
        
        if library_id:
            # Save to database
            was_completed_before = LessonProgressModel.is_completed(library_id, lesson_path)
            LessonProgressModel.update_progress(library_id, lesson_path, completed, progress_seconds)
            
            # Update daily stats if newly completed
            if completed and not was_completed_before:
                DailyStatsModel.increment_lessons_completed()
            
            # Update library progress counts
            completed_count = LessonProgressModel.get_completed_count(library_id)
            item = LibraryModel.get_by_id(library_id)
            if item:
                LibraryModel.update_progress(course.path, completed_count, item['total_lessons'])
        
        # Also update JSON file
        progress = ProgressTracker.load_progress(course)
        progress[lesson_path] = {
            'completed': completed,
            'progress_seconds': progress_seconds,
            'last_accessed': datetime.now().isoformat()
        }
        progress['last_accessed_path'] = lesson_path
        ProgressTracker.save_progress(course, progress)

    @staticmethod
    def apply_progress_to_tree(course: Course):
        """Apply saved progress to the course tree."""
        progress = ProgressTracker.load_progress(course)

        def apply_to_node(node: DirectoryNode):
            for lesson in node.lessons:
                lesson_path = os.path.relpath(lesson.path, course.path)
                lesson_path = lesson_path.replace('\\', '/')
                if lesson_path.startswith('/'):
                    lesson_path = lesson_path[1:]

                lesson_path_with_title = f"{lesson_path}/{lesson.title.replace(' ', '_')}"

                if lesson_path in progress:
                    lesson.completed = progress[lesson_path].get('completed', False)
                    lesson.last_accessed = progress[lesson_path].get('last_accessed')
                    lesson.progress_seconds = progress[lesson_path].get('progress_seconds', 0)
                elif lesson_path_with_title in progress:
                    lesson.completed = progress[lesson_path_with_title].get('completed', False)
                    lesson.last_accessed = progress[lesson_path_with_title].get('last_accessed')
                    lesson.progress_seconds = progress[lesson_path_with_title].get('progress_seconds', 0)

            for child in node.children.values():
                apply_to_node(child)

        apply_to_node(course.root_node)
        course.last_accessed_path = progress.get('last_accessed_path')

    @staticmethod
    def get_completion_stats(course: Course) -> Dict[str, Any]:
        """Calculate completion statistics."""
        return DynamicCourseParser._calculate_completion_stats(course.root_node)
