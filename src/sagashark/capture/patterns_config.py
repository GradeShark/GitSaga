"""
Configurable patterns for project-specific saga generation.
Users can customize these patterns for their specific projects.
"""

import json
from pathlib import Path
from typing import Dict, List, Any


class PatternsConfig:
    """Manages configurable patterns for saga generation."""
    
    def __init__(self, config_path: Path = None):
        """Initialize with optional custom config path."""
        self.config_path = config_path or Path.cwd() / '.sagashark' / 'patterns.json'
        self.patterns = self.load_patterns()
    
    def load_patterns(self) -> Dict[str, Any]:
        """Load patterns from config file or use defaults."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    custom_patterns = json.load(f)
                # Merge with defaults
                default_patterns = self.get_default_patterns()
                for key, value in custom_patterns.items():
                    if key in default_patterns:
                        if isinstance(value, dict):
                            default_patterns[key].update(value)
                        elif isinstance(value, list):
                            default_patterns[key].extend(value)
                        else:
                            default_patterns[key] = value
                return default_patterns
            except Exception as e:
                print(f"Error loading custom patterns: {e}, using defaults")
        
        return self.get_default_patterns()
    
    def get_default_patterns(self) -> Dict[str, Any]:
        """Get default patterns for saga generation."""
        return {
            "error_patterns": [
                # Standard error patterns
                r'(?:Error|ERROR):\s*([^\n]+)',
                r'(?:Failed|FAILED):\s*([^\n]+)',
                r'(?:Exception|EXCEPTION):\s*([^\n]+)',
                r'(?:Warning|WARNING):\s*([^\n]+)',
                r'(?:Fatal|FATAL):\s*([^\n]+)',
                # Language-specific exceptions
                r'\b(?:TypeError|ValueError|AttributeError|KeyError|IndexError|NameError|ImportError|RuntimeError|SyntaxError):\s*([^\n]+)',
                # HTTP errors
                r'HTTP\s+(?:4\d{2}|5\d{2})\s*[:-]?\s*([^\n]+)',
                r'(?:status|code)\s*[=:]\s*(?:4\d{2}|5\d{2})\s*[:-]?\s*([^\n]+)',
            ],
            
            "verification_steps": {
                # Frontend files
                '.blade.php': 'Visit the affected routes in browser and verify UI changes',
                '.vue': 'Run `npm run dev` and test Vue components in browser',
                '.jsx': 'Run `npm start` and verify React component behavior',
                '.tsx': 'Run `npm start` and verify TypeScript React components',
                '.html': 'Open HTML file in browser and verify rendering',
                '.css': 'Check visual styling in browser across different screen sizes',
                '.scss': 'Compile SCSS and verify styles: `npm run build:css`',
                
                # Backend files
                '.php': 'Run `php artisan test` or `phpunit` for PHP tests',
                '.py': 'Run `pytest` or `python -m unittest` for Python tests',
                '.js': 'Run `npm test` for JavaScript tests',
                '.ts': 'Run `npm test` and `npm run typecheck` for TypeScript',
                '.go': 'Run `go test ./...` for Go tests',
                '.rs': 'Run `cargo test` for Rust tests',
                '.java': 'Run `mvn test` or `gradle test` for Java tests',
                '.rb': 'Run `rspec` or `rails test` for Ruby tests',
                
                # Database files
                'migration': 'Run migrations and verify database state',
                '.sql': 'Review and test SQL queries in database client',
                'schema': 'Verify database schema changes are applied correctly',
                
                # Configuration files
                '.env': 'Verify environment variables are set correctly',
                '.json': 'Validate JSON syntax',
                '.yaml': 'Validate YAML syntax',
                '.yml': 'Validate YAML configuration files',
                'dockerfile': 'Build and test Docker image: `docker build .`',
                '.gitignore': 'Verify git is ignoring the correct files: `git status --ignored`',
                
                # Documentation
                '.md': 'Review documentation changes for accuracy and clarity',
                'readme': 'Ensure README instructions are up-to-date and accurate',
            },
            
            "framework_patterns": {
                # Laravel/Sail specific
                "laravel": {
                    'app/Http/Controllers': 'Test controller endpoints with Postman or browser',
                    'app/Models': 'Run model tests: `sail test --filter ModelTest`',
                    'routes/': 'Check routes: `sail artisan route:list`',
                    'database/migrations': 'Run `sail artisan migrate:status` and verify migration',
                    'resources/views': 'Clear view cache: `sail artisan view:clear` and test in browser',
                    'tests/': 'Run specific test file: `sail test path/to/test`',
                },
                
                # Django specific
                "django": {
                    'views.py': 'Test view endpoints with browser or API client',
                    'models.py': 'Run model tests: `python manage.py test`',
                    'urls.py': 'Check URL patterns are correct',
                    'migrations/': 'Run `python manage.py migrate` and verify',
                    'templates/': 'Clear template cache and test in browser',
                    'tests.py': 'Run specific test: `python manage.py test app.tests`',
                },
                
                # React specific
                "react": {
                    'components/': 'Run component tests: `npm test`',
                    'hooks/': 'Test custom hooks behavior',
                    'contexts/': 'Verify context provider behavior',
                    'pages/': 'Test page routing and rendering',
                    '__tests__/': 'Run test suite: `npm test`',
                },
                
                # Vue specific
                "vue": {
                    'components/': 'Run component tests: `npm run test:unit`',
                    'composables/': 'Test composable functions',
                    'stores/': 'Verify store state management',
                    'views/': 'Test view components in browser',
                    'router/': 'Verify routing configuration',
                },
            },
            
            "debug_patterns": [
                # JavaScript/TypeScript
                (r'\+.*(?:console\.log|console\.error|console\.debug)', 'Added JavaScript debugging'),
                # Python
                (r'\+.*(?:print\(|pprint\(|debug\(|breakpoint\()', 'Added Python debugging'),
                # PHP
                (r'\+.*(?:dd\(|dump\(|var_dump\(|print_r\()', 'Added PHP debugging'),
                # Ruby
                (r'\+.*(?:puts|p\s+|pp\s+|binding\.pry)', 'Added Ruby debugging'),
                # Go
                (r'\+.*(?:fmt\.Print|log\.Print|debug\.Print)', 'Added Go debugging'),
                # Java
                (r'\+.*(?:System\.out\.print|logger\.debug|printStackTrace)', 'Added Java debugging'),
                # Swift
                (r'\+.*(?:NSLog|print\(|debugPrint)', 'Added Swift debugging'),
                # Rust
                (r'\+.*(?:println!|dbg!|eprintln!)', 'Added Rust debugging'),
            ],
            
            "investigation_patterns": {
                "conditionals": r'[-+].*\s+if\s*\(',
                "error_handling": r'[-+].*(?:try|catch|except|rescue|panic|recover)',
                "function_changes": r'[-+].*(?:function|def|func|method|proc)\s+\w+',
                "todo_comments": r'[-+].*(?:TODO|FIXME|HACK|XXX|BUG|NOTE):',
                "assertions": r'[-+].*(?:assert|expect|should|test|it\()',
            }
        }
    
    def save_example_config(self):
        """Save an example configuration file for users to customize."""
        example_config = {
            "_comment": "Customize these patterns for your project. This file extends the default patterns.",
            
            "error_patterns": [],
            
            "verification_steps": {
                ".custom": "Run custom verification command"
            },
            
            "framework_patterns": {
                "your_framework": {
                    "pattern/": "Verification step for this pattern"
                }
            },
            
            "project_specific": {
                "test_command": "npm test",
                "build_command": "npm run build",
                "deploy_command": "npm run deploy"
            }
        }
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path.with_suffix('.example.json'), 'w') as f:
            json.dump(example_config, f, indent=2)
        
        return self.config_path.with_suffix('.example.json')
    
    def get_error_patterns(self) -> List[str]:
        """Get error patterns for extraction."""
        return self.patterns.get('error_patterns', [])
    
    def get_verification_steps(self) -> Dict[str, str]:
        """Get verification steps mapping."""
        return self.patterns.get('verification_steps', {})
    
    def get_framework_patterns(self, framework: str = None) -> Dict[str, str]:
        """Get framework-specific patterns."""
        framework_patterns = self.patterns.get('framework_patterns', {})
        if framework:
            return framework_patterns.get(framework, {})
        
        # Return all framework patterns merged
        merged = {}
        for patterns in framework_patterns.values():
            merged.update(patterns)
        return merged
    
    def get_debug_patterns(self) -> List[tuple]:
        """Get debug statement patterns."""
        return self.patterns.get('debug_patterns', [])
    
    def get_investigation_patterns(self) -> Dict[str, str]:
        """Get investigation patterns."""
        return self.patterns.get('investigation_patterns', {})
    
    def detect_framework(self, files_changed: List[str]) -> str:
        """Detect framework based on changed files."""
        # Simple heuristic-based detection
        file_paths = ' '.join(files_changed).lower()
        
        if 'artisan' in file_paths or 'app/Http' in file_paths:
            return 'laravel'
        elif 'manage.py' in file_paths or 'django' in file_paths:
            return 'django'
        elif 'package.json' in file_paths:
            if 'react' in file_paths or '.jsx' in file_paths or '.tsx' in file_paths:
                return 'react'
            elif 'vue' in file_paths or '.vue' in file_paths:
                return 'vue'
        
        return None