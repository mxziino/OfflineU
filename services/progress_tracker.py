import json
import os
from datetime import datetime
from typing import Dict, Any

from models.course import Course
from models.directory_node import DirectoryNode
from services.dynamic_course_parser import DynamicCourseParser


class ProgressTracker:
    """Handles progress tracking and persistence"""

    @staticmethod
    def load_progress(course: Course) -> Dict[str, Any]:
        """Load progress from JSON file"""
        try:
            with open(course.progress_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def save_progress(course: Course, progress_data: Dict[str, Any]):
        """Save progress to JSON file"""
        try:
            with open(course.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            print(f"Error saving progress: {e}")

    @staticmethod
    def update_lesson_progress(course: Course, lesson_path: str, completed: bool = False, progress_seconds: int = 0):
        """Update progress for specific lesson by path"""
        progress = ProgressTracker.load_progress(course)

        progress[lesson_path] = {
            'completed': completed,
            'progress_seconds': progress_seconds,
            'last_accessed': datetime.now().isoformat()
        }

        # Update last accessed path
        progress['last_accessed_path'] = lesson_path

        ProgressTracker.save_progress(course, progress)

    @staticmethod
    def apply_progress_to_tree(course: Course):
        """Apply saved progress to the course tree"""
        progress = ProgressTracker.load_progress(course)

        def apply_to_node(node: DirectoryNode):
            # Apply progress to lessons in this node
            for lesson in node.lessons:
                lesson_path = os.path.relpath(lesson.path, course.path)
                lesson_path = lesson_path.replace('\\', '/')
                if lesson_path.startswith('/'):
                    lesson_path = lesson_path[1:]

                # Check both the base path and path with title
                lesson_path_with_title = f"{lesson_path}/{lesson.title.replace(' ', '_')}"

                if lesson_path in progress:
                    lesson.completed = progress[lesson_path].get('completed', False)
                    lesson.last_accessed = progress[lesson_path].get('last_accessed')
                    lesson.progress_seconds = progress[lesson_path].get('progress_seconds', 0)
                elif lesson_path_with_title in progress:
                    lesson.completed = progress[lesson_path_with_title].get('completed', False)
                    lesson.last_accessed = progress[lesson_path_with_title].get('last_accessed')
                    lesson.progress_seconds = progress[lesson_path_with_title].get('progress_seconds', 0)

            # Recursively apply to children
            for child in node.children.values():
                apply_to_node(child)

        apply_to_node(course.root_node)
        course.last_accessed_path = progress.get('last_accessed_path')

    @staticmethod
    def get_completion_stats(course: Course) -> Dict[str, Any]:
        """Calculate completion statistics"""
        return DynamicCourseParser._calculate_completion_stats(course.root_node)
