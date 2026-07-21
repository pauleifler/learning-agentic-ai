import json

from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd

from tool_schemas import tools
from tools import tool_registry

from models import OppositionReport, TeamProfileReport
from planner import create_plan


load_dotenv()

client = OpenAI()


def run_agent(user_message: str,
              data: pd.DataFrame
):
    
    plan = create_plan(
    user_message
    )

    if plan.analysis_type == "team_profile":
        response_model = TeamProfileReport
    elif plan.analysis_type == "opposition_analysis":
        response_model = OppositionReport

    messages = [
        {
            "role": "system",
            "content": """
    You are a Liverpool FC performance analyst.

    Analyse upcoming fixtures from Liverpool's perspective.

    Use only supplied statistical evidence.

    Produce concise professional opposition analysis.

    Avoid repeating information.
    Do not invent player information or tactical details.
    """,
        },
        {
            "role": "user",
            "content": user_message,
        }
    ]

    while True:

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=tools,
        )

        message = response.choices[0].message

# No tool requested - generate structured report
        if not message.tool_calls:

            final_response = client.chat.completions.parse(
                model="gpt-4.1-mini",
                messages=messages,
                response_format=response_model,
            )

            report = final_response.choices[0].message.parsed

            return report


        # Add the assistant decision to state
        messages.append(
            message
        )


        # Execute requested tools
        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(
                f"Tool selected: {tool_name}"
            )

            print(arguments)

            tool_function = tool_registry[tool_name]

            result = tool_function(
                data=data,
                **arguments
            )


            # Add tool observation
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        result,
                        default=str
                    ),
                }
            )