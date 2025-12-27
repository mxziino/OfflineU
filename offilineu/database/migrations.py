"""
Database migrations for OfflineU.
Handles schema creation and versioning.
"""
import sqlite3
from datetime import datetime


# Current schema version
SCHEMA_VERSION = 4


def run_migrations(conn: sqlite3.Connection):
    """Run all pending migrations."""
    # Create migrations tracking table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Get current version
    cursor = conn.execute("SELECT MAX(version) FROM schema_migrations")
    row = cursor.fetchone()
    current_version = row[0] if row[0] is not None else 0
    
    # Run migrations
    migrations = [
        (1, migrate_v1_initial_schema),
        (2, migrate_v2_course_cache),
        (3, migrate_v3_add_tags),
        (4, migrate_v4_lesson_notes),
    ]
    
    for version, migration_fn in migrations:
        if version > current_version:
            print(f"Running migration v{version}...")
            migration_fn(conn)
            conn.execute(
                "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                (version, datetime.now().isoformat())
            )
            conn.commit()
            print(f"Migration v{version} completed.")


def migrate_v1_initial_schema(conn: sqlite3.Connection):
    """Initial schema creation."""
    
    # Library table - all courses and learning paths
    conn.execute("""
        CREATE TABLE IF NOT EXISTS library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT UNIQUE NOT NULL,
            load_mode TEXT DEFAULT 'course',
            total_lessons INTEGER DEFAULT 0,
            completed_lessons INTEGER DEFAULT 0,
            last_accessed DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_library_path ON library(path)")
    
    # Lesson progress table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lesson_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            library_id INTEGER NOT NULL,
            lesson_path TEXT NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            progress_seconds INTEGER DEFAULT 0,
            completed_at DATETIME,
            last_accessed DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (library_id) REFERENCES library(id) ON DELETE CASCADE,
            UNIQUE(library_id, lesson_path)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lesson_library ON lesson_progress(library_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lesson_path ON lesson_progress(lesson_path)")
    
    # Study sessions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            library_id INTEGER,
            lesson_path TEXT,
            started_at DATETIME NOT NULL,
            ended_at DATETIME,
            duration_seconds INTEGER DEFAULT 0,
            FOREIGN KEY (library_id) REFERENCES library(id) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_session_date ON study_sessions(started_at)")
    
    # Daily statistics table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE UNIQUE NOT NULL,
            lessons_completed INTEGER DEFAULT 0,
            time_spent_seconds INTEGER DEFAULT 0,
            courses_accessed INTEGER DEFAULT 0
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_stats_date ON daily_stats(date)")


def migrate_v2_course_cache(conn: sqlite3.Connection):
    """Add course cache table for fast loading."""
    
    # Course cache table - stores serialized directory tree
    conn.execute("""
        CREATE TABLE IF NOT EXISTS course_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            library_id INTEGER UNIQUE NOT NULL,
            course_name TEXT NOT NULL,
            course_path TEXT NOT NULL,
            root_node_json TEXT NOT NULL,
            total_lessons INTEGER DEFAULT 0,
            cached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            file_count INTEGER DEFAULT 0,
            FOREIGN KEY (library_id) REFERENCES library(id) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_library ON course_cache(library_id)")


def migrate_v3_add_tags(conn: sqlite3.Connection):
    """Add tags column to library table."""
    
    # Add tags column to store JSON array of tag strings
    conn.execute("""
        ALTER TABLE library ADD COLUMN tags TEXT DEFAULT '[]'
    """)


def migrate_v4_lesson_notes(conn: sqlite3.Connection):
    """Add lesson notes table for markdown notes."""
    
    # Lesson notes table - stores markdown notes per lesson
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lesson_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            library_id INTEGER NOT NULL,
            lesson_path TEXT NOT NULL,
            content TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (library_id) REFERENCES library(id) ON DELETE CASCADE,
            UNIQUE(library_id, lesson_path)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_library ON lesson_notes(library_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_path ON lesson_notes(lesson_path)")
