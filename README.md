# GitSaga - Track the Story Behind Your Code

GitSaga is a local-first development context manager that captures and retrieves the stories behind your code. It helps you remember debugging journeys, architectural decisions, and implementation patterns that typically get lost between coding sessions.

## Features

- **📝 Capture Development Context**: Create "sagas" to document debugging sessions, feature implementations, and architectural decisions
- **🤖 Automatic Capture (v2)**: Auto-detects significant commits and creates sagas using AI
- **🔍 Smart Search**: Find relevant past solutions with text-based search (semantic search coming soon)
- **🌿 Git Integration**: Automatically captures branch context and modified files
- **💯 100% Local**: No cloud dependencies, your data stays on your machine
- **⚡ Fast & Simple**: Lightweight CLI with instant search across hundreds of sagas
- **🎯 DSPy Structure**: Enforces complete documentation with AI-powered templates

## Quick Start

### Installation

```bash
# Install from source (PyPI package coming soon)
git clone https://github.com/yourusername/gitsaga.git
cd gitsaga
pip install -e .

# That's it! GitSaga will offer to set up AI features on first run
# Or manually set up AI anytime with:
saga setup-ai
```

### Basic Usage

```bash
# Initialize GitSaga in your project
cd your-project
saga init

# Create your first saga
saga commit "Fixed JWT timeout issue in Redis session handler"

# Search your sagas
saga search "timeout"
saga search "redis race condition"

# View recent sagas
saga log
saga log --since=yesterday

# Show a specific saga
saga show saga-a4c3b1e8
```

## Core Concepts

### What is a Saga?

A saga is a markdown document that captures the context around a piece of development work. Each saga includes:

- **Title**: Brief description of what was done
- **Content**: Detailed explanation, code snippets, lessons learned
- **Metadata**: Branch, timestamp, modified files, tags
- **Type**: debugging, feature, architecture, or optimization

### Directory Structure

```
your-project/
└── .gitsaga/
    ├── config.json        # GitSaga configuration
    ├── sagas/            # Your saga documents (git-tracked)
    │   ├── main/         # Sagas from main branch
    │   │   ├── debugging/
    │   │   ├── feature/
    │   │   └── architecture/
    │   └── feature-auth/ # Sagas from feature branches
    └── index/            # Search index (git-ignored)
```

## CLI Commands

### `saga init`
Initialize GitSaga in the current repository.

### `saga commit <message>`
Create a new saga with the given message as the title.

Options:
- `--type`: Specify saga type (debugging, feature, architecture, optimization)
- `--tags`: Add comma-separated tags
- `--content`: Provide content directly (otherwise prompts interactively)

### `saga search <query>`
Search for sagas matching the query.

Options:
- `--limit`: Maximum number of results (default: 5)

### `saga log`
Show recent sagas chronologically.

Options:
- `--limit`: Number of sagas to show (default: 10)
- `--since`: Show sagas since date (YYYY-MM-DD, "yesterday", "week", "month")

### `saga show <id>`
Display the full content of a specific saga.

### `saga status`
Show repository statistics and recent activity.

## V2 Features (Automatic Capture)

**Note**: GitSaga automatically offers to set up AI on first run. The setup is completely optional - GitSaga works great without it, but AI features provide richer, more structured sagas.

### `saga capture`
Manually capture a saga from any commit.

Options:
- `--commit`: Specify commit (default: HEAD)
- `--force`: Force capture even if not significant

### `saga monitor`
Analyze recent commits and auto-capture significant ones.

Options:
- `--since`: Analyze commits since (default: HEAD~10)
- `--dry-run`: Preview without saving

### `saga score <commit>`
Check a commit's significance score for saga capture.

### `saga template <type>`
Generate a saga template (debugging, feature, incident).

Options:
- `--output`: Save to file instead of displaying

### `saga validate <file>`
Check saga completeness and get improvement suggestions.

### `saga install-hooks`
Install git hooks for automatic saga capture on commit.

### `saga setup-ai`
One-command setup for AI features (installs Ollama + downloads model).

## Example Workflow

```bash
# Morning: Check what you worked on yesterday
$ saga log --since=yesterday
📅 Recent activity:
- Fixed JWT timeout issue
- Implemented Redis distributed locks
- Updated deployment configuration

# Start debugging a problem
$ saga commit "Investigating WebSocket memory leak"
# ... work on the problem ...

# Document the solution
$ saga commit "WebSocket memory leak - solved with connection pooling" \
  --type=debugging \
  --tags="websocket,memory,performance"

# Later: Find that solution again
$ saga search "websocket memory"
🔍 Found: websocket-memory-leak-fix.md (score: 15.5)
```

## Saga Example

```markdown
---
id: saga-jwt-fix-001
title: JWT Refresh Token Race Condition Fix
type: debugging
timestamp: 2024-01-15T14:30:00
branch: main
tags: [jwt, auth, race-condition, redis]
files_changed: [auth.py, redis_handler.py]
---

## Problem
Intermittent JWT timeouts in production causing user logouts during high traffic.

## Investigation
1. Analyzed server logs - found concurrent refresh requests
2. Identified race condition in token refresh logic
3. Tested Redis distributed lock solution

## Solution
Implemented Redis distributed lock to prevent concurrent token refreshes:
- Added 10-second lock timeout
- Proper error handling for lock failures
- Monitoring for lock contention

## Lessons Learned
- Always consider concurrency in authentication flows
- Redis locks are effective for distributed systems
- Monitor production logs for timing patterns
```

## Future Roadmap

### Phase 2: Semantic Search
- FAISS vector database for semantic search
- Find conceptually related sagas even without keyword matches

### Phase 3: Auto-Capture
- Git hooks for automatic saga creation
- Significance scoring to filter noise

### Phase 4: Context Butler
- AI-powered context compression
- Smart context injection for coding sessions

## Contributing

GitSaga is in early development. Contributions, ideas, and feedback are welcome!

## License

MIT License - See LICENSE file for details

## Why GitSaga?

Every debugging session teaches something worth remembering. GitSaga ensures that knowledge isn't lost when you close your terminal. It's like having perfect memory for your development journey.

**Never debug the same problem twice.**