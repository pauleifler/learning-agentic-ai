---
type: concept
status: learning
domain:
  - agentic-ai
created: 2026-07-15
confidence: 1
tags:
  - ai/agents
category: "    Python Fundamentals"
---

# iloc

## Definition

iloc` selects rows and columns in a pandas DataFrame by their numerical position.

## Why it matters

Use `iloc` when the position of the data is important rather than its label.

## How it works

Describe the mechanism.

## Example

```python

data = (
    data
    .sort_values("date")
    .reset_index(drop=True)
)

data.iloc[0]      # First row

data.iloc[-1]     # Last row

data.iloc[:5]     # First five rows

data.iloc[2:5]    # Rows 2–4

```

## Interview explanation

`iloc` is pandas’ integer-location indexer. It retrieves rows and columns based on their numerical position, similar to indexing a Python list.

## Related concepts

- [[DataFrame]]
- [[loc]]