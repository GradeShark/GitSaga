"""
Significance scoring to determine if a commit is saga-worthy
Based on patterns from real debugging sessions
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime, timedelta


@dataclass
class CommitContext:
    """Context about a commit for significance scoring"""
    message: str
    files_changed: List[str]
    lines_added: int
    lines_deleted: int
    branch: str
    author: str
    timestamp: datetime
    diff_content: str = ""
    session_duration: timedelta = None
    is_merge: bool = False
    is_revert: bool = False
    previous_commits: List[str] = None


class SignificanceScorer:
    """
    Determines if a commit represents a saga-worthy moment.
    Based on patterns from actual debugging documentation.
    """
    
    # Keywords that indicate significant debugging work
    BREAKTHROUGH_KEYWORDS = [
        'finally', 'fixed', 'resolved', 'solved', 'found',
        'breakthrough', 'root cause', 'discovered', 'working'
    ]
    
    # Keywords that indicate major work
    MAJOR_KEYWORDS = [
        'critical', 'major', 'important', 'security', 'performance',
        'migration', 'refactor', 'architecture', 'breaking'
    ]
    
    # Conventional commit types (worth capturing)
    CONVENTIONAL_COMMIT_TYPES = [
        'feat', 'feature', 'fix', 'docs', 'style', 'refactor', 
        'test', 'chore', 'perf', 'build', 'ci'
    ]
    
    # Keywords that indicate struggle/investigation
    STRUGGLE_KEYWORDS = [
        'debug', 'investigation', 'hours', 'attempt', 'trying',
        'issue', 'problem', 'error', 'bug', 'crash'
    ]
    
    # Trivial keywords that reduce significance
    TRIVIAL_KEYWORDS = [
        'typo', 'spacing', 'comment', 'formatting', 'style',
        'whitespace', 'rename', 'todo', 'wip', 'minor'
    ]
    
    # Critical files that increase significance
    CRITICAL_FILES = [
        'database', 'migration', 'auth', 'security', 'payment',
        'config', 'env', 'docker', 'requirements', 'package.json',
        '.yml', '.yaml', 'nginx', 'apache'
    ]
    
    # File patterns that indicate configuration/infrastructure
    INFRASTRUCTURE_PATTERNS = [
        r'\.env', r'docker', r'nginx', r'apache', r'\.conf$',
        r'requirements\.txt', r'package\.json', r'composer\.json',
        r'migration', r'schema', r'database'
    ]
    
    def __init__(self):
        self.min_threshold = 0.3  # Minimum score to be saga-worthy
        
    def calculate_score(self, context: CommitContext) -> Dict[str, Any]:
        """
        Calculate significance score based on multiple factors.
        Returns score and breakdown of factors.
        """
        score = 0.0
        factors = []
        
        # 1. Check commit message for breakthrough moments (high value)
        breakthrough_score = self._score_breakthrough(context.message)
        if breakthrough_score > 0:
            score += breakthrough_score
            factors.append(f"Breakthrough moment (+{breakthrough_score:.2f})")
        
        # 2. Check for conventional commit types
        conventional_score = self._score_conventional_commits(context.message)
        if conventional_score > 0:
            score += conventional_score
            factors.append(f"Conventional commit (+{conventional_score:.2f})")
        
        # 3. Check for major work indicators
        major_score = self._score_major_work(context.message)
        if major_score > 0:
            score += major_score
            factors.append(f"Major work (+{major_score:.2f})")
        
        # 4. Check for debugging/investigation
        struggle_score = self._score_struggle(context.message)
        if struggle_score > 0:
            score += struggle_score
            factors.append(f"Investigation/debugging (+{struggle_score:.2f})")
        
        # 5. Check file criticality
        file_score = self._score_critical_files(context.files_changed)
        if file_score > 0:
            score += file_score
            factors.append(f"Critical files modified (+{file_score:.2f})")
        
        # 6. Check change magnitude
        magnitude_score = self._score_change_magnitude(
            context.lines_added, context.lines_deleted
        )
        if magnitude_score > 0:
            score += magnitude_score
            factors.append(f"Large changes (+{magnitude_score:.2f})")
        
        # 7. Session duration (if available from AI coding session)
        if context.session_duration:
            duration_score = self._score_session_duration(context.session_duration)
            if duration_score > 0:
                score += duration_score
                factors.append(f"Long session (+{duration_score:.2f})")
        
        # 8. Check for configuration/infrastructure changes
        infra_score = self._score_infrastructure(context.files_changed)
        if infra_score > 0:
            score += infra_score
            factors.append(f"Infrastructure changes (+{infra_score:.2f})")
        
        # 9. Penalize trivial commits
        trivial_penalty = self._score_trivial(context.message)
        if trivial_penalty < 0:
            score += trivial_penalty
            factors.append(f"Trivial changes ({trivial_penalty:.2f})")
        
        # 10. Check for patterns like "413 error", "HTTP 500", etc
        error_pattern_score = self._score_error_patterns(context.message)
        if error_pattern_score > 0:
            score += error_pattern_score
            factors.append(f"Error fix pattern (+{error_pattern_score:.2f})")
        
        # 11. Branch context (feature branches often have significant work)
        branch_score = self._score_branch_context(context.branch)
        if branch_score > 0:
            score += branch_score
            factors.append(f"Feature branch (+{branch_score:.2f})")
        
        return {
            'score': min(score, 1.0),  # Cap at 1.0
            'is_significant': score >= self.min_threshold,
            'factors': factors,
            'suggested_type': self._suggest_saga_type(context, factors)
        }
    
    def _score_breakthrough(self, message: str) -> float:
        """Score breakthrough/success moments"""
        message_lower = message.lower()
        for keyword in self.BREAKTHROUGH_KEYWORDS:
            if keyword in message_lower:
                # "Finally fixed" is worth more than just "fixed"
                if 'finally' in message_lower or 'hours' in message_lower:
                    return 0.4
                return 0.3
        return 0.0
    
    def _score_conventional_commits(self, message: str) -> float:
        """Score conventional commit types"""
        # Check for conventional commit format: type(scope): description
        # or just type: description
        import re
        pattern = r'^(feat|fix|docs|style|refactor|test|chore|perf|build|ci)(\([^)]*\))?:'
        if re.match(pattern, message.lower()):
            commit_type = re.match(pattern, message.lower()).group(1)
            
            # Some types are more significant than others
            high_value_types = ['feat', 'fix', 'refactor', 'perf']
            medium_value_types = ['docs', 'test', 'chore', 'build', 'ci']
            
            if commit_type in high_value_types:
                return 0.4  # High significance
            elif commit_type in medium_value_types:
                return 0.35  # Medium significance (enough to trigger capture)
        
        return 0.0
    
    def _score_major_work(self, message: str) -> float:
        """Score major/critical work"""
        message_lower = message.lower()
        for keyword in self.MAJOR_KEYWORDS:
            if keyword in message_lower:
                if 'critical' in message_lower or 'security' in message_lower:
                    return 0.35
                return 0.25
        return 0.0
    
    def _score_struggle(self, message: str) -> float:
        """Score debugging/investigation work"""
        message_lower = message.lower()
        matches = sum(1 for k in self.STRUGGLE_KEYWORDS if k in message_lower)
        if matches >= 2:
            return 0.3
        elif matches == 1:
            return 0.15
        return 0.0
    
    def _score_critical_files(self, files: List[str]) -> float:
        """Score based on critical file modifications"""
        if not files:
            return 0.0
        
        for file in files:
            file_lower = file.lower()
            for critical in self.CRITICAL_FILES:
                if critical in file_lower:
                    return 0.25
        return 0.0
    
    def _score_change_magnitude(self, added: int, deleted: int) -> float:
        """Score based on size of changes"""
        total_changes = added + deleted
        
        if total_changes > 500:
            return 0.3  # Major refactor
        elif total_changes > 100:
            return 0.2  # Significant change
        elif total_changes > 50:
            return 0.1  # Notable change
        return 0.0
    
    def _score_session_duration(self, duration: timedelta) -> float:
        """Score based on how long the work took"""
        hours = duration.total_seconds() / 3600
        
        if hours > 4:
            return 0.35  # Long debugging session
        elif hours > 2:
            return 0.25  # Significant time investment
        elif hours > 1:
            return 0.15  # Notable session
        return 0.0
    
    def _score_infrastructure(self, files: List[str]) -> float:
        """Score infrastructure/configuration changes"""
        if not files:
            return 0.0
        
        for file in files:
            for pattern in self.INFRASTRUCTURE_PATTERNS:
                if re.search(pattern, file, re.IGNORECASE):
                    return 0.2
        return 0.0
    
    def _score_trivial(self, message: str) -> float:
        """Penalize trivial commits"""
        message_lower = message.lower()
        for keyword in self.TRIVIAL_KEYWORDS:
            if keyword in message_lower:
                # Don't penalize if it also has significant keywords
                if any(k in message_lower for k in self.BREAKTHROUGH_KEYWORDS + self.MAJOR_KEYWORDS):
                    return 0.0
                return -0.3
        return 0.0
    
    def _score_error_patterns(self, message: str) -> float:
        """Score commits that mention specific error codes/patterns"""
        error_patterns = [
            r'\b\d{3}\s+error\b',  # HTTP errors like "413 error"
            r'HTTP\s+\d{3}',        # HTTP status codes
            r'error\s+code',        # Error codes
            r'exception',           # Exceptions
            r'crash',               # Crashes
            r'timeout',             # Timeouts
            r'memory\s+leak',       # Memory issues
            r'race\s+condition',    # Concurrency issues
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return 0.25
        return 0.0
    
    def _score_branch_context(self, branch: str) -> float:
        """Score based on branch naming"""
        branch_lower = branch.lower()
        
        if 'hotfix' in branch_lower or 'critical' in branch_lower:
            return 0.2
        elif 'feature' in branch_lower or 'fix' in branch_lower or 'bug' in branch_lower:
            return 0.1
        return 0.0
    
    def _suggest_saga_type(self, context: CommitContext, factors: List[str]) -> str:
        """Suggest the type of saga based on context"""
        message_lower = context.message.lower()
        
        # Check for conventional commit types first
        import re
        pattern = r'^(feat|fix|docs|style|refactor|test|chore|perf|build|ci)(\([^)]*\))?:'
        match = re.match(pattern, message_lower)
        if match:
            commit_type = match.group(1)
            type_mapping = {
                'feat': 'feature',
                'fix': 'debugging', 
                'docs': 'general',
                'style': 'general',
                'refactor': 'architecture',
                'test': 'general',
                'chore': 'general',
                'perf': 'optimization',
                'build': 'general',
                'ci': 'general'
            }
            return type_mapping.get(commit_type, 'general')
        
        # Fallback to keyword detection
        if any(k in message_lower for k in ['fix', 'bug', 'error', 'crash', 'issue']):
            return 'debugging'
        elif any(k in message_lower for k in ['feature', 'add', 'implement', 'new']):
            return 'feature'
        elif any(k in message_lower for k in ['refactor', 'architecture', 'design']):
            return 'architecture'
        elif any(k in message_lower for k in ['performance', 'optimize', 'speed']):
            return 'optimization'
        else:
            return 'general'