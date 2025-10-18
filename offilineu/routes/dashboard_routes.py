import os

from flask import Blueprint, render_template

from offilineu.services.progress_tracker import ProgressTracker
from offilineu.utils.current_course import get_current_course

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route('/')
def index():
    """Main dashboard"""
    current_course = get_current_course()
    courses_directory = os.environ.get("COURSES_PATH")
    if current_course is None:
        # Show dashboard with course selection option
        return render_template('course_dashboard.html',
                               course=None,
                               courses_directory=courses_directory,
                               stats={'total_lessons': 0, 'completed_lessons': 0, 'completion_percentage': 0})

    # Apply progress data to tree
    ProgressTracker.apply_progress_to_tree(current_course)
    stats = ProgressTracker.get_completion_stats(current_course)

    return render_template('course_dashboard.html',
                           course=current_course,
                           stats=stats)
