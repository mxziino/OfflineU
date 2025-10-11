#!/usr/bin/env python3
"""
OfflineU - Self-hosted Course Viewer & Tracker
Enhanced version with dynamic subdirectory navigation
"""

import argparse
import mimetypes
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for

from models.directory_node import DirectoryNode
from models.lesson import Lesson
from services.dynamic_course_parser import DynamicCourseParser
from services.progress_tracker import ProgressTracker
from utils.create_templates import CreateTemplates
from utils.supported_extensions import AUDIO_EXTENSIONS, VIDEO_EXTENSIONS

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "my-super-secret-key")

# Global course storage
current_course = None


@app.route('/')
def index():
    """Main dashboard"""
    global current_course

    if current_course is None:
        # Show dashboard with course selection option
        return render_template('course_dashboard.html',
                               course=None,
                               stats={'total_lessons': 0, 'completed_lessons': 0, 'completion_percentage': 0})

    # Apply progress data to tree
    ProgressTracker.apply_progress_to_tree(current_course)
    stats = ProgressTracker.get_completion_stats(current_course)

    return render_template('course_dashboard.html',
                           course=current_course,
                           stats=stats)


@app.route('/browse')
def browse_directories():
    """Browse directories for course selection"""
    path = request.args.get('path', '')
    
    try:
        # If no path specified, start with available drives on Windows
        if not path:
            import platform
            if platform.system() == 'Windows':
                # Get available drives on Windows
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
                print(f"Returning {len(drives)} drives")
                return jsonify({
                    'current_path': 'Select a Drive',
                    'parent_path': None,
                    'directories': drives
                })
            else:
                # On other systems, start from home directory
                path = str(Path.home())

        current_path = Path(path)
        if not current_path.exists() or not current_path.is_dir():
            # Fallback to home directory if path doesn't exist
            current_path = Path.home()

        print(f"Browsing directory: {current_path}")

        # Get directories and basic info
        directories = []
        try:
            for item in sorted(current_path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    try:
                        # Check if this looks like a course directory
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
            print(f"Access denied to {current_path}: {str(e)}")
            return jsonify({'error': f'Access denied to {current_path}: {str(e)}'}), 403

        # Determine parent path
        parent = None
        if current_path.parent != current_path:
            try:
                parent = str(current_path.parent)
            except (PermissionError, OSError):
                pass

        print(f"Found {len(directories)} directories")
        return jsonify({
            'current_path': str(current_path),
            'parent_path': parent,
            'directories': directories
        })

    except Exception as e:
        print(f"Error in browse_directories: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/load_course', methods=['POST'])
def load_course():
    """Load course from selected directory"""
    global current_course

    data = request.json
    course_path = data.get('course_path')

    if not course_path or not os.path.exists(course_path):
        return jsonify({'error': 'Invalid course path'}), 400

    try:
        current_course = DynamicCourseParser.scan_directory(course_path)
        return jsonify({'success': True, 'course_name': current_course.name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/lesson/<path:lesson_path>')
def view_lesson(lesson_path: str):
    """View specific lesson by path"""
    global current_course

    if not current_course:
        return redirect(url_for('index'))

    # Find the lesson in the tree
    lesson = find_lesson_in_tree(current_course.root_node, lesson_path)
    
    if not lesson:
        return redirect(url_for('index'))

    # Get all lessons for navigation
    all_lessons = get_all_lessons(current_course.root_node)
    current_index = -1
    
    # Find current lesson index
    for i, (path, lesson_obj) in enumerate(all_lessons):
        if lesson_obj == lesson:
            current_index = i
            break
    
    # Get next and previous lessons
    prev_lesson = None
    next_lesson = None
    
    if current_index > 0:
        prev_lesson = all_lessons[current_index - 1][0]
    
    if current_index < len(all_lessons) - 1:
        next_lesson = all_lessons[current_index + 1][0]

    # Update last accessed
    ProgressTracker.update_lesson_progress(current_course, lesson_path)

    return render_template('lesson_view.html',
                           course=current_course,
                           lesson=lesson,
                           lesson_path=lesson_path,
                           prev_lesson=prev_lesson,
                           next_lesson=next_lesson)


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


def find_lesson_in_tree(node: DirectoryNode, target_path: str) -> Optional[Lesson]:
    """Find a lesson in the tree by path"""
    # Check lessons in current node
    for lesson in node.lessons:
        lesson_url = get_lesson_url(lesson, current_course.path)
        
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
        result = find_lesson_in_tree(child, target_path)
        if result:
            return result
    
    return None


def get_all_lessons(node: DirectoryNode) -> List[Tuple[str, Lesson]]:
    """Get all lessons from the tree with their paths"""
    lessons = []
    
    def collect_lessons(n: DirectoryNode, current_path: str = ""):
        # Add lessons from this node
        for lesson in n.lessons:
            lesson_url = get_lesson_url(lesson, current_course.path)
            lessons.append((lesson_url, lesson))
        
        # Recursively collect from children
        for child in n.children.values():
            collect_lessons(child, current_path)
    
    collect_lessons(node)
    return lessons


@app.route('/api/progress', methods=['POST'])
def update_progress():
    """API endpoint to update lesson progress"""
    global current_course

    if not current_course:
        return jsonify({'error': 'No course loaded'}), 400

    data = request.json
    lesson_path = data.get('lesson_path')
    completed = data.get('completed', False)
    progress_seconds = data.get('progress_seconds', 0)

    try:
        ProgressTracker.update_lesson_progress(
            current_course, lesson_path, completed, progress_seconds
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/files/<path:filepath>')
def serve_file(filepath):
    """Serve course files"""
    global current_course

    if not current_course:
        return "No course loaded", 404

    # Security: ensure file is within course directory
    try:
        # URL decode the filepath and normalize it
        from urllib.parse import unquote
        decoded_filepath = unquote(filepath)
        
        # Construct the full path relative to the course directory
        full_path = os.path.join(current_course.path, decoded_filepath)
        full_path = os.path.abspath(full_path)
        course_path = os.path.abspath(current_course.path)

        print(f"File request: {filepath}")
        print(f"Decoded filepath: {decoded_filepath}")
        print(f"Full path: {full_path}")
        print(f"Course path: {course_path}")

        # Security check: ensure file is within course directory
        if not full_path.startswith(course_path):
            print(f"Access denied: {full_path} not in {course_path}")
            return "Access denied", 403

        if not os.path.exists(full_path):
            print(f"File not found: {full_path}")
            return "File not found", 404

        print(f"Serving file: {full_path}")

        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(full_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        return send_file(full_path, mimetype=mime_type)
    except Exception as e:
        print(f"Error serving file: {str(e)}")
        return f"Error serving file: {str(e)}", 500

@app.route('/health')
def healthcheck():
    """Healthcheck endpoint for Docker"""
    return jsonify({"status": "healthy"}), 200

@app.route('/reset_course')
def reset_course():
    """Reset current course selection"""
    global current_course
    current_course = None
    return redirect(url_for('index'))





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OfflineU Course Viewer & Tracker')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--create-templates', action='store_true', help='Create basic templates')
    parser.add_argument('course_path', nargs='?', help='Path to course directory')

    args = parser.parse_args()

    # Create templates if requested
    if args.create_templates:
        CreateTemplates.create()
        print("Templates created successfully!")
        if not args.course_path:
            sys.exit(0)

    # Autoload course if provided
    if args.course_path or os.environ.get('AUTO_LOAD_COURSE'):
        course_path = args.course_path or os.environ.get('AUTO_LOAD_COURSE')

        if not os.path.exists(course_path):
            print(f"Error: Course path does not exist: {course_path}", file=sys.stderr)
            sys.exit(1)

        try:
            current_course = DynamicCourseParser.scan_directory(course_path)
            print(f"Auto-loaded course: {current_course.name}")
            print(f"Built dynamic directory tree with {len(current_course.root_node.children)} top-level items")
        except Exception as e:
            print(f"Error loading course: {e}", file=sys.stderr)
            if args.debug:
                import traceback

                traceback.print_exc()
            sys.exit(1)

    # Create templates directory if it doesn't exist
    if not Path('templates').exists():
        print("Templates directory not found. Creating basic templates...")
        CreateTemplates.create()

    print(f"Starting OfflineU on http://{args.host}:{args.port}")
    print("Use --create-templates to regenerate template files")

    try:
        app.run(debug=args.debug, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nShutting down OfflineU...")
    except Exception as e:
        print(f"Error starting server: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)
