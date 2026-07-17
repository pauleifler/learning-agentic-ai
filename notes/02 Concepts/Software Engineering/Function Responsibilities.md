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


# Software Design - Function Responsibilities

## Definition

Every function should have one clear responsibility.

A function should perform one well-defined task and have a single reason to change. It should answer one business question rather than trying to solve multiple problems.

Examples:

- `load_data()` → Load and prepare data.
- `get_next_fixture()` → Find the next fixture.
- `calculate_league_table()` → Calculate the current league table.

## Why it matters

Functions with a single responsibility are:

- Easier to understand.
- Easier to test.
- Easier to reuse.
- Easier to debug.
- Easier to modify without breaking unrelated behaviour.

As applications grow, small focused functions can be combined to solve larger problems without duplicating code.

## How it works

Each function should have one primary purpose.

Good example:

```python

def get_team_position(
    league_table: pd.DataFrame,
    team: str,
) -> int:

```

This function only answers one question:

> "What is this team's league position?"

It does not calculate the league table or compare teams.

Larger tasks are achieved by combining multiple small functions through an orchestrator rather than creating one large function.

## Example

Poor design:

```python

def analyse_match():
    load_data()
    calculate_league_table()
    compare_teams()
    generate_report()
    save_report()
```

This function has multiple responsibilities and becomes difficult to maintain.

Better design:

```python

load_data()

calculate_league_table()

compare_teams()

generate_pre_match_report()
```

Each function has one responsibility, while another function (such as `gather_match_context()`) coordinates them.

## Failure modes

A function may have too many responsibilities if:

- Its name contains words like "and", "then", or "everything".
- It becomes very long.
- It is difficult to describe in one sentence.
- Small changes require modifying unrelated code.
- It is hard to test in isolation.

Splitting functions too aggressively can also reduce readability, so aim for cohesive units of work rather than the smallest possible functions.

## Implementation

When writing a new function, ask:

1. What single question does this function answer?
2. Can I describe its purpose in one sentence?
3. Does it return one logical result?
4. If the business rules changed, would there be only one reason to edit this function?

If the answer to any of these is "no", consider splitting the function.

## Interview explanation

I try to design functions so that each has one clear responsibility. For example, in my Football Copilot project, `get_next_fixture()` only finds the next fixture, `calculate_league_table()` only builds the league table, and `compare_teams()` only compares two teams. I then use an orchestrator, `gather_match_context()`, to combine these tools into a larger workflow. This makes the code easier to test, reuse and maintain.

## Related concepts

- [[Orchestrators vs Tools]]
- [[Single Responsibility Principle]]
- [[Modular Programming]]
- [[Separation of Concerns]]
- [[Code Reuse]]

## Sources

- *Clean Code* — Robert C. Martin
- *The Pragmatic Programmer* — David Thomas & Andrew Hunt
- Python Documentation – Defining Functions

## Key takeaways

- A good function has one clear responsibility.
- Every function should answer one business question.
- Small, focused functions are easier to understand, test and reuse.
- Complex workflows should be built by combining small functions rather than writing one large function.
- Orchestrators coordinate functions; they should not duplicate business logic.
- If a function is difficult to describe in one sentence, it may have too many responsibilities.