# Changelog

All notable changes to GitSaga will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-08-14

### Added
- Initial MVP release of GitSaga
- Core saga management system with markdown storage
- CLI commands: `init`, `commit`, `search`, `log`, `show`, `status`
- Text-based search with multi-factor relevance scoring
- Git integration for branch and file context
- ANSI Shadow ASCII art banner (like Claude Code)
- Windows compatibility with UTF-8 encoding support
- Rich terminal UI with tables and colored output
- Saga types: debugging, feature, architecture, optimization
- Tag system for categorization
- Branch-aware saga organization
- Configuration system with `.gitsaga/config.json`

### Technical Details
- Built with Python 3.8+, Click, and Rich
- 100% local operation - no cloud dependencies
- Git-native storage using markdown with YAML frontmatter
- Zero database requirement - just files and folders

### Known Issues
- Vector/semantic search not yet implemented
- No automatic saga capture from git commits
- No Context Butler for AI integration
- Manual saga creation only

### Contributors
- Initial implementation by Claude Code

---

## Roadmap

### [0.2.0] - Planned
- Add FAISS vector search with sentence-transformers
- Implement git hooks for auto-capture
- Add significance scoring for automatic saga creation
- Import existing documentation (CLAUDE.md files)

### [0.3.0] - Planned  
- Context Butler with TinyLlama integration
- Progressive context loading
- Claude Code integration
- Export functionality

### [1.0.0] - Future
- Full semantic search
- Team collaboration features
- Cloud backup (optional)
- VS Code extension