from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from offilineu.models.lesson import Lesson


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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'path': self.path,
            'type': self.type,
            'children': {k: v.to_dict() for k, v in self.children.items()},
            'lessons': [l.to_dict() for l in self.lessons],
            'completed': self.completed,
            'last_accessed': self.last_accessed,
            'order': self.order,
            'has_content': self.has_content
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DirectoryNode':
        """Create DirectoryNode from dictionary."""
        node = cls(
            name=data.get('name', ''),
            path=data.get('path', ''),
            type=data.get('type', 'directory'),
            completed=data.get('completed', False),
            last_accessed=data.get('last_accessed'),
            order=data.get('order', 0),
            has_content=data.get('has_content', False)
        )
        # Recursively restore children
        for key, child_data in data.get('children', {}).items():
            node.children[key] = DirectoryNode.from_dict(child_data)
        # Restore lessons
        for lesson_data in data.get('lessons', []):
            node.lessons.append(Lesson.from_dict(lesson_data))
        return node
