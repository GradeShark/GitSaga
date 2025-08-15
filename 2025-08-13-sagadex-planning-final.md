# Sagadex Master Document
*The Definitive Technical & Business Blueprint*

**Version**: 5.0 (Personal Tool Focus)  
**Date**: August 14, 2025  
**Status**: Technical Specification  
**Purpose**: Build a local-first development context manager for personal productivity

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Core Problem & Solution](#core-problem--solution)
3. [Technical Architecture](#technical-architecture)
4. [Implementation Details](#implementation-details)
5. [Local Development Setup](#local-development-setup)
6. [Usage Workflow](#usage-workflow)
7. [Development Timeline](#development-timeline)
8. [Example Sagas](#example-sagas)

---

## Executive Summary

**Sagadex** is an AI-powered development context repository that transforms ephemeral coding decisions into searchable, versionable knowledge. It captures the "sagas" behind your code - the debugging adventures, architectural decisions, and implementation journeys that are typically lost after development sessions.

### The Core Innovation
**"The GitHub of Context Management"** - Just as GitHub revolutionized code versioning, Sagadex revolutionizes development context versioning. It treats development context as a first-class citizen alongside source code, creating a versioned, searchable, and intelligent knowledge repository that lives with your codebase.

### Key Value Proposition
"Never debug the same problem twice. Never lose development context again."

### Who This Is For
- **Me**: A developer who manually creates time-stamped documentation files
- **Anyone**: Who loses context between coding sessions
- **Future**: Other developers who face the same problem

### Core Principles
1. **100% Local**: Everything runs on my machine
2. **Git-Native**: Context versioned with my code
3. **Zero Dependencies**: No cloud services, no subscriptions
4. **Near-Zero Cost**: Just ~$0.50/month in electricity

---

## Core Problem & Solution

### The Problem: Lost Development Context

Every developer manually creates time-stamped documentation files to track critical debugging sessions and decisions. These ephemeral contexts include:

- **Debugging journeys** that took days to solve
- **Architectural decisions** and their rationale
- **Failed approaches** that shouldn't be repeated
- **Implementation patterns** that work for specific problems

This valuable context is almost always lost, leading to:
- **Duplicated effort** - Solving the same problems repeatedly
- **Knowledge silos** - Critical decisions trapped in individual minds
- **Onboarding friction** - New developers can't understand "why"
- **Technical debt** - Lost context makes refactoring dangerous

### Why Current Solutions Fail

- **Git commits**: Show what changed, not the journey
- **Documentation**: Quickly becomes outdated and unsearchable
- **Code comments**: Limited context, disconnected from decisions
- **Wikis/Notion**: Not versioned with code, becomes stale

### The Sagadex Solution

Three foundational principles guide everything:

1. **Local-First Architecture**
   - All core operations run locally
   - No internet dependency for primary features
   - Complete data sovereignty

2. **Context-Code Coupling**
   - Knowledge repository branches with your code
   - Context state maps to code state at any point
   - Sagas evolve with your codebase

3. **Intelligent Retrieval**
   - AI-powered semantic search beyond keywords
   - Automatic context optimization for token limits
   - Multi-signal relevance scoring

---

## Technical Architecture

### System Overview

Sagadex operates as a three-tier system with the local tier being completely self-sufficient:

```
┌─────────────────────────────────────────────────────────┐
│                    Developer Machine                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │            Local Core (100% Functional)           │   │
│  │  • File watching & git hooks                     │   │
│  │  • Local vector database (FAISS + SQLite)        │   │
│  │  • CLI interface (saga command)                  │   │
│  │  • Automatic saga capture                        │   │
│  │  • Full search and retrieval                     │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                   Optional Enhancement
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Cloud Services (Optional)                   │
│  • Encrypted backup & sync                              │
│  • Team collaboration features                          │
│  • Community saga sharing                               │
│  • Advanced analytics                                   │
└─────────────────────────────────────────────────────────┘
```

### Data Flow Pipeline

```
User Query ("authentication timeout debugging")
    ↓
[Step 1: Candidate Retrieval]
    • FAISS vector search (local)
    • Retrieve top 25-50 candidates
    ↓
[Step 2: Multi-Signal Scoring]
    • Vector similarity (35% weight)
    • Recency decay (25% weight)
    • Keyword overlap (15% weight)
    • Graph centrality (10% weight)
    • Document type (10% weight)
    • Status weight (5% weight)
    ↓
[Step 3: Token Optimization]
    • Knapsack algorithm for token budget
    • Maximize relevance within limits
    • Progressive disclosure by importance
    ↓
[Step 4: Context Formatting]
    • Hierarchical structure
    • Clear section headers
    • Token usage statistics
    ↓
[Formatted Context → LLM Integration]
```

---

## Technical Specifications

### Directory Structure

```
my-project/
└── .sagadex/
    ├── config.json                 # Project configuration
    │
    ├── sagas/                      # VERSIONED WITH GIT
    │   ├── main/                   # Main branch sagas
    │   │   ├── problems/          # Bugs & solutions
    │   │   │   ├── active/        # Current investigations
    │   │   │   ├── resolved/      # Complete solutions
    │   │   │   └── lessons/       # Pitfalls to avoid
    │   │   ├── features/          # Feature development
    │   │   │   ├── active/        # In-progress
    │   │   │   ├── completed/     # Shipped features
    │   │   │   └── decisions/     # Design rationale
    │   │   ├── knowledge/         # Documentation
    │   │   │   ├── infrastructure/
    │   │   │   ├── local-env/
    │   │   │   └── admin/
    │   │   ├── configuration/     # Config & environment
    │   │   ├── operations/        # Commands & procedures
    │   │   ├── temporal/          # Time-sensitive info
    │   │   └── rules/             # Policies & standards
    │   └── [branch-name]/         # Branch-specific sagas
    │
    ├── index/                      # NOT VERSIONED (gitignored)
    │   ├── metadata.db            # SQLite database
    │   ├── vector_index.faiss     # FAISS binary index
    │   └── id_mapping.json        # Saga ID mapping
    │
    ├── cache/                      # Temporary files
    ├── logs/                       # Operation logs
    └── templates/                  # Saga templates
```

### Saga Document Format

#### Filename Convention
```
YYYY-MM-DD-HHMM-descriptive-title.md
Example: 2025-08-13-1430-jwt-timeout-fix.md
```

Local time is used (not UTC) to match developer's mental model of when work occurred.

#### Frontmatter Schema
```yaml
---
id: "saga-a4c3b1e8"                      # Unique ID
title: "Resolved JWT Timeout Issue"
type: "debugging"                        # debugging|feature|architecture|optimization
timestamp: "2025-08-13T14:30:00-07:00"   # ISO 8601 with timezone
status: "active"                         # active|archived|deprecated
tags: ["jwt", "auth", "redis", "timeout"]
severity: "critical"                     # critical|high|medium|low
outcome: "resolved"                      # resolved|mitigated|documented|failed
files_changed:
  - "app/Services/AuthService.php"
  - "app/Services/RedisLockProvider.php"
---

## Problem
[Description of the issue]

## Investigation
[Debugging journey and hypothesis testing]

## Solution
[Complete implementation with code]

## Lessons Learned
[Key takeaways and patterns]
```

### Database Schema

```sql
CREATE TABLE sagas (
    id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    saga_type TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    timestamp TEXT NOT NULL,
    tags TEXT,  -- JSON array
    content TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    embedding BLOB  -- Vector embedding
);

CREATE TABLE saga_relationships (
    source_id TEXT,
    target_id TEXT,
    relationship_type TEXT,
    PRIMARY KEY (source_id, target_id)
);

CREATE VIRTUAL TABLE sagas_fts USING fts5(
    title, content,
    content='sagas'
);
```

### Core Components

#### 1. AutoChronicler - Automated Capture Engine
```python
class AutoChronicler:
    """Multi-trigger automation with AI classification"""
    
    def calculate_significance(self, event):
        """Multi-factor significance scoring"""
        score = 0.0
        
        # File importance (config files = +0.3)
        if event.affects_critical_files():
            score += 0.3
            
        # Change magnitude (>10 lines = +0.2)
        if event.lines_changed > 10:
            score += 0.2
            
        # Keywords ("fix", "feature" = +0.3)
        if event.has_significance_keywords():
            score += 0.3
            
        # Event source (AI session = +0.2)
        if event.from_ai_session():
            score += 0.2
            
        return score
```

#### 2. SagaVectorDB - Local RAG Engine
```python
class SagaVectorDB:
    """Local vector database with semantic search"""
    
    def __init__(self):
        self.conn = sqlite3.connect('.sagadex/index/metadata.db')
        self.index = faiss.IndexFlatIP(768)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def search(self, query, k=25):
        """Semantic search with multi-signal ranking"""
        query_vector = self.encoder.encode(query)
        distances, indices = self.index.search(query_vector, k)
        return self._rank_results(indices, distances, query)
```

#### 3. ContextOptimizer - Token-Aware Selection
```python
class ContextOptimizer:
    """Optimizes context selection for token limits"""
    
    def optimize_selection(self, candidates, token_limit):
        """Knapsack optimization for maximum relevance"""
        # Sort by value density (relevance per token)
        sorted_candidates = sorted(
            candidates,
            key=lambda c: c.score / c.token_count,
            reverse=True
        )
        
        selected = []
        total_tokens = 0
        
        for candidate in sorted_candidates:
            if total_tokens + candidate.token_count <= token_limit:
                selected.append(candidate)
                total_tokens += candidate.token_count
                
        return selected
```

---

## Implementation Blueprint

### Technology Stack

```python
# Core Dependencies (100% Open Source)
dependencies = {
    "sentence-transformers": "2.2.2",  # Apache 2.0 - Embeddings
    "faiss-cpu": "1.7.4",              # MIT - Vector search
    "sqlite3": "built-in",             # Public Domain - Metadata
    "click": "8.1.7",                  # BSD - CLI framework
    "rich": "13.5.2",                  # MIT - Terminal UI
    "gitpython": "3.1.40",             # BSD - Git integration
    "watchdog": "3.0.0",               # Apache 2.0 - File watching
}

# Optional AI Providers
ai_providers = {
    "local": ["ollama", "llama.cpp"],
    "cloud": ["openai", "anthropic", "cohere"],
    "self-hosted": ["vllm", "text-generation-inference"]
}
```

### Performance Characteristics

| Saga Count | Search Time | Storage | Memory |
|------------|-------------|---------|---------|
| 50         | ~10ms       | 500KB   | 10MB    |
| 500        | ~15ms       | 5MB     | 50MB    |
| 5,000      | ~50ms       | 50MB    | 100MB   |
| 50,000     | ~200ms      | 500MB   | 500MB   |

### Cost Analysis

**Local Operation (Monthly)**:
- Electricity: ~$0.30-0.50
- Storage: Negligible (~10KB per saga)
- API Calls: $0 (all local)
- **Total: ~$0.50/month**

**Cloud Alternative Comparison**:
- Pinecone: $70+/month
- Weaviate Cloud: $25+/month
- OpenAI Embeddings: $0.13/million tokens
- **Sagadex saves 99%+ on operational costs**

---

## Usage Workflow

### My Daily Workflow

```bash
# Morning: Check what I worked on yesterday
$ saga log --since=yesterday
📅 Recent sagas:
- JWT timeout debugging (resolved)
- Theme system implementation (completed)
- Deployment configuration (updated)

# Starting work: Find relevant context
$ saga search "authentication timeout"
🔍 Found 3 relevant sagas from past debugging sessions

# During development: Auto-capture important moments
$ git commit -m "fix: resolve JWT race condition"
🎯 Auto-captured saga (significance: 0.85)

# Manual capture for important context
$ saga commit "Finally figured out the WebSocket memory leak"
✅ Saga created with full context

# End of day: Review and organize
$ saga status
📊 127 total sagas, 8 added this week
```

### Key Use Cases

1. **Debugging Memory**: Never solve the same bug twice
2. **Decision Tracking**: Remember why you chose specific approaches
3. **Onboarding Myself**: When returning to old projects
4. **Pattern Recognition**: Find similar problems across projects
5. **Knowledge Preservation**: Capture hard-won insights

---

## Development Timeline

### Phase 1: Core Foundation (Weeks 1-4)
- [x] Directory structure and configuration
- [x] SQLite schema implementation
- [x] Basic CLI framework
- [x] Manual saga creation

### Phase 2: Intelligence Layer (Weeks 5-8)
- [ ] Sentence transformer integration
- [ ] FAISS index management
- [ ] Semantic search implementation
- [ ] Multi-signal ranking algorithm

### Phase 3: Automation (Weeks 9-12)
- [ ] Git hooks integration
- [ ] Significance scoring
- [ ] Auto-classification system
- [ ] File watching implementation

### Phase 4: Polish & Launch (Weeks 13-16)
- [ ] Performance optimization
- [ ] Comprehensive testing
- [ ] Documentation completion
- [ ] Beta testing program
- [ ] Public launch

---

## Installation & Deployment

### Quick Start (2 minutes)

```bash
# Install via pip
pip install sagadex

# Initialize in your project
cd your-project
saga init

# Create your first saga
saga commit "Fixed authentication timeout issue"

# Search your knowledge
saga search "timeout"
```

### Installation Methods

**Python Users**:
```bash
pip install sagadex          # Standard
pipx install sagadex         # Isolated
```

**Non-Python Users**:
```bash
# macOS/Linux
brew install sagadex

# Windows
# Download sagadex-setup.exe (includes Python runtime)
```

**Offline Installation**:
```bash
# For air-gapped environments
# Download on internet-connected machine:
pip download sagadex --dest ./sagadex-offline
# Transfer folder and install:
pip install --no-index --find-links ./sagadex-offline sagadex
```

---

## Future Ideas (Maybe Someday)

### Potential Enhancements
- **Sharing**: Optional ability to share sagas with others
- **Team Sync**: Git-based collaboration for teams
- **IDE Integration**: VS Code extension for in-editor access
- **Advanced AI**: Support for different embedding models
- **Cross-Project Search**: Search across multiple repositories

### Success Metrics (Personal)
- **Search Success**: Finding what I need in <3 attempts
- **Time Saved**: At least 30 minutes per debugging session
- **Knowledge Retained**: Never losing important context again
- **Pattern Discovery**: Finding connections between problems

---

## Appendix: CLI Reference

### Core Commands

```bash
# Initialization
saga init                    # Initialize in current directory

# Creating Sagas
saga commit <message>        # Create saga from current context
saga import <file>          # Import existing documentation

# Searching
saga search <query>         # Semantic search
saga show <id>             # Display specific saga
saga log --since=<date>    # Chronological view

# Management
saga status                # Repository statistics
saga audit                 # Health check and cleanup
saga export --format=<fmt> # Export knowledge base

# Collaboration (Pro)
saga sync                  # Sync with cloud
saga share <id>           # Share to hub
saga team add <email>     # Add team member
```

### Interactive Mode

```bash
$ saga
🧠 Sagadex Interactive Mode

> /search authentication timeout
> /show 1
> /commit "Fixed race condition"
> /help
> /exit
```

---

## Appendix A: Example Sagas

### Bug Fix Saga
```markdown
---
id: "saga-jwt-fix-001"
title: "JWT Refresh Token Race Condition Fix"
type: "debugging"
timestamp: "2025-08-13T14:30:00-07:00"
status: "active"
tags: ["jwt", "auth", "race-condition", "redis"]
severity: "critical"
outcome: "resolved"
---

## Problem
Intermittent JWT timeouts in production causing user logouts during high traffic.

## Investigation
1. Analyzed server logs - found concurrent refresh requests
2. Identified race condition in token refresh logic
3. Tested Redis distributed lock solution

## Solution
```php
// Before: No concurrency control
public function refreshToken($token) {
    $decoded = JWT::decode($token);
    $newToken = $this->generateToken($decoded->user_id);
    $this->invalidateToken($token);
    return $newToken;
}

// After: Redis lock prevents race condition
public function refreshToken($token) {
    return Redis::lock('token-refresh-'.$userId, 10)->get(function() use ($token) {
        $decoded = JWT::decode($token);
        if ($this->isTokenBlacklisted($token)) {
            throw new TokenExpiredException();
        }
        $newToken = $this->generateToken($decoded->user_id);
        $this->blacklistToken($token);
        return $newToken;
    });
}
```

## Lessons Learned
- Always consider concurrency in authentication flows
- Redis locks are effective for distributed systems
- Monitor production logs for timing patterns
```

### Feature Development Saga
```markdown
---
id: "saga-dark-mode-001"
title: "Dark Mode Theme Implementation"
type: "feature"
timestamp: "2025-08-10T09:00:00-07:00"
status: "active"
tags: ["ui", "theme", "css", "user-experience"]
---

## Requirements
System-wide dark mode with instant switching and no FOUC.

## Implementation
```javascript
// Theme manager with localStorage persistence
const ThemeManager = {
    init() {
        const saved = localStorage.getItem('theme') || 'light';
        document.documentElement.dataset.theme = saved;
    },
    toggle() {
        const current = document.documentElement.dataset.theme;
        const next = current === 'light' ? 'dark' : 'light';
        document.documentElement.dataset.theme = next;
        localStorage.setItem('theme', next);
    }
};

// CSS variables approach
:root[data-theme="light"] {
    --bg-primary: #ffffff;
    --text-primary: #000000;
}

:root[data-theme="dark"] {
    --bg-primary: #1a1a1a;
    --text-primary: #ffffff;
}
```

## Testing Results
- ✅ No FOUC on any page
- ✅ Smooth transitions (200ms)
- ✅ Persistence across sessions
- ✅ Accessibility maintained
```

## Appendix B: Quick Start Examples

### First-Time Setup
```bash
# 1. Install Sagadex (one-time, ~90MB model download)
$ pip install sagadex
Downloading sentence-transformers model...
✅ Installation complete!

# 2. Initialize in your project
$ cd my-project
$ saga init
✅ Created .sagadex/ directory
✅ Initialized local database
✅ Git hooks installed

# 3. Import existing docs (optional)
$ saga import CLAUDE.md
📄 Importing existing documentation...
✅ Created 12 sagas from CLAUDE.md

# 4. Your first saga
$ saga commit "Implemented Redis caching for API responses"
✅ Saga created: 2025-08-14-1030-redis-caching-implementation.md

# 5. Search your knowledge
$ saga search "caching"
🔍 Found 3 relevant sagas:
1. redis-caching-implementation (0.95)
2. database-query-optimization (0.72)
3. cdn-setup-guide (0.61)
```

### Daily Workflow
```bash
# Morning: Review recent work
$ saga log --since=yesterday
📅 Recent activity:
- Fixed auth timeout issue
- Implemented dark mode
- Updated deployment scripts

# During debugging
$ saga search "similar timeout errors"
🔍 Found previous solution:
> JWT refresh race condition (3 weeks ago)
> Solution: Added Redis locks

# After fixing a bug
$ git commit -m "fix: resolve payment webhook timeout"
🎯 Sagadex: Auto-captured (significance: 0.85)
✅ Created saga: payment-webhook-timeout-fix.md

# End of day review
$ saga status
📊 Repository Statistics:
- Total sagas: 127
- This week: 8 new, 3 updated
- Most referenced: auth-system-architecture.md
- Token usage: 2.1MB index, 5.4MB content
```

## Appendix C: Frequently Asked Questions

### Privacy & Security

**Q: Is my code and context data private?**  
A: Yes. Core Sagadex is 100% local. Your data never leaves your machine unless you explicitly enable cloud features. Even then, cloud sync uses end-to-end encryption.

**Q: Can I use this with proprietary code?**  
A: Absolutely. Sagadex is designed for proprietary codebases. Use the local-only mode for complete data sovereignty.

### Technical

**Q: What's the actual performance impact?**  
A: Minimal. Search takes <100ms for most repos. Git hooks add <50ms to commits. Background indexing uses <1% CPU.

**Q: How does it compare to just using grep?**  
A: Sagadex uses semantic search. It finds conceptually related content, not just keyword matches. "auth bug" finds "login race condition" even without matching words.

**Q: Which AI models are supported?**  
A: All major providers (OpenAI, Anthropic, Cohere) plus local models (Ollama, llama.cpp). The core uses sentence-transformers locally - no API needed.

### Adoption

**Q: How long before I see value?**  
A: Immediately for search. Within a week, you'll have enough sagas for powerful knowledge retrieval. Most users report significant time savings within 2 weeks.

**Q: Can my team use this?**  
A: Yes. Sagas are just markdown files in your repo. Team members can read them without installing anything. If they want search capabilities, they can install Sagadex locally.

**Q: What if I want to stop using it?**  
A: Your sagas are markdown files in your repo. Export anytime with `saga export`. No lock-in, no data hostage.

## Project Status

- **Current Stage**: Personal tool specification
- **GitHub**: Will create repo when MVP is ready
- **Documentation**: This document + inline code comments
- **Usage**: Personal productivity tool first

---

*"Every debugging session teaches something worth remembering."*

**Sagadex - Never Lose Development Context Again**

---

## Appendix D: Context Butler Innovation (NEW BREAKTHROUGH!)

### The Context Butler System

The Context Butler is Sagadex's revolutionary approach to solving the LLM context problem. Instead of hoping Claude reads your CLAUDE.md file, the Butler actively prepares and injects optimal context.

#### How It Works

```python
class ContextButler:
    """
    Intelligent context preparation at near-zero cost
    Uses local models to avoid API expenses
    """
    
    def __init__(self):
        # Free components only
        self.git = GitAnalyzer()           # Git commands
        self.vectors = FAISSSearch()       # Local vectors  
        self.llm = TinyLlama()            # 638MB local model
        
    def prepare_session(self):
        # 1. Find where user left off (free - git)
        recent_work = {
            "branch": git.current_branch(),
            "last_commit": git.log("-1"),
            "modified_files": git.status(),
            "last_saga": get_most_recent_saga()
        }
        
        # 2. Find relevant context (free - vectors)
        # This searches 10,000 sagas in milliseconds
        similar_work = self.vectors.find_similar(
            query=recent_work,
            k=5  # Just top 5, not all 10,000!
        )
        
        # 3. Compress to 140 chars (free - local LLM)
        compressed = self.llm.compress(
            recent=recent_work,
            similar=similar_work,
            limit=140
        )
        
        # Output: "JWT:RedisLock|BUG#47:websocket|LAST:theme"
        return compressed
```

#### Cost Optimization Strategy

| Approach | Cost/Session | Quality | Speed |
|----------|-------------|---------|-------|
| Template-based | $0.00 | Good | <10ms |
| Local TinyLlama | $0.00 | Better | ~500ms |
| Local Llama2 | $0.00 | Best | ~2s |
| Claude API | ~$0.01 | Overkill | ~1s |

**Key: We NEVER use expensive models for context preparation!**

### Progressive Context Loading

Start minimal, expand on demand:

```bash
# Stage 1: Compressed start (140 chars)
"JWT:fix|BUG:websocket|LAST:theme|HOT:auth.php"

# Stage 2: User requests more
/context jwt
> Loading all JWT-related sagas...

# Stage 3: User requests specific
/context saga-892
> Loading complete debugging session...

# Stage 4: User cleans up
/forget old-stuff
> Freed 5,000 tokens
```

### Dual-Context System (Human + AI)

The meta-breakthrough: Sagadex updates BOTH your memory and Claude's:

```python
def load_context(query):
    context = search(query)
    
    # Update human (visual reminder)
    display_to_user(context)  # "Oh RIGHT, that's how!"
    
    # Update AI (same context)
    inject_to_claude(context)  # Claude knows too
    
    # Both intelligences synchronized!
```

### Implementation: Automated Claude Launch

```python
def launch_contextualized_claude():
    # 1. Butler prepares context
    context = ContextButler().prepare_session()
    
    # 2. Launch Claude Code
    claude = subprocess.Popen(['claude-code'])
    time.sleep(2)
    
    # 3. Force-feed context
    pyautogui.typewrite(f"PROJECT CONTEXT: {context}")
    pyautogui.press('enter')
    pyautogui.typewrite("Acknowledge context before proceeding.")
    pyautogui.press('enter')
    
    # 4. Claude MUST see context - we literally typed it!
```

### Why This Changes Everything

1. **Solves the CLAUDE.md problem** - No more hoping it reads files
2. **Near-zero cost** - Uses local models for preparation
3. **Intelligent compression** - 140 chars of pure relevance
4. **Progressive loading** - Start small, expand as needed
5. **Dual benefit** - Updates both human and AI understanding

### The Complete Flow

```
Git Status → Vector Search → Local LLM → 140 chars → Claude
     ↓            ↓              ↓           ↓          ↓
  Recent      Top 5 of       Compress    Inject    Ready!
   Work        10,000         to fit    directly
```

This innovation means:
- **You** remember what you were doing
- **Claude** knows what you were doing  
- **Nobody** pays for expensive context preparation
- **Everyone** starts with optimal context

The Context Butler is essentially using AI to solve the AI context problem, creating a beautiful recursive solution that costs almost nothing to run.

---

## Appendix E: Implementation Specifications

### Git Hook Implementation

```bash
#!/bin/bash
# .sagadex/hooks/post-commit
# Installed to .git/hooks/post-commit during saga init

# Get commit details
COMMIT_MSG=$(git log -1 --pretty=%B)
COMMIT_HASH=$(git rev-parse HEAD)
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD)

# Check significance
if saga-internal should-capture "$COMMIT_MSG" "$CHANGED_FILES"; then
    saga-internal auto-capture \
        --commit="$COMMIT_HASH" \
        --message="$COMMIT_MSG" \
        --files="$CHANGED_FILES" &
fi
```

### Vector Database Specifications

```python
# Exact model and dimensions
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_DIMENSIONS = 384  # NOT 768 - MiniLM-L6-v2 uses 384
INDEX_TYPE = faiss.IndexFlatIP  # Inner product for cosine similarity

# Index management
class IndexManager:
    def add_saga(self, saga):
        """Incremental index update"""
        embedding = self.encoder.encode(saga.content)
        self.index.add(embedding.reshape(1, -1))
        self.save_index()
    
    def rebuild_index(self):
        """Full rebuild from scratch"""
        # Triggered when: corruption detected, major version upgrade
        pass
```

### Claude Code Integration

```python
class ClaudeIntegration:
    def inject_context(self, context):
        """Try multiple methods in order"""
        
        # Method 1: Direct CLI if available
        if self.claude_cli_available():
            subprocess.run(['claude', '--context', context])
            return
        
        # Method 2: pyautogui with validation
        if self.can_use_pyautogui():
            pyautogui.typewrite(context)
            time.sleep(0.5)
            # Validate by checking window title
            if "Claude" in pyautogui.getActiveWindowTitle():
                return
        
        # Method 3: Clipboard + notification
        pyperclip.copy(context)
        print("Context copied to clipboard. Paste into Claude.")
```

### Session State Management

```python
# .sagadex/session/current.json
{
    "session_id": "uuid-here",
    "started": "2024-08-14T10:30:00Z",
    "context_loaded": [
        {"id": "saga-123", "tokens": 500, "type": "full"},
        {"id": "saga-456", "tokens": 200, "type": "summary"}
    ],
    "total_tokens": 700,
    "compressed_context": "JWT:fix|BUG:websocket|LAST:theme"
}
```

### Error Handling

```python
class SagaErrorHandler:
    def handle_git_errors(self):
        if repo.head.is_detached:
            # Use commit hash as branch name
            branch = repo.head.commit.hexsha[:8]
        
    def handle_merge_conflicts(self):
        # Sagas from both branches kept
        # Add conflict marker in merged saga
        pass
    
    def handle_corrupt_index(self):
        # Auto-rebuild from sagas
        logger.warning("Index corrupted, rebuilding...")
        self.rebuild_index_from_scratch()
```

### Import Strategy for Existing Docs

```python
class CLAUDEImporter:
    def import_file(self, filepath):
        content = Path(filepath).read_text()
        
        # Split by common patterns
        sections = self.split_by_patterns(content, [
            r'^#{1,3}\s+',  # Markdown headers
            r'^\d{4}-\d{2}-\d{2}',  # Date stamps
            r'^---+$',  # Horizontal rules
        ])
        
        for section in sections:
            # Extract date if present
            date = self.extract_date(section) or datetime.now()
            
            # Generate saga
            saga = Saga(
                title=self.extract_title(section),
                content=section,
                timestamp=date,
                tags=self.auto_tag(section)
            )
            
            # Check duplicates
            if not self.is_duplicate(saga):
                self.save_saga(saga)
```

---

END OF MASTER DOCUMENT