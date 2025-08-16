# SagaShark Commit Convention for Claude Code

## Overview
When working on this project, use SagaShark's significance scoring system to determine when to write detailed debugging sagas directly in commit messages. This eliminates the need for external LLMs while leveraging Claude Code's intelligence.

## Significance Scoring System

### Score every commit from 1-10:
- **9-10**: Critical bugs, production incidents, breakthrough solutions
- **7-8**: Complex debugging, significant features, architectural changes
- **5-6**: Standard features, moderate refactoring, important documentation
- **3-4**: Minor features, small bug fixes, routine updates
- **1-2**: Typos, formatting, trivial changes

## Commit Message Requirements

### ⭐ HIGH SIGNIFICANCE (Score 7+)
Write DETAILED saga-style commit messages with the following sections:

```
[SAGASHARK:8] Fix: Database connection pool exhaustion causing user lockouts

## Problem Statement
- **Symptoms**: [What users experienced]
- **Error Messages**: [Exact errors encountered]
- **Impact**: [Number of users affected, severity]
- **Environment**: [Production/staging, relevant versions]

## Investigation Journey
1. Initial hypothesis: [What you thought it was]
2. Debugging steps taken:
   - [Each step with results]
   - [Dead ends and why they failed]
   - [Key insights that led to breakthrough]
3. Root cause discovery: [The "aha" moment]

## Root Cause Analysis
- **Immediate Cause**: [Direct technical cause]
- **Underlying Cause**: [Deeper systemic issue]
- **Contributing Factors**: [What made it worse]

## Solution Implemented
```code
# Key code changes with explanation
[Actual code that fixed the issue]
```
- **Why This Works**: [Explain the fix mechanism]
- **Alternative Considered**: [Other approaches and why rejected]

## Verification & Testing
- Test case added: [Description]
- Manual verification: [Steps taken]
- Performance impact: [Metrics before/after]
- Regression check: [What you verified didn't break]

## Lessons Learned
- **What went wrong**: [Process/code that allowed this bug]
- **Prevention**: [How to prevent similar issues]
- **Monitoring added**: [New alerts/metrics]
- **Documentation updated**: [What docs changed]

## Follow-up Tasks
- [ ] Add monitoring for connection pool metrics
- [ ] Review similar code patterns elsewhere
- [ ] Update team runbook

**Time Spent**: 4 hours
**Complexity**: High (distributed system, race condition)
**Files Changed**: 5 files across 3 services
```

### ⚡ NORMAL SIGNIFICANCE (Score 4-6)
Use structured but concise messages:

```
[SAGASHARK:5] Add user profile image upload

- Added image upload to profile settings
- Validates file size (max 5MB) and type (jpg/png)
- Stores in S3 with CDN delivery
- Tests included for validation logic
```

### 📝 LOW SIGNIFICANCE (Score 1-3)
Standard brief commits:

```
Fix typo in README
Update dependencies
Format code with prettier
```

## Token Economics Strategy

### When to spend tokens on detailed commits:
- **Always (Score 9-10)**: Critical issues deserve full documentation
- **Usually (Score 7-8)**: Complex debugging benefits from detail
- **Rarely (Score 5-6)**: Only if particularly instructive
- **Never (Score 1-4)**: Keep these concise

### Estimated token usage:
- Detailed saga commit: 300-500 tokens (10% of commits)
- Normal commit: 20-50 tokens (60% of commits)
- Brief commit: 5-15 tokens (30% of commits)
- **Result**: Rich documentation at minimal token cost

## SagaShark Integration

### Automatic Capture
SagaShark will automatically detect and extract commits marked with `[SAGASHARK:n]` where n is the score.

### Benefits
1. **No external LLM needed** - Claude Code is your LLM
2. **Perfect accuracy** - Claude knows exactly what happened
3. **Zero configuration** - Works immediately
4. **Token efficient** - Only detailed when valuable
5. **Searchable history** - All debugging knowledge preserved

## Trigger Phrases

Use these phrases to remind yourself when a detailed commit is warranted:

- "This was tricky to debug..."
- "Finally figured out..."
- "Spent hours on this..."
- "This could happen again..."
- "Team should know about..."
- "Breakthrough moment when..."

## Examples from Real Debugging

### Example 1: Score 9 - Critical Production Bug
```
[SAGASHARK:9] Fix: Memory leak in WebSocket handler causing server crashes

## Problem Statement
- **Symptoms**: Server crashes every 4-6 hours with OOM errors
- **Error Messages**: "FATAL ERROR: Reached heap limit Allocation failed"
- **Impact**: 100% downtime, affecting 10,000+ active users
- **Environment**: Production Node.js 18.17, 2GB RAM containers

## Investigation Journey
1. Initial hypothesis: Traffic spike overwhelming server
   - Checked metrics: Traffic was normal
   - Dead end: Not a load issue
   
2. Memory profiling revealed steady RAM growth
   - Heap snapshots showed WebSocket objects accumulating
   - Breakthrough: Sockets not being cleaned up on disconnect

[... continues with full debugging saga ...]
```

### Example 2: Score 5 - Standard Feature
```
[SAGASHARK:5] Add dark mode toggle to settings

- Implemented theme context provider
- Persists preference to localStorage  
- Smooth transition with CSS variables
- Accessibility tested with screen readers
```

## Remember

> "If you had to explain this bug to yourself in 6 months, what would you want to know?"

When the answer involves a journey, not just a destination, write a saga.

## Customization

Adjust these guidelines based on your project's needs:
- Increase detail threshold for critical systems
- Add team-specific sections (e.g., "Customer Impact")
- Include links to monitoring dashboards
- Reference ticket numbers or incident reports

---

*This convention turns every significant debugging session into a permanent learning opportunity, using Claude Code as the intelligent documentarian.*