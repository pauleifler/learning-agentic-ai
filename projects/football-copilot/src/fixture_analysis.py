import pandas as pd

from main import build_fixture_comparison
from main import identify_key_insights
from main import build_match_context

def analyse_fixture(
    data: pd.DataFrame,
    team: str,
    league: str,
    analysis_date: str | pd.Timestamp,
) -> dict:
    """
    Analyse a team's next fixture and return a complete match context.
    """

    fixture_analysis = build_fixture_comparison(
        data=data,
        team=team,
        league=league,
        analysis_date=analysis_date,
    )

    comparison = fixture_analysis["comparison"]

    insights = identify_key_insights(
        comparison
    )

    return build_match_context(
        fixture=fixture_analysis["fixture"],
        team_context=fixture_analysis["team_context"],
        opponent_context=fixture_analysis["opponent_context"],
        comparison=comparison,
        insights=insights,
    )

