import os
from pathlib import Path

from flask import Blueprint, request, jsonify

from offilineu.services.dynamic_course_parser import DynamicCourseParser
from offilineu.utils.current_course import get_current_course, set_current_course
from offilineu.utils.supported_extensions import VIDEO_EXTENSIONS, AUDIO_EXTENSIONS

browse_bp = Blueprint("browse", __name__)


@browse_bp.route('/browse')
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


@browse_bp.route('/load_course', methods=['POST'])
def load_course():
    data = request.json
    course_path = data.get('course_path')

    if not course_path or not os.path.exists(course_path):
        return jsonify({'error': 'Invalid course path'}), 400

    try:
        set_current_course(DynamicCourseParser.scan_directory(course_path))
        return jsonify({'success': True, 'course_name': get_current_course().name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
