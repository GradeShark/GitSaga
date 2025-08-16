# Installing Ollama for SagaShark AI Features

SagaShark works great without AI, but if you want enhanced saga generation and structured documentation, you can install Ollama and TinyLlama.

## Quick Install (Windows)

### Option 1: Download Installer (Recommended)
1. Go to https://ollama.com/download/windows
2. Download and run OllamaSetup.exe
3. After installation, open a new terminal and run:
   ```bash
   ollama pull tinyllama
   ```

### Option 2: Using winget
```bash
winget install Ollama.Ollama
# Then:
ollama pull tinyllama
```

## Verify Installation

After installing, test it:

```bash
# Check Ollama is installed
ollama --version

# Check TinyLlama is downloaded
ollama list

# Test SagaShark with AI
saga capture --commit HEAD
```

## What You Get With AI

Without AI:
- Basic saga capture from commit messages
- Simple templates
- Manual documentation

With AI (Ollama + TinyLlama):
- Structured saga generation
- Automatic symptom/root cause/solution extraction
- Enhanced templates based on commit context
- Better search relevance

## Troubleshooting

If `ollama` command not found after install:
1. Close and reopen your terminal
2. Or add to PATH: `C:\Users\[YourUsername]\AppData\Local\Programs\Ollama`

If TinyLlama download fails:
- Make sure Ollama service is running: `ollama serve`
- Try again: `ollama pull tinyllama`

## Space Requirements
- Ollama: ~500MB
- TinyLlama model: ~638MB
- Total: ~1.2GB

## Privacy Note
Everything runs 100% locally on your machine. No data is sent to any servers.