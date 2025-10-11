from flask import Blueprint, render_template, redirect, url_for

from offilineu.services.lesson_service import LessonService
from offilineu.services.progress_tracker import ProgressTracker
from offilineu.utils.current_course import get_current_course, set_current_course

lesson_bp = Blueprint("lesson", __name__)


@lesson_bp.route('/lesson/<path:lesson_path>')
def view_lesson(lesson_path: str):
    """View specific lesson by path"""

    if not get_current_course():
        return redirect(url_for('dashboard.index'))

    # Find the lesson in the tree
    lesson = LessonService.find_lesson_in_tree(get_current_course().root_node, lesson_path)

    if not lesson:
        return redirect(url_for('index'))

    # Get all lessons for navigation
    all_lessons = LessonService.get_all_lessons(get_current_course().root_node)
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
    ProgressTracker.update_lesson_progress(get_current_course(), lesson_path)

    return render_template('lesson_view.html',
                           course=get_current_course(),
                           lesson=lesson,
                           lesson_path=lesson_path,
                           prev_lesson=prev_lesson,
                           next_lesson=next_lesson)


@lesson_bp.route('/reset_course')
def reset_course():
    """Reset current course selection"""
    set_current_course(None)
    return redirect(url_for("dashboard.index"))
