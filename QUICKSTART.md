# GitSaga Quick Start Guide

**Get up and running in 2 minutes!**

## Installation

```bash
# Clone and install
git clone https://github.com/yourusername/gitsaga.git
cd gitsaga
pip install -e .
```

## Your First Saga in 30 Seconds

```bash
# 1. Go to your project
cd your-project

# 2. Initialize GitSaga
saga init

# 3. Create your first saga
saga commit "Finally fixed that authentication bug" --type=debugging

# 4. Search your knowledge
saga search "authentication"
```

## The Cool Banner

When you run your first command, you'll see the ANSI Shadow banner:
```
 ██████╗ ██╗████████╗███████╗ █████╗  ██████╗  █████╗ 
██╔════╝ ██║╚══██╔══╝██╔════╝██╔══██╗██╔════╝ ██╔══██╗
██║  ███╗██║   ██║   ███████╗███████║██║  ███╗███████║
██║   ██║██║   ██║   ╚════██║██╔══██║██║   ██║██╔══██║
╚██████╔╝██║   ██║   ███████║██║  ██║╚██████╔╝██║  ██║
 ╚═════╝ ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
```

## Essential Commands

### Create a Saga
```bash
# Quick saga
saga commit "Implemented Redis caching"

# Detailed saga
saga commit "Fixed memory leak in WebSocket handler" \
  --type=debugging \
  --tags="websocket,memory,performance" \
  --content="Found connection pool wasn't releasing..."
```

### Search Your Knowledge
```bash
# Find relevant sagas
saga search "memory leak"
saga search "redis"
saga search "authentication timeout"
```

### View Recent Work
```bash
# See recent sagas
saga log

# See yesterday's work
saga log --since=yesterday

# See last week
saga log --since=week
```

### Check Status
```bash
# Repository overview
saga status
```

## Saga Types

- **debugging** - Bug fixes and troubleshooting
- **feature** - New functionality
- **architecture** - Design decisions
- **optimization** - Performance improvements
- **general** - Everything else

## Example Workflow

```bash
# Morning: What did I work on yesterday?
saga log --since=yesterday

# Start debugging a problem
saga commit "Investigating API timeout issues" --type=debugging

# ... work on the problem ...

# Document the solution
saga commit "Fixed API timeouts with connection pooling" \
  --type=debugging \
  --tags="api,timeout,connection-pool" \
  --content="Root cause: connections weren't being reused..."

# Later: Find that solution again
saga search "timeout"
```

## What Gets Created

```
your-project/
└── .gitsaga/
    ├── config.json         # Settings
    └── sagas/             # Your sagas (markdown files)
        ├── main/          # Main branch sagas
        │   ├── debugging/
        │   └── feature/
        └── feature-xyz/   # Branch-specific sagas
```

## Tips

1. **Be descriptive** - Your future self will thank you
2. **Use tags** - Makes searching easier
3. **Document failures** - "This didn't work because..."
4. **Include code snippets** - Add solutions directly in sagas
5. **Regular commits** - Create sagas as you work, not after

## No Cloud, No Database, No BS

- ✅ 100% local - your data stays on your machine
- ✅ Git-native - sagas version with your code
- ✅ Zero config - just `saga init` and go
- ✅ Fast - search hundreds of sagas in milliseconds

## Need Help?

```bash
# See all commands
saga --help

# Get help on specific command
saga commit --help
saga search --help
```

---

**Remember:** Every debugging session teaches something worth remembering. GitSaga ensures that knowledge isn't lost.

Start building your development story today! 🚀