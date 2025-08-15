"""
Configuration management for GitSaga
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Manage GitSaga configuration"""
    
    DEFAULT_CONFIG = {
        'version': '0.1.0',
        'auto_capture': False,
        'min_significance': 0.5,
        'excluded_paths': ['node_modules', 'venv', '__pycache__', '.git'],
        'default_type': 'general',
        'max_search_results': 10
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config from file or defaults"""
        self.config_path = config_path or Path.cwd() / '.gitsaga' / 'config.json'
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                # Merge with defaults
                config = self.DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
            except (json.JSONDecodeError, IOError):
                return self.DEFAULT_CONFIG.copy()
        else:
            return self.DEFAULT_CONFIG.copy()
    
    def save(self):
        """Save current configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        self.config.update(updates)
    
    @classmethod
    def init_repository(cls, path: Path) -> 'Config':
        """Initialize a new GitSaga repository"""
        gitsaga_dir = path / '.gitsaga'
        gitsaga_dir.mkdir(exist_ok=True)
        
        # Create directory structure
        (gitsaga_dir / 'sagas').mkdir(exist_ok=True)
        (gitsaga_dir / 'index').mkdir(exist_ok=True)
        
        # Create and save default config
        config = cls(gitsaga_dir / 'config.json')
        config.save()
        
        # Create .gitignore for index directory
        gitignore_path = gitsaga_dir / '.gitignore'
        gitignore_content = "# GitSaga index files (regeneratable)\nindex/\n"
        gitignore_path.write_text(gitignore_content)
        
        return config