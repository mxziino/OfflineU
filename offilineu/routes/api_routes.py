"""
API Routes for OfflineU React Frontend
All routes prefixed with /api/
"""

import os
from pathlib import Path
from flask import Blueprint, request, jsonify

from offilineu.services.dynamic_course_parser import DynamicCourseParser
from offilineu.services.progress_tracker import ProgressTracker
from offilineu.services.library_service import (get_library, add_to_library, remove_from_library,
                                                  update_library_tags, get_all_tags)
from offilineu.services.course_cache_service import load_course_cached
from offilineu.services.stats_service import (
    get_dashboard_stats, get_weekly_stats, get_monthly_stats,
    get_completion_history, get_streak
)
from offilineu.utils.current_course import get_current_course, set_current_course
from offilineu.utils.supported_extensions import VIDEO_EXTENSIONS, AUDIO_EXTENSIONS
from offilineu.models.directory_node import DirectoryNode

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ============================================
# Library endpoints
# ============================================

@api_bp.route('/library')
def get_library_courses():
    """Get course library with optional filtering"""
    search = request.args.get('search', '')
    tags = request.args.get('tags', '')
    
    items = get_library()
    
    # Filter by search query
    if search:
        search_lower = search.lower()
        items = [item for item in items if search_lower in item['name'].lower()]
    
    # Filter by tags (OR logic - match any of the provided tags)
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        if tag_list:
            items = [
                item for item in items 
                if any(tag in item.get('tags', []) for tag in tag_list)
            ]
    
    return jsonify(items)


@api_bp.route('/library', methods=['POST'])
def add_library_course():
    """Add course to library"""
    data = request.json
    name = data.get('name')
    path = data.get('path')
    load_mode = data.get('load_mode', 'course')
    total_lessons = data.get('total_lessons', 0)
    completed_lessons = data.get('completed_lessons', 0)
    
    if name and path:
        add_to_library(name, path, load_mode, total_lessons, completed_lessons)
        return jsonify({'success': True})
    return jsonify({'error': 'Missing name or path'}), 400


@api_bp.route('/library', methods=['DELETE'])
def remove_library_course():
    """Remove course from library"""
    data = request.json
    path = data.get('path')
    if path:
        remove_from_library(path)
        return jsonify({'success': True})
    return jsonify({'error': 'Missing path'}), 400


@api_bp.route('/library/tags', methods=['GET'])
def get_library_tags():
    """Get all available tags in the library"""
    return jsonify({'tags': get_all_tags()})


@api_bp.route('/library/tags', methods=['PUT'])
def update_library_item_tags():
    """Update tags for a library item"""
    data = request.json
    path = data.get('path')
    tags = data.get('tags', [])
    
    if not path:
        return jsonify({'error': 'Missing path'}), 400
    
    if not isinstance(tags, list):
        return jsonify({'error': 'Tags must be an array'}), 400
    
    update_library_tags(path, tags)
    return jsonify({'success': True})


@api_bp.route('/browse')
def browse_directories():
    """Browse directories for course selection"""
    path = request.args.get('path', '')

    try:
        # If no path specified, start with available drives on Windows
        if not path:
            import platform
            if platform.system() == 'Windows':
                import string
                drives = []
                for letter in string.ascii_uppercase:
                    drive = f"{letter}:\\"
                    if os.path.exists(drive):
                        drives.append({
                            'name': f"Drive {letter}:",
                            'path': drive,
                            'media_files': 0,
                            'is_course_candidate': False
                        })
                return jsonify({
                    'current_path': 'Select a Drive',
                    'parent_path': None,
                    'directories': drives
                })
            else:
                path = str(Path.home())

        current_path = Path(path)
        if not current_path.exists() or not current_path.is_dir():
            current_path = Path.home()

        directories = []
        try:
            for item in sorted(current_path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    try:
                        media_count = len([f for f in item.rglob('*')
                                           if f.suffix.lower() in VIDEO_EXTENSIONS | AUDIO_EXTENSIONS])

                        directories.append({
                            'name': item.name,
                            'path': str(item),
                            'media_files': media_count,
                            'is_course_candidate': media_count > 0
                        })
                    except (PermissionError, OSError):
                        directories.append({
                            'name': item.name + " (Access Denied)",
                            'path': str(item),
                            'media_files': 0,
                            'is_course_candidate': False
                        })
        except (PermissionError, OSError) as e:
            return jsonify({'error': f'Access denied to {current_path}'}), 403

        parent = None
        if current_path.parent != current_path:
            try:
                parent = str(current_path.parent)
            except (PermissionError, OSError):
                pass

        return jsonify({
            'current_path': str(current_path),
            'parent_path': parent,
            'directories': directories
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/course/load', methods=['POST'])
def load_course():
    """Load a course from path (uses cache for fast loading)"""
    data = request.json
    course_path = data.get('course_path')
    load_as = data.get('load_as', 'course')  # 'course' or 'learning_path'

    if not course_path:
        return jsonify({'error': 'No course path provided', 'success': False}), 400
    
    # Normalize path for Windows/Unix compatibility
    course_path = os.path.normpath(course_path)
    
    if not os.path.exists(course_path):
        return jsonify({'error': f'Path does not exist: {course_path}', 'success': False}), 400

    try:
        # Use cached loading for instant response
        course = load_course_cached(course_path)
        if course:
            set_current_course(course)
            return jsonify({
                'success': True, 
                'course_name': course.name,
                'is_learning_path': load_as == 'learning_path'
            })
        else:
            return jsonify({'error': 'Failed to load course', 'success': False}), 500
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@api_bp.route('/course/info')
def get_course_info():
    """Get current course info and tree structure"""
    current_course = get_current_course()
    
    if not current_course:
        return jsonify(None), 404

    ProgressTracker.apply_progress_to_tree(current_course)
    stats = ProgressTracker.get_completion_stats(current_course)
    stats['last_accessed_path'] = current_course.last_accessed_path

    return jsonify({
        'course': course_to_dict(current_course),
        'stats': stats
    })


@api_bp.route('/course/reset', methods=['POST'])
def reset_course():
    """Reset current course selection"""
    set_current_course(None)
    return jsonify({'success': True})


@api_bp.route('/lesson/<path:lesson_path>')
def get_lesson(lesson_path: str):
    """Get lesson details by path"""
    current_course = get_current_course()
    
    if not current_course:
        return jsonify({'error': 'No course loaded'}), 400

    ProgressTracker.apply_progress_to_tree(current_course)
    
    # Find the lesson in the tree
    lesson = find_lesson_by_path(current_course.root_node, lesson_path)
    
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404

    # Get prev/next lessons
    all_lessons = get_all_lessons(current_course.root_node, current_course.path)
    current_index = -1
    for i, (path, _) in enumerate(all_lessons):
        if lesson_path in path or path in lesson_path:
            current_index = i
            break

    prev_lesson = all_lessons[current_index - 1][0] if current_index > 0 else None
    next_lesson = all_lessons[current_index + 1][0] if current_index < len(all_lessons) - 1 else None

    return jsonify({
        'lesson': lesson_to_dict(lesson),
        'course_name': current_course.name,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson
    })


def course_to_dict(course):
    """Convert course to JSON-serializable dict"""
    return {
        'name': course.name,
        'path': course.path,
        'root_node': node_to_dict(course.root_node),
        'progress_file': course.progress_file,
        'last_accessed_path': course.last_accessed_path
    }


def node_to_dict(node: DirectoryNode):
    """Convert directory node to JSON-serializable dict"""
    return {
        'name': node.name,
        'path': node.path,
        'type': node.type,
        'has_content': node.has_content,
        'children': {name: node_to_dict(child) for name, child in node.children.items()},
        'lessons': [lesson_to_dict(lesson) for lesson in node.lessons]
    }


def lesson_to_dict(lesson):
    """Convert lesson to JSON-serializable dict"""
    return {
        'title': lesson.title,
        'path': lesson.path,
        'lesson_type': lesson.lesson_type,
        'video_file': lesson.video_file,
        'audio_file': lesson.audio_file,
        'subtitle_file': lesson.subtitle_file,
        'text_files': lesson.text_files,
        'completed': lesson.completed,
        'progress_seconds': lesson.progress_seconds
    }


def find_lesson_by_path(node: DirectoryNode, search_path: str):
    """Find a lesson by path in the tree"""
    current_course = get_current_course()
    
    # Normalize search path
    normalized_search = search_path.replace('\\', '/').strip('/')
    
    for lesson in node.lessons:
        # Build the full expected path for this lesson (same format as frontend)
        relative_path = lesson.path.replace(current_course.path, '').replace('\\', '/').strip('/')
        full_path = f"{relative_path}/{lesson.title.replace(' ', '_')}"
        
        # Debug logging (disabled)
        # print(f"Comparing: '{full_path}' vs '{normalized_search}'")
        
        # Normalized match comparison
        if full_path == normalized_search:
            return lesson
    
    for child in node.children.values():
        result = find_lesson_by_path(child, search_path)
        if result:
            return result
    
    return None


def get_all_lessons(node: DirectoryNode, course_path: str):
    """Get all lessons in order as list of (path, lesson) tuples"""
    lessons = []
    
    for lesson in node.lessons:
        relative_path = lesson.path.replace(course_path, '').replace('\\', '/').lstrip('/')
        full_path = f"{relative_path}/{lesson.title.replace(' ', '_')}"
        lessons.append((full_path, lesson))
    
    for child in node.children.values():
        lessons.extend(get_all_lessons(child, course_path))
    
    return lessons


# ============================================
# Statistics endpoints
# ============================================

@api_bp.route('/stats/dashboard')
def get_stats_dashboard():
    """Get dashboard statistics summary."""
    try:
        stats = get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/stats/weekly')
def get_stats_weekly():
    """Get weekly statistics."""
    try:
        stats = get_weekly_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/stats/monthly')
def get_stats_monthly():
    """Get monthly statistics."""
    try:
        stats = get_monthly_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/stats/history')
def get_stats_history():
    """Get lesson completion history."""
    days = request.args.get('days', 30, type=int)
    try:
        history = get_completion_history(days)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/stats/streak')
def get_stats_streak():
    """Get current study streak."""
    try:
        streak = get_streak()
        return jsonify({'streak': streak})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
