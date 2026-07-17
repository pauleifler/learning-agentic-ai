# Football Copilot Function Map

## Purpose

This note documents the architecture of the Football Copilot analytics engine.

The project is built as a layered pipeline. Each function has a single responsibility and produces progressively richer data structures that are consumed by later stages.

---

# High Level Pipeline

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
main()
```

---

# Architecture Layers

```text
Data Layer
│
├── load_match_data()
├── normalise_analysis_date()
├── get_team_matches()
└── add_team_match_outcomes()

Analytics Layer
│
├── summarise_matches()
├── build_team_profile()
├── calculate_league_table()
├── build_all_team_profiles()
├── calculate_league_rankings()
└── compare_teams()

Context Layer
│
├── get_next_fixture()
├── build_team_context()
├── identify_key_insights()
└── build_match_context()

Orchestration Layer
│
├── analyse_fixture()
└── main()

Future AI Layer
│
├── Prompt Builder
├── Report Generation
├── Tool Calling
├── Reflection
└── Streamlit UI
```

---

# Function Responsibilities

## load_match_data()

### Purpose

Load all football-data.co.uk CSV files into one standardised DataFrame.

### Returns

Chronologically sorted match data with consistent column names.

---

## normalise_analysis_date()

### Purpose

Convert strings or timestamps into a standard pandas Timestamp.

Used throughout the project to avoid inconsistent date handling.

---

## get_team_matches()

### Purpose

Retrieve every completed match for a selected team before the analysis date.

Returns raw match history.

---

## add_team_match_outcomes()

### Purpose

Convert home/away match data into team-relative data.

Creates metrics including:

- venue
- goals scored
- goals conceded
- result
- points
- shots
- shots conceded
- shots on target
- shots on target conceded
- corners
- corners conceded
- yellow cards
- red cards

This is the project's normalisation step.

---

## summarise_matches()

### Purpose

Calculate aggregate statistics from any collection of team-relative matches.

Examples:

- full season
- last six matches
- home matches
- away matches

Returns metrics including:

- PPG
- goals
- shots
- shots on target
- corners
- bookings
- per-game averages

---

## build_team_profile()

### Purpose

Build the complete statistical profile for one team.

Returns

```text
Season

Recent

Home

Away

Form trend
```

---

## calculate_league_table()

### Purpose

Construct the league table using only matches before the analysis date.

Returns

- position
- played
- won
- drawn
- lost
- goals for
- goals against
- goal difference
- points

---

## build_all_team_profiles()

### Purpose

Create profiles for every team in the league.

This avoids recalculating statistics repeatedly.

---

## calculate_league_rankings()

### Purpose

Rank every team across every important metric.

Current rankings include

Higher is better

- Points
- PPG
- Goals scored
- Shots
- Shots on target
- Corners

Lower is better

- Goals conceded
- Shots conceded
- Shots on target conceded
- Corners conceded
- Yellow cards
- Red cards

---

## get_next_fixture()

### Purpose

Identify the next scheduled fixture after the analysis date.

Returns

- date
- kick-off
- home team
- away team
- opponent
- venue

---

## build_team_context()

### Purpose

Combine

- team profile
- league table
- league rankings
- next fixture

into one reusable object.

Returns

```text
Team

Analysis date

Profile

League

Ranks

Next fixture
```

---

## compare_teams()

### Purpose

Compare the home and away teams using

- season performance
- recent form
- venue performance
- league position
- statistical differences

Returns one comparison object.

---

## identify_key_insights()

### Purpose

Identify statistically meaningful differences between the two teams.

Produces structured evidence that will later be interpreted by an LLM.

The LLM should explain these insights, not calculate them.

---

## build_match_context()

### Purpose

Combine every stage of the analysis into one object.

Returns

```text
Fixture

Home context

Away context

Comparison

Insights
```

This becomes the primary input to downstream components.

---

## analyse_fixture()

### Purpose

Coordinate the complete analytics pipeline.

Produces a fully analysed fixture.

This is the public entry point to the analytics engine.

---

## main()

### Purpose

Application entry point.

Responsible only for

- selecting inputs
- loading data
- calling analyse_fixture()
- displaying or saving results

It should contain almost no business logic.

---

# Design Principles

## 1. Single Responsibility

Every function performs one job.

---

## 2. Layered Architecture

Data

↓

Analytics

↓

Context

↓

AI

---

## 3. Progressive Enrichment

The application builds richer objects at each stage.

```text
CSV

↓

Raw Match Data

↓

Team Match Data

↓

Team Profile

↓

League Rankings

↓

Team Context

↓

Comparison

↓

Insights

↓

Match Context
```

---

## 4. Deterministic Analytics

Python is responsible for

- calculations
- rankings
- comparisons
- evidence selection

---

## 5. AI Responsibilities

The LLM should

- explain
- summarise
- communicate
- acknowledge uncertainty

It should not calculate league tables or football statistics.

---

# Current Vision

Football Copilot is no longer simply a football prediction tool.

It is becoming:

> **An AI-powered football analytics engine with an agentic reporting layer.**

The deterministic analytics engine produces trusted evidence.

The AI layer will consume that evidence to generate explainable, grounded match previews.