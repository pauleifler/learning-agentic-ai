import json

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

from tool_schemas import tools
from tools import tool_registry

from typing import Any
from models import AgentResult, ToolCallRecord


load_dotenv()

client = OpenAI()


SYSTEM_PROMPT = """
You are Football Copilot, an AI assistant that analyses football performance
using statistical data.

Your role is to answer questions by selecting and using the most appropriate
available tools.

## Tool selection

Use get_team_profile when:
- The user asks about one team's overall performance.
- The user asks about a team's strengths, weaknesses or recent form.

Use compare_teams when:
- The user names two teams and asks to compare their performance.
- The teams do not necessarily have an upcoming fixture against each other.

Use compare_next_fixture when:
- The user asks about a team's next or upcoming fixture.
- The user asks how a team compares with its next opponent.

Use get_league_table when:
- The user asks for league positions.
- The user asks to see a league table.
- The user asks which team is top, bottom or in a particular position.

Ranking tools

There are four separate ranking tools.

- get_season_metric_rankings
  Use when the user asks about overall season performance or league rankings.

- get_recent_metric_rankings
  Use when the user asks about recent form, current form, momentum or the last six matches.

- get_home_metric_rankings
  Use when the user asks specifically about home performance.

- get_away_metric_rankings
  Use when the user asks specifically about away performance.

  Examples

"Who has the best recent attack?"
→ get_recent_metric_rankings

"Who has the best home defence?"
→ get_home_metric_rankings

"Who has the best away record?"
→ get_away_metric_rankings

"Who has the best defence this season?"
→ get_season_metric_rankings

Metric interpretation:
- Best attack: goals_scored_per_game
- Best defence: goals_conceded_per_game
- Best recent form: recent_ppg
- Most shots: shots_per_game
- Fewest shots conceded: shots_conceded_per_game
- Most shots on target: shots_on_target_per_game
- Biggest recent improvement: form_change_ppg

## Principles

- Use tools for all statistical football questions.
- Never invent statistics.
- Base conclusions only on data returned by the tools.
- Clearly distinguish statistical evidence from interpretation.
- Use more than one tool when the question requires multiple capabilities.
- If the available tools or data cannot answer the question, explain why.
- When asked for a league table, show the complete table unless the user
  requests a shorter version.

When using the result of one tool as input to another tool:

- Extract the exact value returned by the first tool.
- Never use placeholders such as "Top Team", "League Leader" or an empty string.
- Use team names exactly as they appear in tool results.
- Before calling a tool, ensure every required argument contains a real value.

Example:
If get_league_table returns Liverpool in position 1, and the user asks to compare
the top team with Manchester City, call:

compare_teams(
    team="Liverpool",
    opponent="Man City",
    league="Premier League",
    analysis_date="2025-04-11"
)


"""


def execute_tool(
    tool_name: str,
    arguments: dict,
    data: pd.DataFrame,
) -> dict:
    """Execute a registered tool using the shared football dataset."""

    if tool_name not in tool_registry:
        raise ValueError(f"Unknown tool: {tool_name}")

    tool_function = tool_registry[tool_name]

    return tool_function(
        data=data,
        **arguments,
    )


def run_agent(
    user_message: str,
    conversation_history: list[dict],
    data: pd.DataFrame,
) -> AgentResult:
    """
    Run the football agent until it produces a final answer.

    Returns the final answer together with details of every
    tool called during the agent run.
    """

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    for message in conversation_history:
        messages.append(
            {
                "role": "user",
                "content": message["question"],
            }
        )

        messages.append(
            {
                "role": "assistant",
                "content": message["answer"],
            }
        )

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    tool_calls_used: list[ToolCallRecord] = []

    while True:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        # Preserve the assistant's tool-call request before
        # adding the tool results.
        messages.append(assistant_message)

        # No tool calls means the model has produced its final answer.
        if not assistant_message.tool_calls:
            return {
                "answer": assistant_message.content or "",
                "tool_calls": tool_calls_used,
            }

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            arguments: dict[str, Any] = {}

            try:
                arguments = json.loads(
                    tool_call.function.arguments
                )

                print(f"\nTool selected: {tool_name}")
                print(f"Arguments: {arguments}")

                result = execute_tool(
                    tool_name=tool_name,
                    arguments=arguments,
                    data=data,
                )

                print("\nTool result:")
                print(
                    json.dumps(
                        result,
                        indent=2,
                        default=str,
                    )
                )

                tool_output = {
                    "success": True,
                    "result": result,
                }

                tool_calls_used.append(
                    {
                        "name": tool_name,
                        "arguments": arguments,
                        "success": True,
                    }
                )

            except json.JSONDecodeError as error:
                tool_output = {
                    "success": False,
                    "error": f"Invalid tool arguments: {error}",
                }

                tool_calls_used.append(
                    {
                        "name": tool_name,
                        "arguments": {},
                        "success": False,
                        "error": str(error),
                    }
                )

            except Exception as error:
                tool_output = {
                    "success": False,
                    "error": str(error),
                }

                tool_calls_used.append(
                    {
                        "name": tool_name,
                        "arguments": arguments,
                        "success": False,
                        "error": str(error),
                    }
                )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        tool_output,
                        default=str,
                    ),
                }
            )