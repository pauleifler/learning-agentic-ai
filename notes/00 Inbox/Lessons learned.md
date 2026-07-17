# Refactoring Lessons

## 1. Build pipelines instead of large functions

Prefer:

Data

↓

Analytics

↓

Context

↓

Presentation

rather than one large function performing every step.

---

## 2. Single Responsibility Principle

Every function should have one clear purpose.

Examples

- load data
- calculate summaries
- compare teams
- identify insights

---

## 3. Work with progressively richer objects

Raw match data

↓

Team-relative match data

↓

Team profile

↓

Team context

↓

Fixture comparison

↓

Match context

---

## 4. Use dictionaries as domain objects

Instead of passing many variables:

team

league

analysis_date

league_table

...

prefer passing one structured object.

Example:

team_context

match_context

---

## 5. Separate deterministic logic from AI

Python should:

- calculate
- rank
- compare
- identify evidence

LLM should:

- explain
- summarise
- communicate