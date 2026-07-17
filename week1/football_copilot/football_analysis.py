from pathlib import Path
import os

import pandas as pd
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from pprint import pprint
import json

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY was not found. Check that it exists in your .env file."
    )

client = OpenAI(api_key=api_key)

DATA_FILE = Path(__file__).parent / "data" / "football_results.xlsx"

def load_data(file_path: Path) -> pd.DataFrame:
    """Load analytics data from a excel file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    data = pd.read_excel(file_path)
    data["date"] = pd.to_datetime(data["date"])
    data = (
        data
        .sort_values("date")
        .reset_index(drop=True)
    )
    return data
   
POINTS_BY_RESULT = {
    "Win": 3,
    "Draw": 1,
    "Loss": 0,
    }

def get_team_matches(data: pd.DataFrame, team: str, current_round: int) -> pd.DataFrame:
    team_matches = data[
        ((data["home_team"] == team) | (data["away_team"] == team)) &
        (data["round_number"] <= current_round)
    ].copy()
    team_matches["is_home"] = team_matches["home_team"] == team
    team_matches["opponent"] = team_matches.apply(
        lambda row: row["away_team"] if row["is_home"] else row["home_team"], axis=1
    )
    team_matches["goals_for"] = team_matches.apply(
        lambda row: row["home_goals"] if row["is_home"] else row["away_goals"], axis=1 
    )
    team_matches["goals_against"] = team_matches.apply(
        lambda row: row["away_goals"] if row["is_home"] else row["home_goals"], axis=1
    )
    team_matches["result"] = team_matches.apply(
        lambda row: "Win" if row["goals_for"] > row["goals_against"] else ("Draw" if row["goals_for"] == row["goals_against"] else "Loss"), axis=1
    )
    team_matches["points"] = team_matches["result"].map(POINTS_BY_RESULT)
    return (
        team_matches
        .sort_values("date")
        .reset_index(drop=True)
    )

def calculate_match_metrics(matches: pd.DataFrame) -> dict:
    """Calculate performance metrics for a collection of matches."""

    games_played = len(matches)

    if games_played == 0:
        return {
            "games_played": 0,
            "points": 0,
            "ppg": 0.0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
            "goals_scored_per_game": 0.0,
            "goals_conceded_per_game": 0.0,
            "goal_difference_per_game": 0.0,
            "btts_percentage": 0.0,
            "clean_sheet_percentage": 0.0,
            "failed_to_score_percentage": 0.0,
        }

    points = int(matches["points"].sum())

    wins = int(matches["result"].eq("Win").sum())
    draws = int(matches["result"].eq("Draw").sum())
    losses = int(matches["result"].eq("Loss").sum())
    goals_for = int(matches["goals_for"].sum())
    goals_against = int(matches["goals_against"].sum())

    goals_scored_per_game = (
        matches["goals_for"].sum() / games_played
    )

    goals_conceded_per_game = (
        matches["goals_against"].sum() / games_played
    )

    btts = (
        (matches["goals_for"] > 0)
        & (matches["goals_against"] > 0)
    )

    return {
        "games_played": games_played,
        "points": points,
        "ppg": points / games_played,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "goals_scored_per_game": float(goals_scored_per_game),
        "goals_conceded_per_game": float(
            goals_conceded_per_game
        ),
        "goal_difference_per_game": float(
            goals_scored_per_game
            - goals_conceded_per_game
        ),
        "btts_percentage": round(
            btts.mean() * 100,
            1,
        ),
        "clean_sheet_percentage": round(
            matches["goals_against"].eq(0).mean() * 100,
            1,
        ),
        "failed_to_score_percentage": round(
            matches["goals_for"].eq(0).mean() * 100,
            1,
        ),
    }


def assess_recent_form_change(
    team_matches: pd.DataFrame,
    recent_match_count: int = 6,
    bootstrap_samples: int = 5000,
    random_seed: int = 82,
) -> dict:
    """Assess whether recent PPG differs meaningfully from earlier form."""

    minimum_matches = recent_match_count * 2

    if len(team_matches) < minimum_matches:
        return {
            "status": "insufficient_data",
            "message": (
                f"At least {minimum_matches} matches are required "
                "to compare recent and previous form."
            ),
        }

    recent_matches = team_matches.tail(recent_match_count)
    previous_matches = team_matches.iloc[:-recent_match_count]

    recent_points = recent_matches["points"].to_numpy(dtype=float)
    previous_points = previous_matches["points"].to_numpy(dtype=float)

    recent_ppg = float(recent_points.mean())
    previous_ppg = float(previous_points.mean())
    observed_difference = recent_ppg - previous_ppg

    rng = np.random.default_rng(random_seed)

    bootstrap_differences = []

    for _ in range(bootstrap_samples):
        recent_sample = rng.choice(
            recent_points,
            size=len(recent_points),
            replace=True,
        )

        previous_sample = rng.choice(
            previous_points,
            size=len(previous_points),
            replace=True,
        )

        bootstrap_differences.append(
            recent_sample.mean() - previous_sample.mean()
        )

    lower_bound, upper_bound = np.percentile(
        bootstrap_differences,
        [2.5, 97.5],
    )

    if lower_bound > 0:
        assessment = "improving"
    elif upper_bound < 0:
        assessment = "declining"
    else:
        assessment = "inconclusive"

    return {
        "status": "complete",
        "recent_matches": len(recent_matches),
        "previous_matches": len(previous_matches),
        "recent_ppg": round(recent_ppg, 2),
        "previous_ppg": round(previous_ppg, 2),
        "ppg_difference": round(observed_difference, 2),
        "confidence_interval_95": {
            "lower": round(float(lower_bound), 2),
            "upper": round(float(upper_bound), 2),
        },
        "assessment": assessment,
    }


def build_team_profile(team_matches: pd.DataFrame) -> dict:
    """Build season, recent, home and away team profiles."""

    if team_matches.empty:
        raise ValueError(
            "Cannot build a profile from an empty match dataset."
        )

    season = calculate_match_metrics(team_matches)
    recent = calculate_match_metrics(team_matches.tail(6))

    home_matches = team_matches[
        team_matches["is_home"]
    ]

    away_matches = team_matches[
        ~team_matches["is_home"]
    ]

    home = calculate_match_metrics(home_matches)
    away = calculate_match_metrics(away_matches)

    return {
        "season": season,
        "recent_form": recent,
        "home": home,
        "away": away,
        "form_change_ppg": recent["ppg"] - season["ppg"],
    }


def display_team_profile(
        team: str,
        current_round: int,
        profile: dict,
        ) -> None:
    """Display the team profile in a readable format."""

    print(f"\n===== {team} Profile (Round {current_round}) =====\n")

    for section, values in profile.items():

        print(f"\n--- {section.upper()} ---")

        if isinstance(values, dict):
            for metric, value in values.items():
                print(f"{metric:<35} {value}")
        else:
            print(values)


def calculate_league_table(
    data: pd.DataFrame,
    league: str,
    current_round: int,
) -> pd.DataFrame:
    """Calculate the league table up to a specified round."""
    
    league_matches = data[
        (data["league"] == league)
        & (data["round_number"] <= current_round)
    ].copy()

    if league_matches.empty:
        raise ValueError(
            f"No matches found for {league} through round {current_round}."
        )

    teams = sorted(
        pd.concat(
            [
                league_matches["home_team"],
                league_matches["away_team"],
            ]
        ).unique()
    )

    league_table = []

    for team in teams:
        team_matches = get_team_matches(
            data,
            team,
            current_round,
        )
        
        profile = build_team_profile(team_matches)

        league_table.append(
            {
                "team": team,
                "played": profile["season"]["games_played"],
                "wins": profile["season"]["wins"],
                "draws": profile["season"]["draws"],
                "losses": profile["season"]["losses"],
                "goals_for": profile["season"]["goals_for"],
                "goals_against": profile["season"]["goals_against"],
                "goal_difference": profile["season"]["goals_for"] - profile["season"]["goals_against"],
                "points": profile["season"]["points"],  
            }
        )
    league_table_df = pd.DataFrame(league_table)

    league_table_df = (
        league_table_df
        .sort_values(
            by=[
                "points",
                "goal_difference",
                "goals_for",
            ],
            ascending=[
                False,
                False,
                False,
            ],
        )
        .reset_index(drop=True)
    )

    league_table_df.insert(
    0,
    "position",
    range(1, len(league_table_df) + 1),
    )

    return league_table_df


def get_team_position(league_table: pd.DataFrame, team: str) -> int:
    """Get the current position of a team in the league table."""
    matching_rows = league_table[league_table["team"] == team]

    if matching_rows.empty:
        raise ValueError(f"{team} is not in the league table.")
    
    return int(matching_rows.iloc[0]["position"])


def get_next_fixture(data: pd.DataFrame, team: str, current_round: int) -> dict:
    future_matches = data[
        (
            (data["home_team"] == team)
            | (data["away_team"] == team)
        )
        & (data["round_number"] > current_round)
    ].copy()

    if future_matches.empty:
        raise ValueError(
            f"No fixture found for {team} after round {current_round}."
        )
    
    next_fixture = (
        future_matches
        .sort_values(["round_number", "date"])
        .iloc[0]
    )

    is_home = next_fixture["home_team"] == team

    opponent = (
        next_fixture["away_team"]
        if is_home
        else next_fixture["home_team"]
    )

    venue = "home" if is_home else "away"

    return {
        "round_number": int(next_fixture["round_number"]),
        "date": next_fixture["date"].strftime("%Y-%m-%d"),
        "league": next_fixture["league"],
        "team": team,
        "opponent": opponent,
        "venue": venue,
    }


def compare_teams(team: str,
                  opponent: str,
                  league_table: pd.DataFrame,
                  data: pd.DataFrame,
                  current_round: int,
                  team_venue: str
                  ) -> dict:
    """Compare two teams based on their profiles."""
    
    team_matches = get_team_matches(
        data,
        team,
        current_round,
    ) 
    
    opponent_matches = get_team_matches(
        data,
        opponent,
        current_round,
    )

    team_profile = build_team_profile(team_matches)
    opponent_profile = build_team_profile(opponent_matches)

    team_position = get_team_position(league_table, team)
    opponent_position = get_team_position(league_table, opponent)

    if team_venue == "home":
        team_venue_profile = team_profile["home"]
        opponent_venue_profile = opponent_profile["away"]
        opponent_venue = "away"
    else:
        team_venue_profile = team_profile["away"]
        opponent_venue_profile = opponent_profile["home"]
        opponent_venue = "home"

    return {
        "team": team,
        "opponent": opponent,
        "team_venue": team_venue,
        "opponent_venue": opponent_venue,
        "team_position": team_position,
        "opponent_position": opponent_position,
        "team_season_ppg": round(team_profile["season"]["ppg"], 2),
        "opponent_season_ppg": round(
            opponent_profile["season"]["ppg"],
            2,
        ),
        "team_recent_ppg": round(
            team_profile["recent_form"]["ppg"],
            2,
        ),
        "opponent_recent_ppg": round(
            opponent_profile["recent_form"]["ppg"],
            2,
        ),
        "team_venue_ppg": round(
            team_venue_profile["ppg"],
            2,
        ),
        "opponent_venue_ppg": round(
            opponent_venue_profile["ppg"],
            2,
        ),
        "team_venue_goals_scored_per_game": round(
            team_venue_profile["goals_scored_per_game"],
            2,
        ),
        "opponent_venue_goals_scored_per_game": round(
            opponent_venue_profile["goals_scored_per_game"],
            2,
        ),
        "team_venue_goals_conceded_per_game": round(
            team_venue_profile["goals_conceded_per_game"],
            2,
        ),
        "opponent_venue_goals_conceded_per_game": round(
            opponent_venue_profile["goals_conceded_per_game"],
            2,
        ),
        "team_form_change_ppg": round(
            team_profile["form_change_ppg"],
            2,
        ),
        "opponent_form_change_ppg": round(
            opponent_profile["form_change_ppg"],
            2,
        ),
    }


def analyse_fixture_context(
    team_matches: pd.DataFrame,
    league_table: pd.DataFrame,
    match_count: int = 6,
) -> dict:
    """Assess recent opponent strength and venue balance."""

    if team_matches.empty:
        raise ValueError(
            "Cannot analyse fixture difficulty from an empty match dataset."
        )

    if league_table.empty:
        raise ValueError(
            "Cannot analyse fixture difficulty from an empty league table."
        )

    if match_count <= 0:
        raise ValueError(
            "match_count must be greater than zero."
        )

    recent_matches = (
        team_matches
        .tail(match_count)
        .copy()
    )

    position_lookup = league_table[
        ["team", "position", "points", "played"]
    ].copy()

    position_lookup["opponent_ppg"] = (
        position_lookup["points"]
        / position_lookup["played"]
    )

    position_lookup = position_lookup.rename(
        columns={
            "team": "opponent",
            "position": "opponent_position",
        }
    )

    position_lookup = position_lookup[
        [
            "opponent",
            "opponent_position",
            "opponent_ppg",
        ]
    ]

    recent_matches = recent_matches.merge(
        position_lookup,
        on="opponent",
        how="left",
    )

    missing_positions = recent_matches[
        "opponent_position"
    ].isna()

    if missing_positions.any():
        missing_opponents = sorted(
            recent_matches.loc[
                missing_positions,
                "opponent",
            ].unique()
        )

        raise ValueError(
            "League positions were not found for: "
            f"{missing_opponents}"
        )

    matches_analysed = len(recent_matches)

    opponent_positions = recent_matches[
        "opponent_position"
    ]

    opponent_ppg = recent_matches[
        "opponent_ppg"
    ]

    median_opponent_position = float(
        opponent_positions.median()
    )

    average_opponent_ppg = float(
        opponent_ppg.mean()
    )

    position_range = int(
        opponent_positions.max()
        - opponent_positions.min()
    )

    position_standard_deviation = float(
        opponent_positions.std(ddof=0)
    )

    league_size = len(league_table)

    top_quarter_limit = league_size * 0.25
    halfway_limit = league_size * 0.50
    third_quarter_limit = league_size * 0.75

    top_quarter_opponents = int(
        (
            opponent_positions
            <= top_quarter_limit
        ).sum()
    )

    upper_middle_opponents = int(
        (
            (
                opponent_positions
                > top_quarter_limit
            )
            & (
                opponent_positions
                <= halfway_limit
            )
        ).sum()
    )

    lower_middle_opponents = int(
        (
            (
                opponent_positions
                > halfway_limit
            )
            & (
                opponent_positions
                <= third_quarter_limit
            )
        ).sum()
    )

    bottom_quarter_opponents = int(
        (
            opponent_positions
            > third_quarter_limit
        ).sum()
    )

    if (
        top_quarter_opponents > 0
        and bottom_quarter_opponents > 0
        and position_standard_deviation
        >= league_size * 0.25
    ):
        schedule_profile = "mixed extremes"

    elif (
        top_quarter_opponents
        >= matches_analysed / 2
    ):
        schedule_profile = (
            "mostly strong opposition"
        )

    elif (
        bottom_quarter_opponents
        >= matches_analysed / 2
    ):
        schedule_profile = (
            "mostly weak opposition"
        )

    elif (
        position_standard_deviation
        <= league_size * 0.10
    ):
        schedule_profile = (
            "consistent opponent strength"
        )

    else:
        schedule_profile = (
            "mixed opponent strength"
        )

    home_matches = int(
        recent_matches["is_home"].sum()
    )

    away_matches = (
        matches_analysed - home_matches
    )

    home_match_percentage = (
        home_matches
        / matches_analysed
        * 100
    )

    away_match_percentage = (
        away_matches
        / matches_analysed
        * 100
    )

    if home_match_percentage >= 65:
        venue_balance = "home-heavy"

    elif home_match_percentage <= 35:
        venue_balance = "away-heavy"

    else:
        venue_balance = "balanced"

    hardest_match = recent_matches.loc[
        recent_matches[
            "opponent_position"
        ].idxmin()
    ]

    easiest_match = recent_matches.loc[
        recent_matches[
            "opponent_position"
        ].idxmax()
    ]

    recent_opponents = []

    for _, match in recent_matches.iterrows():
        recent_opponents.append(
            {
                "opponent": match["opponent"],
                "position": int(
                    match["opponent_position"]
                ),
                "ppg": round(
                    float(
                        match["opponent_ppg"]
                    ),
                    2,
                ),
                "venue": (
                    "home"
                    if match["is_home"]
                    else "away"
                ),
            }
        )

    return {
        "matches_requested": match_count,
        "matches_analysed": (
            matches_analysed
        ),
        "median_opponent_position": round(
            median_opponent_position,
            2,
        ),
        "average_opponent_ppg": round(
            average_opponent_ppg,
            2,
        ),
        "position_range": position_range,
        "position_standard_deviation": round(
            position_standard_deviation,
            2,
        ),
        "top_quarter_opponents": (
            top_quarter_opponents
        ),
        "upper_middle_opponents": (
            upper_middle_opponents
        ),
        "lower_middle_opponents": (
            lower_middle_opponents
        ),
        "bottom_quarter_opponents": (
            bottom_quarter_opponents
        ),
        "schedule_profile": (
            schedule_profile
        ),
        "home_matches": home_matches,
        "away_matches": away_matches,
        "home_match_percentage": round(
            home_match_percentage,
            1,
        ),
        "away_match_percentage": round(
            away_match_percentage,
            1,
        ),
        "venue_balance": venue_balance,
        "hardest_opponent": {
            "team": hardest_match[
                "opponent"
            ],
            "position": int(
                hardest_match[
                    "opponent_position"
                ]
            ),
            "ppg": round(
                float(
                    hardest_match[
                        "opponent_ppg"
                    ]
                ),
                2,
            ),
        },
        "easiest_opponent": {
            "team": easiest_match[
                "opponent"
            ],
            "position": int(
                easiest_match[
                    "opponent_position"
                ]
            ),
            "ppg": round(
                float(
                    easiest_match[
                        "opponent_ppg"
                    ]
                ),
                2,
            ),
        },
        "recent_opponents": (
            recent_opponents
        ),
    }


def analyse_league_rankings(
    data: pd.DataFrame,
    league_table: pd.DataFrame,
    team: str,
    current_round: int,
) -> dict:
    """Rank a team against the league for selected performance metrics."""

    rankings = []

    for league_team in league_table["team"]:
        team_matches = get_team_matches(
            data=data,
            team=league_team,
            current_round=current_round,
        )

        profile = build_team_profile(team_matches)

        rankings.append(
            {
                "team": league_team,
                "season_ppg": profile["season"]["ppg"],
                "goals_scored_per_game": (
                    profile["season"]["goals_scored_per_game"]
                ),
                "goals_conceded_per_game": (
                    profile["season"]["goals_conceded_per_game"]
                ),
                "home_ppg": profile["home"]["ppg"],
                "away_ppg": profile["away"]["ppg"],
            }
        )

    rankings_df = pd.DataFrame(rankings)

    if team not in rankings_df["team"].values:
        raise ValueError(
            f"Team '{team}' was not found in the rankings data."
        )

    rankings_df["ppg_rank"] = (
        rankings_df["season_ppg"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    rankings_df["attack_rank"] = (
        rankings_df["goals_scored_per_game"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    rankings_df["defence_rank"] = (
        rankings_df["goals_conceded_per_game"]
        .rank(method="min", ascending=True)
        .astype(int)
    )

    rankings_df["home_rank"] = (
        rankings_df["home_ppg"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    rankings_df["away_rank"] = (
        rankings_df["away_ppg"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    team_row = rankings_df[
        rankings_df["team"] == team
    ].iloc[0]

    return {
        "team": team,
        "league_size": len(rankings_df),
        "ppg_rank": int(team_row["ppg_rank"]),
        "attack_rank": int(team_row["attack_rank"]),
        "defence_rank": int(team_row["defence_rank"]),
        "home_rank": int(team_row["home_rank"]),
        "away_rank": int(team_row["away_rank"]),
    }

def classify_rank(rank: int, league_size: int) -> str:
    """Classify a league ranking as strong, average or weak."""

    strong_limit = max(1, round(league_size / 3))
    weak_limit = round((league_size * 2) / 3)

    if rank <= strong_limit:
        return "strong"

    if rank >= weak_limit:
        return "weak"

    return "average"


def identify_key_insights(
    comparison: dict,
    team_fixture_context: dict,
    opponent_fixture_context: dict,
    team_rankings: dict,
    opponent_rankings: dict,
) -> list[str]:
    """Generate balanced deterministic insights for both teams."""

    insights = []

    team = comparison["team"]
    opponent = comparison["opponent"]

    recent_ppg_difference = (
        comparison["team_recent_ppg"]
        - comparison["opponent_recent_ppg"]
    )

    venue_ppg_difference = (
        comparison["team_venue_ppg"]
        - comparison["opponent_venue_ppg"]
    )

    # Recent form comparison
    if recent_ppg_difference >= 0.5:
        insights.append(
            f"{team} are in clearly stronger recent form than "
            f"{opponent}, based on points per game."
        )
    elif recent_ppg_difference <= -0.5:
        insights.append(
            f"{opponent} are in clearly stronger recent form than "
            f"{team}, based on points per game."
        )
    else:
        insights.append(
            f"Recent form is broadly similar between "
            f"{team} and {opponent}."
        )

    # Venue-specific form comparison
    if venue_ppg_difference >= 0.5:
        insights.append(
            f"{team} have the stronger venue-specific record "
            "for this fixture."
        )
    elif venue_ppg_difference <= -0.5:
        insights.append(
            f"{opponent} have the stronger venue-specific record "
            "for this fixture."
        )
    else:
        insights.append(
            "The teams have similar venue-specific records."
        )

    # League position comparison
    if comparison["team_position"] < comparison["opponent_position"]:
        insights.append(
            f"{team} currently hold the higher league position."
        )
    elif comparison["team_position"] > comparison["opponent_position"]:
        insights.append(
            f"{opponent} currently hold the higher league position."
        )
    else:
        insights.append(
            f"{team} and {opponent} are level on league position."
        )

    # Recent fixture difficulty
    team_schedule_profile = team_fixture_context["schedule_profile"]
    opponent_schedule_profile = (
        opponent_fixture_context["schedule_profile"]
    )

    if team_schedule_profile == "mostly strong opposition":
        insights.append(
            f"{team}'s recent form has come against mostly strong "
            "opposition."
        )
    elif team_schedule_profile == "mostly weak opposition":
        insights.append(
            f"{team}'s recent form has come against mostly weaker "
            "opposition."
        )

    if opponent_schedule_profile == "mostly strong opposition":
        insights.append(
            f"{opponent}'s recent form has come against mostly strong "
            "opposition."
        )
    elif opponent_schedule_profile == "mostly weak opposition":
        insights.append(
            f"{opponent}'s recent form has come against mostly weaker "
            "opposition."
        )

    # Recent venue balance
    team_venue_balance = team_fixture_context["venue_balance"]
    opponent_venue_balance = opponent_fixture_context["venue_balance"]

    if team_venue_balance == "away-heavy":
        insights.append(
            f"{team}'s recent fixture run has been away-heavy."
        )
    elif team_venue_balance == "home-heavy":
        insights.append(
            f"{team}'s recent fixture run has been home-heavy."
        )

    if opponent_venue_balance == "away-heavy":
        insights.append(
            f"{opponent}'s recent fixture run has been away-heavy."
        )
    elif opponent_venue_balance == "home-heavy":
        insights.append(
            f"{opponent}'s recent fixture run has been home-heavy."
        )

    # Rank classifications
    team_attack_level = classify_rank(
        rank=team_rankings["attack_rank"],
        league_size=team_rankings["league_size"],
    )

    opponent_attack_level = classify_rank(
        rank=opponent_rankings["attack_rank"],
        league_size=opponent_rankings["league_size"],
    )

    team_defence_level = classify_rank(
        rank=team_rankings["defence_rank"],
        league_size=team_rankings["league_size"],
    )

    opponent_defence_level = classify_rank(
        rank=opponent_rankings["defence_rank"],
        league_size=opponent_rankings["league_size"],
    )

    # Team attack
    if team_attack_level == "strong":
        insights.append(
            f"{team} rank among the league's strongest attacking sides."
        )
    elif team_attack_level == "weak":
        insights.append(
            f"{team} rank among the league's weaker attacking sides."
        )

    # Opponent attack
    if opponent_attack_level == "strong":
        insights.append(
            f"{opponent} rank among the league's strongest attacking "
            "sides."
        )
    elif opponent_attack_level == "weak":
        insights.append(
            f"{opponent} rank among the league's weaker attacking sides."
        )

    # Team defence
    if team_defence_level == "strong":
        insights.append(
            f"{team} rank among the league's strongest defensive sides."
        )
    elif team_defence_level == "weak":
        insights.append(
            f"{team} rank among the league's weaker defensive sides."
        )

    # Opponent defence
    if opponent_defence_level == "strong":
        insights.append(
            f"{opponent} rank among the league's strongest defensive "
            "sides."
        )
    elif opponent_defence_level == "weak":
        insights.append(
            f"{opponent} rank among the league's weaker defensive sides."
        )

    return insights


def gather_match_context(
        data: pd.DataFrame,
        team: str,
        current_round: int,
)  -> dict:
    """Gather all data required for a pre-match report."""

    fixture = get_next_fixture(
        data=data,
        team=team,
        current_round=current_round,
    )

    league_table = calculate_league_table(
        data=data,
        league=fixture["league"],
        current_round=current_round,
    )

    comparison = compare_teams(
        team=team,
        opponent=fixture["opponent"],
        team_venue=fixture["venue"],
        current_round=current_round,
        data=data,
        league_table=league_table,
    )

    team_matches = get_team_matches(
        data=data,
        team=team,
        current_round=current_round,
    )

    team_fixture_context = analyse_fixture_context(
        team_matches=team_matches,
        league_table=league_table,
        match_count=6,
    )

    opponent_matches = get_team_matches(
        data=data,
        team=fixture["opponent"],
        current_round=current_round,
    )

    opponent_fixture_context = analyse_fixture_context(
        team_matches=opponent_matches,
        league_table=league_table,
        match_count=6,
    )

    team_league_rankings = analyse_league_rankings(
        data=data,
        league_table=league_table,
        current_round=current_round,
        team=team,
    )

    opponent_league_rankings = analyse_league_rankings(
        data=data,
        league_table=league_table,
        current_round=current_round,
        team=fixture["opponent"],
    )

    key_insights = identify_key_insights(
        comparison=comparison,
        team_fixture_context=team_fixture_context,
        opponent_fixture_context=opponent_fixture_context,
        team_rankings=team_league_rankings,
        opponent_rankings=opponent_league_rankings,
    )

    return {
        "fixture": fixture,
        "comparison": comparison,
        "fixture_context": {
            "team": team_fixture_context,
            "opponent": opponent_fixture_context,
        },
        "league_rankings": {
            "team": team_league_rankings,
            "opponent": opponent_league_rankings,
        },
        "key_insights": key_insights,
    }


def generate_match_report(context: dict) -> str:
    """Generate a grounded pre-match report from analytical context."""

    context_json = json.dumps(
        context,
        indent=2,
    )

    instructions = """
You are a football analytics writer.

Write a concise, evidence-based pre-match report using only the supplied
match context.

Rules:
- Do not invent statistics, events, injuries, players or tactical details.
- Do not use outside knowledge.
- Treat the supplied statistics as the source of truth.
- Distinguish factual observations from interpretation.
- Do not predict an exact score.
- Do not claim that a team will definitely win.
- Use plain, professional language.
- Mention both teams.
- Focus on the most meaningful evidence rather than repeating every metric.
- Predict the score of the fixture

Structure the report under these headings:

Fixture Overview
Form and League Position
Home and Away Context
Strengths and Weaknesses
Key Match Takeaway
Score Prediction
""".strip()

    response = client.responses.create(
        model="gpt-5.6",
        reasoning={"effort": "low"},
        instructions=instructions,
        input=(
            "Create a pre-match report from the following JSON context:\n\n"
            f"{context_json}"
        ),
    )

    report = response.output_text

    if not report:
        raise ValueError(
            "The model returned an empty match report."
        )

    return report


def main() -> None:
    data = load_data(DATA_FILE)

    team = "QPR"
    current_round = 25

    context = gather_match_context(
        data=data,
        team=team,
        current_round=current_round,
    )

    print("\n===== DETERMINISTIC KEY INSIGHTS =====\n")

    for insight in context["key_insights"]:
        print(f"- {insight}")

    print("\n===== AI PRE-MATCH REPORT =====\n")

    report = generate_match_report(context)

    print(report)

if __name__ == "__main__":
    main()