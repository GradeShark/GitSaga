"""
Interactive saga capture for high-value debugging information.
Prompts for the crucial details that make sagas actually useful.
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from ..core.saga import Saga


class InteractiveCapturer:
    """
    Captures the HIGH-VALUE information that makes sagas useful:
    - Root cause (not just symptoms)
    - Failed attempts (what didn't work)
    - Why the solution works
    - Lessons learned
    """
    
    def __init__(self, saga_dir: Path = None):
        self.saga_dir = saga_dir or Path.cwd() / '.gitsaga'
        self.context_file = self.saga_dir / '.last_capture_context.json'
    
    def should_capture_interactively(self, score: float, commit_msg: str) -> bool:
        """Determine if we should prompt for details"""
        # High-value keywords that warrant interactive capture
        HIGH_VALUE_KEYWORDS = [
            'fix', 'fixed', 'resolve', 'resolved', 'debug',
            'finally', 'hours', 'critical', 'bug', 'issue'
        ]
        
        msg_lower = commit_msg.lower()
        
        # Always prompt for high-score commits
        if score >= 0.6:
            return True
        
        # Prompt if commit message indicates debugging
        if any(keyword in msg_lower for keyword in HIGH_VALUE_KEYWORDS):
            return True
        
        return False
    
    def capture_high_value_info(self, commit_msg: str, auto_saga: Saga) -> Saga:
        """
        Interactively capture the valuable information.
        Quick prompts for the essential details.
        """
        print("\n🎯 GitSaga: This looks like an important debugging session!")
        print(f"Commit: {commit_msg[:60]}...")
        print("-" * 60)
        
        # Store responses
        responses = {}
        
        # 1. Root Cause (CRITICAL)
        print("\n❓ What was the ROOT CAUSE? (not symptoms)")
        print("   Example: 'Redis connection pool was exhausted due to missing cleanup'")
        responses['root_cause'] = self._get_input("> ") or "Not specified"
        
        # 2. Failed Attempts (VALUABLE)
        print("\n❌ What did you try that DIDN'T work? (or press Enter to skip)")
        print("   Example: 'Increased pool size - made it worse'")
        responses['failed_attempts'] = self._get_input("> ")
        
        # 3. Why Solution Works (IMPORTANT)
        print("\n✅ WHY does this fix work?")
        print("   Example: 'Properly closes connections after use, preventing pool exhaustion'")
        responses['why_works'] = self._get_input("> ") or "Not specified"
        
        # 4. Lessons Learned (CRUCIAL for future)
        print("\n📝 Key lesson for next time?")
        print("   Example: 'Always check connection cleanup in finally blocks'")
        responses['lesson'] = self._get_input("> ") or "Not specified"
        
        # 5. Time spent (for context)
        print("\n⏱️  How long did this take? (e.g., '2h', '30m', or Enter to skip)")
        responses['time_spent'] = self._get_input("> ")
        
        # Save context for potential reuse
        self._save_context(responses)
        
        # Enhance the saga with high-value information
        enhanced_content = self._build_enhanced_content(
            auto_saga.content,
            responses,
            commit_msg
        )
        
        auto_saga.content = enhanced_content
        
        # Update saga type if it's clearly debugging
        if responses['root_cause'] != "Not specified":
            auto_saga.saga_type = 'debugging'
        
        print("\n✨ Enhanced saga captured with valuable debugging context!")
        
        return auto_saga
    
    def _get_input(self, prompt: str) -> str:
        """Get user input with timeout option"""
        try:
            # On Windows, just use regular input
            if sys.platform == 'win32':
                return input(prompt).strip()
            else:
                # On Unix, could implement timeout
                import select
                
                print(prompt, end='', flush=True)
                
                # Wait up to 30 seconds for input
                ready, _, _ = select.select([sys.stdin], [], [], 30)
                
                if ready:
                    return sys.stdin.readline().strip()
                else:
                    print("\n(Timeout - skipping)")
                    return ""
        except (KeyboardInterrupt, EOFError):
            print("\n(Skipped)")
            return ""
    
    def _build_enhanced_content(self, base_content: str, 
                                responses: Dict[str, Any],
                                commit_msg: str) -> str:
        """Build saga with high-value sections prominently featured"""
        
        sections = []
        
        # Header
        sections.append(f"# {commit_msg.split(':')[-1].strip()[:80]}")
        sections.append("")
        sections.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        sections.append(f"**Type**: Debugging")
        if responses.get('time_spent'):
            sections.append(f"**Time Spent**: {responses['time_spent']}")
        sections.append("")
        sections.append("---")
        sections.append("")
        
        # ROOT CAUSE (Most Important - Top Billing)
        sections.append("## 🎯 ROOT CAUSE")
        sections.append("")
        sections.append(responses['root_cause'])
        sections.append("")
        
        # WHY THE FIX WORKS
        sections.append("## ✅ WHY THIS FIX WORKS")
        sections.append("")
        sections.append(responses['why_works'])
        sections.append("")
        
        # FAILED ATTEMPTS (If any)
        if responses.get('failed_attempts'):
            sections.append("## ❌ WHAT DIDN'T WORK")
            sections.append("")
            sections.append(responses['failed_attempts'])
            sections.append("")
        
        # LESSONS LEARNED (Critical for future)
        sections.append("## 📝 LESSONS LEARNED")
        sections.append("")
        sections.append(f"**Key Takeaway**: {responses['lesson']}")
        sections.append("")
        
        # Add the auto-generated content at the bottom
        sections.append("## 📊 Technical Details")
        sections.append("")
        sections.append("### Auto-captured Context")
        sections.append(base_content)
        
        return '\n'.join(sections)
    
    def _save_context(self, responses: Dict[str, Any]):
        """Save responses for potential reuse or analysis"""
        self.context_file.parent.mkdir(parents=True, exist_ok=True)
        
        context = {
            'timestamp': datetime.now().isoformat(),
            'responses': responses
        }
        
        with open(self.context_file, 'w') as f:
            json.dump(context, f, indent=2)
    
    def quick_capture(self) -> Optional[Dict[str, str]]:
        """
        Super quick capture - just the essentials in one prompt.
        For when you don't want to answer multiple questions.
        """
        print("\n🎯 GitSaga Quick Capture (or press Enter to skip)")
        print("In one line, what was the problem and solution?")
        summary = self._get_input("> ").strip()
        
        if not summary:
            return None
        
        # Try to extract problem and solution
        if 'because' in summary.lower():
            parts = summary.split('because', 1)
            problem = parts[0].strip()
            solution = parts[1].strip() if len(parts) > 1 else "See commit"
        elif 'by' in summary.lower():
            parts = summary.split('by', 1)  
            problem = parts[0].strip()
            solution = parts[1].strip() if len(parts) > 1 else "See commit"
        else:
            problem = summary
            solution = "See commit diff"
        
        return {
            'root_cause': problem,
            'solution': solution,
            'lesson': 'Captured via quick mode'
        }


class WeightedSagaScorer:
    """
    Scores sagas based on content quality, heavily weighting
    the high-value sections.
    """
    
    # Section weights - what actually matters for future debugging
    SECTION_WEIGHTS = {
        'diff': 0.35,             # CRITICAL - the actual code solution to reproduce
        'solution_why': 0.30,     # CRITICAL - why the fix works (for understanding)
        'root_cause': 0.20,       # IMPORTANT - understanding the real problem
        'lessons_learned': 0.10,  # VALUABLE - preventing recurrence
        'symptoms': 0.03,         # USEFUL - recognizing the issue
        'failed_attempts': 0.02   # MINOR - nice to have but not critical
    }
    
    def score_saga_quality(self, saga_content: str) -> Dict[str, Any]:
        """
        Score a saga based on how well it captures valuable information.
        """
        content_lower = saga_content.lower()
        scores = {}
        
        # Check for high-value sections
        scores['has_root_cause'] = (
            'root cause' in content_lower and 
            'not specified' not in content_lower
        )
        
        scores['has_lessons'] = (
            'lesson' in content_lower and
            'to be filled' not in content_lower and
            'not specified' not in content_lower
        )
        
        scores['has_solution_why'] = (
            'why' in content_lower and 
            ('fix works' in content_lower or 'solution works' in content_lower)
        )
        
        scores['has_failed_attempts'] = (
            "didn't work" in content_lower or
            'failed' in content_lower or
            'tried' in content_lower
        )
        
        # Calculate weighted score
        quality_score = 0.0
        
        if scores['has_root_cause']:
            quality_score += self.SECTION_WEIGHTS['root_cause']
        
        if scores['has_lessons']:
            quality_score += self.SECTION_WEIGHTS['lessons_learned']
        
        if scores['has_solution_why']:
            quality_score += self.SECTION_WEIGHTS['solution_why']
        
        if scores['has_failed_attempts']:
            quality_score += self.SECTION_WEIGHTS['failed_attempts']
        
        # Basic sections get minimal weight
        if 'symptom' in content_lower or '##' in content_lower:
            quality_score += self.SECTION_WEIGHTS['symptoms']
        
        if 'diff' in content_lower or '```' in content_lower:
            quality_score += self.SECTION_WEIGHTS['diff']
        
        return {
            'quality_score': quality_score,
            'is_high_quality': quality_score >= 0.5,
            'missing_critical': [],
            'sections_present': scores
        }
        
        # Identify what's missing
        missing = []
        if not scores['has_root_cause']:
            missing.append('root_cause')
        if not scores['has_lessons']:
            missing.append('lessons_learned')
        if not scores['has_solution_why']:
            missing.append('solution_explanation')
        
        return {
            'quality_score': quality_score,
            'is_high_quality': quality_score >= 0.5,
            'missing_critical': missing,
            'sections_present': scores
        }