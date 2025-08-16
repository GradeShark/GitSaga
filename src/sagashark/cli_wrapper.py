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
        # Configure Python for UTF-8 without launching subprocess
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            # Fallback for older Python versions
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        
        # Set environment variable for UTF-8
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Import and run the actual CLI
    from sagashark.cli import cli
    cli()

if __name__ == '__main__':
    main()