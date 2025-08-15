#!/usr/bin/env python3
"""
Wrapper script to ensure proper encoding for Windows
"""

import sys
import os

def main():
    """Main entry point with proper encoding setup"""
    # Set UTF-8 encoding for Windows
    if sys.platform == "win32":
        # Set console code page to UTF-8
        import subprocess
        try:
            subprocess.run('chcp 65001', shell=True, capture_output=True, check=False)
        except:
            pass
        
        # Configure Python for UTF-8
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    # Import and run the actual CLI
    from gitsaga.cli import cli
    cli()

if __name__ == '__main__':
    main()