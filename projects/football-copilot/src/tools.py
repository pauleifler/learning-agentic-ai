from fixture_analysis import analyse_fixture
from analytics import build_all_team_profiles, calculate_league_table

VALID_LEAGUES = {
    "Premier League",
    "Championship",
    "League One",
    "League Two",
}

def analyse_team_fixture(
    data,
    team: str,
    league: str,
    analysis_date: str,
) -> dict:
    """
    Analyse a team's next fixture and produce
    structured opposition context.
    """

    if league not in VALID_LEAGUES:
        raise ValueError(
            f"Unsupported league: {league}"
        )

    return analyse_fixture(
        data=data,
        team=team,
        league=league,
        analysis_date=analysis_date,
    )

def get_team_profile(
    data,
    team: str,
    league: str,
    analysis_date: str,
) -> dict:
    """
    Return the statistical profile for one team.
    """

    league_table = calculate_league_table(
        data=data,
        league=league,
        analysis_date=analysis_date,
    )

    profiles = build_all_team_profiles(
        data=data,
        league_table=league_table,
        analysis_date=analysis_date,
    )

    return profiles[team]


tool_registry = {
    "analyse_team_fixture": analyse_team_fixture,
    "get_team_profile": get_team_profile
}
