#!/usr/bin/env python3
"""
Simple script to install Ollama and TinyLlama for GitSaga
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
    print("GitSaga AI Setup - Installing Ollama & TinyLlama")
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
    
    # Check if TinyLlama is installed
    print("\n[INFO] Checking for TinyLlama model...")
    if installer.is_model_downloaded('tinyllama'):
        print("[OK] TinyLlama model already installed")
    else:
        print("[INFO] Downloading TinyLlama (638MB)...")
        if installer.download_model('tinyllama', '638MB'):
            print("[OK] TinyLlama downloaded successfully")
        else:
            print("[ERROR] Failed to download TinyLlama")
            print("You can try manually: ollama pull tinyllama")
            return False
    
    print("\n" + "=" * 50)
    print("[SUCCESS] GitSaga AI features are ready to use!")
    print("=" * 50)
    print("\nYou can now use commands like:")
    print("  saga capture --commit HEAD")
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