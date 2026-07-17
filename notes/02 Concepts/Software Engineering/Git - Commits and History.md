---
type: concept
status: learning
domain:
  - agentic-ai
created: 2026-07-16
confidence: 1
tags:
  - ai/agents
category: "    Software & AI Engineering"
---

# Git - Commits and History

## Definition

A commit is a snapshot of your project at a specific point in time.

Think of it as a save point that records:
- What changed
- When it changed
- Why it changed

Each commit has a unique ID (hash).

## Why it matters

What problem does it solve?

## How it works

**Common commands**

Check **current status**, this shows:
- Modified files
- New files
- Staged files
- Branch information

```bash

git status

```

Stage a file

```bash

git add filename.py

```

Stage everything

```bash

git add .

```

Commit changes

```bash

git commit -m "feat: add league table calculation"

```

Upload commits to Github

```bash

git push

```

View recent commits

```bash

git log

```

Quit

```

q

```

Compact history

```bash

git log --oneline

```

Graph View

```bash

git log --oneline --graph --decorate

```

**Viewing Changes**

See unstaged changes

```bash

git diff

```

See a summary

```bash

git diff --stat

```

See the status

```bash

git status

```

# Professional Commit Messages

Use a prefix.

**feat**

New functionality.

```

feat: add league table generation

```

**fix**

Bug fix.

```

fix: handle teams with no previous matches

```

 **refactor**

Improves code without changing behaviour.

```

refactor: extract reusable match metrics

```

 **docs**

Documentation changes.

```

docs: update README

```

**chore**

Maintenance.

```

chore: update .gitignore

```

**Git workflow**
```

Working Directory

        │

        ▼

git add

        │

        ▼

Staging Area

        │

        ▼

git commit

        │

        ▼

Repository History

        │

        ▼

git push

        │

        ▼

GitHub

```

## Example

Give a concrete example.

## Failure modes

When might it fail or be inappropriate?

## Implementation

How would you implement or test it?

## Interview explanation

Git is a distributed version control system used to track changes in source code. I use it to create small, meaningful commits, maintain a clear project history and collaborate safely through GitHub.

## Related concepts

- [[]]

## Sources

-