# Changelog

All notable changes to SagaShark will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-15

### Added
- **Automatic Saga Capture**: Intelligent significance scoring (0.3-1.0) automatically captures important commits
- **Interactive Debugging Prompts**: High-value commits trigger prompts for root cause, solution explanation, and lessons learned
- **Weighted Quality Scoring**: Prioritizes reproducible solutions (code: 35%, explanation: 30%, root cause: 25%)
- **`saga enhance` Command**: Add debugging details to any commit after the fact
- **Git Hook Integration**: Post-commit hook for automatic capture
- **Ollama/TinyLlama Support**: Optional local AI enhancement (100% private)
- **DSPy Integration**: Structured saga generation with consistent quality
- **FAISS Vector Search**: Semantic similarity search (when dependencies available)
- **Auto-installer**: Zero-friction setup for Ollama and models
- **MCP Server**: Model Context Protocol server for Claude integration
- **Rich CLI Interface**: Beautiful formatting, progress indicators, and helpful prompts

### Changed
- **Directory Structure**: All sagas now consistently save to `.sagashark/sagas/` (removed `.sagadex`)
- **Significance Thresholds**: Bug fixes score 0.70+, critical issues score 1.00
- **Banner Display**: Now shows only once per session instead of every command
- **Error Handling**: Graceful fallbacks when AI features unavailable
- **Windows Compatibility**: Fixed encoding issues and PowerShell console flashing

### Fixed
- Interactive capture bug causing UnboundLocalError
- Directory inconsistency between `.sagashark` and `.sagadex`
- Windows Unicode encoding errors
- PowerShell console flashing issue
- DSPy warning spam

### Removed
- `.sagadex` directory usage (consolidated to `.sagashark`)

## [1.0.0] - 2024-01-01

### Added
- Initial release
- Basic saga creation and search
- Manual documentation capture
- Git integration for context
- Text-based search
- Simple CLI interface