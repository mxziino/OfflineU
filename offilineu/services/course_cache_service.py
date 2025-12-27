"""
Course Cache Service - Manages course structure caching for fast loading.
"""
from typing import Optional
from offilineu.models.course import Course
from offilineu.models.directory_node import DirectoryNode
from offilineu.services.dynamic_course_parser import DynamicCourseParser
from offilineu.services.progress_tracker import ProgressTracker
from offilineu.database import init_db
from offilineu.database.models.library import LibraryModel
from offilineu.database.models.course_cache import CourseCacheModel

# Ensure database is initialized
_db_initialized = False


def _ensure_db():
    """Initialize database if not already done."""
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True


def load_course_cached(course_path: str, force_rescan: bool = False) -> Optional[Course]:
    """
    Load a course, using cache if available.
    
    Args:
        course_path: Path to the course directory
        force_rescan: If True, always rescan the filesystem
        
    Returns:
        Course object with structure loaded from cache or filesystem
    """
    _ensure_db()
    
    # Get library item
    library_item = LibraryModel.get_by_path(course_path)
    if not library_item:
        # Course not in library, must scan fresh
        print(f"Course not in library, scanning: {course_path}")
        return _scan_and_cache(course_path, None)
    
    library_id = library_item['id']
    
    # Check cache
    if not force_rescan:
        cached = CourseCacheModel.get_cached(library_id)
        if cached:
            print(f"Loading from cache: {cached['course_name']}")
            # Reconstruct Course from cache
            root_node = DirectoryNode.from_dict(cached['root_node'])
            course = Course(
                name=cached['course_name'],
                path=cached['course_path'],
                root_node=root_node,
                progress_file=f"{cached['course_path']}/.offlineu_progress.json"
            )
            # Apply progress from database
            ProgressTracker.apply_progress_to_tree(course)
            return course
    
    # No cache or forced rescan
    print(f"Scanning filesystem: {course_path}")
    return _scan_and_cache(course_path, library_id)


def _scan_and_cache(course_path: str, library_id: Optional[int]) -> Optional[Course]:
    """Scan course from filesystem and cache the result."""
    try:
        course = DynamicCourseParser.scan_directory(course_path)
        
        # Calculate stats
        stats = DynamicCourseParser._calculate_completion_stats(course.root_node)
        total_lessons = stats.get('total_lessons', 0)
        
        # Get or create library entry
        if library_id is None:
            library_id = LibraryModel.add(
                name=course.name,
                path=course_path,
                load_mode='course',
                total_lessons=total_lessons
            )
            # Fetch the actual ID if it was an update
            item = LibraryModel.get_by_path(course_path)
            if item:
                library_id = item['id']
        else:
            # Update total lessons
            LibraryModel.update_progress(course_path, 0, total_lessons)
        
        if library_id:
            # Cache the course structure
            CourseCacheModel.save_cache(
                library_id=library_id,
                course_name=course.name,
                course_path=course_path,
                root_node=course.root_node.to_dict(),
                total_lessons=total_lessons
            )
            print(f"Cached course: {course.name} ({total_lessons} lessons)")
        
        # Apply progress
        ProgressTracker.apply_progress_to_tree(course)
        return course
        
    except Exception as e:
        print(f"Error loading course: {e}")
        return None


def invalidate_cache(course_path: str) -> bool:
    """Invalidate cache for a course (e.g., when files change)."""
    _ensure_db()
    item = LibraryModel.get_by_path(course_path)
    if item:
        return CourseCacheModel.invalidate(item['id'])
    return False


def refresh_cache(course_path: str) -> Optional[Course]:
    """Force refresh cache for a course."""
    return load_course_cached(course_path, force_rescan=True)
