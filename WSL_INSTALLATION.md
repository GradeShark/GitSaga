# SagaShark WSL Installation Guide

This guide explains how to install and use SagaShark in Windows Subsystem for Linux (WSL) when SagaShark is already installed on Windows.

## Prerequisites
- SagaShark installed on Windows (in `C:\Users\[username]\OneDrive\Documents\SagaShark`)
- WSL with Python 3 installed
- Access to Windows filesystem from WSL (via `/mnt/c/`)

## Installation Steps

### 1. Create the Wrapper Script

Create a file `~/saga.sh` in your WSL home directory:

```bash
nano ~/saga.sh
```

Add the following content:

```bash
#!/bin/bash
# SagaShark WSL Wrapper Script
# Runs Windows SagaShark from WSL environment

# Set Python path to find SagaShark modules
export PYTHONPATH=/mnt/c/Users/h444n/OneDrive/Documents/SagaShark/src:$PYTHONPATH

# Run SagaShark as a Python module (handles relative imports correctly)
python3 -m sagashark.cli "$@"
```

**Important**: Do NOT include a `cd` command in the wrapper - it should use your current directory.

### 2. Make the Script Executable

```bash
chmod +x ~/saga.sh
```

### 3. Create an Alias

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
echo "alias saga='~/saga.sh'" >> ~/.bashrc
source ~/.bashrc
```

### 4. Test the Installation

```bash
# Navigate to your project
cd /home/[username]/your-project

# Initialize SagaShark
saga init

# Install git hooks for automatic capture
saga install-hooks
```

## Common Issues and Solutions

### Issue: "attempted relative import with no known parent package"
**Solution**: Make sure the wrapper uses `python3 -m sagashark.cli` instead of calling `cli.py` directly.

### Issue: SagaShark detects wrong directory (.sagashark in source folder)
**Solution**: Remove any `cd` commands from the wrapper script. The wrapper should operate in your current directory.

### Issue: Import errors
**Solution**: Verify the PYTHONPATH is correctly set to the `src` directory:
```bash
export PYTHONPATH=/mnt/c/Users/[username]/OneDrive/Documents/SagaShark/src:$PYTHONPATH
```

### Issue: Permission denied
**Solution**: Make sure the wrapper script is executable:
```bash
chmod +x ~/saga.sh
```

## Usage Example

Once installed, SagaShark works exactly like the Windows version:

```bash
# Create a saga
saga commit "Fixed database connection issue"

# Search for sagas
saga search "timeout"

# Enhance a commit with debugging details
saga enhance HEAD

# Organize sagas into date hierarchy
saga organize

# View recent sagas
saga log --since=7d
```

## Auto-Organization Feature

SagaShark v2 includes automatic organization of sagas into a date-based hierarchy:

```
.sagashark/sagas/
├── 2024/
│   ├── 01-January/
│   │   ├── week-01/
│   │   └── week-02/
│   └── 02-February/
└── 2025/
    └── 01-January/
        └── week-03/
```

To organize existing sagas:
```bash
# Preview changes
saga organize --dry-run

# Apply organization
saga organize --cleanup
```

## Updating SagaShark

When SagaShark is updated on Windows, the changes are immediately available in WSL:

```bash
# On Windows (or from WSL)
cd /mnt/c/Users/[username]/OneDrive/Documents/SagaShark
git pull origin main

# Changes are immediately available in WSL - no reinstallation needed!
```

## Benefits of This Setup

1. **Single Installation**: Maintain one SagaShark installation used by both Windows and WSL
2. **Immediate Updates**: Changes to SagaShark code are instantly available in both environments
3. **Shared Sagas**: Both environments can access the same saga database
4. **No Sudo Required**: Works entirely in user space
5. **Cross-Platform Development**: Perfect for projects that span Windows and WSL

## Troubleshooting

If you encounter issues:

1. Verify Python 3 is installed: `python3 --version`
2. Check the wrapper script path: `cat ~/saga.sh`
3. Verify PYTHONPATH: `echo $PYTHONPATH`
4. Test module import: `python3 -c "import sys; sys.path.insert(0, '/mnt/c/Users/h444n/OneDrive/Documents/SagaShark/src'); import sagashark"`

## Credits

This WSL integration method was developed through collaboration between Builder (Windows) and Helper (WSL) using a cross-environment chat system, demonstrating the first documented case of two Claude instances working together across different operating environments.