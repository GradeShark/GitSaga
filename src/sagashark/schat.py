#!/usr/bin/env python3
"""
schat v2 - SagaChat wrapper for Claude with REAL-TIME capture
Automatically captures all Claude conversations to sagachat with live updates
"""

import sys
import os
import subprocess
import select
from datetime import datetime
from pathlib import Path
import re
import time
import signal
import atexit
import threading
import queue
import io

class RealTimeSchatWrapper:
    def __init__(self):
        """Initialize the real-time schat wrapper"""
        # Determine saga directory based on environment
        self.saga_base = self._get_saga_dir()
        self.chat_dir = self.saga_base / 'sagachat'
        self.chat_dir.mkdir(parents=True, exist_ok=True)
        
        # Session management
        self.session_file = None
        self.temp_session_file = None
        self.final_session_file = None
        self.message_count = 0
        self.session_started = datetime.now()
        self.first_user_message = None
        self.session_active = True
        self.last_flush = time.time()
        
        # Buffer for incomplete lines
        self.line_buffer = ""
        self.message_buffer = []
        
        # Create initial session files
        self._init_session_files()
        
        # Setup cleanup handlers
        atexit.register(self._cleanup_session)
        signal.signal(signal.SIGINT, self._handle_interrupt)
        if sys.platform != 'win32':
            signal.signal(signal.SIGTERM, self._handle_interrupt)
    
    def _get_saga_dir(self):
        """Get .sagashark directory (works in WSL and Windows)"""
        # Check if we're in a project with .sagashark
        cwd = Path.cwd()
        if (cwd / '.sagashark').exists():
            return cwd / '.sagashark'
        
        # Otherwise use home directory
        return Path.home() / '.sagashark'
    
    def _init_session_files(self):
        """Initialize session files with temporary name"""
        now = datetime.now()
        
        # Create year/month/week structure (matching saga structure)
        year = now.strftime("%Y")
        month = now.strftime("%m-%B")  # "08-August" format
        week = self._get_week_of_month(now)
        
        session_dir = self.chat_dir / year / month / week
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Start with temporary filename
        timestamp = now.strftime("%Y-%m-%d-%H%M")
        temp_name = f"{timestamp}-active-session.md"
        self.temp_session_file = session_dir / temp_name
        self.session_file = self.temp_session_file
        
        # Check for orphaned sessions on startup
        self._check_orphaned_sessions(session_dir)
        
        # Write initial header with active status
        self._write_initial_header()
        
        print(f"[SagaChat] Recording to {self.session_file.name}")
        print("[SagaChat] Real-time capture enabled - file updates live")
        print("Starting Claude...\n")
    
    def _check_orphaned_sessions(self, session_dir):
        """Check for and clean up orphaned active sessions"""
        for active_file in session_dir.glob("*-active-session.md"):
            if active_file != self.temp_session_file:
                # Found an orphaned session, mark it as interrupted
                print(f"[SagaChat] Found incomplete session: {active_file.name}")
                self._mark_session_interrupted(active_file)
    
    def _mark_session_interrupted(self, session_file):
        """Mark a session as interrupted"""
        try:
            with open(session_file, 'a', encoding='utf-8') as f:
                f.write("\n\n### [WARNING] SESSION INTERRUPTED\n")
                f.write(f"Session was not properly closed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.flush()
            
            # Rename to remove 'active' marker
            new_name = session_file.name.replace('-active-session.md', '-interrupted.md')
            new_path = session_file.parent / new_name
            session_file.rename(new_path)
        except Exception as e:
            print(f"[SagaChat] Warning: Could not clean up orphaned session: {e}")
    
    def _write_initial_header(self):
        """Write initial session header"""
        header = f"""---
id: chat-{self.session_started.strftime('%Y-%m-%d-%H%M')}
title: Claude Session (topic pending)
started: {self.session_started.isoformat()}
status: active
model: claude
messages: 0
last_update: {datetime.now().isoformat()}
---

## Conversation

"""
        with open(self.session_file, 'w', encoding='utf-8') as f:
            f.write(header)
            f.flush()
    
    def _update_header(self, title=None, status=None):
        """Update session header with title or status"""
        try:
            content = self.session_file.read_text(encoding='utf-8')
            
            if title:
                content = re.sub(
                    r'title: .*',
                    f'title: {title}',
                    content
                )
            
            if status:
                content = re.sub(
                    r'status: .*',
                    f'status: {status}',
                    content
                )
            
            # Update message count and last update
            content = re.sub(
                r'messages: \d+',
                f'messages: {self.message_count}',
                content
            )
            content = re.sub(
                r'last_update: .*',
                f'last_update: {datetime.now().isoformat()}',
                content
            )
            
            self.session_file.write_text(content, encoding='utf-8')
        except Exception as e:
            # Don't crash on header update failure
            pass
    
    def _append_to_session(self, content, flush_immediately=True):
        """Append content to session file with optional immediate flush"""
        try:
            with open(self.session_file, 'a', encoding='utf-8') as f:
                f.write(content)
                if flush_immediately:
                    f.flush()
                    os.fsync(f.fileno())  # Force OS to write to disk
        except Exception as e:
            print(f"[SagaChat] Warning: Could not write to session file: {e}")
    
    def _process_line(self, line):
        """Process a single line of output"""
        # Add to buffer
        self.line_buffer += line
        
        # Check if we have a complete line
        if '\n' in self.line_buffer:
            complete_lines = self.line_buffer.split('\n')
            # Keep the incomplete part
            self.line_buffer = complete_lines[-1]
            
            # Process complete lines
            for complete_line in complete_lines[:-1]:
                self._process_complete_line(complete_line)
    
    def _process_complete_line(self, line):
        """Process a complete line and detect message boundaries"""
        # Remove ANSI codes
        clean_line = self._strip_ansi(line)
        
        # Detect message boundaries
        if self._is_user_message_start(clean_line):
            self._flush_current_message()
            self._start_message('User', clean_line)
        elif self._is_claude_message_start(clean_line):
            self._flush_current_message()
            self._start_message('Claude', clean_line)
        else:
            # Add to current message buffer
            self.message_buffer.append(clean_line)
        
        # Periodic flush (every 5 seconds)
        if time.time() - self.last_flush > 5:
            self._flush_current_message()
    
    def _is_user_message_start(self, line):
        """Detect start of user message"""
        patterns = [
            r'^Human:',
            r'^You:',
            r'^User:',
            r'^>',  # Common prompt indicator
        ]
        return any(re.match(pattern, line.strip()) for pattern in patterns)
    
    def _is_claude_message_start(self, line):
        """Detect start of Claude message"""
        patterns = [
            r'^Assistant:',
            r'^Claude:',
            r'^AI:',
        ]
        return any(re.match(pattern, line.strip()) for pattern in patterns)
    
    def _start_message(self, role, first_line):
        """Start a new message"""
        self.message_buffer = [first_line]
        self.current_role = role
        self.current_message_time = datetime.now()
    
    def _flush_current_message(self):
        """Flush current message buffer to file"""
        if not self.message_buffer or not hasattr(self, 'current_role'):
            return
        
        # Format message
        timestamp = self.current_message_time.strftime("%H:%M:%S")
        message_content = '\n'.join(self.message_buffer)
        
        # Extract topic from first user message
        if self.current_role == 'User' and not self.first_user_message:
            self.first_user_message = message_content
            self._extract_and_rename_session()
        
        # Write message
        formatted_message = f"\n### {self.current_role} [{timestamp}]\n\n{message_content}\n"
        self._append_to_session(formatted_message)
        
        # Update counters
        self.message_count += 1
        self._update_header()
        
        # Clear buffer
        self.message_buffer = []
        self.last_flush = time.time()
    
    def _extract_and_rename_session(self):
        """Extract topic from first message and rename session file"""
        if not self.first_user_message:
            return
        
        # Extract topic
        topic = self._extract_topic(self.first_user_message)
        
        # Create new filename
        timestamp = self.session_started.strftime("%Y-%m-%d-%H%M")
        new_name = f"{timestamp}-{topic}.md"
        new_path = self.session_file.parent / new_name
        
        # Rename file
        try:
            self.session_file.rename(new_path)
            self.session_file = new_path
            self.final_session_file = new_path
            
            # Update header with extracted title
            self._update_header(title=self.first_user_message[:100])
            
            print(f"[SagaChat] Session renamed to: {new_name}")
        except Exception as e:
            print(f"[SagaChat] Could not rename session: {e}")
    
    def _extract_topic(self, message):
        """Extract a topic from the first user message"""
        # Clean up the message
        topic = message.strip().lower()
        
        # Remove common prefixes
        prefixes = [
            'help me', 'can you', 'i need to', 'please',
            'how do i', 'what is', 'explain', 'show me'
        ]
        for prefix in prefixes:
            if topic.startswith(prefix):
                topic = topic[len(prefix):].strip()
                break
        
        # Take first 50 chars and clean for filename
        topic = re.sub(r'[^\w\s-]', '', topic)[:50].strip()
        topic = re.sub(r'[-\s]+', '-', topic)
        
        return topic or 'conversation'
    
    def _strip_ansi(self, text):
        """Remove ANSI escape sequences"""
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m|\x1b\[K|\r')
        return ansi_escape.sub('', text)
    
    def run(self):
        """Run Claude with real-time capture"""
        try:
            if sys.platform == 'win32':
                self._run_windows()
            else:
                self._run_unix()
        except KeyboardInterrupt:
            self._cleanup_session()
        except Exception as e:
            print(f"[SagaChat] Error: {e}")
            self._cleanup_session()
    
    def _run_windows(self):
        """Windows-specific implementation using subprocess with pipes"""
        # Start Claude process
        process = subprocess.Popen(
            ['claude'],
            stdin=sys.stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffered
            encoding='utf-8',
            errors='replace'
        )
        
        try:
            # Read output in real-time
            for line in process.stdout:
                # Display to user
                print(line, end='')
                
                # Process for capture
                self._process_line(line)
            
            # Wait for process to complete
            process.wait()
        finally:
            self._cleanup_session()
    
    def _run_unix(self):
        """Unix/Linux/WSL implementation using pty for better terminal handling"""
        import pty
        import select
        
        # Create pseudo-terminal
        master_fd, slave_fd = pty.openpty()
        
        # Start Claude process
        process = subprocess.Popen(
            ['claude'],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=subprocess.STDOUT,
            close_fds=True
        )
        
        try:
            while process.poll() is None:
                # Check for data
                r, _, _ = select.select([master_fd, sys.stdin], [], [], 0.1)
                
                if master_fd in r:
                    try:
                        data = os.read(master_fd, 1024).decode('utf-8', errors='replace')
                        # Display to user
                        sys.stdout.write(data)
                        sys.stdout.flush()
                        
                        # Process for capture
                        self._process_line(data)
                    except OSError:
                        break
                
                if sys.stdin in r:
                    # Forward user input to Claude
                    data = sys.stdin.read(1)
                    os.write(master_fd, data.encode())
            
        finally:
            os.close(master_fd)
            os.close(slave_fd)
            self._cleanup_session()
    
    def _handle_interrupt(self, signum, frame):
        """Handle interrupt signal"""
        print("\n[SagaChat] Interrupt received, saving session...")
        self._cleanup_session()
        sys.exit(0)
    
    def _cleanup_session(self):
        """Clean up and finalize session"""
        if not self.session_active:
            return
        
        self.session_active = False
        
        # Flush any remaining buffer
        self._flush_current_message()
        
        # Mark session as completed
        self._append_to_session(f"\n### Session ended at {datetime.now().strftime('%H:%M:%S')}\n")
        self._update_header(status='completed')
        
        # Final rename if needed
        if self.session_file.name.endswith('-active-session.md'):
            final_name = self.session_file.name.replace('-active-session.md', '-completed.md')
            final_path = self.session_file.parent / final_name
            try:
                self.session_file.rename(final_path)
                self.session_file = final_path
            except:
                pass
        
        print(f"\n[SagaChat] Session saved to {self.session_file.name}")
        print(f"[SagaChat] Total messages: {self.message_count}")
    
    def _get_week_of_month(self, date):
        """Get week number of the month (1-5) to match saga structure"""
        first_day = date.replace(day=1)
        days_since_first = (date - first_day).days
        week_num = (days_since_first // 7) + 1
        return f"week-{week_num:02d}"

# Keep original functions for list and search
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
    
    for session in sessions[:20]:
        timestamp = datetime.fromtimestamp(session.stat().st_mtime)
        rel_path = session.relative_to(saga_dir)
        
        # Show status indicator
        if "completed" in session.name:
            status = "[OK]"
        elif "interrupted" in session.name:
            status = "[!!]"
        else:
            status = "[*]"
        print(f"  {status} {timestamp.strftime('%Y-%m-%d %H:%M')} - {session.stem}")
    
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

def main():
    """Main entry point for schat v2"""
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print("schat v2 - Auto-capture Claude conversations with REAL-TIME updates")
            print("\nUsage:")
            print("  schat           Start Claude with real-time capture")
            print("  schat --list    List recent chat sessions")
            print("  schat --search  Search chat sessions")
            print("\nFeatures:")
            print("  - Real-time file updates (never lose work)")
            print("  - Crash recovery (sessions marked if interrupted)")
            print("  - Live monitoring (tail -f the session file)")
            print("  - Smart topic extraction from first message")
            print("\nSessions are saved to .sagashark/sagachat/")
            return
            
        elif sys.argv[1] == '--list':
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
        print("[ERROR] Claude CLI not found. Please ensure 'claude' is in your PATH.")
        sys.exit(1)
    
    # Start real-time wrapped Claude session
    wrapper = RealTimeSchatWrapper()
    wrapper.run()

if __name__ == '__main__':
    main()