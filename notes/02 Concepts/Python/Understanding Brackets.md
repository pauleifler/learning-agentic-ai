---
type: concept
status: learning
domain:
  - agentic-ai
created: 2026-07-16
confidence: 1
tags:
  - ai/agents
category: "    Python Fundamentals"
---

# Understanding Brackets

## Definition

Python uses different brackets for different purposes.

Round brackets ()
- Call a function

Square brackets [] - think create or select
- Create a list
- Select a column
- Filter rows

Curly brackets {}
- Create a dictionary

## Why it matters

What problem does it solve?

## How it works

Describe the mechanism.

## Example

**Round brackets calling a function**

```python

print("Hello")

```

```python

sorted(my_list)

```

```python

pd.concat(my_list)

```

**Square brackets - create a list**

```python

teams = [
    "Leeds",
    "Burnley",
]

```

**Square brackets - select a column**

```python

data["league"]

```

**Square brackets - filter rows**

```python

data[
    data["league"] == "Championship"
]

```

**Curly brackets**

```python

points = {
    "Win": 3,
    "Draw": 1,
    "Loss": 0,
}

```

## Failure modes

When might it fail or be inappropriate?

## Implementation

How would you implement or test it?

## Interview explanation

Explain it in approximately 60 seconds.

## Related concepts

- [[]]

## Sources

-