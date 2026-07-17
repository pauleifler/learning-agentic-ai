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

# Delimiters

## Definition

A delimiter is a way in prompt engineering to focus on a distinct part of the input.

## Why it matters

It helps you wrote clear instructions

## How it works

A delimiter can be any clear punctuation which clearly identifies a section of the input.

## Example

text = f"""
You should express what you want a model to do by \ 
providing instructions that are as clear and \ 
specific as you can possibly make them. \ 
This will guide the model towards the desired output, \ 
and reduce the chances of receiving irrelevant \ 
or incorrect responses. Don't confuse writing a \ 
clear prompt with writing a short prompt. \ 
In many cases, longer prompts provide more clarity \ 
and context for the model, which can lead to \ 
more detailed and relevant outputs.
"""
prompt = f"""
Summarize the text delimited by triple backticks \ 
into a single sentence.
```{text}```
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