---
type: concept
status: learning
domain:
  - agentic-ai
created: 2026-07-15
confidence: 1
tags:
  - ai/agents
category: "    Software & AI Engineering"
---

# System Prompt vs User Prompt

## Definition

A system prompt defines the model's role, behaviour and constraints. These change infrequently

A user prompt contains the specific task for the interaction with the LLM. Changes in every request

## Why it matters

The system prompt defines **how the model should behave**.

The user prompt defines **what the model should do**.

Separating them makes applications easier to maintain and reuse.

## How it works

Describe the mechanism.

## Example

**System Prompts**
- You are a senior digital analytics consultant.
- Explain concepts clearly.
- Distinguish facts from hypotheses.

**User Prompt**
- Analyse these metrics and identify the most important commercial findings.

## Failure modes

When might it fail or be inappropriate?

## Implementation

How would you implement or test it?

## Interview explanation

The system prompt establishes the model's role, behaviour and constraints, while the user prompt contains the specific task or question for a particular interaction. Keeping them separate improves consistency, reuse and maintainability.

## Related concepts

- [[]]

## Sources

-