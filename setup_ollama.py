#!/usr/bin/env python3
"""
Script to install Ollama and a SAFE model for GitSaga

⚠️ WARNING: DO NOT USE TINYLLAMA - it will corrupt your sagas with hallucinations.
Only use models with 7B+ parameters.
"""

import os
import sys

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gitsaga.setup.auto_installer import OllamaAutoInstaller

def main():
    print("=" * 50)
    print("GitSaga AI Setup - Installing Ollama & SAFE Models")
    print("=" * 50)
    print("\n⚠️  CRITICAL WARNING:")
    print("Small models like TinyLlama WILL corrupt your sagas!")
    print("Only 7B+ parameter models are safe to use.")
    print("=" * 50)
    
    installer = OllamaAutoInstaller()
    
    # Check if Ollama is installed
    if installer.is_ollama_installed():
        print("\n[OK] Ollama is already installed")
    else:
        print("\n[INFO] Ollama not found. Installing...")
        if installer.install_ollama():
            print("[OK] Ollama installed successfully")
        else:
            print("[ERROR] Failed to install Ollama")
            print("Please install manually from: https://ollama.com")
            return False
    
    # Start Ollama server
    print("\n[INFO] Starting Ollama server...")
    if installer.start_ollama_server():
        print("[OK] Ollama server started")
    else:
        print("[WARNING] Could not start Ollama server")
        print("You may need to start it manually")
    
    # Offer safe model choices
    print("\n[INFO] Select a SAFE model (7B+ parameters only):")
    print("1. llama2 (7B) - Recommended, well-tested")
    print("2. codellama (7B) - Best for code understanding")
    print("3. mistral (7B) - Fast and accurate")
    print("4. Skip AI setup - GitSaga works great without AI")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    model_map = {
        '1': ('llama2', '3.8GB'),
        '2': ('codellama', '3.8GB'),
        '3': ('mistral', '4.1GB')
    }
    
    if choice == '4':
        print("\n[INFO] Skipping AI setup. GitSaga will work without AI enhancement.")
        return True
    
    if choice not in model_map:
        print("[ERROR] Invalid choice")
        return False
    
    model_name, model_size = model_map[choice]
    
    # Check if model is installed
    print(f"\n[INFO] Checking for {model_name} model...")
    if installer.is_model_downloaded(model_name):
        print(f"[OK] {model_name} model already installed")
    else:
        print(f"[INFO] Downloading {model_name} ({model_size})...")
        print("[INFO] This may take several minutes...")
        if installer.download_model(model_name, model_size):
            print(f"[OK] {model_name} downloaded successfully")
        else:
            print(f"[ERROR] Failed to download {model_name}")
            print(f"You can try manually: ollama pull {model_name}")
            return False
    
    print("\n" + "=" * 50)
    print("[SUCCESS] GitSaga AI features are ready to use!")
    print("=" * 50)
    print("\nYou can now use commands like:")
    print("  saga capture HEAD")
    print("  saga monitor")
    print("  saga enhance")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Setup failed: {e}")
        sys.exit(1)