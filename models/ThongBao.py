from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import json

@dataclass
class ThongBao:
    id: str
    title: str
    date: str  # Published date on CITD (Format: YYYY-MM-DD-HH-MM-SS)
    author: str
    topic: str
    tags: List[str]
    content_md_path: str
    original_url: str
    assets: List[str] = field(default_factory=list)
    content: str = "" # Full markdown content for regeneration
    created_at: str = field(default_factory=lambda: datetime.now().isoformat()) # Scraped time

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date,
            "author": self.author,
            "topic": self.topic,
            "tags": self.tags,
            "content_md_path": self.content_md_path,
            "original_url": self.original_url,
            "assets": self.assets,
            "content": self.content,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        # Handle potential missing fields if loading older JSONs
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            date=data.get("date", ""),
            author=data.get("author", "Unknown"),
            topic=data.get("topic", "Thông báo học vụ"),
            tags=data.get("tags", []),
            content_md_path=data.get("content_md_path", ""),
            original_url=data.get("original_url", ""),
            assets=data.get("assets", []),
            content=data.get("content", ""),
            created_at=data.get("created_at", datetime.now().isoformat())
        )
    
    @classmethod
    def load_from_json(cls, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def save_to_json(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)
