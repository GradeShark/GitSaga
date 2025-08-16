# SagaShark Installation & Testing Guide

## 🚀 Quick Install & Test

### 1. Install SagaShark
```bash
# From the sagashark directory:
pip install -e .

# Or for a clean install:
pip install .
```

### 2. Test in Your Repository
```bash
# Navigate to any git repository
cd /path/to/your/project

# Initialize SagaShark
saga init
# (It will prompt to set up AI features - say yes!)

# Test manual saga creation
saga commit "Testing SagaShark installation"

# Test automatic capture from recent commits
saga monitor --since HEAD~5

# Score your last commit
saga score HEAD

# Install git hooks for auto-capture
saga install-hooks

# Make a test commit to trigger auto-capture
git add .
git commit -m "fix: Testing automatic saga capture"

# Search your sagas
saga search "test"

# View all sagas
saga log
```

## 📦 What Gets Installed

### Core Dependencies (Required)
- `click` - CLI framework
- `gitpython` - Git integration
- `rich` - Beautiful terminal output
- `pyyaml` - Configuration files
- `python-dateutil` - Date handling

### AI Dependencies (Auto-installed)
- `dspy-ai` - Structure enforcement
- `ollama` - Python client for Ollama
- `faiss-cpu` - Vector search
- `sentence-transformers` - Text embeddings

### External Tools (Optional, auto-setup on first run)
- **Ollama server** - Downloaded and installed if you choose
- **TinyLlama model** - 638MB, downloaded on first AI use

## 🧪 Testing Features

### Test Significance Scoring
```bash
# Create commits with different patterns
git commit -m "fix: Critical authentication bug causing user lockouts"
saga score HEAD  # Should score high

git commit -m "chore: Update README"
saga score HEAD  # Should score low
```

### Test Automatic Capture
```bash
# Monitor your last 10 commits
saga monitor --dry-run  # Preview what would be captured
saga monitor            # Actually capture significant ones
```

### Test Templates
```bash
# Generate a debugging template
saga template debugging > debug.md

# Generate and fill a feature template
saga template feature --output feature.md
```

### Test Vector Search (if installed)
```bash
# Build search index
saga reindex

# Find similar sagas
saga find-similar <saga-id>

# Search semantically
saga search "performance issues with database"
```

## 🔧 Troubleshooting

### If Ollama doesn't auto-install:
```bash
# Manual setup
saga setup-ai

# Or install Ollama directly:
# Windows: winget install Ollama.Ollama
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.ai/install.sh | sh
```

### If vector search isn't working:
```bash
# Ensure dependencies are installed
pip install faiss-cpu sentence-transformers

# Rebuild index
saga reindex
```

### Windows encoding issues:
```bash
# Use the wrapper (already set as default)
saga --help  # Should work without encoding errors
```

## ✅ Verify Installation

Run this checklist:
```bash
saga --version           # Should show version
saga --help             # Should list all commands
saga init               # Should initialize in current directory
saga commit "test"      # Should create a saga
saga search "test"      # Should find your saga
saga status            # Should show repository stats
```

## 🎯 Next Steps

1. **Set up git hooks**: `saga install-hooks`
2. **Import existing commits**: `saga monitor --since HEAD~50`
3. **Customize settings**: Edit `.sagashark/config.json`
4. **Create your first real saga** after debugging something!

## 💡 Pro Tips

- SagaShark works great without AI, but AI makes it magical
- Run `saga capture --force` after any significant debugging session
- Use `saga template debugging` to document complex bugs
- The more sagas you create, the better the search becomes

---

Ready to preserve those "Pokemon catching" debugging moments! 🎉