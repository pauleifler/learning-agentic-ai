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

# When to Return from a Function

## Definition

A function should `return` something when another part of the program needs to use the result.

If the function's only purpose is to perform an action (such as printing or saving a file), it usually doesn't need to return anything.

## Why it matters

What problem does it solve?

## How it works

Ask yourself:

> "Will another part of my program need this value?"

If **yes**, return it.

If **no**, don't.

`return` does two things:

1. Immediately exits the function.

2. Sends a value back to the caller.

Example:

```python

def example():

    print("Start")

    return 10

    print("End")

```

Output:

```

Start

```

The final `print()` never runs because the function ends at `return`.

---

**Returning Multiple Values**

Python can return more than one value.

```python

def divide(a, b):

    quotient = a // b

    remainder = a % b

    return quotient, remainder

```

Usage:

```python

q, r = divide(10, 3)

```

Result:

```

q = 3

r = 1

```

## Example

```python

def calculate_area(width, height):

    return width * height

```

The returned value can be stored:

```python

area = calculate_area(10, 5)

print(area)

```

Output:

```

50

```


**Functions That Don't Return**

These functions perform an action.

Example:

```python

def greet(name):

    print(f"Hello {name}")

```

Calling it:

```python

greet("Paul")

```

prints:

```

Hello Paul

```

There is nothing useful to return because the function's purpose is simply to display text.




## Failure modes

Using `print()` instead of `return`.

Incorrect:

```python

def add(a, b):

    print(a + b)

```

This prints:

```

5

```

But you can't use the result:

```python

result = add(2, 3)

print(result)

```

Output:

```

5

None

```

Because nothing was returned.

Correct:

```python

def add(a, b):

    return a + b

```

Now:

```python

result = add(2, 3)

print(result)

```

Output:

```

5

```

## Returning complex objects

Functions can return more than simple values.

Example:

```python

return {

    "fixture": fixture,
    "comparison": comparison,
    "league_table": league_table,

}

```

## Implementation

How would you implement or test it?

## Interview explanation

A function should return a value when that value is needed elsewhere in the program. Functions whose purpose is to perform an action, such as displaying information or writing a file, often return nothing (`None`). Separating functions that calculate data from those that perform actions makes code easier to reuse, test and maintain.

## Related concepts

- [[]]

## Sources

-