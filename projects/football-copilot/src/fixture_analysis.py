import pandas as pd

from data_processing import normalise_analysis_date
from analytics import identify_key_insights, calculate_league_table, build_all_team_profiles, calculate_league_rankings, build_team_context, build_team_profile, compare_teams


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


def build_fixture_comparison(
    data: pd.DataFrame,
    team: str,
    league: str,
    analysis_date: str | pd.Timestamp,
) -> dict:
    """
    Build a complete comparison for a team's next fixture
    from the selected team's perspective.
    """

    analysis_date = normalise_analysis_date(
        analysis_date
    )

    next_fixture = get_next_fixture(
        data=data,
        team=team,
        analysis_date=analysis_date,
    )

    if next_fixture is None:
        raise ValueError(
            f"No upcoming fixture was found for '{team}'."
        )

    required_fixture_keys = {
        "home_team",
        "away_team",
    }

    missing_keys = required_fixture_keys.difference(
        next_fixture.keys()
    )

    if missing_keys:
        raise ValueError(
            "Next fixture is missing required keys: "
            f"{sorted(missing_keys)}"
        )

    home_team = next_fixture["home_team"]
    away_team = next_fixture["away_team"]

    if team == home_team:
        team_name = home_team
        opponent_name = away_team
        venue = "Home"

    elif team == away_team:
        team_name = away_team
        opponent_name = home_team
        venue = "Away"

    else:
        raise ValueError(
            f"Selected team '{team}' was not found "
            "in the upcoming fixture."
        )

    league_table = calculate_league_table(
        data=data,
        league=league,
        analysis_date=analysis_date,
    )

    team_profiles = build_all_team_profiles(
        data=data,
        league_table=league_table,
        analysis_date=analysis_date,
    )

    league_rankings = calculate_league_rankings(
        team_profiles=team_profiles,
    )

    for club in [team_name, opponent_name]:
        if club not in team_profiles:
            raise ValueError(
                f"Profile was not found for '{club}'."
            )

    team_context = build_team_context(
        team=team_name,
        team_profile=team_profiles[team_name],
        league_table=league_table,
        league_rankings=league_rankings,
        next_fixture=next_fixture,
        analysis_date=analysis_date,
    )

    opponent_context = build_team_context(
        team=opponent_name,
        team_profile=team_profiles[opponent_name],
        league_table=league_table,
        league_rankings=league_rankings,
        next_fixture=next_fixture,
        analysis_date=analysis_date,
    )

    comparison = compare_teams(
        team_context=team_context,
        opponent_context=opponent_context,
        venue=venue,
    )

    return {
        "fixture": {
            "team": team_name,
            "opponent": opponent_name,
            "venue": venue,
            "date": next_fixture.get("date"),
        },
        "league_table": league_table,
        "team_context": team_context,
        "opponent_context": opponent_context,
        "comparison": comparison,
    }


def build_match_context(
    fixture: dict,
    team_context: dict,
    opponent_context: dict,
    comparison: dict,
    insights: list[dict],
) -> dict:
    """
    Combine every stage of the analysis into one
    team-perspective analysis object.
    """

    return {
        "analysis_date": team_context["analysis_date"],

        "fixture": {
            "team": team_context["team"],
            "opponent": opponent_context["team"],
            "venue": fixture["venue"],
            "date": fixture.get("date"),
        },

        "team": team_context,

        "opponent": opponent_context,

        "comparison": comparison,

        "insights": insights,
    }


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

