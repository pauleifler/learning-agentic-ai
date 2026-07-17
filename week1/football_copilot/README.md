# ⚽ Football Copilot

An AI-powered football analytics engine built in Python.

Football Copilot transforms historical football match data into structured analytical context that can be consumed by Large Language Models (LLMs) to generate explainable, evidence-based match previews.

The project separates deterministic statistical analysis from AI-generated reasoning, ensuring calculations remain transparent, repeatable and grounded in data.

---

# Features

## Current

- Load and combine football-data.co.uk CSV datasets
- Generate league tables for any analysis date
- Build detailed team performance profiles
- Calculate league-wide statistical rankings
- Compare two teams using multiple performance metrics
- Identify key evidence-based insights
- Generate structured match context ready for AI consumption

## Planned

- LLM-generated match previews
- OpenAI tool calling
- Agentic workflow
- Streamlit web interface
- Automated testing suite

---

# Architecture

```text
Football Data CSVs
        │
        ▼
load_match_data()
        │
        ▼
calculate_league_table()
        │
        ▼
build_all_team_profiles()
        │
        ▼
calculate_league_rankings()
        │
        ▼
build_team_context()
        │
        ▼
compare_teams()
        │
        ▼
identify_key_insights()
        │
        ▼
build_match_context()
        │
        ▼
analyse_fixture()
        │
        ▼
LLM Match Report
```

---

# Project Structure

```text
football-copilot/

├── data/
│   └── football-data CSV files
│
├── notebooks/
│   └── experimentation
│
├── src/
│   └── analytics engine
│
├── README.md
└── requirements.txt
```

*(Update this structure if your repository differs.)*

---

# Analytics Pipeline

The application follows a layered architecture.

## Data Layer

Responsible for loading and transforming raw football data.

Functions include:

- `load_match_data()`
- `normalise_analysis_date()`
- `get_team_matches()`
- `add_team_match_outcomes()`

---

## Analytics Layer

Responsible for calculating statistics and comparisons.

Functions include:

- `summarise_matches()`
- `build_team_profile()`
- `calculate_league_table()`
- `build_all_team_profiles()`
- `calculate_league_rankings()`
- `compare_teams()`

---

## Context Layer

Packages analytical outputs into reusable context objects.

Functions include:

- `get_next_fixture()`
- `build_team_context()`
- `identify_key_insights()`
- `build_match_context()`

---

## Orchestration Layer

Coordinates the complete workflow.

Functions include:

- `analyse_fixture()`
- `main()`

---

# Example Workflow

```python
data = load_match_data()

match_context = analyse_fixture(
    data=data,
    team="Liverpool",
    league="Premier League",
    analysis_date="2024-10-01",
)
```

The returned `match_context` contains:

- fixture information
- team profiles
- league table
- league rankings
- statistical comparison
- evidence-based insights

This object is designed to become the primary input to an LLM.

---

# Design Principles

## Single Responsibility

Each function performs one task.

---

## Layered Architecture

```text
Data

↓

Analytics

↓

Context

↓

AI
```

---

## Progressive Enrichment

The application builds increasingly rich data structures.

```text
Football Data

↓

Team Match Data

↓

Team Profile

↓

League Rankings

↓

Team Context

↓

Fixture Comparison

↓

Key Insights

↓

Match Context
```

---

## Deterministic Analytics

Python is responsible for:

- statistical calculations
- league tables
- rankings
- comparisons
- evidence generation

---

## AI Responsibilities

The future AI layer will:

- explain findings
- summarise evidence
- generate reports
- acknowledge uncertainty

The LLM is **not** responsible for performing statistical calculations.

---

# Technology Stack

- Python
- pandas
- football-data.co.uk datasets

### Planned

- OpenAI API
- Streamlit
- Pydantic
- pytest

---

# Roadmap

## Phase 1 ✅

- Data loading
- Team-relative match data
- League table generation
- Team profiles
- League rankings
- Fixture comparison
- Match context generation

## Phase 2 🚧

- Prompt engineering
- AI-generated match previews
- Structured outputs
- Report validation

## Phase 3

- OpenAI tool calling
- Agentic orchestration
- Multi-step reasoning

## Phase 4

- Streamlit application
- Interactive dashboard
- User-configurable analyses

---

# Learning Objectives

This project is being developed as a practical exploration of:

- Python software engineering
- Data modelling
- Layered application architecture
- LLM integration
- Agentic AI application design
- Explainable AI systems

---

# Future Vision

Football Copilot is evolving into an AI-powered football analytics engine.

Rather than asking an LLM to calculate statistics directly, the application first builds deterministic analytical evidence using Python. The AI layer will then consume that evidence to generate grounded, explainable match previews and answer user questions using structured context.