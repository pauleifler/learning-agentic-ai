from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

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
    POINTS = {
    "Win": 3,
    "Draw": 1,
    "Loss": 0,
    }
    team_matches["points"] = team_matches["result"].map(POINTS)
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


def display_team_profile(team: str,current_round: int,profile: dict,) -> None:
    """Display the team profile in a readable format."""

    print(f"\n===== {team} Profile (Round {current_round}) =====\n")

    for section, values in profile.items():

        print(f"\n--- {section.upper()} ---")

        if isinstance(values, dict):
            for metric, value in values.items():
                print(f"{metric:<35} {value}")
        else:
            print(values)


def main() -> None:
    data = load_data(DATA_FILE)

    team = "Leeds"
    current_round = 25

    team_matches = get_team_matches(
        data,
        team,
        current_round,
    )

    profile = build_team_profile(team_matches)

    display_team_profile(
        team,
        current_round,
        profile,
    )

if __name__ == "__main__":
    main()
