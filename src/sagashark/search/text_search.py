"""
Simple text-based search for SagaShark MVP
No dependencies on vector databases or ML models
"""

from pathlib import Path
from typing import List, Tuple
from datetime import datetime
import re

from ..core.saga import Saga


class TextSearcher:
    """Simple text-based saga search"""
    
    def __init__(self, saga_dir: Path):
        self.saga_dir = saga_dir
    
    def search(self, query: str, limit: int = 10) -> List[Tuple[Saga, float]]:
        """
        Search for sagas matching the query.
        Returns list of (saga, relevance_score) tuples.
        """
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Search all saga files
        for saga_file in self._get_all_saga_files():
            try:
                saga = Saga.from_file(saga_file)
                score = self._calculate_relevance(saga, query_lower, query_words)
                
                if score > 0:
                    results.append((saga, score, saga_file))
            except Exception:
                # Skip files that can't be parsed
                continue
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        return [(saga, score) for saga, score, _ in results[:limit]]
    
    def _get_all_saga_files(self) -> List[Path]:
        """Get all markdown files in saga directory"""
        saga_files = []
        
        if self.saga_dir.exists():
            # Find all .md files recursively
            saga_files = list(self.saga_dir.glob('**/*.md'))
        
        # Sort by modification time (newest first)
        saga_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        return saga_files
    
    def _calculate_relevance(self, saga: Saga, query: str, query_words: set) -> float:
        """
        Calculate relevance score for a saga.
        Higher score = more relevant.
        """
        score = 0.0
        
        # Title match (highest weight)
        title_lower = saga.title.lower()
        if query in title_lower:
            score += 10.0  # Exact phrase in title
        else:
            # Check word overlap
            title_words = set(title_lower.split())
            word_matches = len(query_words & title_words)
            score += word_matches * 3.0
        
        # Content match
        content_lower = saga.content.lower()
        if query in content_lower:
            score += 5.0  # Exact phrase in content
            # Bonus for multiple occurrences
            occurrences = content_lower.count(query)
            score += min(occurrences - 1, 5) * 0.5
        else:
            # Check word overlap in content
            content_words = set(content_lower.split())
            word_matches = len(query_words & content_words)
            score += min(word_matches * 0.5, 3.0)
        
        # Tag match
        for tag in saga.tags:
            if query in tag.lower():
                score += 2.0
            elif any(word in tag.lower() for word in query_words):
                score += 1.0
        
        # Type match
        if saga.saga_type in query:
            score += 1.5
        
        # Recency bonus (newer is slightly better)
        days_old = (datetime.now() - saga.timestamp).days
        if days_old < 7:
            score += 1.0
        elif days_old < 30:
            score += 0.5
        
        # Branch relevance (if query mentions branch)
        if saga.branch.lower() in query:
            score += 2.0
        
        return score
    
    def search_by_type(self, saga_type: str, limit: int = 10) -> List[Saga]:
        """Search for sagas by type"""
        results = []
        
        for saga_file in self._get_all_saga_files():
            try:
                saga = Saga.from_file(saga_file)
                if saga.saga_type == saga_type:
                    results.append(saga)
                    if len(results) >= limit:
                        break
            except Exception:
                continue
        
        return results
    
    def search_by_tag(self, tag: str, limit: int = 10) -> List[Saga]:
        """Search for sagas by tag"""
        results = []
        tag_lower = tag.lower()
        
        for saga_file in self._get_all_saga_files():
            try:
                saga = Saga.from_file(saga_file)
                if any(tag_lower in t.lower() for t in saga.tags):
                    results.append(saga)
                    if len(results) >= limit:
                        break
            except Exception:
                continue
        
        return results
    
    def get_recent(self, limit: int = 10) -> List[Saga]:
        """Get most recent sagas"""
        results = []
        
        for saga_file in self._get_all_saga_files()[:limit]:
            try:
                saga = Saga.from_file(saga_file)
                results.append(saga)
            except Exception:
                continue
        
        return results