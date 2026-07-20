from pydantic import BaseModel, Field


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