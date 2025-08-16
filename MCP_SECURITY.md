# MCP Server Security Guidelines for GitSaga

## Overview
The Model Context Protocol (MCP) server for GitSaga operates locally and communicates via stdio, making it inherently more secure than network-based services. However, proper security measures are still essential.

## Security Architecture

### 1. Communication Model
- **Protocol**: stdio (stdin/stdout) only
- **Network**: No network sockets or ports
- **Access**: Only accessible by parent process (Claude Desktop)
- **Authentication**: Implicit via process ownership

### 2. File System Security

#### Path Validation
```python
from pathlib import Path

class SecureSagaServer:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir.resolve()
    
    def validate_path(self, path: str) -> Path:
        """Prevent path traversal attacks"""
        resolved = (self.base_dir / path).resolve()
        if not resolved.is_relative_to(self.base_dir):
            raise ValueError(f"Path {path} is outside saga directory")
        return resolved
```

#### Restricted Operations
- ✅ Read sagas from `.gitsaga/sagas/`
- ✅ Write new sagas to designated directories
- ✅ Search within project boundaries
- ❌ Access system files
- ❌ Modify git configuration
- ❌ Execute arbitrary commands

### 3. Input Validation

#### Command Sanitization
```python
def sanitize_search_query(query: str) -> str:
    """Remove dangerous characters from search queries"""
    # Remove potential regex bombs
    if len(query) > 1000:
        raise ValueError("Query too long")
    
    # Escape special regex characters
    import re
    return re.escape(query)
```

#### Size Limits
- Maximum saga size: 1MB
- Maximum search results: 100
- Maximum path depth: 10 levels
- Query timeout: 5 seconds

### 4. Content Security

#### Secret Detection
```python
import re

SENSITIVE_PATTERNS = [
    r'(?i)(api[_-]?key|apikey)[\s:=]+[\w\-]+',
    r'(?i)(secret|token|password)[\s:=]+[\w\-]+',
    r'(?i)bearer\s+[\w\-\.]+',
    r'ssh-rsa\s+[\w\+/=]+',
    r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----'
]

def contains_secrets(content: str) -> bool:
    """Check if content contains potential secrets"""
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, content):
            return True
    return False
```

### 5. Resource Protection

#### Rate Limiting
```python
from collections import defaultdict
from time import time

class RateLimiter:
    def __init__(self, max_requests=100, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def check_rate_limit(self, operation: str) -> bool:
        now = time()
        # Clean old requests
        self.requests[operation] = [
            t for t in self.requests[operation] 
            if now - t < self.window
        ]
        
        if len(self.requests[operation]) >= self.max_requests:
            return False
        
        self.requests[operation].append(now)
        return True
```

## Security Checklist

### Before Deployment
- [ ] All paths validated against base directory
- [ ] Input sanitization implemented
- [ ] Size limits enforced
- [ ] Timeouts configured
- [ ] Secret detection active
- [ ] Rate limiting enabled
- [ ] Error messages don't leak sensitive info
- [ ] Logging doesn't include sensitive data

### Runtime Security
- [ ] Run with minimum required permissions
- [ ] Monitor resource usage
- [ ] Log security events
- [ ] Validate all user inputs
- [ ] Escape output when necessary
- [ ] Handle errors gracefully

## Threat Model

### Low Risk (Inherent to MCP)
1. **Remote exploitation**: Not possible (no network access)
2. **Unauthorized access**: Protected by OS process isolation
3. **Man-in-the-middle**: Not applicable (stdio communication)

### Medium Risk (Requires Mitigation)
1. **Path traversal**: Mitigated by path validation
2. **Resource exhaustion**: Mitigated by limits and timeouts
3. **Information disclosure**: Mitigated by secret scanning

### Acceptable Risks
1. **Local file access**: Required for functionality
2. **Git repository access**: Core feature
3. **Saga modification**: By design

## Implementation Example

```python
# mcp_server.py
import asyncio
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server

class SecureGitSagaServer:
    def __init__(self):
        self.base_dir = Path.cwd() / '.gitsaga'
        self.rate_limiter = RateLimiter()
        
    async def search_sagas(self, query: str) -> list:
        # Validate input
        if not self.rate_limiter.check_rate_limit('search'):
            raise ValueError("Rate limit exceeded")
        
        query = sanitize_search_query(query)
        
        # Validate paths
        saga_dir = self.validate_path('sagas')
        
        # Perform search with timeout
        try:
            results = await asyncio.wait_for(
                self._search(saga_dir, query),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            raise ValueError("Search timeout")
        
        # Filter sensitive content
        return [r for r in results if not contains_secrets(r)]
```

## Security Updates

### Regular Reviews
- Monthly: Review access logs for anomalies
- Quarterly: Update sensitive pattern detection
- Yearly: Full security audit

### Incident Response
1. If suspicious activity detected:
   - Log the event with details
   - Terminate the MCP server
   - Review saga files for corruption
   - Report to user

2. If secrets detected in sagas:
   - Warn user immediately
   - Don't save the saga
   - Log the event (without the secret)
   - Suggest using environment variables

## Conclusion

The MCP server for GitSaga has a minimal attack surface due to:
1. Local-only stdio communication
2. No network exposure
3. Process-level isolation
4. Limited scope (saga management only)

With proper input validation, path restrictions, and resource limits, the MCP server presents minimal security risk while providing powerful local automation capabilities.

## Resources
- [MCP Security Best Practices](https://modelcontextprotocol.io/docs/security)
- [OWASP Input Validation](https://owasp.org/www-community/controls/Input_Validation)
- [Path Traversal Prevention](https://owasp.org/www-community/attacks/Path_Traversal)