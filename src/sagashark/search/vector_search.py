"""
FAISS-based vector search for semantic saga retrieval.
Finds sagas by meaning, not just keywords.
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False
    print("Vector search not available. Install with: pip install faiss-cpu sentence-transformers")


@dataclass
class SearchResult:
    """Result from vector search"""
    saga_id: str
    title: str
    score: float
    preview: str
    file_path: Path
    

class VectorSearcher:
    """
    Semantic search using FAISS vector similarity.
    Finds sagas by meaning rather than exact keyword matches.
    """
    
    # Use a small, fast model that runs on CPU
    DEFAULT_MODEL = 'all-MiniLM-L6-v2'  # 80MB, very fast
    
    def __init__(self, saga_dir: Path, model_name: str = None):
        """
        Initialize vector searcher.
        
        Args:
            saga_dir: Directory containing sagas
            model_name: Sentence transformer model to use
        """
        if not VECTOR_SEARCH_AVAILABLE:
            raise ImportError("Vector search requires faiss-cpu and sentence-transformers")
            
        self.saga_dir = saga_dir
        self.index_dir = saga_dir / '.vector_index'
        self.index_dir.mkdir(exist_ok=True)
        
        # Initialize model
        self.model_name = model_name or self.DEFAULT_MODEL
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        
        # Vector dimension from model
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        # Initialize or load index
        self.index = None
        self.saga_metadata = []
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        index_file = self.index_dir / 'faiss.index'
        metadata_file = self.index_dir / 'metadata.json'
        
        if index_file.exists() and metadata_file.exists():
            try:
                # Load existing index
                self.index = faiss.read_index(str(index_file))
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.saga_metadata = json.load(f)
                print(f"Loaded vector index with {len(self.saga_metadata)} sagas")
            except Exception as e:
                print(f"Could not load index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create new FAISS index"""
        # Use IndexFlatIP for inner product (cosine similarity after normalization)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.saga_metadata = []
        print("Created new vector index")
    
    def index_saga(self, saga_id: str, title: str, content: str, file_path: Path):
        """
        Add a saga to the vector index.
        
        Args:
            saga_id: Unique saga identifier
            title: Saga title
            content: Full saga content
            file_path: Path to saga file
        """
        # Combine title and content for richer embedding
        text = f"{title}\n\n{content}"
        
        # Limit text length to avoid memory issues
        max_length = 2000
        if len(text) > max_length:
            # Take beginning and end for better context
            text = text[:max_length//2] + "\n...\n" + text[-max_length//2:]
        
        # Generate embedding
        embedding = self.model.encode(text)
        
        # Normalize for cosine similarity
        embedding = embedding / np.linalg.norm(embedding)
        
        # Add to index
        self.index.add(np.array([embedding], dtype='float32'))
        
        # Store metadata
        self.saga_metadata.append({
            'saga_id': saga_id,
            'title': title,
            'preview': content[:200] + '...' if len(content) > 200 else content,
            'file_path': str(file_path)
        })
    
    def reindex_all(self):
        """Reindex all sagas in the directory"""
        print("Reindexing all sagas...")
        
        # Clear existing index
        self._create_new_index()
        
        # Find all saga files
        saga_files = list((self.saga_dir / 'sagas').glob('**/*.md'))
        
        for saga_file in saga_files:
            try:
                # Read saga file
                content = saga_file.read_text(encoding='utf-8')
                
                # Extract metadata from frontmatter
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        import yaml
                        metadata = yaml.safe_load(parts[1])
                        saga_content = parts[2].strip()
                        
                        saga_id = metadata.get('id', saga_file.stem)
                        title = metadata.get('title', 'Untitled')
                        
                        # Index the saga
                        self.index_saga(saga_id, title, saga_content, saga_file)
                        
            except Exception as e:
                print(f"Error indexing {saga_file}: {e}")
                continue
        
        # Save index
        self._save_index()
        print(f"Indexed {len(self.saga_metadata)} sagas")
    
    def _save_index(self):
        """Save index and metadata to disk"""
        index_file = self.index_dir / 'faiss.index'
        metadata_file = self.index_dir / 'metadata.json'
        
        # Save FAISS index
        faiss.write_index(self.index, str(index_file))
        
        # Save metadata
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.saga_metadata, f, indent=2)
    
    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """
        Search for sagas using semantic similarity.
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of search results ordered by relevance
        """
        if self.index is None or self.index.ntotal == 0:
            print("Index is empty. Run reindex_all() first.")
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode(query)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Search in FAISS
        distances, indices = self.index.search(
            np.array([query_embedding], dtype='float32'), 
            min(limit, self.index.ntotal)
        )
        
        # Build results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.saga_metadata):
                metadata = self.saga_metadata[idx]
                results.append(SearchResult(
                    saga_id=metadata['saga_id'],
                    title=metadata['title'],
                    score=float(dist),  # Higher is better for inner product
                    preview=metadata['preview'],
                    file_path=Path(metadata['file_path'])
                ))
        
        return results
    
    def find_similar(self, saga_id: str, limit: int = 5) -> List[SearchResult]:
        """
        Find sagas similar to a given saga.
        
        Args:
            saga_id: ID of saga to find similar ones for
            limit: Maximum results to return
            
        Returns:
            List of similar sagas
        """
        # Find the saga in metadata
        saga_idx = None
        for i, metadata in enumerate(self.saga_metadata):
            if metadata['saga_id'] == saga_id:
                saga_idx = i
                break
        
        if saga_idx is None:
            print(f"Saga {saga_id} not found in index")
            return []
        
        # Get the saga's embedding from the index
        saga_embedding = self.index.reconstruct(saga_idx)
        
        # Search for similar
        distances, indices = self.index.search(
            np.array([saga_embedding], dtype='float32'),
            min(limit + 1, self.index.ntotal)  # +1 to exclude self
        )
        
        # Build results, excluding the query saga itself
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != saga_idx and idx < len(self.saga_metadata):
                metadata = self.saga_metadata[idx]
                results.append(SearchResult(
                    saga_id=metadata['saga_id'],
                    title=metadata['title'],
                    score=float(dist),
                    preview=metadata['preview'],
                    file_path=Path(metadata['file_path'])
                ))
        
        return results[:limit]
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index"""
        return {
            'total_sagas': len(self.saga_metadata),
            'index_size': self.index.ntotal if self.index else 0,
            'model': self.model_name,
            'dimension': self.dimension,
            'index_dir': str(self.index_dir)
        }


class HybridSearcher:
    """
    Combines vector search with keyword search for best results.
    Falls back to keyword search if vectors not available.
    """
    
    def __init__(self, saga_dir: Path):
        self.saga_dir = saga_dir
        
        # Try to initialize vector search
        self.vector_searcher = None
        if VECTOR_SEARCH_AVAILABLE:
            try:
                self.vector_searcher = VectorSearcher(saga_dir)
            except Exception as e:
                print(f"Could not initialize vector search: {e}")
        
        # Always have text search as fallback
        from .text_search import TextSearcher
        self.text_searcher = TextSearcher(saga_dir)
    
    def search(self, query: str, limit: int = 5, mode: str = 'hybrid') -> List[Any]:
        """
        Search using specified mode.
        
        Args:
            query: Search query
            limit: Maximum results
            mode: 'vector', 'text', or 'hybrid'
            
        Returns:
            Search results
        """
        if mode == 'vector' and self.vector_searcher:
            return self.vector_searcher.search(query, limit)
        elif mode == 'text':
            return self.text_searcher.search(query, limit)
        elif mode == 'hybrid' and self.vector_searcher:
            # Get results from both
            vector_results = self.vector_searcher.search(query, limit)
            text_results = self.text_searcher.search(query, limit)
            
            # Merge and deduplicate
            seen_ids = set()
            merged = []
            
            # Interleave results
            for v_result, t_result in zip(vector_results, text_results):
                if v_result.saga_id not in seen_ids:
                    merged.append(v_result)
                    seen_ids.add(v_result.saga_id)
                if t_result.id not in seen_ids:
                    merged.append(t_result)
                    seen_ids.add(t_result.id)
            
            return merged[:limit]
        else:
            # Fallback to text search
            return self.text_searcher.search(query, limit)