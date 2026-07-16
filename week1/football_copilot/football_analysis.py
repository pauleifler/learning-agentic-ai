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



def main() -> None:
    data = load_data(DATA_FILE)

    league = "Championship"
    team = "QPR"
    opponent = "Bristol City"
    current_round = 25
    team_venue = "home"

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

    league_table = calculate_league_table(
        data=data,
        league="Championship",
        current_round=25,
    )

    position = get_team_position(league_table, team)

    comparison = compare_teams(
        team=team,
        opponent=opponent,
        current_round=current_round,
        data=data,
        team_venue=team_venue,
        league_table=league_table,
    )

    for metric, value in comparison.items():
        print(f"{metric:<40} {value}")

if __name__ == "__main__":
    main()
