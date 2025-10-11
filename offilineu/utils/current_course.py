from threading import Lock

_current_course = None
_current_course_lock = Lock()


def get_current_course():
    """Get the current course (thread safe)"""
    with _current_course_lock:
        return _current_course


def set_current_course(value):
    """Set the current course (thread safe)"""
    with _current_course_lock:
        global _current_course
        _current_course = value
