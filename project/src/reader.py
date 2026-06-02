from dataclasses import dataclass, field
from typing import List


@dataclass
class CategoryRule:
    name: str
    folder: str
    description: str = ""
    priority: int = 0
    keywords: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)


@dataclass
class ClassificationResult:
    category: str
    folder: str
    score: int
    matched_terms: List[str]
    reason: str = ""


from pathlib import Path

class EmailMessage:
    def __init__(self, filename: str, subject: str, body: str, path: Path = None, blocked: bool = False):
        self.filename = filename
        self.subject = subject
        self.body = body
        self.path = path
        self.blocked = blocked

    def get_full_text(self) -> str:
        return f"{self.subject} {self.body}".lower()