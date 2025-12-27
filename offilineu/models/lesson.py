from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any


@dataclass
class Lesson:
    title: str
    path: str
    lesson_type: str  # 'video', 'audio', 'text', 'quiz', 'mixed'
    video_file: Optional[str] = None
    audio_file: Optional[str] = None
    subtitle_file: Optional[str] = None
    text_files: List[str] = None
    completed: bool = False
    last_accessed: Optional[str] = None
    progress_seconds: int = 0
    order: int = 0

    def __post_init__(self):
        if self.text_files is None:
            self.text_files = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Lesson':
        """Create Lesson from dictionary."""
        return cls(
            title=data.get('title', ''),
            path=data.get('path', ''),
            lesson_type=data.get('lesson_type', 'text'),
            video_file=data.get('video_file'),
            audio_file=data.get('audio_file'),
            subtitle_file=data.get('subtitle_file'),
            text_files=data.get('text_files', []),
            completed=data.get('completed', False),
            last_accessed=data.get('last_accessed'),
            progress_seconds=data.get('progress_seconds', 0),
            order=data.get('order', 0)
        )
