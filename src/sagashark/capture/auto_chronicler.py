"""
AutoChronicler - Automatic saga capture from git commits
Monitors commits and creates sagas for significant debugging sessions
"""

import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..core.saga import Saga
from ..core.repository import GitRepository
from .significance import SignificanceScorer, CommitContext
from .patterns_config import PatternsConfig

try:
    from ..butler.dspy_integration import SagaEnhancer
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    # Don't print warning on import, only when actually needed


@dataclass
class SessionContext:
    """Context from AI coding session"""
    tool: str  # claude, cursor, copilot, etc
    session_id: Optional[str] = None
    duration: Optional[timedelta] = None
    conversation_summary: Optional[str] = None
    files_touched: List[str] = None
    commands_run: List[str] = None
    errors_encountered: List[str] = None
    

class AutoChronicler:
    """
    Automatically captures development context and creates sagas
    for significant debugging sessions and implementations.
    """
    
    def __init__(self, repo_path: Path = None, use_ai: bool = False):
        self.repo_path = repo_path or Path.cwd()
        self.repo = GitRepository(self.repo_path)
        self.scorer = SignificanceScorer()
        self.saga_dir = self.repo_path / '.sagashark'
        self.context_file = self.repo_path / '.saga_context.json'
        self.patterns = PatternsConfig(self.saga_dir / 'patterns.json')
        
        # Initialize AI enhancer if available and requested
        self.enhancer = None
        if use_ai and DSPY_AVAILABLE:
            try:
                self.enhancer = SagaEnhancer()
                # Only show this in verbose mode or when explicitly setting up
                if os.environ.get('SAGA_VERBOSE'):
                    print("AI enhancement enabled with DSPy")
            except Exception as e:
                # Silent fail unless verbose
                if os.environ.get('SAGA_VERBOSE'):
                    print(f"Could not initialize AI enhancer: {e}")
                self.enhancer = None
        
    def capture_from_commit(self, commit_hash: str = 'HEAD') -> Optional[Saga]:
        """
        Analyze a commit and create a saga if significant.
        
        Args:
            commit_hash: Git commit hash to analyze (default: HEAD)
            
        Returns:
            Created Saga if significant, None otherwise
        """
        # Get commit context
        context = self._get_commit_context(commit_hash)
        if not context:
            return None
            
        # Check significance
        score_result = self.scorer.calculate_score(context)
        
        if not score_result['is_significant']:
            print(f"Commit not significant enough for saga (score: {score_result['score']:.2f})")
            return None
            
        # Load session context if available
        session = self._load_session_context()
        
        # Build saga content
        saga_content = self._build_saga_content(context, score_result, session)
        
        # Create saga
        saga = Saga(
            title=self._generate_title(context),
            content=saga_content,
            saga_type=score_result['suggested_type'],
            branch=context.branch,
            tags=self._extract_tags(context, score_result),
            files_changed=context.files_changed,
            commit_id=context.commit_sha
        )
        
        # Don't save here - let the caller decide where to save
        # This prevents duplicate saves when capture command also saves
        
        # Clear session context after capture
        self._clear_session_context()
        
        print(f"✨ Created saga: {saga.title}")
        print(f"   Score: {score_result['score']:.2f}")
        print(f"   Type: {saga.saga_type}")
        print(f"   Factors: {', '.join(score_result['factors'])}")
        
        return saga
        
    def _get_commit_context(self, commit_hash: str) -> Optional[CommitContext]:
        """Extract context from a git commit"""
        try:
            # Get commit info
            cmd = ['git', 'show', '--stat', '--format=%H%n%an%n%ae%n%at%n%s%n%b', commit_hash]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            if result.returncode != 0:
                return None
                
            lines = result.stdout.strip().split('\n')
            if len(lines) < 5:
                return None
                
            commit_sha = lines[0]
            author = lines[1]
            email = lines[2]
            timestamp = datetime.fromtimestamp(int(lines[3]))
            subject = lines[4]
            
            # Find where the body ends and stats begin
            stats_start = -1
            for i, line in enumerate(lines[5:], 5):
                if line and (line[0].isdigit() or line.startswith(' ')):
                    stats_start = i
                    break
                    
            body = '\n'.join(lines[5:stats_start]) if stats_start > 5 else ''
            message = f"{subject}\n{body}".strip()
            
            # Get files changed
            cmd = ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            files_changed = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Get diff stats
            cmd = ['git', 'show', '--stat', '--format=', commit_hash]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            
            lines_added = 0
            lines_deleted = 0
            
            for line in result.stdout.split('\n'):
                # Parse lines like: " file.py | 10 ++++++----"
                if '|' in line and ('+' in line or '-' in line):
                    parts = line.split('|')[1].strip()
                    # Count + and - symbols
                    lines_added += parts.count('+')
                    lines_deleted += parts.count('-')
            
            # Get current branch
            branch = self.repo.get_current_branch()
            
            # Check if merge or revert
            is_merge = 'Merge' in message
            is_revert = 'Revert' in message or 'revert' in message.lower()
            
            # Get diff content (limited)
            cmd = ['git', 'show', '--format=', commit_hash]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            diff_content = result.stdout[:5000]  # Limit diff size
            
            # Try to get session duration from context file
            session = self._load_session_context()
            session_duration = session.duration if session else None
            
            return CommitContext(
                message=message,
                files_changed=files_changed,
                lines_added=lines_added,
                lines_deleted=lines_deleted,
                branch=branch,
                author=author,
                timestamp=timestamp,
                diff_content=diff_content,
                session_duration=session_duration,
                is_merge=is_merge,
                is_revert=is_revert,
                commit_sha=commit_sha
            )
            
        except Exception as e:
            print(f"Error getting commit context: {e}")
            return None
            
    def _load_session_context(self) -> Optional[SessionContext]:
        """Load AI session context if available"""
        if not self.context_file.exists():
            return None
            
        try:
            with open(self.context_file, 'r') as f:
                data = json.load(f)
                
            # Parse duration if present
            duration = None
            if 'duration_seconds' in data:
                duration = timedelta(seconds=data['duration_seconds'])
                
            return SessionContext(
                tool=data.get('tool', 'unknown'),
                session_id=data.get('session_id'),
                duration=duration,
                conversation_summary=data.get('conversation_summary'),
                files_touched=data.get('files_touched', []),
                commands_run=data.get('commands_run', []),
                errors_encountered=data.get('errors_encountered', [])
            )
        except Exception as e:
            print(f"Could not load session context: {e}")
            return None
            
    def _clear_session_context(self):
        """Clear the session context file after capture"""
        if self.context_file.exists():
            self.context_file.unlink()
            
    def _build_saga_content(self, context: CommitContext, 
                           score_result: Dict[str, Any],
                           session: Optional[SessionContext]) -> str:
        """
        Build detailed saga content based on commit and session context.
        Uses DSPy for enhancement if available.
        """
        # Try AI enhancement first if available
        if self.enhancer and score_result['suggested_type'] in ['debugging', 'feature', 'incident']:
            enhanced = self._build_enhanced_content(context, score_result, session)
            if enhanced:
                return enhanced
        
        # Fallback to manual content building
        content = []
        
        # Header with timestamp and significance
        content.append(f"**Timestamp**: {context.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"**Branch**: {context.branch}")
        content.append(f"**Significance Score**: {score_result['score']:.2f}")
        content.append(f"**Factors**: {', '.join(score_result['factors'])}")
        content.append("")
        content.append("---")
        content.append("")
        
        # Session context if available
        if session:
            content.append("## 🔧 Development Session")
            content.append(f"**Tool**: {session.tool}")
            if session.duration:
                hours = session.duration.total_seconds() / 3600
                content.append(f"**Duration**: {hours:.1f} hours")
            if session.conversation_summary:
                content.append(f"**Summary**: {session.conversation_summary}")
            content.append("")
            
        # The Problem/Issue
        content.append("## 📋 The Problem")
        
        # Extract errors and problems from commit message and diff
        errors = self._extract_errors(context)
        
        # Extract problem from commit message
        if 'fix' in context.message.lower() or 'bug' in context.message.lower():
            content.append("### Symptoms")
            if errors['from_message']:
                for error in errors['from_message']:
                    content.append(f"- {error}")
            elif errors['from_diff']:
                for error in errors['from_diff'][:3]:  # Limit to 3 from diff
                    content.append(f"- {error}")
            else:
                content.append(f"- {context.message.split('\n')[0]}")
            
            # Add stack traces if found
            if errors['stack_traces']:
                content.append("")
                content.append("### Error Details")
                content.append("```")
                for trace in errors['stack_traces'][:1]:  # Show first stack trace
                    content.append(trace)
                content.append("```")
        else:
            content.append(context.message)
        content.append("")
        
        # Investigation/Implementation
        if score_result['suggested_type'] == 'debugging':
            content.append("## 🔍 Investigation")
            
            # Add investigation context from diff
            investigation_contexts = self._extract_investigation_context(context.diff_content)
            if investigation_contexts:
                content.append("### Investigation Steps Found in Code")
                for inv_context in investigation_contexts:
                    content.append(f"- **{inv_context['description']}**")
                    if inv_context.get('code'):
                        content.append("  ```")
                        for line in inv_context['code'].split('\n')[:3]:  # Show first 3 lines
                            content.append(f"  {line}")
                        content.append("  ```")
                content.append("")
        else:
            content.append("## 💡 Implementation")
            
        # Commands run during session
        if session and session.commands_run:
            content.append("### Commands Executed")
            content.append("```bash")
            for cmd in session.commands_run[:10]:  # Limit to 10 most relevant
                content.append(cmd)
            content.append("```")
            content.append("")
            
        # Files changed
        content.append("### Files Modified")
        for file in context.files_changed[:20]:  # Limit display
            file_type = self._get_file_type(file)
            content.append(f"- `{file}` ({file_type})")
        if len(context.files_changed) > 20:
            content.append(f"- ... and {len(context.files_changed) - 20} more files")
        content.append("")
        
        # Code changes (if significant)
        if context.lines_added > 10 or context.lines_deleted > 10:
            content.append("### Key Changes")
            content.append(f"- **Lines added**: {context.lines_added}")
            content.append(f"- **Lines deleted**: {context.lines_deleted}")
            content.append("")
            
            # Add snippet of diff if available
            if context.diff_content:
                content.append("#### Code Diff (excerpt)")
                content.append("```diff")
                # Get first 30 lines of meaningful diff
                diff_lines = context.diff_content.split('\n')[:30]
                for line in diff_lines:
                    if line.startswith('+') or line.startswith('-') or line.startswith('@@'):
                        content.append(line)
                content.append("```")
                content.append("")
                
        # Errors encountered
        if session and session.errors_encountered:
            content.append("## ⚠️ Errors Encountered")
            for error in session.errors_encountered[:5]:
                content.append(f"- {error}")
            content.append("")
            
        # Resolution/Outcome
        if 'fix' in context.message.lower() or 'resolve' in context.message.lower():
            content.append("## ✅ Resolution")
            content.append(context.message)
            content.append("")
            
        # Lessons learned (for debugging sagas)
        if score_result['suggested_type'] == 'debugging':
            content.append("## 📝 Lessons Learned")
            content.append("- [To be filled in during review]")
            content.append("")
            
        # Verification steps
        if score_result['suggested_type'] in ['debugging', 'feature']:
            content.append("## 🧪 Verification")
            verification_steps = self._generate_verification_steps(context.files_changed)
            if verification_steps:
                for step in verification_steps:
                    content.append(f"- {step}")
            else:
                content.append("- [Add verification steps]")
            content.append("")
            
        return '\n'.join(content)
    
    def _build_enhanced_content(self, context: CommitContext,
                               score_result: Dict[str, Any],
                               session: Optional[SessionContext]) -> Optional[str]:
        """Build AI-enhanced saga content using DSPy"""
        try:
            # Prepare context for DSPy
            dspy_context = {
                'commit_message': context.message,
                'files_changed': context.files_changed,
                'diff_content': context.diff_content,
                'session_context': ''
            }
            
            # Add session context if available
            if session:
                session_info = []
                if session.tool:
                    session_info.append(f"Tool: {session.tool}")
                if session.duration:
                    hours = session.duration.total_seconds() / 3600
                    session_info.append(f"Duration: {hours:.1f} hours")
                if session.conversation_summary:
                    session_info.append(f"Summary: {session.conversation_summary}")
                if session.errors_encountered:
                    session_info.append(f"Errors: {', '.join(session.errors_encountered[:3])}")
                dspy_context['session_context'] = ' | '.join(session_info)
            
            # Get enhanced content from DSPy
            saga_type = score_result['suggested_type']
            enhanced = self.enhancer.enhance_saga(saga_type, dspy_context)
            
            # Format enhanced content into markdown
            content = []
            
            # Header
            content.append(f"# {self._generate_title(context)}")
            content.append("")
            content.append(f"**Date**: {context.timestamp.strftime('%Y-%m-%d')}")
            content.append(f"**Type**: {saga_type.title()}")
            content.append(f"**Branch**: {context.branch}")
            content.append(f"**Significance Score**: {score_result['score']:.2f}")
            content.append("")
            content.append("---")
            content.append("")
            
            if saga_type == 'debugging':
                # Symptoms
                if enhanced.get('symptoms'):
                    content.append("## 📋 The Problem")
                    content.append("")
                    content.append("### Symptoms")
                    content.append(enhanced['symptoms'])
                    content.append("")
                
                # Investigation
                if enhanced.get('investigation_steps'):
                    content.append("## 🔍 Investigation")
                    content.append("")
                    content.append(enhanced['investigation_steps'])
                    content.append("")
                
                # Failed Attempts
                if enhanced.get('failed_attempts'):
                    content.append("## ❌ Failed Attempts")
                    content.append("")
                    content.append(enhanced['failed_attempts'])
                    content.append("")
                
                # Root Cause
                if enhanced.get('root_cause'):
                    content.append("## 💡 Root Cause")
                    content.append("")
                    content.append(enhanced['root_cause'])
                    content.append("")
                
                # Solution
                if enhanced.get('solution'):
                    content.append("## ✅ Solution")
                    content.append("")
                    content.append(enhanced['solution'])
                    
                    # Add code diff if available
                    if context.diff_content:
                        content.append("")
                        content.append("### Code Changes")
                        content.append("```diff")
                        diff_lines = context.diff_content.split('\n')[:50]
                        content.extend(diff_lines)
                        content.append("```")
                    content.append("")
                
                # Verification
                if enhanced.get('verification'):
                    content.append("## 🧪 Verification")
                    content.append("")
                    content.append(enhanced['verification'])
                    content.append("")
                
                # Lessons Learned
                if enhanced.get('lessons'):
                    content.append("## 📝 Lessons Learned")
                    content.append("")
                    content.append(enhanced['lessons'])
                    content.append("")
                    
            elif saga_type == 'feature':
                # Feature content structure
                for section, title in [
                    ('feature_description', '## 📋 Feature Overview'),
                    ('requirements', '## 📝 Requirements'),
                    ('implementation_approach', '## 🏗️ Implementation'),
                    ('key_decisions', '## 🎯 Key Decisions'),
                    ('testing_approach', '## 🧪 Testing'),
                    ('future_considerations', '## 🔮 Future Considerations')
                ]:
                    if enhanced.get(section):
                        content.append(title)
                        content.append("")
                        content.append(enhanced[section])
                        content.append("")
                        
            elif saga_type in ['incident', 'critical']:
                # Incident content structure
                for section, title in [
                    ('incident_summary', '## 📊 Executive Summary'),
                    ('timeline', '## 🕐 Timeline'),
                    ('impact', '## 💥 Impact Assessment'),
                    ('root_causes', '## 🔍 Root Causes'),
                    ('immediate_fix', '## 🚨 Immediate Actions'),
                    ('long_term_fix', '## 📋 Long-term Fixes'),
                    ('postmortem', '## 📝 Postmortem')
                ]:
                    if enhanced.get(section):
                        content.append(title)
                        content.append("")
                        content.append(enhanced[section])
                        content.append("")
            
            # Add metadata footer
            content.append("---")
            content.append("")
            content.append(f"**Files Changed**: {len(context.files_changed)}")
            content.append(f"**Lines Added**: {context.lines_added}")
            content.append(f"**Lines Deleted**: {context.lines_deleted}")
            
            if session and session.tool:
                content.append(f"**Development Tool**: {session.tool}")
            
            content.append("")
            content.append("*Generated with SagaShark AutoChronicler + DSPy*")
            
            return '\n'.join(content)
            
        except Exception as e:
            print(f"Error during AI enhancement: {e}")
            return None
        
    def _generate_title(self, context: CommitContext) -> str:
        """Generate a descriptive title for the saga"""
        # Use commit subject as base
        subject = context.message.split('\n')[0]
        
        # Clean up common prefixes
        subject = re.sub(r'^(fix|feat|chore|docs|test|refactor|style)(\([^)]+\))?:\s*', '', subject, flags=re.IGNORECASE)
        
        # Capitalize first letter
        if subject:
            subject = subject[0].upper() + subject[1:]
            
        # Limit length
        if len(subject) > 80:
            subject = subject[:77] + "..."
            
        return subject
        
    def _extract_tags(self, context: CommitContext, score_result: Dict[str, Any]) -> List[str]:
        """Extract relevant tags from commit context"""
        tags = []
        
        # Add saga type as tag
        tags.append(score_result['suggested_type'])
        
        # Extract from commit message
        message_lower = context.message.lower()
        
        # Common tags
        tag_keywords = {
            'bugfix': ['fix', 'bug', 'issue', 'error'],
            'feature': ['feature', 'add', 'new', 'implement'],
            'performance': ['performance', 'optimize', 'speed', 'faster'],
            'security': ['security', 'vulnerability', 'auth', 'permission'],
            'database': ['database', 'migration', 'schema', 'query'],
            'api': ['api', 'endpoint', 'rest', 'graphql'],
            'ui': ['ui', 'ux', 'frontend', 'css', 'style'],
            'testing': ['test', 'spec', 'coverage', 'jest', 'pytest'],
            'documentation': ['docs', 'readme', 'documentation'],
            'configuration': ['config', 'env', 'settings', 'setup']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                tags.append(tag)
                
        # Add file-based tags
        for file in context.files_changed:
            if 'test' in file.lower():
                tags.append('testing')
            elif file.endswith('.md'):
                tags.append('documentation')
            elif 'migration' in file.lower():
                tags.append('database')
                
        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
                
        return unique_tags[:10]  # Limit to 10 tags
        
    def _get_file_type(self, filepath: str) -> str:
        """Get a human-readable file type description"""
        ext = Path(filepath).suffix.lower()
        
        type_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React',
            '.tsx': 'React TypeScript',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.java': 'Java',
            '.c': 'C',
            '.cpp': 'C++',
            '.cs': 'C#',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.xml': 'XML',
            '.md': 'Markdown',
            '.txt': 'Text',
            '.sh': 'Shell',
            '.bash': 'Bash',
            '.dockerfile': 'Docker',
            '.gitignore': 'Git',
            '.env': 'Environment'
        }
        
        return type_map.get(ext, 'File')
    
    def _extract_errors(self, context: CommitContext) -> Dict[str, List[str]]:
        """Extract error messages from commit message and diff content."""
        errors = {
            'from_message': [],
            'from_diff': [],
            'stack_traces': []
        }
        
        # Get error patterns from config
        error_patterns = self.patterns.get_error_patterns()
        
        # Extract from commit message
        for pattern in error_patterns:
            matches = re.findall(pattern, context.message, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                error_msg = match.strip() if isinstance(match, str) else match[0].strip()
                if error_msg and len(error_msg) > 5:  # Filter out too short matches
                    errors['from_message'].append(error_msg)
        
        # Extract from diff content
        if context.diff_content:
            for pattern in error_patterns:
                matches = re.findall(pattern, context.diff_content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    error_msg = match.strip() if isinstance(match, str) else match[0].strip()
                    if error_msg and len(error_msg) > 5 and error_msg not in errors['from_message']:
                        errors['from_diff'].append(error_msg)
            
            # Look for stack traces
            stack_pattern = r'(?:Traceback \(most recent call last\):|at .+\(.+:\d+\))[\s\S]{50,500}'
            stack_matches = re.findall(stack_pattern, context.diff_content)
            errors['stack_traces'] = stack_matches[:2]  # Limit to 2 stack traces
        
        # Deduplicate while preserving order
        errors['from_message'] = list(dict.fromkeys(errors['from_message']))[:5]
        errors['from_diff'] = list(dict.fromkeys(errors['from_diff']))[:5]
        
        return errors
    
    def _generate_verification_steps(self, files_changed: List[str]) -> List[str]:
        """Generate verification steps based on file types."""
        steps = []
        seen_types = set()
        
        # Get verification mappings from config
        verification_map = self.patterns.get_verification_steps()
        
        # Detect framework and get framework-specific patterns
        framework = self.patterns.detect_framework(files_changed)
        framework_patterns = self.patterns.get_framework_patterns(framework)
        
        for file_path in files_changed:
            file_lower = file_path.lower()
            path_obj = Path(file_path)
            ext = path_obj.suffix.lower()
            
            # Check for framework-specific patterns
            for pattern, step in framework_patterns.items():
                if pattern in file_path and pattern not in seen_types:
                    steps.append(step)
                    seen_types.add(pattern)
                    break
            
            # Check file extensions
            if ext in verification_map and ext not in seen_types:
                steps.append(verification_map[ext])
                seen_types.add(ext)
            
            # Check for special file names
            if 'migration' in file_lower and 'migration' not in seen_types:
                steps.append(verification_map['migration'])
                seen_types.add('migration')
            elif 'schema' in file_lower and 'schema' not in seen_types:
                steps.append(verification_map['schema'])
                seen_types.add('schema')
            elif 'dockerfile' in file_lower and 'dockerfile' not in seen_types:
                steps.append(verification_map['dockerfile'])
                seen_types.add('dockerfile')
            elif 'readme' in file_lower and 'readme' not in seen_types:
                steps.append(verification_map['readme'])
                seen_types.add('readme')
            
            # Limit to reasonable number of steps
            if len(steps) >= 5:
                break
        
        # Add general verification step if we have tests
        if any('test' in f.lower() or 'spec' in f.lower() for f in files_changed):
            steps.insert(0, 'Run all tests to ensure nothing is broken')
        
        return steps
    
    def _extract_investigation_context(self, diff_content: str, max_contexts: int = 3) -> List[Dict[str, str]]:
        """Extract investigation context from git diff.
        
        Looks for:
        - Added debug statements (console.log, print, dd, var_dump, etc.)
        - Removed error handling
        - Modified conditionals
        - Changed function signatures
        """
        contexts = []
        
        if not diff_content:
            return contexts
        
        # Split diff into hunks
        hunk_pattern = r'@@[^@]+@@.*?(?=@@|$)'
        hunks = re.findall(hunk_pattern, diff_content, re.DOTALL)
        
        # Get patterns from config
        debug_patterns = self.patterns.get_debug_patterns()
        investigation_patterns = self.patterns.get_investigation_patterns()
        
        for hunk in hunks[:max_contexts * 2]:  # Process more hunks than we need
            context = {}
            
            # Look for debug statements
            for pattern, description in debug_patterns:
                if re.search(pattern, hunk):
                    context['type'] = 'debugging'
                    context['description'] = description
                    context['code'] = self._extract_relevant_lines(hunk, pattern)
                    break
            
            # Look for other investigation patterns
            if not context:
                for pattern_type, pattern in investigation_patterns.items():
                    if re.search(pattern, hunk):
                        context['type'] = pattern_type
                        if pattern_type == 'conditionals':
                            context['description'] = 'Modified conditional logic'
                        elif pattern_type == 'error_handling':
                            context['description'] = 'Changed error handling'
                        elif pattern_type == 'function_changes':
                            context['description'] = 'Modified function signature'
                        elif pattern_type == 'todo_comments':
                            context['description'] = 'Added TODO/FIXME comment'
                        elif pattern_type == 'assertions':
                            context['description'] = 'Modified test assertions'
                        else:
                            context['description'] = f'Modified {pattern_type}'
                        context['code'] = self._extract_relevant_lines(hunk, pattern)
                        break
            
            if context:
                contexts.append(context)
                if len(contexts) >= max_contexts:
                    break
        
        return contexts
    
    def _extract_relevant_lines(self, hunk: str, pattern: str, context_lines: int = 2) -> str:
        """Extract relevant lines around a pattern match."""
        lines = hunk.split('\n')
        relevant_lines = []
        
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                # Get surrounding context
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                relevant_lines.extend(lines[start:end])
        
        # Remove duplicate lines and clean up
        seen = set()
        unique_lines = []
        for line in relevant_lines:
            if line not in seen and line.strip():
                seen.add(line)
                unique_lines.append(line)
        
        return '\n'.join(unique_lines[:10])  # Limit to 10 lines
        
    def monitor_commits(self, since: str = 'HEAD~10'):
        """
        Monitor recent commits and capture sagas for significant ones.
        
        Args:
            since: Git revision to start from (default: last 10 commits)
        """
        # Get list of commits
        cmd = ['git', 'rev-list', '--reverse', f'{since}..HEAD']
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
        
        if result.returncode != 0:
            print(f"Error getting commits: {result.stderr}")
            return
            
        commits = result.stdout.strip().split('\n')
        if not commits or commits == ['']:
            print("No commits to analyze")
            return
            
        print(f"Analyzing {len(commits)} commits...")
        captured = 0
        
        for commit in commits:
            saga = self.capture_from_commit(commit)
            if saga:
                captured += 1
                
        print(f"\n📚 Captured {captured} sagas from {len(commits)} commits")
        
    def save_session_context(self, tool: str, **kwargs):
        """
        Save context from current AI coding session.
        This would be called by IDE plugins or git hooks.
        
        Args:
            tool: Name of the tool (claude, cursor, etc)
            **kwargs: Additional context like duration, files, etc
        """
        context = {
            'tool': tool,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        with open(self.context_file, 'w') as f:
            json.dump(context, f, indent=2)
            
        print(f"Session context saved for {tool}")