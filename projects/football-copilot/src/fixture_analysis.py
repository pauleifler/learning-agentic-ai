import pandas as pd

from data_processing import normalise_analysis_date
from analytics import (
    identify_key_insights,
    calculate_league_table,
    build_team_profiles_for_league,
    calculate_league_rankings,
    build_team_context,
    compare_teams as compare_team_contexts,
)


def get_next_fixture(
    data: pd.DataFrame,
    team: str,
    analysis_date: str | pd.Timestamp,
) -> dict:
    """
    Return a team's first fixture on or after the analysis date.
    """

    analysis_date = normalise_analysis_date(analysis_date)

    team_exists = (
        data["home_team"].eq(team)
        | data["away_team"].eq(team)
    ).any()

    if not team_exists:
        raise ValueError(
            f"Team '{team}' was not found in the dataset."
        )

    future_fixtures = data[
        (
            data["home_team"].eq(team)
            | data["away_team"].eq(team)
        )
        & data["date"].ge(analysis_date)
    ].copy()

    if future_fixtures.empty:
        raise ValueError(
            f"No fixture was found for {team} "
            f"on or after {analysis_date.date()}."
        )

    next_fixture = (
        future_fixtures
        .sort_values(["date", "kickoff_time"])
        .iloc[0]
    )

    if next_fixture["home_team"] == team:
        opponent = next_fixture["away_team"]
        venue = "Home"
    else:
        opponent = next_fixture["home_team"]
        venue = "Away"

    return {
        "date": next_fixture["date"],
        "kickoff_time": next_fixture["kickoff_time"],
        "league": next_fixture["league"],
        "team": team,
        "opponent": opponent,
        "venue": venue,
        "home_team": next_fixture["home_team"],
        "away_team": next_fixture["away_team"],
    }


def build_next_fixture_comparison(
    data: pd.DataFrame,
    team: str,
    league: str,
    analysis_date: str | pd.Timestamp,
) -> dict:

    """
    Compare a team with its next opponent using the
    correct home or away context.
    """

    analysis_date = normalise_analysis_date(
        analysis_date
    )

    next_fixture = get_next_fixture(
        data=data,
        team=team,
        analysis_date=analysis_date,
    )

    comparison_data = build_team_comparison(
        data=data,
        team=team,
        opponent=next_fixture["opponent"],
        league=league,
        analysis_date=analysis_date,
        venue=next_fixture["venue"],
    )

    return {
        "fixture": next_fixture,
        **comparison_data,

    }
    

def build_team_comparison(
    data: pd.DataFrame,
    team: str,
    opponent: str,
    league: str,
    analysis_date: str | pd.Timestamp,
    venue: str | None = None,
) -> dict:
    """
    Compare two teams at a specified point in time.
    """

    analysis_date = normalise_analysis_date(
        analysis_date
    )

    league_table = calculate_league_table(
        data=data,
        league=league,
        analysis_date=analysis_date,
    )

    team_profiles = build_team_profiles_for_league(
        data=data,
        league_table=league_table,
        analysis_date=analysis_date,
    )

    league_rankings = calculate_league_rankings(
        team_profiles=team_profiles,
    )

    for club in [team, opponent]:
        if club not in team_profiles:
            raise ValueError(
                f"Profile was not found for '{club}'."
            )

    team_context = build_team_context(
        team=team,
        team_profile=team_profiles[team],
        league_table=league_table,
        league_rankings=league_rankings,
        next_fixture=None,
        analysis_date=analysis_date,
    )

    opponent_context = build_team_context(
        team=opponent,
        team_profile=team_profiles[opponent],
        league_table=league_table,
        league_rankings=league_rankings,
        next_fixture=None,
        analysis_date=analysis_date,
    )

    if venue is None:
        return {
            "team": team_context,
            "opponent": opponent_context,
        }

    comparison = compare_team_contexts(
        team_context=team_context,
        opponent_context=opponent_context,
        venue=venue,
    )

    return {
        "team": team_context,
        "opponent": opponent_context,
        "comparison": comparison,
    }


