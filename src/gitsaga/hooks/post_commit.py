#!/usr/bin/env python3
"""
Git post-commit hook for automatic saga capture.
Install by copying to .git/hooks/post-commit and making executable.
"""

import sys
import os
from pathlib import Path

# Add gitsaga to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / 'src'))

from gitsaga.capture.auto_chronicler import AutoChronicler


def main():
    """Run post-commit saga capture"""
    try:
        chronicler = AutoChronicler()
        
        # Capture from the commit that was just made
        saga = chronicler.capture_from_commit('HEAD')
        
        if saga:
            print(f"GitSaga: Captured saga '{saga.title}'")
        else:
            print("GitSaga: Commit not significant enough for saga capture")
            
    except Exception as e:
        # Don't fail the commit if saga capture fails
        print(f"GitSaga: Error during capture: {e}")
        

if __name__ == '__main__':
    main()