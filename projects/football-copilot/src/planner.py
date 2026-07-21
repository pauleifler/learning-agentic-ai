from openai import OpenAI
from dotenv import load_dotenv

from models import AnalysisPlan

load_dotenv()

client = OpenAI()


def create_plan(
    user_message: str,
) -> AnalysisPlan:

    response = client.chat.completions.parse(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """
You are a football analysis task planner.

Decide which type of analysis is required.

Use:
- opposition_analysis for upcoming fixture analysis
- team_profile for questions about one team's performance
""",
            },
            {
                "role": "user",
                "content": user_message,
            }
        ],
        response_format=AnalysisPlan,
    )

    return response.choices[0].message.parsed
