import json

from dotenv import load_dotenv
from openai import OpenAI

from tool_schemas import tools
from tools import tool_registry

from models import OppositionReport


load_dotenv()

client = OpenAI()


def run_agent(user_message: str):

    messages = [
        {
            "role": "system",
            "content": """
    You are a Liverpool FC performance analyst.

    Analysis date is 1st October 2024.  

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
                response_format=OppositionReport,
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

            tool_function = tool_registry[tool_name]

            result = tool_function(
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