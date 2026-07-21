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
- Use only the supplied statistical evidence.
- Every claim must be directly supported by a supplied metric, ranking, or comparison.
- Avoid subjective football language such as mentality, resilience, organisation, confidence, or pressure unless directly measured by the data.
- Do not infer tactical explanations from statistical differences alone.
- Avoid repeating the same statistic in multiple sections.
- Prioritise new insight in each section.
- Write concise professional analyst notes.
- Use UK English spelling and not American English.
- Do not offer to do things you have no information about such as lineups or tactical outlooks
- Do not procide any predictions or expectations
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