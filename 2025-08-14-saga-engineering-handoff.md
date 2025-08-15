# Saga Engineering Handoff Document
**Date**: August 14, 2025  
**Author**: Development Team  
**Purpose**: Technical handoff for Saga implementation  
**Status**: Ready for development

---

## Executive Technical Summary

Saga (by Sagadex) is a local-first development context management system that solves the ephemeral context problem in software development. Think of it as "Git for development context" - it versions, stores, and intelligently retrieves the knowledge gained during debugging sessions, architectural decisions, and feature implementations.

**Core Innovation**: The Context Butler - an intelligent agent that uses local vector search and small language models to prepare optimal context for coding sessions at near-zero cost (~$0.50/month electricity).

**Current State**: Comprehensive specification complete, ready for MVP implementation.

---

## Problem Statement & Solution

### The Problem We're Solving
Developers constantly create ad-hoc documentation (`2024-08-13-jwt-timeout-FINALLY-FIXED.md`) during debugging sessions, then lose this valuable context. Current solutions (git commits, code comments, wikis) fail to capture the full journey and reasoning behind solutions.

### Our Solution
Saga automatically captures, indexes, and retrieves development context using:
1. **Git-native storage** - Markdown files versioned with code in `.sagadex/sagas/`
2. **Semantic search** - FAISS vectors for finding conceptually related content
3. **Intelligent compression** - Context Butler prepares minimal viable context
4. **Progressive loading** - Start with 140 chars, expand on demand

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                   Local Machine                          │
│                                                          │
│  ┌─────────────────────┐  ┌──────────────────────────┐ │
│  │   Git Repository     │  │    Saga Components       │ │
│  │                      │  │                          │ │
│  │  .sagadex/           │  │  1. AutoChronicler       │ │
│  │  ├── sagas/          │  │     (Git hook listener)  │ │
│  │  │   ├── main/       │  │                          │ │
│  │  │   └── [branch]/   │  │  2. SagaVectorDB         │ │
│  │  ├── index/          │  │     (FAISS + SQLite)     │ │
│  │  ├── config.json     │  │                          │ │
│  │  └── session/        │  │  3. ContextButler        │ │
│  │                      │  │     (TinyLlama local)    │ │
│  │  .git/hooks/         │  │                          │ │
│  │  └── post-commit ────┼──┤  4. ContextOptimizer     │ │
│  │                      │  │     (Token management)   │ │
│  └─────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Data Flow Pipeline

```python
# 1. Capture (Automatic via git hook or manual)
git commit -m "fix: JWT timeout" 
    → post-commit hook 
    → significance check (>0.7 threshold)
    → create saga markdown
    → update vector index

# 2. Retrieval (Semantic search)
saga search "authentication timeout"
    → encode query to vector
    → FAISS k-NN search (k=25)
    → multi-signal ranking
    → return top results

# 3. Context Preparation (Butler system)
saga start
    → analyze git state
    → find recent work
    → compress to 140 chars
    → inject to Claude
```

---

## Implementation Roadmap

### Phase 1: Core MVP (Week 1-2)
**Goal**: Basic capture and retrieval working locally

#### 1.1 Project Structure
```bash
saga/
├── src/
│   ├── __init__.py
│   ├── cli.py              # Click-based CLI entry point
│   ├── core/
│   │   ├── saga.py         # Saga document model
│   │   ├── repository.py   # Git integration
│   │   └── config.py       # Configuration management
│   ├── capture/
│   │   ├── auto_chronicler.py  # Automatic capture logic
│   │   ├── significance.py     # Scoring algorithm
│   │   └── hooks.py            # Git hook management
│   ├── search/
│   │   ├── vector_db.py        # FAISS wrapper
│   │   ├── embeddings.py       # Sentence transformer
│   │   └── ranking.py          # Multi-signal scoring
│   └── butler/
│       ├── context_butler.py   # Main butler logic
│       ├── compression.py      # TinyLlama integration
│       └── session.py          # Session state management
├── tests/
├── setup.py
└── requirements.txt
```

#### 1.2 Dependencies
```python
# requirements.txt
click==8.1.7                    # CLI framework
gitpython==3.1.40               # Git operations
rich==13.5.2                    # Terminal UI
pyyaml==6.0                     # Config files
sentence-transformers==2.2.2    # Embeddings (includes torch)
faiss-cpu==1.7.4                # Vector search
ollama==0.1.7                   # Local LLM interface (optional)
pyautogui==0.9.54              # Claude injection
pyperclip==1.8.2               # Clipboard fallback
watchdog==3.0.0                # File watching
```

#### 1.3 Core Classes

```python
# src/core/saga.py
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import hashlib
import yaml

@dataclass
class Saga:
    """Core saga document model"""
    id: str  # saga-{hash[:8]}
    title: str
    content: str
    saga_type: str  # debugging|feature|architecture|optimization
    timestamp: datetime
    branch: str
    tags: list[str]
    files_changed: list[str]
    status: str = "active"  # active|archived|deprecated
    
    @classmethod
    def from_markdown(cls, filepath: Path) -> 'Saga':
        """Parse saga from markdown file"""
        content = filepath.read_text()
        # Parse YAML frontmatter
        if content.startswith('---'):
            _, frontmatter, body = content.split('---', 2)
            metadata = yaml.safe_load(frontmatter)
            return cls(
                id=metadata.get('id', cls._generate_id(content)),
                title=metadata['title'],
                content=body.strip(),
                saga_type=metadata.get('type', 'general'),
                timestamp=datetime.fromisoformat(metadata['timestamp']),
                branch=metadata.get('branch', 'main'),
                tags=metadata.get('tags', []),
                files_changed=metadata.get('files_changed', []),
                status=metadata.get('status', 'active')
            )
    
    @staticmethod
    def _generate_id(content: str) -> str:
        """Generate unique saga ID from content"""
        hash_obj = hashlib.sha256(content.encode())
        return f"saga-{hash_obj.hexdigest()[:8]}"
    
    def to_markdown(self) -> str:
        """Serialize to markdown with frontmatter"""
        frontmatter = {
            'id': self.id,
            'title': self.title,
            'type': self.saga_type,
            'timestamp': self.timestamp.isoformat(),
            'branch': self.branch,
            'tags': self.tags,
            'files_changed': self.files_changed,
            'status': self.status
        }
        return f"---\n{yaml.dump(frontmatter)}---\n\n{self.content}"
```

```python
# src/search/vector_db.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import sqlite3
import json
from pathlib import Path

class SagaVectorDB:
    """Local vector database using FAISS and SQLite"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.index_path = db_path / "index"
        self.index_path.mkdir(exist_ok=True)
        
        # Initialize embedding model (384 dimensions)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize FAISS index
        self.dimension = 384
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # Initialize SQLite for metadata
        self.conn = sqlite3.connect(self.index_path / "metadata.db")
        self._init_database()
        
        # Load existing index if available
        self._load_index()
    
    def _init_database(self):
        """Create SQLite schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sagas (
                id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                title TEXT NOT NULL,
                saga_type TEXT,
                branch TEXT,
                timestamp TEXT,
                tags TEXT,  -- JSON array
                content TEXT,
                embedding_id INTEGER,
                file_hash TEXT
            )
        """)
        self.conn.commit()
    
    def add_saga(self, saga: Saga, filepath: Path):
        """Add saga to index"""
        # Generate embedding
        embedding = self.encoder.encode(saga.content)
        
        # Add to FAISS
        embedding_id = self.index.ntotal
        self.index.add(embedding.reshape(1, -1))
        
        # Store metadata in SQLite
        self.conn.execute("""
            INSERT OR REPLACE INTO sagas 
            (id, file_path, title, saga_type, branch, timestamp, tags, content, embedding_id, file_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            saga.id,
            str(filepath),
            saga.title,
            saga.saga_type,
            saga.branch,
            saga.timestamp.isoformat(),
            json.dumps(saga.tags),
            saga.content,
            embedding_id,
            hashlib.md5(saga.content.encode()).hexdigest()
        ))
        self.conn.commit()
        
        # Save index to disk
        self._save_index()
    
    def search(self, query: str, k: int = 10) -> list[tuple[Saga, float]]:
        """Semantic search for relevant sagas"""
        # Encode query
        query_vector = self.encoder.encode(query)
        
        # Search FAISS
        scores, indices = self.index.search(
            query_vector.reshape(1, -1), 
            min(k, self.index.ntotal)
        )
        
        # Fetch saga metadata
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx == -1:  # FAISS returns -1 for empty results
                break
            
            cursor = self.conn.execute(
                "SELECT * FROM sagas WHERE embedding_id = ?", (int(idx),)
            )
            row = cursor.fetchone()
            if row:
                # Reconstruct saga (simplified)
                saga = Saga(
                    id=row[0],
                    title=row[2],
                    content=row[7],
                    saga_type=row[3],
                    timestamp=datetime.fromisoformat(row[5]),
                    branch=row[4],
                    tags=json.loads(row[6]),
                    files_changed=[],  # Would need separate table
                    status='active'
                )
                results.append((saga, float(score)))
        
        return results
```

```python
# src/butler/context_butler.py
import subprocess
from pathlib import Path
import json
from datetime import datetime, timedelta

class ContextButler:
    """Intelligent context preparation system"""
    
    def __init__(self, repo_path: Path, vector_db: SagaVectorDB):
        self.repo_path = repo_path
        self.vector_db = vector_db
        self.session_path = repo_path / ".sagadex" / "session"
        self.session_path.mkdir(exist_ok=True)
    
    def prepare_context(self) -> str:
        """Prepare compressed context for coding session"""
        
        # 1. Analyze current git state
        git_state = self._get_git_state()
        
        # 2. Find recent work (last 24 hours)
        recent_sagas = self._get_recent_sagas(hours=24)
        
        # 3. Find semantically similar work
        if git_state['last_commit']:
            similar = self.vector_db.search(git_state['last_commit'], k=5)
        else:
            similar = []
        
        # 4. Compress to 140 characters
        context = self._compress_context(git_state, recent_sagas, similar)
        
        # 5. Save session state
        self._save_session_state(context, git_state, similar)
        
        return context
    
    def _get_git_state(self) -> dict:
        """Get current git repository state"""
        try:
            # Get branch
            branch = subprocess.check_output(
                ['git', 'branch', '--show-current'],
                cwd=self.repo_path,
                text=True
            ).strip()
            
            # Get last commit
            last_commit = subprocess.check_output(
                ['git', 'log', '-1', '--pretty=%B'],
                cwd=self.repo_path,
                text=True
            ).strip()
            
            # Get modified files
            modified = subprocess.check_output(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                text=True
            ).strip()
            
            return {
                'branch': branch,
                'last_commit': last_commit,
                'modified_files': modified.split('\n') if modified else []
            }
        except subprocess.CalledProcessError:
            return {'branch': 'unknown', 'last_commit': '', 'modified_files': []}
    
    def _compress_context(self, git_state: dict, recent: list, similar: list) -> str:
        """Compress context to 140 characters"""
        # Priority order for compression
        parts = []
        
        # Add branch if not main
        if git_state['branch'] != 'main':
            parts.append(f"BR:{git_state['branch'][:10]}")
        
        # Add most recent saga title
        if recent:
            parts.append(f"LAST:{recent[0].title[:20]}")
        
        # Add top similar saga reference
        if similar:
            saga, score = similar[0]
            if score > 0.7:
                parts.append(f"REF:{saga.id}")
        
        # Add modified file indicators
        if git_state['modified_files']:
            hot_files = [f.split('/')[-1] for f in git_state['modified_files'][:2]]
            parts.append(f"HOT:{','.join(hot_files)[:20]}")
        
        # Join with pipe separator
        context = '|'.join(parts)
        
        # Truncate to 140 chars
        if len(context) > 140:
            context = context[:137] + '...'
        
        return context
    
    def _save_session_state(self, context: str, git_state: dict, similar: list):
        """Save current session state for progressive loading"""
        session = {
            'session_id': datetime.now().isoformat(),
            'compressed_context': context,
            'git_state': git_state,
            'loaded_sagas': [],
            'similar_refs': [s[0].id for s in similar[:5]],
            'total_tokens': len(context) * 2  # Rough estimate
        }
        
        session_file = self.session_path / "current.json"
        session_file.write_text(json.dumps(session, indent=2))
```

### Phase 2: CLI Implementation (Week 2)

```python
# src/cli.py
import click
from rich.console import Console
from rich.table import Table
from pathlib import Path
from .core.saga import Saga
from .search.vector_db import SagaVectorDB
from .butler.context_butler import ContextButler

console = Console()

@click.group()
@click.pass_context
def cli(ctx):
    """Saga - Development Context Manager"""
    ctx.ensure_object(dict)
    repo_path = Path.cwd()
    sagadex_path = repo_path / ".sagadex"
    
    if sagadex_path.exists():
        ctx.obj['repo_path'] = repo_path
        ctx.obj['sagadex_path'] = sagadex_path
        ctx.obj['vector_db'] = SagaVectorDB(sagadex_path)

@cli.command()
@click.argument('message')
@click.pass_context
def commit(ctx, message):
    """Create a new saga"""
    # Implementation for manual saga creation
    saga = Saga(
        id=Saga._generate_id(message),
        title=message,
        content="",  # Would prompt for content
        saga_type="general",
        timestamp=datetime.now(),
        branch=get_current_branch(),
        tags=[],
        files_changed=get_modified_files()
    )
    
    # Save and index
    filepath = save_saga(saga)
    ctx.obj['vector_db'].add_saga(saga, filepath)
    console.print(f"✅ Saga created: {saga.id}")

@cli.command()
@click.argument('query')
@click.pass_context
def search(ctx, query):
    """Search for relevant sagas"""
    results = ctx.obj['vector_db'].search(query, k=5)
    
    # Display results
    table = Table(title=f"Search Results for '{query}'")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Score", style="yellow")
    table.add_column("Date", style="blue")
    
    for saga, score in results:
        table.add_row(
            saga.id[:8],
            saga.title[:50],
            f"{score:.2f}",
            saga.timestamp.strftime("%Y-%m-%d")
        )
    
    console.print(table)

@cli.command()
@click.pass_context
def start(ctx):
    """Start a contextualized coding session"""
    butler = ContextButler(ctx.obj['repo_path'], ctx.obj['vector_db'])
    context = butler.prepare_context()
    
    console.print(f"🤖 Context Butler prepared: {context}")
    
    # Attempt to inject into Claude
    try:
        inject_to_claude(context)
        console.print("✅ Context injected to Claude")
    except Exception as e:
        console.print(f"⚠️  Could not auto-inject. Context copied to clipboard.")
        pyperclip.copy(context)
```

### Phase 3: Automation & Hooks (Week 3)

#### Git Hook Installation
```python
# src/capture/hooks.py
def install_git_hook(repo_path: Path):
    """Install post-commit hook"""
    hook_content = '''#!/bin/bash
# Saga auto-capture hook

# Only run if saga is installed
if command -v saga &> /dev/null; then
    saga internal-capture \\
        --commit="$(git rev-parse HEAD)" \\
        --message="$(git log -1 --pretty=%B)" \\
        --files="$(git diff-tree --no-commit-id --name-only -r HEAD)" &
fi
'''
    
    hook_path = repo_path / ".git" / "hooks" / "post-commit"
    hook_path.write_text(hook_content)
    hook_path.chmod(0o755)
```

#### Significance Scoring
```python
# src/capture/significance.py
class SignificanceScorer:
    """Determine if an event is worth capturing"""
    
    KEYWORDS = {
        'high': ['fix', 'bug', 'critical', 'security', 'breaking'],
        'medium': ['feature', 'implement', 'add', 'update', 'refactor'],
        'low': ['formatting', 'typo', 'whitespace', 'comment', 'docs']
    }
    
    CRITICAL_FILES = [
        'requirements.txt', 'package.json', 'Gemfile',
        'docker-compose.yml', 'Dockerfile',
        '.env.example', 'config.py', 'settings.py'
    ]
    
    def score(self, commit_msg: str, files: list[str]) -> float:
        """Score from 0.0 to 1.0"""
        score = 0.0
        
        # Check commit message keywords
        msg_lower = commit_msg.lower()
        for keyword in self.KEYWORDS['high']:
            if keyword in msg_lower:
                score += 0.3
                break
        
        # Check critical files
        for file in files:
            if any(critical in file for critical in self.CRITICAL_FILES):
                score += 0.3
                break
        
        # Check change magnitude (would need diff stats)
        if len(files) > 5:
            score += 0.2
        
        # Check branch (feature branches more likely significant)
        if 'feature/' in get_current_branch():
            score += 0.2
        
        return min(score, 1.0)
```

### Phase 4: Context Butler & LLM Integration (Week 4)

#### TinyLlama Integration
```bash
# Install Ollama locally (one-time)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull tinyllama  # 638MB model
```

```python
# src/butler/compression.py
import requests
import json

class TinyLlamaCompressor:
    """Use local TinyLlama for intelligent compression"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
    
    def compress(self, context: dict, limit: int = 140) -> str:
        """Compress context intelligently"""
        prompt = f"""Compress this development context to {limit} characters.
Include only the MOST critical information.
Use format: KEY:value|KEY:value

Context:
- Branch: {context.get('branch', 'main')}
- Last commit: {context.get('last_commit', '')}
- Recent work: {context.get('recent_work', '')}
- Active issues: {context.get('issues', '')}

Compressed (max {limit} chars):"""
        
        try:
            response = requests.post(self.ollama_url, json={
                'model': 'tinyllama',
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.1,  # Low temperature for consistency
                    'max_tokens': 50
                }
            })
            
            if response.status_code == 200:
                result = response.json()['response']
                # Ensure it's within limit
                if len(result) > limit:
                    result = result[:limit-3] + '...'
                return result
        except:
            # Fallback to template-based compression
            pass
        
        return self._template_compress(context, limit)
    
    def _template_compress(self, context: dict, limit: int) -> str:
        """Fallback template-based compression"""
        parts = []
        
        branch = context.get('branch', '')
        if branch and branch != 'main':
            parts.append(f"BR:{branch[:15]}")
        
        last_work = context.get('last_work', '')
        if last_work:
            parts.append(f"LAST:{last_work[:30]}")
        
        result = '|'.join(parts)
        if len(result) > limit:
            result = result[:limit-3] + '...'
        
        return result
```

#### Claude Code Integration
```python
# src/butler/claude_integration.py
import subprocess
import time
import pyautogui
import pyperclip
from pathlib import Path

class ClaudeIntegration:
    """Methods to inject context into Claude Code"""
    
    @staticmethod
    def inject(context: str) -> bool:
        """Try multiple methods to inject context"""
        
        # Method 1: Check if Claude Code CLI exists
        if ClaudeIntegration._try_cli(context):
            return True
        
        # Method 2: Try pyautogui injection
        if ClaudeIntegration._try_pyautogui(context):
            return True
        
        # Method 3: Fallback to clipboard
        return ClaudeIntegration._try_clipboard(context)
    
    @staticmethod
    def _try_cli(context: str) -> bool:
        """Try using Claude Code CLI if available"""
        try:
            # Check if claude-code command exists
            result = subprocess.run(
                ['which', 'claude-code'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Try to pipe context
                subprocess.run(
                    ['claude-code'],
                    input=f"PROJECT CONTEXT: {context}\n",
                    text=True,
                    check=True
                )
                return True
        except:
            pass
        return False
    
    @staticmethod
    def _try_pyautogui(context: str) -> bool:
        """Try typing context using pyautogui"""
        try:
            # Give user time to focus Claude window
            print("Focus Claude Code window in 3 seconds...")
            time.sleep(3)
            
            # Type context
            pyautogui.typewrite(f"PROJECT CONTEXT: {context}\n")
            pyautogui.typewrite("Please acknowledge this context before proceeding.\n")
            
            return True
        except:
            pass
        return False
    
    @staticmethod
    def _try_clipboard(context: str) -> bool:
        """Copy to clipboard as last resort"""
        try:
            full_context = f"""PROJECT CONTEXT: {context}

Please acknowledge this context before proceeding with any requests."""
            
            pyperclip.copy(full_context)
            print("Context copied to clipboard. Paste into Claude Code.")
            return True
        except:
            return False
```

---

## Critical Implementation Notes

### 1. Vector Dimensions
**IMPORTANT**: The all-MiniLM-L6-v2 model outputs 384-dimensional vectors, NOT 768. Using wrong dimensions will cause index errors.

### 2. Git Hook Safety
Always run saga operations in background (`&`) in git hooks to avoid blocking commits. Include timeout handling.

### 3. Index Persistence
FAISS indices must be saved/loaded properly:
```python
# Save
faiss.write_index(self.index, str(self.index_path / "vectors.faiss"))

# Load
if (self.index_path / "vectors.faiss").exists():
    self.index = faiss.read_index(str(self.index_path / "vectors.faiss"))
```

### 4. Branch-Aware Storage
Sagas must be stored under branch-specific directories to maintain context isolation:
```python
saga_path = sagadex_path / "sagas" / branch_name / category / filename
```

### 5. Session State Management
Track loaded context to enable progressive loading:
```python
# When user requests more context
session = load_session_state()
already_loaded = session['loaded_sagas']
# Don't reload what's already there
```

### 6. Error Recovery
Always implement fallbacks:
- Corrupted index → Rebuild from sagas
- Git detached HEAD → Use commit hash as branch
- LLM unavailable → Template-based compression
- Claude injection fails → Clipboard fallback

---

## Testing Strategy

### Unit Tests
```python
# tests/test_saga.py
def test_saga_from_markdown():
    """Test parsing saga from markdown file"""
    content = """---
id: saga-test123
title: Test Saga
type: debugging
timestamp: 2024-08-14T10:00:00
tags: [test, example]
---

## Content
Test content here"""
    
    # Write to temp file and parse
    saga = Saga.from_markdown(temp_file)
    assert saga.id == "saga-test123"
    assert saga.title == "Test Saga"
```

### Integration Tests
- Test git hook triggers on real commits
- Test vector search accuracy with known queries
- Test session state persistence across commands
- Test Claude injection methods in order

### Performance Benchmarks
- Search latency with 1000+ sagas (target: <100ms)
- Index rebuild time (target: <30s for 5000 sagas)
- Memory usage with large indices (target: <500MB)

---

## Deployment & Distribution

### Option 1: PyPI Package
```bash
# setup.py configuration
setup(
    name="saga-cli",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "saga=cli:cli",
        ],
    },
    install_requires=[...],
)

# Users install with:
pip install saga-cli
```

### Option 2: Standalone Binary
Use PyInstaller for zero-dependency distribution:
```bash
pyinstaller --onefile --name saga src/cli.py
# Produces single 'saga' executable
```

### Option 3: Docker Container
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
ENTRYPOINT ["python", "-m", "src.cli"]
```

---

## Known Challenges & Solutions

### Challenge 1: First-Time Model Download
**Problem**: Sentence-transformers downloads 90MB model on first use.
**Solution**: Bundle model in Docker/binary or show progress bar.

### Challenge 2: Cross-Platform Compatibility
**Problem**: pyautogui behavior varies across OS.
**Solution**: OS-specific injection methods with fallbacks.

### Challenge 3: Git Integration Complexity
**Problem**: Various git states (detached HEAD, rebase, etc).
**Solution**: Graceful degradation - use what's available.

### Challenge 4: Index Scaling
**Problem**: FAISS index grows with sagas.
**Solution**: Implement index sharding at 10K+ sagas.

---

## Next Immediate Steps

1. **Set up project structure** - Create directories and initial files
2. **Implement Saga model** - Core data structure with serialization
3. **Build vector database** - FAISS + SQLite integration
4. **Create basic CLI** - Init, commit, search commands
5. **Add git hooks** - Automatic capture on commit
6. **Implement Context Butler** - Basic compression without LLM first
7. **Test with real usage** - Dogfood on actual projects
8. **Add progressive features** - LLM compression, Claude integration

---

## Success Criteria

The MVP is successful when:
1. ✅ `saga init` creates .sagadex structure
2. ✅ `saga commit` creates and indexes sagas
3. ✅ `saga search` finds relevant content semantically
4. ✅ Git commits auto-create sagas when significant
5. ✅ `saga start` produces compressed context
6. ✅ Context can be injected into Claude (any method)
7. ✅ Search returns results in <100ms for 1000 sagas

---

## Questions for Consideration

1. **Conflict Resolution**: How should saga merge conflicts be handled? Current thinking: Keep both versions with conflict markers.

2. **Privacy**: Should certain sagas be marked private (not synced)? Could use `private: true` in frontmatter.

3. **Shared Sagas**: How do team members share sagas? Via git is simple, but could add import/export commands.

4. **Migration Path**: How to import existing documentation? Current plan: Pattern-based splitting of markdown files.

5. **Performance Limits**: When to shard indices? Suggested: 10K sagas per index.

---

## Final Technical Notes

This system is designed to be:
- **Local-first**: No external dependencies for core features
- **Git-native**: Integrates naturally with existing workflows  
- **Cost-effective**: ~$0.50/month operating cost
- **Privacy-preserving**: All data stays on developer's machine
- **Progressive**: Start simple, add intelligence incrementally

The Context Butler innovation is the key differentiator - using local models to prepare context at near-zero cost while maintaining high quality through vector search and intelligent compression.

**Estimated Development Time**: 4 weeks for complete MVP with all features.

---

## Critical Advice & Hard-Won Insights

### The Core Problem is Real
The engineer needs to understand this solves an ACTUAL daily problem: Claude Code doesn't reliably read its CLAUDE.md file, and developers lose critical context between sessions. This isn't theoretical - it's happening right now.

### Start Without the Context Butler
**Biggest mistake**: Trying to build everything at once.

**Better approach**:
- Week 1: Just make `saga commit` + `saga search` work perfectly
- Week 2: Add git hooks for auto-capture
- Week 3: Add Context Butler (simple template version)
- Week 4: Add Claude integration if time permits

Basic capture + search alone would be transformative.

### The 140-Character Limit is Sacred
This isn't arbitrary - it's about cognitive load. A compressed 140-char context at the START gets read. A 2000-word context file gets ignored. Think Twitter - forced brevity creates focus.

### Critical Pitfalls to Avoid

#### 1. Vector Dimension Mismatch (Will Waste Days)
```python
# WRONG - Silent corruption:
self.index = faiss.IndexFlatIP(768)  # Wrong dimensions!
embedding = model.encode(text)  # Returns 384 dims
self.index.add(embedding)  # Corrupts index

# CORRECT:
self.index = faiss.IndexFlatIP(384)  # Matches all-MiniLM-L6-v2
```

#### 2. Git Hook Blocking (Users Will Hate This)
```bash
# WRONG - Blocks git commit:
saga auto-capture "$COMMIT_HASH"  # User waits...

# RIGHT - Background execution:
saga auto-capture "$COMMIT_HASH" &  # Instant return
```

#### 3. Over-Engineering the MVP
```python
# DON'T start with:
class AbstractSagaFactoryProvider:  # 🚫 No!

# DO start with:
def save_saga(content, title):  # Simple!
    Path(f".sagadex/sagas/{title}.md").write_text(content)
```

### Performance Walls to Plan For
- **<1,000 sagas**: Everything instant
- **1,000-10,000 sagas**: Need index optimization
- **10,000+ sagas**: Need sharding strategy

Design for 1,000, plan for 10,000, ignore 100,000 for now.

### Git State Complexity Will Bite You
These WILL happen:
- Detached HEAD state
- Interactive rebase in progress
- Merge conflicts in `.sagadex/sagas/`
- Submodules and worktrees

Solution: Always have fallbacks:
```python
try:
    branch = get_current_branch()
except:
    branch = "unknown"  # Don't crash, degrade gracefully
```

### The "Aha!" Test for Success
The MVP succeeds when this happens:
```bash
$ saga search "that weird websocket thing"
> Found: websocket-memory-leak-fix.md (0.89 match)

"Oh RIGHT! That's exactly how I fixed it!"
```

### Binary Files and Large Diffs
```python
# This will crash naive implementations:
git diff --binary some_image.jpg  # Gigabytes of base64

# Always filter:
if is_binary(file) or file_size > 1_000_000:
    skip_file()
```

### Session State is Trickier Than Expected
The `/context more` command needs to track what's already loaded:
```python
# .sagadex/session/current.json
{
    "loaded_sagas": ["saga-123", "saga-456"],
    "total_tokens": 3400,
    "compressed_context": "JWT:fix|BUG:websocket"
}
```

### Make Ollama/TinyLlama Optional
Many developers won't install Ollama. Graceful fallback:
```python
if ollama_available():
    use_smart_compression()
else:
    use_template_compression()  # Still useful!
```

### The Security Footgun
**Never capture**:
```python
FORBIDDEN_PATTERNS = [
    r'password\s*=\s*["\'].*["\']',
    r'api[_-]?key\s*=\s*["\'].*["\']',
    r'AWS_SECRET',
    r'private_key'
]
```

### Dogfood Immediately
As soon as basic `saga commit` works, use it on Saga itself. You'll find issues 10x faster than any test suite.

### Things NOT to Build (Yet)
- Web UI
- Cloud sync
- Team features  
- Fancy visualizations
- Chat interface
- Perfect import system

**Just make the CLI work flawlessly.**

### The One-Line Value Prop
"Git tracks what changed. Saga tracks why it changed and how you figured it out."

### When You're Stuck
Ask: "What's the simplest thing that would be immediately useful?"

The answer is usually: Make `saga commit` and `saga search` work. Everything else is gravy.

### Final Wisdom
**Ship the simple thing that works, then iterate.** A working tool that captures and searches markdown files is better than a perfect architecture that doesn't exist.

The real test: Can you use Saga to build Saga? If yes, ship it.

---

*End of Technical Handoff Document*