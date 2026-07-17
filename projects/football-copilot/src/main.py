from pathlib import Path
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from pprint import pprint
import json



LEAGUE_NAMES = {
    "E0": "Premier League",
    "E1": "Championship",
    "E2": "League One",
    "E3": "League Two",
}

COLUMN_MAP = {
    "Div": "league_code",
    "Date": "date",
    "Time": "kickoff_time",
    "HomeTeam": "home_team",
    "AwayTeam": "away_team",

    "FTHG": "home_goals",
    "FTAG": "away_goals",
    "FTR": "full_time_result",

    "HTHG": "home_half_time_goals",
    "HTAG": "away_half_time_goals",
    "HTR": "half_time_result",

    "HS": "home_shots",
    "AS": "away_shots",
    "HST": "home_shots_on_target",
    "AST": "away_shots_on_target",

    "HC": "home_corners",
    "AC": "away_corners",

    "HY": "home_yellow_cards",
    "AY": "away_yellow_cards",
    "HR": "home_red_cards",
    "AR": "away_red_cards",
}

def load_match_data(data_directory: Path) -> pd.DataFrame:
    """
    Load and standardise English league match data.

    Reads any available E0-E3 CSV files from the supplied directory,
    retains the required columns, standardises column names and returns
    one combined DataFrame.
    """

    csv_files = sorted(data_directory.glob("E[0-3].csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No E0-E3 CSV files were found in: {data_directory}"
        )

    required_source_columns = list(COLUMN_MAP.keys())
    frames = []

    for file_path in csv_files:
        frame = pd.read_csv(file_path)

        missing_columns = [
            column
            for column in required_source_columns
            if column not in frame.columns
        ]

        if missing_columns:
            raise ValueError(
                f"{file_path.name} is missing required columns: "
                f"{missing_columns}"
            )

        frame = frame[required_source_columns].copy()
        frame = frame.rename(columns=COLUMN_MAP)

        frames.append(frame)

    data = pd.concat(
        frames,
        ignore_index=True,
    )

    data["date"] = pd.to_datetime(
        data["date"],
        format="%d/%m/%Y",
        errors="raise",
    )

    data["league"] = data["league_code"].map(LEAGUE_NAMES)

    if data["league"].isna().any():
        unknown_codes = (
            data.loc[data["league"].isna(), "league_code"]
            .dropna()
            .unique()
            .tolist()
        )

        raise ValueError(
            f"Unknown league codes found: {unknown_codes}"
        )

    data = (
        data.sort_values(
            by=["date", "kickoff_time"],
            na_position="last",
        )
        .reset_index(drop=True)
    )

    return data

DATA_DIRECTORY = Path(__file__).resolve().parent / "data"

data = load_match_data(DATA_DIRECTORY)


def normalise_analysis_date(
    analysis_date: str | pd.Timestamp,
) -> pd.Timestamp:
    """Convert an analysis date into a normalised Pandas Timestamp."""

    parsed_date = pd.Timestamp(analysis_date)

    if pd.isna(parsed_date):
        raise ValueError("analysis_date must be a valid date.")
    
    return parsed_date.normalize()


def get_team_matches(
    data: pd.DataFrame,
    team: str,
    analysis_date: str | pd.Timestamp,
) -> pd.DataFrame:
    """
    Return a team's completed matches before the analysis date.
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

    team_matches = data[
        (
            data["home_team"].eq(team)
            | data["away_team"].eq(team)
        )
        & data["date"].lt(analysis_date)
        & data["full_time_result"].notna()
    ].copy()

    return (
        team_matches
        .sort_values(["date", "kickoff_time"])
        .reset_index(drop=True)
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


def calculate_league_table(
    data: pd.DataFrame,
    league: str,
    analysis_date: str | pd.Timestamp,
) -> pd.DataFrame:
    """
    Calculate the league table using completed matches before the analysis date.
    """

    analysis_date = normalise_analysis_date(analysis_date)

    league_matches = data[
        (data["league"] == league)
        & (data["date"] < analysis_date)
        & (data["full_time_result"].notna())
    ].copy()

    if league_matches.empty:
        raise ValueError(
            f"No completed matches found for {league} "
            f"before {analysis_date.date()}."
        )

    teams = sorted(
        set(league_matches["home_team"])
        | set(league_matches["away_team"])
    )

    table = pd.DataFrame({
        "team": teams,
        "played": 0,
        "won": 0,
        "drawn": 0,
        "lost": 0,
        "goals_for": 0,
        "goals_against": 0,
        "points": 0,
    })

    table = table.set_index("team")

    for _, match in league_matches.iterrows():
        home_team = match["home_team"]
        away_team = match["away_team"]
        home_goals = int(match["home_goals"])
        away_goals = int(match["away_goals"])

        table.loc[home_team, "played"] += 1
        table.loc[away_team, "played"] += 1

        table.loc[home_team, "goals_for"] += home_goals
        table.loc[home_team, "goals_against"] += away_goals

        table.loc[away_team, "goals_for"] += away_goals
        table.loc[away_team, "goals_against"] += home_goals

        if home_goals > away_goals:
            table.loc[home_team, "won"] += 1
            table.loc[away_team, "lost"] += 1
            table.loc[home_team, "points"] += 3

        elif home_goals < away_goals:
            table.loc[away_team, "won"] += 1
            table.loc[home_team, "lost"] += 1
            table.loc[away_team, "points"] += 3

        else:
            table.loc[home_team, "drawn"] += 1
            table.loc[away_team, "drawn"] += 1
            table.loc[home_team, "points"] += 1
            table.loc[away_team, "points"] += 1

    table["goal_difference"] = (
        table["goals_for"]
        - table["goals_against"]
    )

    table = (
        table
        .reset_index()
        .sort_values(
            by=[
                "points",
                "goal_difference",
                "goals_for",
            ],
            ascending=[False, False, False],
        )
        .reset_index(drop=True)
    )

    table["position"] = table.index + 1

    return table[
        [
            "position",
            "team",
            "played",
            "won",
            "drawn",
            "lost",
            "goals_for",
            "goals_against",
            "goal_difference",
            "points",
        ]
    ]


def calculate_league_rankings(
    team_profiles: dict[str, dict],
) -> dict[str, dict]:
    """
    Calculate league-wide rankings from each team's season profile.

    Higher values rank better for attacking metrics.
    Lower values rank better for defensive and disciplinary metrics.
    """

    if not team_profiles:
        return {}

    higher_is_better = [
        "points",
        "ppg",
        "goals_scored",
        "goals_scored_per_game",
        "shots",
        "shots_per_game",
        "shots_on_target",
        "shots_on_target_per_game",
        "corners",
        "corners_per_game",
    ]

    lower_is_better = [
        "goals_conceded",
        "goals_conceded_per_game",
        "shots_conceded",
        "shots_conceded_per_game",
        "shots_on_target_conceded",
        "shots_on_target_conceded_per_game",
        "corners_conceded",
        "corners_conceded_per_game",
        "yellow_cards",
        "yellow_cards_per_game",
        "red_cards",
        "red_cards_per_game",
    ]

    rows = []

    for team, profile in team_profiles.items():
        if "season" not in profile:
            raise ValueError(
                f"Profile for '{team}' does not contain a season summary."
            )

        season = profile["season"]

        row = {"team": team}

        for metric in higher_is_better + lower_is_better:
            if metric not in season:
                raise ValueError(
                    f"Season profile for '{team}' is missing "
                    f"metric '{metric}'."
                )

            row[metric] = season[metric]

        rows.append(row)

    rankings_df = pd.DataFrame(rows).set_index("team")

    rankings = pd.DataFrame(
        index=rankings_df.index
    )

    for metric in higher_is_better:
        rankings[f"{metric}_rank"] = (
            rankings_df[metric]
            .rank(
                method="min",
                ascending=False,
            )
            .astype(int)
        )

    for metric in lower_is_better:
        rankings[f"{metric}_rank"] = (
            rankings_df[metric]
            .rank(
                method="min",
                ascending=True,
            )
            .astype(int)
        )

    return rankings.to_dict(orient="index")


def add_team_match_outcomes(
    team_matches: pd.DataFrame,
    team: str,
) -> pd.DataFrame:
    """
    Add team-relative outcome columns to a team's match history.
    """

    if team_matches.empty:
        raise ValueError(
            f"No historical matches were supplied for {team}."
        )

    matches = team_matches.copy()

    is_home = matches["home_team"].eq(team)
    is_away = matches["away_team"].eq(team)

    if not (is_home | is_away).all():
        raise ValueError(
            f"Some supplied matches do not involve {team}."
        )

    matches["venue"] = is_home.map({
        True: "home",
        False: "away",
    })

    matches["goals_scored"] = matches["home_goals"].where(
        is_home,
        matches["away_goals"],
    )

    matches["goals_conceded"] = matches["away_goals"].where(
        is_home,
        matches["home_goals"],
    )

    matches["result"] = "D"

    matches.loc[
        matches["goals_scored"] > matches["goals_conceded"],
        "result",
    ] = "W"

    matches.loc[
        matches["goals_scored"] < matches["goals_conceded"],
        "result",
    ] = "L"

    matches["points"] = matches["result"].map({
        "W": 3,
        "D": 1,
        "L": 0,
    })

    matches["shots"] = matches["home_shots"].where(
    is_home,
    matches["away_shots"],
)

    matches["shots_conceded"] = matches["away_shots"].where(
        is_home,
        matches["home_shots"],
    )

    matches["shots_on_target"] = matches[
        "home_shots_on_target"
    ].where(
        is_home,
        matches["away_shots_on_target"],
    )

    matches["shots_on_target_conceded"] = matches[
        "away_shots_on_target"
    ].where(
        is_home,
        matches["home_shots_on_target"],
    )

    matches["corners"] = matches["home_corners"].where(
        is_home,
        matches["away_corners"],
    )

    matches["corners_conceded"] = matches["away_corners"].where(
        is_home,
        matches["home_corners"],
    )

    matches["yellow_cards"] = matches[
        "home_yellow_cards"
    ].where(
        is_home,
        matches["away_yellow_cards"],
    )

    matches["red_cards"] = matches[
        "home_red_cards"
    ].where(
        is_home,
        matches["away_red_cards"],
    )

    return matches


def summarise_matches(
    matches: pd.DataFrame,
) -> dict:
    """
    Summarise team-relative match data.
    """

    if matches.empty:
        return {
            "matches_played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "points": 0,
            "ppg": 0.0,
            "goals_scored": 0,
            "goals_conceded": 0,
            "goals_scored_per_game": 0.0,
            "goals_conceded_per_game": 0.0,
            "shots": 0,
            "shots_per_game": 0.0,
            "shots_conceded": 0,
            "shots_conceded_per_game": 0.0,
            "shots_on_target": 0,
            "shots_on_target_per_game": 0.0,
            "shots_on_target_conceded": 0,
            "shots_on_target_conceded_per_game": 0.0,
            "corners": 0,
            "corners_per_game": 0.0,
            "corners_conceded": 0,
            "corners_conceded_per_game": 0.0,
            "yellow_cards": 0,
            "yellow_cards_per_game": 0.0,
            "red_cards": 0,
            "red_cards_per_game": 0.0,
        }

    matches_played = len(matches)

    wins = int((matches["result"] == "W").sum())
    draws = int((matches["result"] == "D").sum())
    losses = int((matches["result"] == "L").sum())

    points = int(matches["points"].sum())

    goals_scored = int(matches["goals_scored"].sum())
    goals_conceded = int(matches["goals_conceded"].sum())

    shots = int(matches["shots"].sum())
    shots_conceded = int(matches["shots_conceded"].sum())

    shots_on_target = int(
        matches["shots_on_target"].sum()
    )
    shots_on_target_conceded = int(
        matches["shots_on_target_conceded"].sum()
    )

    corners = int(matches["corners"].sum())
    corners_conceded = int(
        matches["corners_conceded"].sum()
    )

    yellow_cards = int(
        matches["yellow_cards"].sum()
    )
    red_cards = int(
        matches["red_cards"].sum()
    )

    return {
        "matches_played": matches_played,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "points": points,
        "ppg": points / matches_played,
        "goals_scored": goals_scored,
        "goals_conceded": goals_conceded,
        "goals_scored_per_game": goals_scored / matches_played,
        "goals_conceded_per_game": goals_conceded / matches_played,
        "shots": shots,
        "shots_per_game": shots / matches_played,
        "shots_conceded": shots_conceded,
        "shots_conceded_per_game": (
            shots_conceded / matches_played
        ),
        "shots_on_target": shots_on_target,
        "shots_on_target_per_game": (
            shots_on_target / matches_played
        ),
        "shots_on_target_conceded": (
            shots_on_target_conceded
        ),
        "shots_on_target_conceded_per_game": (
            shots_on_target_conceded / matches_played
        ),
        "corners": corners,
        "corners_per_game": corners / matches_played,
        "corners_conceded": corners_conceded,
        "corners_conceded_per_game": (
            corners_conceded / matches_played
        ),
        "yellow_cards": yellow_cards,
        "yellow_cards_per_game": (
            yellow_cards / matches_played
        ),
        "red_cards": red_cards,
        "red_cards_per_game": (
            red_cards / matches_played
        ),
    }


def build_team_profile(
    team_results: pd.DataFrame,
) -> dict:
    """
    Build a complete performance profile for a team.
    """

    season = summarise_matches(team_results)

    recent = summarise_matches(
        team_results.tail(6)
    )

    home = summarise_matches(
        team_results[
            team_results["venue"] == "home"
        ]
    )

    away = summarise_matches(
        team_results[
            team_results["venue"] == "away"
        ]
    )

    return {
        "season": season,
        "recent": recent,
        "home": home,
        "away": away,
        "matches_played": season["matches_played"],
        "form_change_ppg": round(
            recent["ppg"] - season["ppg"],
            2,
        ),
    }


def build_all_team_profiles(
    data: pd.DataFrame,
    league_table: pd.DataFrame,
    analysis_date: str | pd.Timestamp,
) -> dict[str, dict]:
    """
    Build a season profile for every team in the league table.
    """

    team_profiles = {}

    for team in league_table["team"]:
        team_matches = get_team_matches(
            data=data,
            team=team,
            analysis_date=analysis_date,
        )

        team_results = add_team_match_outcomes(
            team_matches=team_matches,
            team=team,
        )

        team_profiles[team] = build_team_profile(
            team_results
        )

    return team_profiles


def build_team_context(
    team: str,
    team_profile: dict,
    league_table: pd.DataFrame,
    league_rankings: dict[str, dict],
    next_fixture: dict | None,
    analysis_date: str | pd.Timestamp,
) -> dict:
    """
    Combine a team's profile, league-table record,
    statistical rankings, and next fixture.
    """

    analysis_date = normalise_analysis_date(
        analysis_date
    )

    if "team" not in league_table.columns:
        raise ValueError(
            "League table is missing the 'team' column."
        )

    team_row = league_table[
        league_table["team"] == team
    ]

    if team_row.empty:
        raise ValueError(
            f"Team '{team}' was not found in the league table."
        )

    if team not in league_rankings:
        raise ValueError(
            f"Rankings were not found for team '{team}'."
        )

    team_row = team_row.iloc[0]

    return {
        "team": team,
        "analysis_date": analysis_date,
        "profile": team_profile,
        "league": {
            "position": int(team_row["position"]),
            "played": int(team_row["played"]),
            "won": int(team_row["won"]),
            "drawn": int(team_row["drawn"]),
            "lost": int(team_row["lost"]),
            "goals_for": int(team_row["goals_for"]),
            "goals_against": int(
                team_row["goals_against"]
            ),
            "goal_difference": int(
                team_row["goal_difference"]
            ),
            "points": int(team_row["points"]),
            "league_size": len(league_table),
        },
        "ranks": league_rankings[team],
        "next_fixture": next_fixture,
    }


def compare_teams(
    home_context: dict,
    away_context: dict,
) -> dict:
    """
    Compare two team-context dictionaries for a fixture.

    The home team is evaluated using its home profile.
    The away team is evaluated using its away profile.
    """

    required_context_keys = {
        "team",
        "profile",
        "league",
        "ranks",
    }

    for label, context in [
        ("home_context", home_context),
        ("away_context", away_context),
    ]:
        missing_keys = required_context_keys.difference(
            context.keys()
        )

        if missing_keys:
            raise ValueError(
                f"{label} is missing required keys: "
                f"{sorted(missing_keys)}"
            )

    home_team = home_context["team"]
    away_team = away_context["team"]

    home_season = home_context["profile"]["season"]
    away_season = away_context["profile"]["season"]

    home_recent = home_context["profile"]["recent"]
    away_recent = away_context["profile"]["recent"]

    home_venue = home_context["profile"]["home"]
    away_venue = away_context["profile"]["away"]

    home_league = home_context["league"]
    away_league = away_context["league"]

    home_ranks = home_context["ranks"]
    away_ranks = away_context["ranks"]

    return {
        "fixture": {
            "home_team": home_team,
            "away_team": away_team,
            "analysis_date": home_context.get(
                "analysis_date"
            ),
        },

        "home_team": {
            "team": home_team,
            "league": home_league,
            "season": home_season,
            "recent": home_recent,
            "venue": home_venue,
            "ranks": home_ranks,
        },

        "away_team": {
            "team": away_team,
            "league": away_league,
            "season": away_season,
            "recent": away_recent,
            "venue": away_venue,
            "ranks": away_ranks,
        },

        "differences": {
            "league_position": (
                away_league["position"]
                - home_league["position"]
            ),

            "points": (
                home_league["points"]
                - away_league["points"]
            ),

            "season_ppg": round(
                home_season["ppg"]
                - away_season["ppg"],
                2,
            ),

            "recent_ppg": round(
                home_recent["ppg"]
                - away_recent["ppg"],
                2,
            ),

            "venue_ppg": round(
                home_venue["ppg"]
                - away_venue["ppg"],
                2,
            ),

            "goals_scored_per_game": round(
                home_venue["goals_scored_per_game"]
                - away_venue["goals_scored_per_game"],
                2,
            ),

            "goals_conceded_per_game": round(
                home_venue["goals_conceded_per_game"]
                - away_venue[
                    "goals_conceded_per_game"
                ],
                2,
            ),

            "shots_per_game": round(
                home_venue["shots_per_game"]
                - away_venue["shots_per_game"],
                2,
            ),

            "shots_on_target_per_game": round(
                home_venue[
                    "shots_on_target_per_game"
                ]
                - away_venue[
                    "shots_on_target_per_game"
                ],
                2,
            ),

            "corners_per_game": round(
                home_venue["corners_per_game"]
                - away_venue["corners_per_game"],
                2,
            ),

            "yellow_cards_per_game": round(
                home_venue["yellow_cards_per_game"]
                - away_venue[
                    "yellow_cards_per_game"
                ],
                2,
            ),

            "red_cards_per_game": round(
                home_venue["red_cards_per_game"]
                - away_venue["red_cards_per_game"],
                2,
            ),
        },
    }


def build_fixture_comparison(
    data: pd.DataFrame,
    team: str,
    league: str,
    analysis_date: str | pd.Timestamp,
) -> dict:
    """
    Build a complete comparison for a team's next fixture.
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

    if home_team not in team_profiles:
        raise ValueError(
            f"Profile was not found for home team "
            f"'{home_team}'."
        )

    if away_team not in team_profiles:
        raise ValueError(
            f"Profile was not found for away team "
            f"'{away_team}'."
        )

    home_context = build_team_context(
        team=home_team,
        team_profile=team_profiles[home_team],
        league_table=league_table,
        league_rankings=league_rankings,
        next_fixture=next_fixture,
        analysis_date=analysis_date,
    )

    away_context = build_team_context(
        team=away_team,
        team_profile=team_profiles[away_team],
        league_table=league_table,
        league_rankings=league_rankings,
        next_fixture=next_fixture,
        analysis_date=analysis_date,
    )

    comparison = compare_teams(
        home_context=home_context,
        away_context=away_context,
    )

    return {
        "fixture": next_fixture,
        "league_table": league_table,
        "home_context": home_context,
        "away_context": away_context,
        "comparison": comparison,
    }


def identify_key_insights(
    comparison: dict,
) -> list[dict]:
    """
    Identify the most important statistical advantages
    from a team comparison.
    """

    insights = []

    differences = comparison["differences"]

    home_team = comparison["home_team"]["team"]
    away_team = comparison["away_team"]["team"]

    thresholds = {
        "season_ppg": 0.50,
        "recent_ppg": 0.75,
        "venue_ppg": 0.75,
        "goals_scored_per_game": 0.50,
        "goals_conceded_per_game": 0.50,
        "shots_per_game": 2.0,
        "shots_on_target_per_game": 1.0,
        "corners_per_game": 1.5,
        "yellow_cards_per_game": 0.50,
        "red_cards_per_game": 0.20,
    }

    for metric, threshold in thresholds.items():

        value = differences[metric]

        if abs(value) < threshold:
            continue

        stronger_team = (
            home_team
            if value > 0
            else away_team
        )

        insights.append({
            "metric": metric,
            "team": stronger_team,
            "difference": round(value, 2),
        })

    return insights


def build_match_context(
    fixture: dict,
    home_context: dict,
    away_context: dict,
    comparison: dict,
    insights: list[dict],
) -> dict:
    """
    Combine every stage of the analysis into one object.
    """

    return {
        "analysis_date": home_context["analysis_date"],

        "fixture": fixture,

        "home_team": home_context,

        "away_team": away_context,

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
        home_context=fixture_analysis["home_context"],
        away_context=fixture_analysis["away_context"],
        comparison=comparison,
        insights=insights,
    )


def main():

    analysis_date = "2024-10-01"

    league = "Premier League"

    team = "Liverpool"

    data = load_match_data()

    match_context = analyse_fixture(

        data=data,

        team=team,

        league=league,

        analysis_date=analysis_date,

    )

    pprint(match_context)

if __name__ == "__main__":
    main()