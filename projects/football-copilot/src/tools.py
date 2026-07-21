from fixture_analysis import analyse_fixture
from data_loader import load_match_data


def analyse_team_fixture(
    team: str,
    league: str,
    analysis_date: str,
) -> dict:
    """
    Analyse a team's next fixture and produce
    structured opposition context.
    """

    data = load_match_data()

    return analyse_fixture(
        data=data,
        team=team,
        league=league,
        analysis_date=analysis_date,
    )

tool_registry = {
    "analyse_team_fixture": analyse_team_fixture
}