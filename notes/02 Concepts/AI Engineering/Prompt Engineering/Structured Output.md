---
type: concept
status: learning
domain:
  - agentic-ai
created: 2026-07-14
confidence: 1
tags:
  - ai/agents
category: "    Software & AI Engineering"
---

## Definition

In your prompt you can ask for a structured output format such ad JSON, HTML etc

## Why it matters

- Makes it easier to interperet
- Can copy directly into python etc

## How it works

In the prompt be specific about the format you want the response to be in

## Example

prompt = f"""
Generate a list of three made-up book titles along \ 
with their authors and genres. 
Provide them in JSON format with the following keys: 
book_id, title, author, genre.
"""
response = get_completion(prompt)
print(response)

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