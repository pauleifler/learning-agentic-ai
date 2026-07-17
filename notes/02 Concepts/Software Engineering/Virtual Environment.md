
## Definition

A virtual environment is an isolated Python environment for a single project. It keeps dependencies separate from other projects and from the system Python installation.

## Why it matters

- Prevents package version conflicts.
- Makes projects reproducible.
- Allows different projects to use different library versions.

## Command

```bash
python3 -m venv .venv
source .venv/bin/activate