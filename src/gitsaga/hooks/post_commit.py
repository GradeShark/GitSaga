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
from gitsaga.capture.interactive_capture import InteractiveCapturer
from gitsaga.capture.significance import SignificanceScorer


def main():
    """Run post-commit saga capture with interactive prompting for high-value commits"""
    try:
        chronicler = AutoChronicler()
        
        # Get commit context and score
        context = chronicler._get_commit_context('HEAD')
        if not context:
            return
        
        scorer = SignificanceScorer()
        score_result = scorer.calculate_score(context)
        score = score_result['score']
        
        # Check if this is significant
        if score < 0.3:
            print("GitSaga: Commit not significant enough for saga capture")
            return
        
        # Capture the basic saga
        saga = chronicler.capture_from_commit('HEAD')
        
        if not saga:
            return
        
        # For high-value commits, prompt for critical debugging info
        capturer = InteractiveCapturer()
        if capturer.should_capture_interactively(score, context.message):
            # Check if we're in an interactive terminal
            if sys.stdin.isatty() and sys.stdout.isatty():
                try:
                    # Prompt for high-value information
                    enhanced_saga = capturer.capture_high_value_info(
                        context.message, 
                        saga
                    )
                    saga = enhanced_saga
                    print(f"GitSaga: Enhanced saga captured with debugging context!")
                except (KeyboardInterrupt, EOFError):
                    print("GitSaga: Skipped interactive capture")
            else:
                # Non-interactive environment, just capture basic saga
                print(f"GitSaga: High-value commit detected! Run 'saga enhance HEAD' to add debugging details.")
        
        # Save the saga
        saga_path = saga.save(Path.cwd() / '.sagashark' / 'sagas')
        print(f"GitSaga: Captured saga '{saga.title}' -> {saga_path.name}")
            
    except Exception as e:
        # Don't fail the commit if saga capture fails
        print(f"GitSaga: Error during capture: {e}")
        

if __name__ == '__main__':
    main()