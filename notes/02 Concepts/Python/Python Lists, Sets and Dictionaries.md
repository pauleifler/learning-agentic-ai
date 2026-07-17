---
type: concept
status: learning
domain:
  - python
confidence: 2
tags:
  - python
  - data-structures
category: "    Python Fundamentals"
---

## **Quick comparison**

|**Type**|**Notation**|**Use it when**|
|---|---|---|
|List|`[ ]`|Order matters or duplicates are allowed|
|Set|`{ }`|Values must be unique|
|Dictionary|`{key: value}`|Values need labels or keys|

---

## **List**

A list stores an ordered sequence of values.

```python
tools = ["search", "calculator", "search"]
```

Key points:

- Uses square brackets: `[ ]`
- Keeps order
- Allows duplicates
- Access items by position

```python
tools[0]
```

Use a list for:

- Steps in a process
- Conversation messages
- Ordered tool names
- Any collection where position matters

---

## **Set**

A set stores unique values.

```python
tools = {"search", "calculator"}
```

Key points:

- Uses curly brackets: `{ }`
- Removes duplicates
- Does not use numeric indexes
- Useful for checking whether something exists

```python
"search" in tools
```

Use a set for:

- Unique permissions
- Removing duplicates
- Comparing groups
- Fast membership checks

Important: an empty set must use:

```python
tools = set()
```

This creates an empty dictionary, not a set:

```python
tools = {}
```

---

## **Dictionary**

A dictionary stores labelled values as key-value pairs.

```python
agent = {
    "name": "Research Agent",
    "active": True,
    "max_steps": 5,
}
```

Key points:

- Uses curly brackets with `key: value`
- Each key must be unique
- Access values using their key

```python
agent["name"]
```

Use a dictionary for:

- Configuration
- Agent state
- User details
- Structured data
- JSON-like information

---

## **Easy decision rule**

Use a **list** when order matters:

```python
steps = ["plan", "search", "answer"]
```

Use a **set** when uniqueness matters:

```python
permissions = {"read", "write"}
```

Use a **dictionary** when labels matter:

```python
settings = {
    "model": "gpt-5",
    "temperature": 0.2,
}
```

## **Memory aid**

```text
[ ]              = list
{value, value}   = set
{key: value}     = dictionary
```