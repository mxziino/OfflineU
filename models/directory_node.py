from dataclasses import dataclass
from typing import Optional, List, Dict

from models.lesson import Lesson


@dataclass
class DirectoryNode:
    """Represents a directory in the course structure"""
    name: str
    path: str
    type: str  # 'directory' or 'lesson'
    children: Dict[str, 'DirectoryNode'] = None
    lessons: List[Lesson] = None
    completed: bool = False
    last_accessed: Optional[str] = None
    order: int = 0
    has_content: bool = False  # Whether this directory contains actual lesson content

    def __post_init__(self):
        if self.children is None:
            self.children = {}
        if self.lessons is None:
            self.lessons = []
