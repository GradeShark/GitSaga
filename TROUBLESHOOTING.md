# GitSaga Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### "saga: command not found"
**Problem**: After installing GitSaga, the `saga` command isn't recognized.

**Solutions**:
1. Ensure GitSaga is installed: `pip show gitsaga`
2. If using virtual environment, make sure it's activated
3. Try using the full module path: `python -m gitsaga.cli`
4. Reinstall with: `pip install -e .` (from the gitsaga directory)

#### PowerShell Console Flashing
**Problem**: A new console window briefly appears and disappears when running saga commands.

**Solution**: This has been fixed in v2.0.0. If you still experience it:
1. Update to the latest version
2. Use the PowerShell alias installer: `powershell .\install-powershell-alias.ps1`

### Ollama/AI Issues

#### "Ollama not found" or AI features not working
**Problem**: GitSaga can't find Ollama even though it's installed.

**Solutions**:
1. **Windows**: Restart PowerShell after Ollama installation
2. Check Ollama is running: `ollama --version`
3. Pull TinyLlama model: `ollama pull tinyllama`
4. If Ollama command not found:
   ```powershell
   # Add to PATH manually or use full path:
   & "C:\Users\[YourUsername]\AppData\Local\Programs\Ollama\ollama.exe" pull tinyllama
   ```

#### DSPy warnings appearing constantly
**Problem**: "DSPy not available" messages spam the console.

**Solution**: Fixed in v2.0.0. The warnings now only appear when actually needed.

### Saga Capture Issues

#### "Commit not significant enough for saga capture"
**Problem**: GitSaga isn't capturing your commits automatically.

**Solutions**:
1. Check significance score: `saga score HEAD`
2. Use keywords like "fix", "resolved", "debug" in commit messages
3. Force capture: `saga capture --force`
4. Lower threshold in code if needed (default: 0.3)

#### Interactive prompts not appearing
**Problem**: High-value commits don't trigger the interactive prompts.

**Solutions**:
1. Ensure you're in an interactive terminal (not CI/CD)
2. Check git hooks are installed: `saga install-hooks`
3. Manually enhance: `saga enhance HEAD`

### Search Issues

#### Search not finding sagas
**Problem**: `saga search` returns no results even though sagas exist.

**Solutions**:
1. Check saga directory: `ls .gitsaga/sagas/`
2. Verify search is looking in right place: `saga status`
3. Try broader search terms
4. Rebuild search index (delete `.gitsaga/index/` and search again)

#### Vector search not working
**Problem**: Semantic search features unavailable.

**Solution**: 
1. Install sentence-transformers: `pip install sentence-transformers`
2. GitSaga will fall back to text search automatically (which works well)

### Directory Issues

#### Sagas saving to wrong location
**Problem**: Some sagas in `.gitsaga/`, others in `.sagadex/`.

**Solution**: Fixed in v2.0.0. All sagas now save to `.gitsaga/sagas/`.
- Remove old directory: `rm -rf .sagadex`
- Move any important sagas: `mv .sagadex/sagas/* .gitsaga/sagas/`

### Windows-Specific Issues

#### Unicode/Encoding Errors
**Problem**: UnicodeEncodeError when running saga commands.

**Solutions**:
1. Set environment variable: `$env:PYTHONIOENCODING = "utf-8"`
2. Or add to PowerShell profile permanently:
   ```powershell
   Add-Content $PROFILE "`n`$env:PYTHONIOENCODING = 'utf-8'"
   ```

#### "The term 'saga' is not recognized"
**Problem**: Windows doesn't recognize the saga command.

**Solutions**:
1. Use the batch wrapper: `saga.bat` (in the gitsaga directory)
2. Or create an alias in PowerShell:
   ```powershell
   function saga { python -m gitsaga.cli $args }
   ```

### Git Hook Issues

#### Hooks not triggering
**Problem**: Commits don't trigger automatic saga capture.

**Solutions**:
1. Verify hooks installed: `ls .git/hooks/post-commit`
2. Reinstall hooks: `saga install-hooks`
3. Check hook has execute permission (Unix): `chmod +x .git/hooks/post-commit`
4. Test manually: `python .git/hooks/post-commit`

## Getting Help

If these solutions don't resolve your issue:

1. Check the [GitHub Issues](https://github.com/yourusername/gitsaga/issues)
2. Run with verbose output: `saga --debug [command]`
3. Check Python version compatibility: `python --version` (requires 3.8+)
4. Verify all dependencies: `pip list | grep -E "gitsaga|click|rich|gitpython"`

## Quick Fixes

### Reset GitSaga completely:
```bash
rm -rf .gitsaga
saga init
saga install-hooks
```

### Reinstall with all dependencies:
```bash
pip uninstall gitsaga -y
cd /path/to/gitsaga
pip install -e ".[all]"
```

### Test basic functionality:
```bash
saga --version
saga status
echo "test" | saga commit "Test saga"
saga search "test"
```