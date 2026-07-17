---
type: project
status: active
domain:
  - agentic-ai
created: "2026-07-15"
repository:
complete: false
tags:
  - ai/project
---

# Analytics Insight Generator2

## Problem

## User

## Success criteria

## Architecture

CSV
 ↓
load_data()
 ↓
calculate_metrics()
 ↓
structured dictionary
 ↓
format_metrics()
 ↓
build_prompt()
 ↓
generate_summary()
 ↓
save_report()

## Milestones

**Day 2**
- Moved calculations into `calculate_metrics()`
- Added revenue per session and average order value
- Identified the strongest and weakest conversion days
- Added a separate `build_prompt()` function
- Required the model to distinguish facts from hypotheses

## Decisions

Day 2 - Python performs deterministic calculations. The LLM interprets, prioritises and communicates the calculated evidence.

## Experiments

## Risks

The current seven-day aggregate dataset is too limited for strong causal or statistical conclusions. More dimensions and historical comparison data will be needed.

## Interview story