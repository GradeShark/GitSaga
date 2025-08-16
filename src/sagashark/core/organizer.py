"""
Saga file organization system.
Automatically organizes sagas into year/month/week folder structure.
"""

import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import re


class SagaOrganizer:
    """
    Organizes saga files into a hierarchical date-based structure:
    .sagashark/sagas/
    ├── 2024/
    │   ├── 01-January/
    │   │   ├── week-01/
    │   │   ├── week-02/
    │   │   └── ...
    │   ├── 02-February/
    │   └── ...
    └── 2025/
        └── ...
    """
    
    def __init__(self, saga_dir: Path = None):
        self.saga_dir = saga_dir or Path.cwd() / '.sagashark' / 'sagas'
        self.saga_dir.mkdir(parents=True, exist_ok=True)
        
    def get_saga_date(self, saga_path: Path) -> Optional[datetime]:
        """Extract date from saga filename or content."""
        # Try to parse date from filename (format: YYYY-MM-DD-HHMM-*.md)
        match = re.match(r'(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})', saga_path.name)
        if match:
            year, month, day, hour, minute = match.groups()
            return datetime(int(year), int(month), int(day), int(hour), int(minute))
        
        # Fallback to file modification time
        if saga_path.exists():
            return datetime.fromtimestamp(saga_path.stat().st_mtime)
        
        return None
    
    def get_week_number(self, date: datetime) -> int:
        """Get week number of the month (1-5)."""
        first_day = date.replace(day=1)
        days_since_first = (date - first_day).days
        return (days_since_first // 7) + 1
    
    def get_organized_path(self, saga_path: Path, date: datetime = None) -> Path:
        """
        Get the organized path for a saga file.
        Example: .sagashark/sagas/2024/03-March/week-02/original-filename.md
        """
        if date is None:
            date = self.get_saga_date(saga_path)
            if date is None:
                date = datetime.now()
        
        year = date.strftime('%Y')
        month = date.strftime('%m-%B')
        week = f"week-{self.get_week_number(date):02d}"
        
        organized_path = self.saga_dir / year / month / week / saga_path.name
        return organized_path
    
    def organize_saga(self, saga_path: Path, date: datetime = None) -> Path:
        """Move a single saga to its organized location."""
        if not saga_path.exists():
            raise FileNotFoundError(f"Saga not found: {saga_path}")
        
        organized_path = self.get_organized_path(saga_path, date)
        
        # Create directory structure if needed
        organized_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Move file if it's not already in the right place
        if saga_path.resolve() != organized_path.resolve():
            # Handle naming conflicts
            if organized_path.exists():
                # Add a counter to make unique
                counter = 1
                stem = organized_path.stem
                suffix = organized_path.suffix
                while organized_path.exists():
                    organized_path = organized_path.parent / f"{stem}-{counter}{suffix}"
                    counter += 1
            
            shutil.move(str(saga_path), str(organized_path))
        
        return organized_path
    
    def organize_all(self, dry_run: bool = False) -> List[Tuple[Path, Path]]:
        """
        Organize all existing sagas into the date hierarchy.
        Returns list of (old_path, new_path) tuples.
        """
        moves = []
        
        # Find all saga files in the root sagas directory
        for saga_file in self.saga_dir.glob('*.md'):
            if saga_file.is_file():
                new_path = self.get_organized_path(saga_file)
                
                if saga_file.resolve() != new_path.resolve():
                    moves.append((saga_file, new_path))
                    
                    if not dry_run:
                        self.organize_saga(saga_file)
        
        # Also check branch directories at root level
        for branch_dir in self.saga_dir.iterdir():
            if branch_dir.is_dir() and not branch_dir.name.isdigit():
                # This is likely a branch directory, not a year
                for saga_file in branch_dir.glob('**/*.md'):
                    if saga_file.is_file():
                        new_path = self.get_organized_path(saga_file)
                        
                        if saga_file.resolve() != new_path.resolve():
                            moves.append((saga_file, new_path))
                            
                            if not dry_run:
                                self.organize_saga(saga_file)
        
        return moves
    
    def cleanup_empty_dirs(self):
        """Remove empty directories after organization."""
        def remove_empty_dirs(path: Path):
            """Recursively remove empty directories."""
            if not path.is_dir():
                return
            
            # Check subdirectories first
            for subdir in path.iterdir():
                if subdir.is_dir():
                    remove_empty_dirs(subdir)
            
            # Remove this directory if it's empty
            try:
                if path != self.saga_dir and not any(path.iterdir()):
                    path.rmdir()
            except (OSError, StopIteration):
                pass
        
        remove_empty_dirs(self.saga_dir)
    
    def get_statistics(self) -> dict:
        """Get statistics about saga organization."""
        stats = {
            'total_sagas': 0,
            'organized_sagas': 0,
            'unorganized_sagas': 0,
            'by_year': {},
            'by_month': {},
            'recent_week': 0
        }
        
        # Count all sagas
        for saga_file in self.saga_dir.glob('**/*.md'):
            if saga_file.is_file():
                stats['total_sagas'] += 1
                
                # Check if organized (in year/month/week structure)
                parts = saga_file.relative_to(self.saga_dir).parts
                if len(parts) >= 4:  # year/month/week/file.md
                    stats['organized_sagas'] += 1
                    
                    year = parts[0]
                    month = parts[1]
                    
                    stats['by_year'][year] = stats['by_year'].get(year, 0) + 1
                    stats['by_month'][f"{year}/{month}"] = stats['by_month'].get(f"{year}/{month}", 0) + 1
                    
                    # Count recent week
                    saga_date = self.get_saga_date(saga_file)
                    if saga_date and (datetime.now() - saga_date).days <= 7:
                        stats['recent_week'] += 1
                else:
                    stats['unorganized_sagas'] += 1
        
        return stats
    
    def find_sagas_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Path]:
        """Find all sagas within a date range."""
        sagas = []
        
        for saga_file in self.saga_dir.glob('**/*.md'):
            if saga_file.is_file():
                saga_date = self.get_saga_date(saga_file)
                if saga_date and start_date <= saga_date <= end_date:
                    sagas.append(saga_file)
        
        return sorted(sagas, key=lambda p: self.get_saga_date(p) or datetime.min)


class AutoOrganizer:
    """
    Automatically organizes sagas as they're created.
    Can be integrated with saga save operations.
    """
    
    def __init__(self, saga_dir: Path = None, auto_organize: bool = True):
        self.organizer = SagaOrganizer(saga_dir)
        self.auto_organize = auto_organize
    
    def save_organized(self, saga_path: Path, content: str = None) -> Path:
        """Save a saga with automatic organization."""
        # If content provided, save it first
        if content is not None:
            saga_path.parent.mkdir(parents=True, exist_ok=True)
            saga_path.write_text(content, encoding='utf-8')
        
        # Organize if enabled
        if self.auto_organize:
            organized_path = self.organizer.organize_saga(saga_path)
            return organized_path
        
        return saga_path
    
    def should_reorganize(self) -> bool:
        """Check if reorganization is needed."""
        stats = self.organizer.get_statistics()
        
        # Reorganize if more than 20% of sagas are unorganized
        if stats['total_sagas'] > 0:
            unorganized_ratio = stats['unorganized_sagas'] / stats['total_sagas']
            return unorganized_ratio > 0.2
        
        return False
    
    def auto_cleanup(self):
        """Automatically organize and cleanup if needed."""
        if self.should_reorganize():
            self.organizer.organize_all()
            self.organizer.cleanup_empty_dirs()
            return True
        return False