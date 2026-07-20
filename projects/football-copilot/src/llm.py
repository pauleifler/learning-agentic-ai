from openai import OpenAI
from dotenv import load_dotenv
from models import OppositionReport


load_dotenv()


client = OpenAI()


def generate_opposition_report(
    analysis_context: dict,
) -> str:
    """
    Generate an opposition analysis report
    from structured analytical context.
    """

    response = client.chat.completions.parse(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """


You are a football performance analyst
working for Liverpool FC.

Your role is to analyse upcoming opponents
using only the supplied evidence, not to create unsupported tactical opinions.

Write a professional opposition report.

Return:
- executive summary
- selected team strengths
- opponent strengths
- opponent weaknesses
- key battles
- risks

For risks:
- identify the risk area
- provide the evidence
- explain the implication

Rules:
- Do not invent information.
- Do not recommend tactical actions unless directly supported by the supplied evidence.
- Do not assume information about pressing, possession, player roles, formations or tactics.
- Only use the supplied statistics.
- Avoid repeating the same statistic in multiple sections.
- Prioritise new insight in each section.
- Write concise professional analyst notes.
- Use UK English spelling and not American English.
""",
            },
            {
                "role": "user",
                "content": str(analysis_context),
            },
        ],

        response_format=OppositionReport,
    )

    return response.choices[0].message.parsed