---
id: saga-649e8ef3
title: Fixed Windows Unicode issues in CLI
type: debugging
timestamp: '2025-08-14T21:06:30.596239'
branch: main
status: active
tags:
- windows
- unicode
- bug
files_changed: []
---

Rich console was throwing UnicodeEncodeError on Windows with emoji characters. Replaced all emojis with ASCII alternatives for cross-platform compatibility.