from pydantic import BaseModel, Field
from typing import Literal


class AnalysisPlan(BaseModel):

    analysis_type: Literal[
        "opposition_analysis",
        "team_profile",
    ] = Field(
        description=(
            "The type of analysis required "
            "based on the user's request."
        )
    )

class KeyBattle(BaseModel):
    area: str = Field(
        description="The statistical area being compared."
    )

    detail: str = Field(
        description="Explanation of the comparison using only supplied evidence."
    )


class Risk(BaseModel):
    area: str = Field(
        description="The potential concern or risk area."
    )

    evidence: str = Field(
        description="The supporting statistical evidence."
    )

    implication: str = Field(
        description="Why this matters for the fixture."
    )


class OppositionReport(BaseModel):

    executive_summary: str = Field(
        description="A concise analytical summary of the fixture."
    )

    team_strengths: list[str] = Field(
        description="Evidence-based strengths of the selected team."
    )

    opponent_strengths: list[str] = Field(
        description="Evidence-based strengths of the opponent."
    )

    opponent_weaknesses: list[str] = Field(
        description="Evidence-based weaknesses of the opponent."
    )

    key_battles: list[KeyBattle]

    risks: list[Risk]


class TeamProfileReport(BaseModel):

    executive_summary: str = Field(
        description="Summary of the team's statistical profile."
    )

    strengths: list[str] = Field(
        description="Evidence-based strengths of the team."
    )

    weaknesses: list[str] = Field(
        description="Evidence-based weaknesses of the team."
    )

    key_metrics: list[str] = Field(
        description="Important supporting statistics."
    )