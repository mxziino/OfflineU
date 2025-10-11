from dataclasses import dataclass
from typing import Optional, List


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
