import mimetypes
import os

from flask import Blueprint, send_file

from offilineu.utils.current_course import get_current_course

files_bp = Blueprint("files", __name__)


@files_bp.route('/files/<path:filepath>')
def serve_file(filepath):
    """Serve course files"""
    current_course = get_current_course()

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
