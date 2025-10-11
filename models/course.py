from dataclasses import dataclass
from typing import Optional

from models.directory_node import DirectoryNode


@dataclass
class Course:
    name: str
    path: str
    root_node: DirectoryNode
    progress_file: str
    last_accessed_path: Optional[str] = None
    completion_percentage: float = 0.0

    def __post_init__(self):
        if self.root_node is None:
            self.root_node = DirectoryNode("", "", "directory")
