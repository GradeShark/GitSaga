"""
Git repository integration for GitSaga
Safe, read-only git operations to capture context
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class GitRepository:
    """Safe git repository information gathering"""
    
    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or Path.cwd()
        self.is_git_repo = (self.repo_path / '.git').exists()
    
    def get_current_branch(self) -> str:
        """Get current git branch name"""
        if not self.is_git_repo:
            return "main"
        
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                branch = result.stdout.strip()
                if branch:
                    return branch
            
            # Handle detached HEAD
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return f"detached-{result.stdout.strip()[:8]}"
                
        except (subprocess.SubprocessError, OSError):
            pass
        
        return "unknown"
    
    def get_modified_files(self) -> List[str]:
        """Get list of modified files in working directory"""
        if not self.is_git_repo:
            return []
        
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                files = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        # Format: "XY filename" - extract filename
                        parts = line[3:].strip()
                        if parts:
                            files.append(parts)
                return files[:10]  # Limit to 10 files
                
        except (subprocess.SubprocessError, OSError):
            pass
        
        return []
    
    def get_last_commit_message(self) -> str:
        """Get the last commit message"""
        if not self.is_git_repo:
            return ""
        
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=%B'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout.strip()[:200]  # Limit length
                
        except (subprocess.SubprocessError, OSError):
            pass
        
        return ""
    
    def get_repo_info(self) -> Dict[str, any]:
        """Get comprehensive repository information"""
        return {
            'branch': self.get_current_branch(),
            'modified_files': self.get_modified_files(),
            'last_commit': self.get_last_commit_message(),
            'is_git_repo': self.is_git_repo
        }
    
    def extract_tags_from_commit(self, message: str) -> List[str]:
        """Extract potential tags from commit message"""
        tags = []
        
        # Common keywords that make good tags
        keywords = ['fix', 'bug', 'feature', 'refactor', 'test', 'docs', 
                   'security', 'performance', 'breaking', 'hotfix']
        
        message_lower = message.lower()
        for keyword in keywords:
            if keyword in message_lower:
                tags.append(keyword)
        
        # Extract from conventional commits (feat:, fix:, etc.)
        import re
        conventional = re.match(r'^(\w+):', message)
        if conventional:
            tags.append(conventional.group(1).lower())
        
        return tags[:5]  # Limit number of tags