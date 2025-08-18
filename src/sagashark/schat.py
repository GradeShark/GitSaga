#!/usr/bin/env python3
"""
schat - SagaChat wrapper for Claude Code
Automatically captures all Claude Code conversations to sagachat
No MCP needed - just wraps the claude command
"""

import sys
import os
import subprocess
import select
from datetime import datetime
from pathlib import Path
import re
import time

class SchatWrapper:
    def __init__(self):
        """Initialize the schat wrapper"""
        # Determine saga directory based on environment
        self.saga_base = self._get_saga_dir()
        self.chat_dir = self.saga_base / 'sagachat'
        self.chat_dir.mkdir(parents=True, exist_ok=True)
        
        # Create session file
        self.session_file = self._create_session_file()
        self.message_count = 0
        
    def _get_saga_dir(self):
        """Get .sagashark directory (works in WSL and Windows)"""
        # Check if we're in a project with .sagashark
        cwd = Path.cwd()
        if (cwd / '.sagashark').exists():
            return cwd / '.sagashark'
        
        # Otherwise use home directory
        return Path.home() / '.sagashark'
    
    def _create_session_file(self):
        """Create a new session file with timestamp"""
        now = datetime.now()
        
        # Create year/month/week structure
        year = now.strftime("%Y")
        month = now.strftime("%m")
        week = now.strftime("week-%U")
        
        session_dir = self.chat_dir / year / month / week
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = now.strftime("%Y-%m-%d-%H%M")
        
        # Try to extract topic from first input (will update later)
        filename = f"{timestamp}-claude-session.md"
        session_path = session_dir / filename
        
        # Write initial header
        with open(session_path, 'w', encoding='utf-8') as f:
            f.write(f"---\n")
            f.write(f"id: chat-{timestamp}\n")
            f.write(f"title: Claude Code Session\n")
            f.write(f"started: {now.isoformat()}\n")
            f.write(f"model: claude\n")
            f.write(f"messages: 0\n")
            f.write(f"---\n\n")
            f.write(f"## Conversation\n\n")
        
        return session_path
    
    def _append_message(self, role, content):
        """Append a message to the session file"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        with open(self.session_file, 'a', encoding='utf-8') as f:
            f.write(f"### {role} [{timestamp}]\n\n")
            f.write(content)
            if not content.endswith('\n'):
                f.write('\n')
            f.write('\n')
        
        self.message_count += 1
        
        # Update message count in frontmatter
        self._update_frontmatter()
    
    def _update_frontmatter(self):
        """Update the frontmatter with current stats"""
        content = self.session_file.read_text(encoding='utf-8')
        
        # Update message count
        content = re.sub(
            r'messages: \d+',
            f'messages: {self.message_count}',
            content
        )
        
        self.session_file.write_text(content, encoding='utf-8')
    
    def _extract_topic_from_input(self, first_input):
        """Extract a topic from the first user input"""
        # Clean up the input
        topic = first_input.strip().lower()
        
        # Remove common starting phrases
        topic = re.sub(r'^(help me |can you |i need to |please |how do i |what is |explain )', '', topic)
        
        # Take first 50 chars and clean for filename
        topic = re.sub(r'[^\w\s-]', '', topic)[:50].strip()
        topic = re.sub(r'[-\s]+', '-', topic)
        
        if topic:
            # Rename the file with the topic
            new_name = self.session_file.stem.rsplit('-', 2)[0] + f"-{topic}.md"
            new_path = self.session_file.parent / new_name
            
            # Update file content with new title
            content = self.session_file.read_text(encoding='utf-8')
            content = re.sub(
                r'title: Claude Code Session',
                f'title: {first_input[:80]}',
                content
            )
            self.session_file.write_text(content, encoding='utf-8')
            
            # Rename file
            self.session_file.rename(new_path)
            self.session_file = new_path
    
    def run(self):
        """Run Claude with capture"""
        print(f"[SagaChat] Recording to {self.session_file.name}")
        print("Starting Claude Code...\n")
        
        # Use script command for complete capture (works better than subprocess)
        if sys.platform == 'win32':
            # Windows: Direct capture with tee
            cmd = f'claude 2>&1 | tee -a "{self.session_file}"'
        else:
            # Linux/WSL: Use script for better terminal handling
            temp_log = Path(f"/tmp/schat-{os.getpid()}.log")
            cmd = f'script -q -f -c "claude" "{temp_log}"'
        
        try:
            # Run the command
            result = subprocess.run(cmd, shell=True)
            
            # On Linux/WSL, parse the script output
            if sys.platform != 'win32' and temp_log.exists():
                self._parse_script_output(temp_log)
                temp_log.unlink()  # Clean up temp file
                
        except KeyboardInterrupt:
            print(f"\n\n[SagaChat] Session saved to {self.session_file.name}")
        except Exception as e:
            print(f"\n[ERROR] {e}")
            print(f"[SagaChat] Partial session saved to {self.session_file.name}")
    
    def _parse_script_output(self, script_file):
        """Parse script command output and format for sagachat"""
        with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m|\x1b\[K|\r')
        content = ansi_escape.sub('', content)
        
        # Split into messages (this is approximate - could be refined)
        lines = content.split('\n')
        
        current_role = None
        current_message = []
        first_user_input = None
        
        for line in lines:
            # Detect role changes (heuristic)
            if line.startswith('Human:') or line.startswith('You:') or line.startswith('> '):
                if current_message and current_role:
                    message_text = '\n'.join(current_message)
                    self._append_message(current_role, message_text)
                    
                    # Extract topic from first user input
                    if current_role == 'User' and not first_user_input:
                        first_user_input = message_text
                        self._extract_topic_from_input(first_user_input)
                
                current_role = 'User'
                current_message = [line]
                
            elif line.startswith('Assistant:') or line.startswith('Claude:'):
                if current_message and current_role:
                    message_text = '\n'.join(current_message)
                    self._append_message(current_role, message_text)
                    
                    # Extract topic from first user input
                    if current_role == 'User' and not first_user_input:
                        first_user_input = message_text
                        self._extract_topic_from_input(first_user_input)
                
                current_role = 'Claude'
                current_message = [line]
                
            else:
                current_message.append(line)
        
        # Don't forget the last message
        if current_message and current_role:
            self._append_message(current_role, '\n'.join(current_message))

def main():
    """Main entry point for schat"""
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print("schat - Auto-capture Claude Code conversations")
            print("\nUsage:")
            print("  schat           Start Claude with auto-capture")
            print("  schat --list    List recent chat sessions")
            print("  schat --search  Search chat sessions")
            print("\nSessions are saved to .sagashark/sagachat/")
            return
        
        elif sys.argv[1] == '--list':
            # List recent sessions
            list_recent_sessions()
            return
            
        elif sys.argv[1] == '--search':
            if len(sys.argv) < 3:
                print("Usage: schat --search <query>")
                return
            search_sessions(' '.join(sys.argv[2:]))
            return
    
    # Check if claude is available (only when starting a session)
    try:
        subprocess.run(['claude', '--version'], capture_output=True, check=False)
    except FileNotFoundError:
        print("[ERROR] Claude Code CLI not found. Please ensure 'claude' is in your PATH.")
        sys.exit(1)
    
    # Start wrapped Claude session
    wrapper = SchatWrapper()
    wrapper.run()

def list_recent_sessions():
    """List recent chat sessions"""
    saga_dir = Path.cwd() / '.sagashark' / 'sagachat'
    if not saga_dir.exists():
        saga_dir = Path.home() / '.sagashark' / 'sagachat'
    
    if not saga_dir.exists():
        print("No chat sessions found.")
        return
    
    # Find all session files from last 7 days
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=7)
    
    sessions = []
    for md_file in saga_dir.rglob('*.md'):
        if md_file.stat().st_mtime > cutoff.timestamp():
            sessions.append(md_file)
    
    if not sessions:
        print("No recent sessions found.")
        return
    
    print("\n[RECENT CHAT SESSIONS]\n")
    sessions.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    for session in sessions[:10]:
        timestamp = datetime.fromtimestamp(session.stat().st_mtime)
        rel_path = session.relative_to(saga_dir)
        print(f"  {timestamp.strftime('%Y-%m-%d %H:%M')} - {session.stem}")
    
    print(f"\nTotal: {len(sessions)} sessions in last 7 days")

def search_sessions(query):
    """Search through chat sessions"""
    saga_dir = Path.cwd() / '.sagashark' / 'sagachat'
    if not saga_dir.exists():
        saga_dir = Path.home() / '.sagashark' / 'sagachat'
    
    if not saga_dir.exists():
        print("No chat sessions found.")
        return
    
    print(f"\n[SEARCHING FOR: {query}]\n")
    
    matches = []
    for md_file in saga_dir.rglob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8', errors='ignore')
            if query.lower() in content.lower():
                # Count occurrences
                count = content.lower().count(query.lower())
                matches.append((md_file, count))
        except:
            continue
    
    if not matches:
        print(f"No sessions found containing '{query}'")
        return
    
    matches.sort(key=lambda x: x[1], reverse=True)
    
    for session, count in matches[:10]:
        rel_path = session.relative_to(saga_dir)
        print(f"  {rel_path} ({count} matches)")
    
    print(f"\nTotal: {len(matches)} sessions contain '{query}'")

if __name__ == '__main__':
    main()