# SagaShark Folder Rename Instructions

## Context
The local development folder is currently named `gitsaga` but needs to be renamed to `SagaShark` for brand consistency. This folder is locked by the current Claude session and cannot be renamed while in use.

## Prerequisites
1. Ensure all changes are committed (already done)
2. Close any terminals/editors using the `gitsaga` folder
3. Close the current Claude Code session

## Step-by-Step Rename Process

### Step 1: Navigate to Parent Directory
```bash
cd C:\Users\h444n\OneDrive\Documents
```

### Step 2: Rename the Folder
```bash
# Windows Command Prompt or PowerShell:
rename gitsaga SagaShark

# OR in Git Bash:
mv gitsaga SagaShark
```

### Step 3: Enter the Renamed Folder
```bash
cd SagaShark
```

### Step 4: Verify Git Still Works
```bash
git status
git remote -v
# Should show: https://github.com/GradeShark/SagaShark.git
```

### Step 5: Test SagaShark CLI
```bash
# Test the CLI still works
python -m src.sagashark.cli status

# Or if installed with pip:
saga status
```

### Step 6: Update WSL Wrapper (if applicable)
If Helper (WSL Claude) needs access, update `~/saga.sh` in WSL:
```bash
# Edit the wrapper script
nano ~/saga.sh

# Change this line:
export PYTHONPATH=/mnt/c/Users/h444n/OneDrive/Documents/gitsaga/src:$PYTHONPATH

# To:
export PYTHONPATH=/mnt/c/Users/h444n/OneDrive/Documents/SagaShark/src:$PYTHONPATH
```

### Step 7: Update Any Shortcuts
- Update any desktop shortcuts
- Update VS Code workspace if saved
- Update terminal bookmarks/aliases

## Verification Checklist
- [ ] Folder successfully renamed to SagaShark
- [ ] Git commands work (status, push, pull)
- [ ] SagaShark CLI works (`saga status`)
- [ ] Can create new sagas
- [ ] WSL wrapper updated (if using)

## Troubleshooting

### If "Device or resource busy" error:
1. Close ALL programs using the folder:
   - Claude Code sessions
   - VS Code
   - Terminal windows
   - File Explorer windows
2. Try again

### If Git doesn't work after rename:
```bash
# Git remotes are URL-based, should work fine
# But if needed, update remote:
git remote set-url origin https://github.com/GradeShark/SagaShark.git
```

### If Python imports fail:
```bash
# Reinstall in development mode
cd C:\Users\h444n\OneDrive\Documents\SagaShark
pip install -e .
```

## Success Confirmation
Once renamed, you should see:
- Folder: `C:\Users\h444n\OneDrive\Documents\SagaShark\`
- Git works normally
- `saga status` shows SagaShark banner
- All sagas in `.sagashark/sagas/` are accessible

## Note
The folder name is purely cosmetic for local development. End users who clone from GitHub will automatically get a folder named `SagaShark`.