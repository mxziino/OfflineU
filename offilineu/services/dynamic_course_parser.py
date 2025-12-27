import re
from pathlib import Path
from typing import Optional, Dict, Any

from offilineu.models.course import Course
from offilineu.models.directory_node import DirectoryNode
from offilineu.models.lesson import Lesson
from offilineu.utils.supported_extensions import *


class DynamicCourseParser:
    """Enhanced parser that builds a proper directory tree structure"""

    @staticmethod
    def scan_directory(course_path: str) -> Course:
        """Scan directory and build dynamic tree structure"""
        course_path = Path(course_path)
        if not course_path.exists() or not course_path.is_dir():
            raise ValueError(f"Invalid course path: {course_path}")

        course_name = course_path.name
        print(f"Scanning course: {course_name}")

        # Build the directory tree
        root_node = DynamicCourseParser._build_directory_tree(course_path, course_path)

        # Calculate completion statistics
        stats = DynamicCourseParser._calculate_completion_stats(root_node)

        progress_file = str(course_path / ".offlineu_progress.json")

        return Course(
            name=course_name,
            path=str(course_path),
            root_node=root_node,
            progress_file=progress_file
        )

    @staticmethod
    def _build_directory_tree(course_path: Path, current_path: Path, depth: int = 0) -> DirectoryNode:
        """Recursively build directory tree structure"""
        if depth > 10:  # Prevent infinite recursion
            return DirectoryNode(current_path.name, str(current_path), "directory")

        node_name = current_path.name if current_path != course_path else "Course Root"
        node = DirectoryNode(
            name=node_name,
            path=str(current_path),
            type="directory",
            order=depth
        )

        try:
            # Natural sort key: extract leading number for sorting
            def natural_sort_key(item):
                name = item.name
                # Try to extract leading number
                match = re.match(r'^(\d+)', name)
                num = int(match.group(1)) if match else 999999
                return (item.is_file(), num, name.lower())
            
            # Get all items in current directory with natural sorting
            items = sorted(current_path.iterdir(), key=natural_sort_key)

            for item in items:
                if item.name.startswith('.'):
                    continue

                if item.is_dir():
                    # Recursively process subdirectory
                    child_node = DynamicCourseParser._build_directory_tree(course_path, item, depth + 1)
                    if child_node.has_content or child_node.children:
                        node.children[child_node.name] = child_node
                        node.has_content = True

                elif item.is_file():
                    # Process file as potential lesson content
                    lesson = DynamicCourseParser._create_lesson_from_file(item, course_path)
                    if lesson:
                        # Add lesson directly to this node's lessons list
                        node.lessons.append(lesson)
                        node.has_content = True

        except (PermissionError, OSError) as e:
            print(f"Error accessing {current_path}: {e}")

        return node

    @staticmethod
    def _create_lesson_from_file(file_path: Path, course_path: Path) -> Optional[Lesson]:
        """Create a lesson from a single file"""
        ext = file_path.suffix.lower()
        filename = file_path.name.lower()

        # Skip non-content files
        if ext in {'.log', '.tmp', '.bak', '.swp', '.DS_Store', '.Thumbs.db'}:
            return None

        # Determine lesson type and files
        video_file = None
        audio_file = None
        subtitle_file = None
        text_files = []
        lesson_type = 'text'

        # Create relative path for file serving - normalize to forward slashes
        relative_path = str(file_path.relative_to(course_path)).replace('\\', '/')

        if ext in VIDEO_EXTENSIONS:
            video_file = relative_path
            lesson_type = 'video'
        elif ext in AUDIO_EXTENSIONS:
            audio_file = relative_path
            lesson_type = 'audio'
        elif ext in SUBTITLE_EXTENSIONS:
            subtitle_file = relative_path
            return None  # Don't create lessons for subtitle files alone
        elif ext in TEXT_EXTENSIONS:
            text_files.append(relative_path)
            if any(indicator in filename for indicator in QUIZ_INDICATORS):
                lesson_type = 'quiz'
        elif ext in ARCHIVE_EXTENSIONS:
            text_files.append(relative_path)
            lesson_type = 'text'  # Archives shown as downloadable resources
        else:
            # Skip unsupported file types
            return None

        # Clean up lesson name for display
        display_name = DynamicCourseParser._clean_lesson_name(file_path.stem)

        return Lesson(
            title=display_name,
            path=str(file_path),  # Store the actual file path, not just parent
            lesson_type=lesson_type,
            video_file=video_file,
            audio_file=audio_file,
            subtitle_file=subtitle_file,
            text_files=text_files,
            order=0
        )

    @staticmethod
    def _clean_lesson_name(name: str) -> str:
        """Clean up lesson name for display"""
        # Replace dashes/underscores with spaces (but keep leading numbers)
        name = re.sub(r'[-_]+', ' ', name)
        # Capitalize words
        name = ' '.join(word.capitalize() for word in name.split() if word)
        return name if name.strip() else "Untitled Lesson"

    @staticmethod
    def _calculate_completion_stats(node: DirectoryNode) -> Dict[str, Any]:
        """Calculate completion statistics for a directory node"""
        total_lessons = 0
        completed_lessons = 0

        def count_lessons_recursive(n: DirectoryNode):
            nonlocal total_lessons, completed_lessons

            # Count lessons in this node
            for lesson in n.lessons:
                total_lessons += 1
                if lesson.completed:
                    completed_lessons += 1

            # Recursively count in children
            for child in n.children.values():
                count_lessons_recursive(child)

        count_lessons_recursive(node)

        completion_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

        return {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'completion_percentage': round(completion_percentage, 1)
        }
