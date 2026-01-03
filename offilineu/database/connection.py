"""
SQLite database connection singleton for OfflineU.
Database file is stored in ~/.offlineu/offlineu.db
"""
import sqlite3
import os
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

# Database location
# Database location
custom_db_path = os.environ.get('OFFLINEU_DB_PATH')
if custom_db_path:
    DB_PATH = Path(custom_db_path)
    DB_DIR = DB_PATH.parent
else:
    DB_DIR = Path.home() / '.offlineu'
    DB_PATH = DB_DIR / 'offlineu.db'

# Connection pool (single connection for SQLite)
_connection: Optional[sqlite3.Connection] = None


def get_db_path() -> Path:
    """Get the database file path, creating directory if needed."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return DB_PATH


def get_db() -> sqlite3.Connection:
    """Get the database connection singleton."""
    global _connection
    
    if _connection is None:
        db_path = get_db_path()
        _connection = sqlite3.connect(str(db_path), check_same_thread=False)
        _connection.row_factory = sqlite3.Row  # Enable dict-like access
        _connection.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
        _connection.execute("PRAGMA journal_mode = WAL")  # Better concurrency
    
    return _connection


def init_db():
    """Initialize the database with schema."""
    from .migrations import run_migrations
    conn = get_db()
    run_migrations(conn)
    conn.commit()


def close_db():
    """Close the database connection."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None


@contextmanager
def get_cursor():
    """Context manager for database cursor with auto-commit."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def execute(query: str, params: tuple = ()) -> sqlite3.Cursor:
    """Execute a query and return the cursor."""
    conn = get_db()
    cursor = conn.execute(query, params)
    conn.commit()
    return cursor


def fetch_one(query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
    """Execute a query and fetch one result."""
    conn = get_db()
    cursor = conn.execute(query, params)
    return cursor.fetchone()


def fetch_all(query: str, params: tuple = ()) -> list:
    """Execute a query and fetch all results."""
    conn = get_db()
    cursor = conn.execute(query, params)
    return cursor.fetchall()
