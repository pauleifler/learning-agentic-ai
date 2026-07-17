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

# Software Design - Orchestrators vs Tools

## Definition

A **tool** is a function that performs one specific task and answers one business question.

An **orchestrator** is a function that coordinates multiple tools to solve a larger problem. It performs little or no business logic itself and instead manages the workflow between tools.

## Why it matters

Breaking an application into small tools makes the code easier to:

- understand
- test
- reuse
- extend

The orchestrator then combines those tools to complete more complex tasks without duplicating logic.

This pattern is fundamental in agentic AI because language models call tools to gather information before generating a response.
## How it works

A tool performs one focused task.

Example:

```python

get_next_fixture()

```

An orchestrator calls several tools in sequence.

```text

gather_match_context()

↓

get_next_fixture()

↓

calculate_league_table()

↓

compare_teams()

↓

Return one context object

```

The orchestrator is responsible for coordinating the workflow, not performing calculations itself.

## Example

```python

context = gather_match_context(
    data=data,
    team="QPR",
    current_round=25,
)

```

Internally this function calls:

- `get_next_fixture()`
- `calculate_league_table()`
- `compare_teams()`

and returns a single object containing everything required for a pre-match report.
## Failure modes

An orchestrator becomes difficult to maintain if it starts containing business logic.

For example, this would be poor design:

```python

def gather_match_context():
    ...
    calculate_goal_difference()
    calculate_points()

```

Those calculations belong in dedicated tools.

Similarly, tools should not start calling many unrelated tools, otherwise responsibilities become blurred.
## Implementation

To test an orchestrator:

1. Test each individual tool first.
2. Verify the orchestrator calls the correct tools.
3. Check that it returns the expected combined output.
4. Ensure the orchestrator performs coordination only and does not duplicate calculations.

## Interview explanation

A tool is a small reusable function that answers one specific question, while an orchestrator coordinates several tools to solve a larger problem. I used this pattern in my Football Copilot project where `gather_match_context()` didn't perform calculations itself—it orchestrated functions like `get_next_fixture()`, `calculate_league_table()` and `compare_teams()` to build all the context required for an AI-generated pre-match report. This separation made the code easier to test and prepared it for agentic AI tool calling.

## Related concepts

- [[Function Responsibilities]]
- [[Single Responsibility Principle]]
- [[Agentic AI]]
- [[Tool Calling]]

## Sources

- *Designing Data-Intensive Applications* — Martin Kleppmann
- *Clean Code* — Robert C. Martin
- OpenAI Function & Tool Calling documentation

## Key takeaways

- A tool should answer one business question.
- An orchestrator coordinates tools rather than performing calculations.
- Orchestrators are common in agentic AI systems.
- Small reusable tools are easier to test and maintain.