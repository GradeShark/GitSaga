"""
Auto-installer for Ollama and required models.
Makes SagaShark truly zero-friction to set up.
"""

import os
import sys
import platform
import subprocess
import urllib.request
import json
from pathlib import Path
import time
import shutil


class OllamaAutoInstaller:
    """Automatically installs Ollama and downloads required models"""
    
    OLLAMA_URLS = {
        'Windows': 'https://github.com/ollama/ollama/releases/latest/download/OllamaSetup.exe',
        'Darwin': 'https://github.com/ollama/ollama/releases/latest/download/Ollama-darwin.zip',
        'Linux': 'https://ollama.ai/install.sh'
    }
    
    DEFAULT_MODEL = 'tinyllama'  # 638MB - good balance of size and capability
    MODEL_SIZES = {
        'tinyllama': '638MB',
        'phi': '1.6GB',
        'llama2': '3.8GB'
    }
    
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.system = platform.system()
        
    def is_ollama_installed(self):
        """Check if Ollama is already installed"""
        return shutil.which('ollama') is not None
    
    def is_ollama_running(self):
        """Check if Ollama server is running"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def start_ollama_server(self):
        """Start Ollama server in background"""
        try:
            if self.system == 'Windows':
                # On Windows, start minimized
                subprocess.Popen(
                    ['ollama', 'serve'],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # On Unix-like systems
                subprocess.Popen(
                    ['ollama', 'serve'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            
            # Wait for server to start
            time.sleep(3)
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Could not start Ollama server: {e}")
            return False
    
    def install_ollama(self):
        """Install Ollama based on the operating system"""
        if self.is_ollama_installed():
            if self.verbose:
                print("[OK] Ollama is already installed")
            return True
        
        print("\nInstalling Ollama (one-time setup)...")
        
        try:
            if self.system == 'Windows':
                return self._install_windows()
            elif self.system == 'Darwin':
                return self._install_mac()
            elif self.system == 'Linux':
                return self._install_linux()
            else:
                print(f"Unsupported OS: {self.system}")
                return False
                
        except Exception as e:
            print(f"Installation error: {e}")
            return False
    
    def _install_windows(self):
        """Install Ollama on Windows"""
        # Try winget first (fastest)
        try:
            result = subprocess.run(
                ['winget', 'install', 'Ollama.Ollama', '--silent'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("[OK] Ollama installed via winget")
                return True
        except FileNotFoundError:
            pass
        
        # Fallback to downloading installer
        print("Downloading Ollama installer...")
        installer_path = Path.home() / 'Downloads' / 'OllamaSetup.exe'
        
        try:
            urllib.request.urlretrieve(
                self.OLLAMA_URLS['Windows'],
                installer_path
            )
            
            print("Running installer (this may take a minute)...")
            subprocess.run([str(installer_path), '/silent'], check=True)
            
            # Clean up installer
            installer_path.unlink(missing_ok=True)
            
            print("[OK] Ollama installed successfully")
            return True
            
        except Exception as e:
            print(f"Could not install automatically: {e}")
            print("Please install manually from: https://ollama.ai")
            return False
    
    def _install_mac(self):
        """Install Ollama on macOS"""
        # Try homebrew first
        try:
            result = subprocess.run(
                ['brew', 'install', 'ollama'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("[OK] Ollama installed via Homebrew")
                return True
        except FileNotFoundError:
            pass
        
        # Fallback to download
        print("Please install Ollama from: https://ollama.ai")
        print("Or run: brew install ollama")
        return False
    
    def _install_linux(self):
        """Install Ollama on Linux"""
        try:
            print("Installing via official script...")
            subprocess.run(
                ['sh', '-c', 'curl -fsSL https://ollama.ai/install.sh | sh'],
                check=True
            )
            print("[OK] Ollama installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("Could not install automatically.")
            print("Please run: curl -fsSL https://ollama.ai/install.sh | sh")
            return False
    
    def has_model(self, model_name):
        """Check if a model is already downloaded"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True
            )
            return model_name in result.stdout
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def pull_model(self, model_name=None):
        """Download the specified model"""
        if model_name is None:
            model_name = self.DEFAULT_MODEL
        
        if self.has_model(model_name):
            if self.verbose:
                print(f"[OK] Model '{model_name}' already downloaded")
            return True
        
        size = self.MODEL_SIZES.get(model_name, 'unknown size')
        print(f"\n Downloading {model_name} model ({size})...")
        print("This is a one-time download, please wait...")
        
        try:
            # Start server if not running
            if not self.is_ollama_running():
                print("Starting Ollama server...")
                self.start_ollama_server()
                time.sleep(3)
            
            # Pull the model
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Show progress
            for line in process.stdout:
                if 'pulling' in line.lower() or '%' in line:
                    print(f"  {line.strip()}")
            
            process.wait()
            
            if process.returncode == 0:
                print(f"[OK] Model '{model_name}' downloaded successfully")
                return True
            else:
                print(f"Failed to download model '{model_name}'")
                return False
                
        except Exception as e:
            print(f"Error downloading model: {e}")
            return False
    
    def full_setup(self):
        """Complete setup: install Ollama and download model"""
        print("\n SagaShark AI Setup")
        print("-" * 40)
        
        # Step 1: Install Ollama if needed
        if not self.is_ollama_installed():
            if not self.install_ollama():
                print("\n[WARNING] Could not install Ollama automatically.")
                print("SagaShark will work without AI features.")
                return False
        
        # Step 2: Start server if needed
        if not self.is_ollama_running():
            print("Starting Ollama server...")
            if not self.start_ollama_server():
                print("[WARNING] Could not start Ollama server.")
                print("You may need to start it manually: ollama serve")
        
        # Step 3: Download model
        if not self.has_model(self.DEFAULT_MODEL):
            print(f"\nSagaShark uses {self.DEFAULT_MODEL} for AI features.")
            response = input("Download now? (y/n): ").lower().strip()
            
            if response == 'y':
                if self.pull_model(self.DEFAULT_MODEL):
                    print("\n[SUCCESS] AI features are ready to use!")
                    return True
                else:
                    print("\n[WARNING] Model download failed.")
                    print("You can try again later with: ollama pull tinyllama")
            else:
                print("\nSkipping model download.")
                print("You can download later with: ollama pull tinyllama")
        else:
            print("\n[SUCCESS] AI features are ready to use!")
            return True
        
        print("\nSagaShark will work without AI enhancement.")
        return False


def check_and_setup_ollama(silent=False):
    """
    Quick check and setup function to be called from other parts of SagaShark.
    
    Args:
        silent: If True, suppress output unless action is needed
    
    Returns:
        bool: True if Ollama is ready, False otherwise
    """
    installer = OllamaAutoInstaller(verbose=not silent)
    
    # Quick check if everything is already set up
    if installer.is_ollama_installed() and installer.has_model('tinyllama'):
        if not installer.is_ollama_running():
            installer.start_ollama_server()
        return True
    
    # If not silent, offer to set up
    if not silent:
        return installer.full_setup()
    
    return False


if __name__ == '__main__':
    # Run full setup when called directly
    installer = OllamaAutoInstaller()
    installer.full_setup()