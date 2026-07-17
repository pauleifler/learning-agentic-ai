---
type: concept
status: learning
domain:
  - agentic-ai
created: 2026-07-17
confidence: 1
tags:
  - ai/agents
---

## Definition

A **workflow** is a predefined sequence of steps that always executes in the same order.

An **agent** is a system that can decide which actions to take, which tools to use, and when it has enough information to answer a question.

The key difference is **decision-making**.

## Why it matters

Many applications are marketed as “AI agents” when they are actually workflows with an LLM added to the end.

Understanding the distinction helps you:

- Design more flexible AI systems.
- Choose the right architecture for a problem.
- Explain agentic AI clearly in interviews.
- Avoid overcomplicating applications that only need a workflow.

## How it works

### **Workflow**

A workflow follows a fixed path regardless of the user’s request.

Load Data
      ↓
Calculate Metrics
      ↓
Generate Context
      ↓
Create Report

The sequence never changes.

Even if some steps are unnecessary, they are still executed.

### **Agent**

An agent starts with a goal rather than a predefined sequence.

User Question
      ↓
Understand Request
      ↓
Decide Which Tool To Use
      ↓
Review Result
      ↓
Need More Information?
      ↓
Yes ──► Call Another Tool
 │
 No
 │
 ▼
Generate Response

The agent chooses actions based on the evidence it has collected.
## Example

**Football Copilot Example**

**Current Architecture (Workflow)**

User selects fixture
        ↓
get_next_fixture()
        ↓
compare_teams()
        ↓
analyse_fixture_context()
        ↓
analyse_league_rankings()
        ↓
identify_key_insights()
        ↓
generate_pre_match_report()

Every function is called in the same order.

**Future Architecture (Agent)**

User:
"How strong is QPR's home form?"

        ↓

Agent decides:

✓ Team profile needed

✓ League ranking needed

✗ Fixture context not needed

✗ Opponent comparison not needed

        ↓

Call required tools only

        ↓

Generate response

## Failure modes

 **“Using an LLM makes something an agent.”**

❌ False.

An LLM can simply be one step in a workflow.

---

 **“Using LangGraph automatically creates an agent.”**

❌ False.

LangGraph can build workflows **or** agents.

The architecture determines whether the system is agentic.

---

 **“Agents replace deterministic code.”**

❌ False.

Well-designed agents rely on deterministic tools for calculations and data retrieval.

The LLM is responsible for reasoning and explanation—not calculating business metrics.

---

## Implementation

How would you implement or test it?

## Interview explanation

A workflow executes a predefined sequence of steps regardless of the request, while an AI agent decides which actions or tools to take based on the user’s goal and the information it gathers. In Football Copilot, the Python functions provide deterministic analytical tools, and the future agent will choose which of those tools to invoke before generating a grounded explanation.

## Related concepts

- [[AI Agents]]
- [[Tool Calling]]
- [[Function Calling]]
- [[Deterministic vs Probabilistic Systems]]
- [[Planning]]
- [[Reasoning]]
- [[State Management]]
- [[LangGraph]]
- [[MCP (Model Context Protocol)]]
- [[Structured Outputs]]

## Sources

- OpenAI documentation (tool calling and Responses API)
- Anthropic documentation (tool use and agent design)
- LangGraph documentation
- ThoughtSpot Agentic Analytics architecture
- _Building Effective Agents_ (Anthropic)

## Key Takeaways
- A workflow follows a fixed path.
- An agent makes decisions about which actions to take.
- Tool selection is a defining characteristic of agentic systems.
- Deterministic Python functions become reusable tools for an agent.
- The LLM should explain evidence, not replace deterministic calculations.
- Football Copilot is currently a workflow that will evolve into an agent by replacing a fixed sequence with intelligent tool selection.