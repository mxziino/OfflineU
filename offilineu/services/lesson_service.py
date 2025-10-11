import os
from typing import Optional, Tuple, List

from offilineu.models.directory_node import DirectoryNode
from offilineu.models.lesson import Lesson
from offilineu.utils.current_course import get_current_course


class LessonService:

    @staticmethod
    def get_lesson_url(lesson: Lesson, course_path: str) -> str:
        """Generate the URL for a lesson"""
        # Create relative path from course root
        lesson_file_path = os.path.relpath(lesson.path, course_path)
        lesson_file_path = lesson_file_path.replace('\\', '/')
        if lesson_file_path.startswith('/'):
            lesson_file_path = lesson_file_path[1:]

        # Append lesson title for uniqueness
        lesson_url = f"{lesson_file_path}/{lesson.title.replace(' ', '_')}"
        return lesson_url

    @staticmethod
    def find_lesson_in_tree(node: DirectoryNode, target_path: str) -> Optional[Lesson]:
        """Find a lesson in the tree by path"""

        current_course = get_current_course()

        # Check lessons in current node
        for lesson in node.lessons:
            lesson_url = LessonService.get_lesson_url(lesson, current_course.path)

            # Check multiple possible path formats
            lesson_file_path = os.path.relpath(lesson.path, current_course.path)
            lesson_file_path = lesson_file_path.replace('\\', '/')
            if lesson_file_path.startswith('/'):
                lesson_file_path = lesson_file_path[1:]

            # Also check with lesson title appended
            lesson_path_with_title = f"{lesson_file_path}/{lesson.title.replace(' ', '_')}"

            if (lesson_url == target_path or
                    lesson_file_path == target_path or
                    lesson_path_with_title == target_path):
                return lesson

        # Recursively search children
        for child in node.children.values():
            result = LessonService.find_lesson_in_tree(child, target_path)
            if result:
                return result

        return None

    @staticmethod
    def get_all_lessons(node: DirectoryNode) -> List[Tuple[str, Lesson]]:
        """Get all lessons from the tree with their paths"""
        lessons = []
        current_course = get_current_course()

        def collect_lessons(n: DirectoryNode, current_path: str = ""):
            # Add lessons from this node
            for lesson in n.lessons:
                lesson_url = LessonService.get_lesson_url(lesson, current_course.path)
                lessons.append((lesson_url, lesson))

            # Recursively collect from children
            for child in n.children.values():
                collect_lessons(child, current_path)

        collect_lessons(node)
        return lessons
