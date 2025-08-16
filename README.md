# SagaShark v2 - Track the Story Behind Your Code 🦈

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/GradeShark/SagaShark)
[![Python](https://img.shields.io/badge/python-3.8+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-purple)](LICENSE)

SagaShark is a local-first development context manager that automatically captures and retrieves debugging solutions from your git history. It creates a searchable knowledge base of your debugging sessions, making that "I fixed this before" moment actually useful.

**v2 Highlights**: Automatic capture with intelligent scoring, interactive debugging prompts, weighted quality system prioritizing reproducible solutions.

## Key Features

### 🎯 Intelligent Automatic Capture
- **Significance Scoring**: Automatically detects important commits (bug fixes score 0.70+, critical issues 1.00)
- **Interactive Prompts**: For high-value commits, prompts for root cause, solution explanation, and lessons learned
- **Weighted Quality System**: Prioritizes actual code (35%), solution explanation (30%), root cause (25%)

### 🔍 Powerful Search & Retrieval  
- **Text Search**: Lightning-fast keyword search across all sagas
- **Relevance Scoring**: Results ranked by match quality
- **Context Preservation**: Full git context, diffs, and file changes included

### 🤖 Optional AI Enhancement

⚠️ **CRITICAL WARNING**: Small LLMs (under 7B parameters) like TinyLlama can **hallucinate and corrupt your sagas** with false information. SagaShark now defaults to `use_ai=False` for safety. Only enable AI with larger models (7B+ parameters recommended).

- **Local LLM Support**: Ollama with 7B+ parameter models ONLY
- **Structured Generation**: DSPy ensures consistent formatting
- **Graceful Fallback**: Works perfectly without AI, enhanced with reliable models only

### ⚡ Zero-Friction Experience
- **Git Hook Integration**: Automatic capture on commit
- **Single Command Setup**: `saga init` handles everything
- **Beautiful CLI**: Rich formatting, progress indicators, helpful prompts

## Quick Start

### Installation

```bash
# Install from source (PyPI package coming soon)
git clone https://github.com/GradeShark/SagaShark.git
cd SagaShark
pip install -e .

# That's it! SagaShark will offer to set up AI features on first run
# Or manually set up AI anytime with:
saga setup-ai
```

**For WSL Users**: See [WSL_INSTALLATION.md](WSL_INSTALLATION.md) for cross-environment setup instructions.

### Basic Usage

```bash
# One-time setup in your project
cd your-project
saga init        # Creates .sagashark/ directory
saga install-hooks  # Enables automatic capture

# That's it! Now SagaShark works automatically:
git commit -m "fix: Resolved database connection timeout"
# SagaShark detects this is significant (score: 0.70) and prompts:
#   > What was the ROOT CAUSE?
#   > WHY does this fix work?
#   > Key lesson for next time?

# Search past solutions
saga search "timeout"        # Find all timeout-related sagas
saga search "connection pool" # Find specific issues

# Enhance commits with debugging details
saga enhance HEAD  # Add root cause & lessons to last commit
saga enhance abc123  # Enhance specific commit

# View recent debugging sessions
saga log
saga log --since=7d  # Last week's sagas

# Manual capture for important context
saga commit "Architecture: Switched to event-driven design"
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
└── .sagashark/
    ├── config.json        # SagaShark configuration
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
Initialize SagaShark in the current repository.

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

**Note**: SagaShark automatically offers to set up AI on first run. The setup is completely optional - SagaShark works great without it, but AI features provide richer, more structured sagas.

### Interactive Capture for High-Value Debugging

When SagaShark detects a significant debugging commit (e.g., "fix", "resolved", "finally"), it **automatically prompts** for the critical information that makes documentation truly valuable:

1. **Root Cause** (25% weight) - The actual underlying problem, not just symptoms
2. **Why the Fix Works** (30% weight) - The reasoning behind the solution for reproducibility
3. **Actual Code Diff** (35% weight) - The concrete solution you can copy/paste
4. **Lessons Learned** (10% weight) - Key takeaways to prevent recurrence

The weighting system ensures sagas without clear, reproducible solutions score poorly. Together, the **code + explanation represent 65%** of the quality score, prioritizing what you need to quickly implement fixes in other projects.

### `saga capture`
Manually capture a saga from any commit.

Options:
- `--commit`: Specify commit (default: HEAD)
- `--force`: Force capture even if not significant

### `saga enhance [commit]`
Add high-value debugging details to a commit (root cause, lessons learned, why the fix works).

Usage:
- `saga enhance` - Enhance the last commit (HEAD)
- `saga enhance abc123` - Enhance a specific commit

This command prompts you for the critical information that makes sagas valuable:
- **Root Cause**: What was the actual problem (not just symptoms)?
- **Failed Attempts**: What solutions didn't work?
- **Why It Works**: Why does this fix solve the problem?
- **Lessons Learned**: What will you do differently next time?

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

## Uninstalling

To uninstall SagaShark:
```bash
# Quick uninstall
pip uninstall sagashark

# For complete cleanup instructions
saga uninstall-help

# Or use the uninstall script
python path/to/sagashark/uninstall.py --keep-sagas
```

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

SagaShark is in early development. Contributions, ideas, and feedback are welcome!

## License

MIT License - See LICENSE file for details

## Why SagaShark?

Every debugging session teaches something worth remembering. SagaShark ensures that knowledge isn't lost when you close your terminal. It's like having perfect memory for your development journey.

**Never debug the same problem twice.**

## Revolutionary Insights: Living Documents & AI Context

### 📝 Living Documents, Not Frozen Commits
Traditional git commits are frozen in time. SagaShark creates **editable markdown files** you can enhance forever:
- Open any saga in your IDE and journal directly - no commands needed
- Add debugging notes during investigation
- Append post-mortem lessons after resolution  
- Document verification steps that actually worked
- Your `.sagashark/sagas/` folder becomes a lab notebook that writes itself, then grows with your insights

### 🚀 10x Faster AI Context Retrieval
SagaShark transforms git from sequential archive to **parallel-accessible knowledge base**:

**Without SagaShark**: Sequential, slow access
```bash
git log                    # Find commits
git show abc123            # View one at a time
git show def456            # Repeat for each...
# Result: Slow, token-intensive for AI assistants
```

**With SagaShark**: Parallel, instant access
```bash
saga search "authentication"     # ALL auth work ever, instantly
ls .sagashark/sagas/2025/08/week-*  # Entire week's context at once
grep -r "timeout" .sagashark/sagas  # Every timeout issue, immediately
```

AI assistants can now consume your **entire debugging history** in one operation instead of dozens of sequential git commands. This is game-changing for AI-assisted development.

### 🎯 The Real Value
SagaShark's killer feature isn't AI enhancement - it's **structural optimization**:
1. Turns frozen commits into living documents for human journaling
2. Turns sequential git into parallel-accessible context for AI assistants
3. Template-based approach ensures accuracy without AI risks
4. Year/month/week organization makes context retrieval trivial

**SagaShark: Git history optimized for both human editing and AI consumption.**