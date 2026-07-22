from typing import Any
import pandas as pd

from fixture_analysis import (
    build_next_fixture_comparison,
    build_team_comparison,
)
from analytics import (
    build_team_profiles_for_league,
    calculate_league_table,
    calculate_league_rankings
)

VALID_LEAGUES = {
    "Premier League",
    "Championship",
    "League One",
    "League Two",
}

TEAM_ALIASES = {
    "Manchester City": "Man City",
    "Manchester United": "Man United",
    "Nottingham Forest": "Nott'm Forest",
    "West Bromich Albion": "WBA",
}

METRIC_CONFIG = {
    "points": {
        "path": ("league", "points"),
        "label": "Points",
        "higher_is_better": True,
    },
    "season_ppg": {
        "path": ("profile", "season", "ppg"),
        "label": "Season points per game",
        "higher_is_better": True,
    },
    "recent_ppg": {
        "path": ("profile", "recent", "ppg"),
        "label": "Recent points per game",
        "higher_is_better": True,
    },
    "goals_scored_per_game": {
        "path": ("profile", "season", "goals_scored_per_game"),
        "label": "Goals scored per game",
        "higher_is_better": True,
    },
    "goals_conceded_per_game": {
        "path": ("profile", "season", "goals_conceded_per_game"),
        "label": "Goals conceded per game",
        "higher_is_better": False,
    },
    "shots_per_game": {
        "path": ("profile", "season", "shots_per_game"),
        "label": "Shots per game",
        "higher_is_better": True,
    },
    "shots_conceded_per_game": {
        "path": ("profile", "season", "shots_conceded_per_game"),
        "label": "Shots conceded per game",
        "higher_is_better": False,
    },
    "shots_on_target_per_game": {
        "path": ("profile", "season", "shots_on_target_per_game"),
        "label": "Shots on target per game",
        "higher_is_better": True,
    },
    "shots_on_target_conceded_per_game": {
        "path": (
            "profile",
            "season",
            "shots_on_target_conceded_per_game",
        ),
        "label": "Shots on target conceded per game",
        "higher_is_better": False,
    },
    "corners_per_game": {
        "path": ("profile", "season", "corners_per_game"),
        "label": "Corners per game",
        "higher_is_better": True,
    },
    "form_change_ppg": {
        "path": ("profile", "form_change_ppg"),
        "label": "Recent form change",
        "higher_is_better": True,
    },
}

def get_nested_value(
    item: dict,
    path: tuple[str, ...],
) -> Any:
    """Retrieve a value from a nested dictionary."""

    value = item

    for key in path:
        value = value[key]

    return value

def normalise_team_name(team: str) -> str:
    """Convert common team-name variations to dataset names."""

    cleaned_team = team.strip()

    if not cleaned_team:
        raise ValueError("Team name cannot be empty.")

    return TEAM_ALIASES.get(cleaned_team, cleaned_team)

def validate_league(league: str) -> None:
    if league not in VALID_LEAGUES:
        raise ValueError(
            f"Unsupported league: {league}"
        )


def compare_teams(
    data,
    team: str,
    opponent: str,
    league: str,
    analysis_date: str,
) -> dict:
    
    validate_league(league)

    team = normalise_team_name(team)
    opponent = normalise_team_name(opponent)

    return build_team_comparison(
        data=data,
        team=team,
        opponent=opponent,
        league=league,
        analysis_date=analysis_date,
    )


def compare_next_fixture(
    data,
    team: str,
    league: str,
    analysis_date: str,
) -> dict:
    """
    Compare a team with its next scheduled opponent.
    """

    validate_league(league)
    team = normalise_team_name(team)

    return build_next_fixture_comparison(
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

    validate_league(league)
    team = normalise_team_name(team)

    league_table = calculate_league_table(
        data=data,
        league=league,
        analysis_date=analysis_date,
    )

    profiles = build_team_profiles_for_league(
        data=data,
        league_table=league_table,
        analysis_date=analysis_date,
    )

    if team not in profiles:
        raise ValueError(
            f"Profile was not found for '{team}'."
        )

    return profiles[team]

def get_league_table(
    data,
    league: str,
    analysis_date: str,
) -> dict:
    """
    Return the league table at a specified point in time.
    """

    validate_league(league)

    league_table = calculate_league_table(
        data=data,
        league=league,
        analysis_date=analysis_date,
    )

    return {
        "league": league,
        "analysis_date": analysis_date,
        "table": league_table.to_dict(orient="records"),
    }

def compare_team_at_position(
    data,
    league: str,
    position: int,
    opponent: str,
    analysis_date: str,
):
    """
    Compare the team currently occupying a league position with another team.
    """

    table = calculate_league_table(
        data=data,
        league=league,
        analysis_date=analysis_date,
    )

    if position < 1 or position > len(table):
        raise ValueError(f"Invalid league position: {position}")

    team = table.iloc[position - 1]["team"]

    return compare_teams(
        data=data,
        team=team,
        opponent=opponent,
        league=league,
        analysis_date=analysis_date,
    )


def get_metric_rankings(
    data: pd.DataFrame,
    league: str,
    metric: str,
    analysis_date: str,
    limit: int = 5,
) -> dict:
    """Return teams ranked by a supported league-wide metric."""

    supported_metrics = {
        "points",
        "ppg",
        "goals_scored",
        "goals_scored_per_game",
        "goals_conceded",
        "goals_conceded_per_game",
        "shots",
        "shots_per_game",
        "shots_conceded",
        "shots_conceded_per_game",
        "shots_on_target",
        "shots_on_target_per_game",
        "shots_on_target_conceded",
        "shots_on_target_conceded_per_game",
        "corners",
        "corners_per_game",
        "corners_conceded",
        "corners_conceded_per_game",
        "yellow_cards",
        "yellow_cards_per_game",
        "red_cards",
        "red_cards_per_game",
    }

    if metric not in supported_metrics:
        raise ValueError(
            f"Unsupported metric: '{metric}'. "
            f"Supported metrics are: {sorted(supported_metrics)}"
        )

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

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

    rankings = calculate_league_rankings(
        team_profiles=team_profiles,
    )

    if not rankings:
        raise ValueError(
            f"No rankings are available for {league} "
            f"on {analysis_date}."
        )

    rank_key = f"{metric}_rank"

    ranking_rows = []

    for team, team_ranks in rankings.items():
        if rank_key not in team_ranks:
            raise ValueError(
                f"Ranking '{rank_key}' is missing for '{team}'."
            )

        metric_value = team_profiles[team]["season"][metric]

        ranking_rows.append(
            {
                "team": team,
                "rank": team_ranks[rank_key],
                "value": metric_value,
            }
        )

    ranking_rows.sort(
        key=lambda row: (
            row["rank"],
            row["team"],
        )
    )

    return {
        "league": league,
        "analysis_date": analysis_date,
        "metric": metric,
        "rank_key": rank_key,
        "teams_ranked": len(ranking_rows),
        "rankings": ranking_rows[:limit],
    }


tool_registry = {
    "compare_teams": compare_teams,
    "compare_next_fixture": compare_next_fixture,
    "get_team_profile": get_team_profile,
    "get_league_table": get_league_table,
    "compare_team_at_position": compare_team_at_position,
    "get_metric_rankings": get_metric_rankings,
}
