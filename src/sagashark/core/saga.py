"""
Core Saga model for GitSaga
Handles creation, serialization, and deserialization of saga documents
"""

import hashlib
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class Saga:
    """
    A saga represents a single development context or story.
    It captures the journey, decisions, and solutions during development.
    """
    title: str
    content: str
    saga_type: str = "general"  # debugging, feature, architecture, optimization
    timestamp: datetime = field(default_factory=datetime.now)
    branch: str = "main"
    tags: List[str] = field(default_factory=list)
    files_changed: List[str] = field(default_factory=list)
    status: str = "active"  # active, archived, deprecated
    id: Optional[str] = None
    
    def __post_init__(self):
        """Generate ID if not provided"""
        if not self.id:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique saga ID from content hash"""
        content = f"{self.title}{self.timestamp.isoformat()}"
        hash_obj = hashlib.sha256(content.encode())
        return f"saga-{hash_obj.hexdigest()[:8]}"
    
    def to_markdown(self) -> str:
        """Serialize saga to markdown with YAML frontmatter"""
        frontmatter = {
            'id': self.id,
            'title': self.title,
            'type': self.saga_type,
            'timestamp': self.timestamp.isoformat(),
            'branch': self.branch,
            'status': self.status,
            'tags': self.tags,
            'files_changed': self.files_changed
        }
        
        # Use literal style for YAML to preserve formatting
        yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        
        return f"---\n{yaml_str}---\n\n{self.content}"
    
    @classmethod
    def from_markdown(cls, content: str) -> 'Saga':
        """Parse saga from markdown content"""
        if not content.startswith('---'):
            raise ValueError("Invalid saga format: missing frontmatter")
        
        # Split frontmatter and content
        parts = content.split('---', 2)
        if len(parts) < 3:
            raise ValueError("Invalid saga format: incomplete frontmatter")
        
        frontmatter_str = parts[1].strip()
        body = parts[2].strip()
        
        # Parse YAML frontmatter
        try:
            metadata = yaml.safe_load(frontmatter_str)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML frontmatter: {e}")
        
        # Create saga from metadata
        return cls(
            id=metadata.get('id'),
            title=metadata.get('title', 'Untitled'),
            content=body,
            saga_type=metadata.get('type', 'general'),
            timestamp=datetime.fromisoformat(metadata.get('timestamp', datetime.now().isoformat())),
            branch=metadata.get('branch', 'main'),
            tags=metadata.get('tags', []),
            files_changed=metadata.get('files_changed', []),
            status=metadata.get('status', 'active')
        )
    
    @classmethod
    def from_file(cls, filepath: Path) -> 'Saga':
        """Load saga from markdown file"""
        if not filepath.exists():
            raise FileNotFoundError(f"Saga file not found: {filepath}")
        
        content = filepath.read_text(encoding='utf-8')
        return cls.from_markdown(content)
    
    def save(self, directory: Path, auto_organize: bool = True) -> Path:
        """Save saga to markdown file with automatic date-based organization"""
        directory.mkdir(parents=True, exist_ok=True)
        
        # Generate concise filename: YYYY-MM-DD-HHMM-key-words.md
        timestamp_str = self.timestamp.strftime("%Y-%m-%d-%H%M")
        
        # Extract key words from title for concise filename
        title_slug = self._create_concise_slug(self.title)
        filename = f"{timestamp_str}-{title_slug}.md"
        
        # Use auto-organization if enabled
        if auto_organize:
            from .organizer import AutoOrganizer
            organizer = AutoOrganizer(directory, auto_organize=True)
            
            # Create temp path and let organizer handle it
            temp_path = directory / filename
            temp_path.write_text(self.to_markdown(), encoding='utf-8')
            filepath = organizer.save_organized(temp_path)
        else:
            filepath = directory / filename
            filepath.write_text(self.to_markdown(), encoding='utf-8')
        
        return filepath
    
    def _slugify(self, text: str) -> str:
        """Convert text to filesystem-safe slug"""
        # Replace non-alphanumeric with hyphens
        import re
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def _create_concise_slug(self, title: str, max_length: int = 30) -> str:
        """Create a concise slug that captures the essence of the title"""
        import re
        
        # Common words to skip for more concise filenames
        skip_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
                     'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 
                     'through', 'during', 'how', 'when', 'where', 'why', 'what',
                     'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had',
                     'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
                     'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        # Extract words and filter
        words = re.findall(r'\b\w+\b', title.lower())
        
        # Keep important words (not in skip list)
        important_words = [w for w in words if w not in skip_words and len(w) > 2]
        
        # If we filtered out too much, keep first few original words
        if len(important_words) < 2:
            important_words = words[:3]
        
        # Take first 3-4 important words
        key_words = important_words[:4]
        
        # Create slug
        slug = '-'.join(key_words)
        
        # Ensure it's not too long
        if len(slug) > max_length:
            # Truncate smartly at word boundary
            slug = slug[:max_length].rsplit('-', 1)[0]
        
        # Fallback if empty
        if not slug:
            slug = self._slugify(title)[:max_length]
        
        return slug
    
    def matches(self, query: str) -> bool:
        """Simple text matching for search"""
        query_lower = query.lower()
        
        # Search in title
        if query_lower in self.title.lower():
            return True
        
        # Search in content
        if query_lower in self.content.lower():
            return True
        
        # Search in tags
        for tag in self.tags:
            if query_lower in tag.lower():
                return True
        
        return False
    
    def get_preview(self, max_lines: int = 3) -> str:
        """Get a preview of the saga content"""
        lines = self.content.split('\n')
        preview_lines = [line.strip() for line in lines[:max_lines] if line.strip()]
        return ' '.join(preview_lines)[:200] + '...' if len(' '.join(preview_lines)) > 200 else ' '.join(preview_lines)