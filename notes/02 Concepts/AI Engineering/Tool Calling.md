---
type: concept
status: learning
domain:
  - agentic-ai
created: 2026-07-17
confidence: 1
tags:
  - ai/agents
category: "    Agentic AI"
---

# Tool Calling

## Definition

Tool calling is the ability for an LLM to request the execution of external functions or tools in order to retrieve information, perform calculations, or interact with other systems.

Instead of relying only on its own knowledge, the model can decide that it needs additional information and ask another piece of software to provide it.

The LLM does **not** execute the code itself. It decides **which tool should be called**, while your application executes the tool and returns the result.

## Why it matters

LLMs are excellent at reasoning and generating natural language but should not be trusted to perform business calculations or retrieve live data from memory alone.

Tool calling allows us to combine:
- Deterministic Python code for calculations.
- Reliable data sources.
- LLM reasoning and explanation.

This makes AI applications more accurate, explainable and trustworthy.

Without tool calling, the model must guess.

With tool calling, the model can gather evidence before answering.

## How it works

The basic process is:

```text

User asks a question

        ↓

LLM analyses the request

        ↓

LLM decides which tool is needed

        ↓

Application executes the tool

        ↓

Tool returns structured data

        ↓

LLM uses the returned data

        ↓

Final response

```

The important point is that the LLM never directly runs Python.

It simply requests that a tool be executed.

## Example

Imagine the user asks:

> "Who has the stronger attack, QPR or Burnley?"

The LLM might decide it needs to compare the two teams.

It requests:

```python

compare_teams(

    team="QPR",

    opponent="Burnley"

)

```

Our application executes:

```python

compare_teams(...)

```

The function returns:

```python

{

    "team_attack_rank": 8,

    "opponent_attack_rank": 2,

    "team_goals_per_game": 1.45,

    "opponent_goals_per_game": 2.10

}

```

The LLM then explains the result in natural language.

Notice that the LLM did **not** calculate the rankings.

Python performed the calculations.

The LLM interpreted the evidence.

---

## Football Copilot Example

### Current architecture

```text

main()

    ↓

compare_teams()

    ↓

analyse_fixture_context()

    ↓

identify_key_insights()

    ↓

generate_pre_match_report()

```

Every function is called manually.

---

### Future architecture

```text

User:

"How difficult has QPR's recent fixture list been?"

        ↓

LLM

        ↓

Chooses:

analyse_fixture_context()

        ↓

Python executes tool

        ↓

Returns structured data

        ↓

LLM explains findings

```

The LLM decides which analytical tool it needs rather than every tool being called every time.

## Failure modes

### "The LLM executes Python."

❌ False.

Your application executes the Python function.

The LLM only requests that the tool be used.

---

### "Tool calling makes the model smarter."

❌ False.

Tool calling gives the model access to reliable information.

The reasoning ability comes from the model itself.

---

### "Every function should be a tool."

❌ False.

Only functions that provide useful capabilities should become tools.

Small helper functions usually remain internal.

For example:

Good tool:

- `compare_teams()`

Not a tool:

- `calculate_points_per_game()`

The agent should ask for meaningful information rather than every low-level calculation.

## Implementation

A good tool should:

- Have one clear responsibility.
- Accept explicit inputs.
- Return structured outputs (usually dictionaries).
- Avoid printing results.
- Include appropriate validation and error handling.
- Be deterministic (the same inputs produce the same outputs).

For example:

```python

def compare_teams(

    team: str,

    opponent: str,

    venue: str,

) -> dict:

```

This function can easily become a tool because it has:

- clear inputs
- predictable outputs
- one responsibility

## Interview explanation

Tool calling allows an LLM to request the execution of external functions instead of relying solely on its own knowledge. The model decides which tool it needs, the application executes that tool, and the returned structured data is then used by the model to produce a grounded response. This combines deterministic software with probabilistic AI reasoning.

## Related concepts

- [[AI Agents]]
- [[Agent vs Workflow]
- [[Function Calling]]
- [[Structured Outputs]]
- [[Reasoning]]
- [[Planning]]
- [[State Management]]
- [[Grounding]]
- [[Prompt Engineering]]
- [[OpenAI Responses API]]
- [[Orchestrators vs Tools]]

## Sources

- OpenAI Documentation – Tool Calling & Responses API
- Anthropic Documentation – Tool Use
- LangGraph Documentation
- ThoughtSpot Agentic Analytics Documentation

## Key Takeaways

- Tool calling allows an LLM to use external functions.
- The LLM decides **which** tool to use but does not execute the code.
- Python performs deterministic calculations.
- The LLM reasons about the returned information.
- Well-designed tools have clear responsibilities, structured inputs and structured outputs.
- Tool calling is one of the core building blocks of agentic AI.


## Where it appears in Football Copilot

### Current

`gather_match_context()` manually calls:
- `compare_teams()`
- `analyse_fixture_context()`
- `analyse_league_rankings()`
- `identify_key_insights()`
and combines their outputs before passing them to the LLM.

### Future

The AI agent will inspect the user's question and decide which analytical tools to call.

For example:

- "How strong is QPR's home form?" → `build_team_profile()`
- "How difficult have recent fixtures been?" → `analyse_fixture_context()`
- "Who has the stronger attack?" → `compare_teams()`

Only the required tools will be executed before the LLM generates a grounded response.