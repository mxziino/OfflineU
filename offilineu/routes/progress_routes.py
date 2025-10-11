from flask import Blueprint, jsonify, request

from offilineu.services.progress_tracker import ProgressTracker
from offilineu.utils.current_course import get_current_course

progress_bp = Blueprint("progress", __name__)


@progress_bp.route('/api/progress', methods=['POST'])
def update_progress():
    """API endpoint to update lesson progress"""
    current_course = get_current_course()

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


@progress_bp.route('/health')
def healthcheck():
    """Healthcheck endpoint for Docker"""
    return jsonify({"status": "healthy"}), 200
