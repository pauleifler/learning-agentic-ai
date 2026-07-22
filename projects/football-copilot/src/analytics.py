import pandas as pd

from data_processing import get_team_matches, normalise_analysis_date

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


def build_team_profiles_for_league(
        
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
    team_context: dict,
    opponent_context: dict,
    venue: str,
) -> dict:
    """
    Compare a team against their opponent
    from the perspective of the selected team.
    """

    required_context_keys = {
        "team",
        "profile",
        "league",
        "ranks",
    }

    for label, context in [
        ("team_context", team_context),
        ("opponent_context", opponent_context),
    ]:
        missing_keys = required_context_keys.difference(
            context.keys()
        )

        if missing_keys:
            raise ValueError(
                f"{label} is missing required keys: "
                f"{sorted(missing_keys)}"
            )

    team = team_context["team"]
    opponent = opponent_context["team"]

    team_season = team_context["profile"]["season"]
    opponent_season = opponent_context["profile"]["season"]

    team_recent = team_context["profile"]["recent"]
    opponent_recent = opponent_context["profile"]["recent"]

    # Select the relevant venue perspective
    if venue == "Home":
        team_venue = team_context["profile"]["home"]
        opponent_venue = opponent_context["profile"]["away"]

    elif venue == "Away":
        team_venue = team_context["profile"]["away"]
        opponent_venue = opponent_context["profile"]["home"]

    else:
        raise ValueError(
            "venue must be either 'Home' or 'Away'"
        )

    team_league = team_context["league"]
    opponent_league = opponent_context["league"]

    team_ranks = team_context["ranks"]
    opponent_ranks = opponent_context["ranks"]

    return {
        "fixture": {
            "team": team,
            "opponent": opponent,
            "venue": venue,
            "analysis_date": team_context.get(
                "analysis_date"
            ),
        },

        "team": {
            "name": team,
            "league": team_league,
            "season": team_season,
            "recent": team_recent,
            "venue": team_venue,
            "ranks": team_ranks,
        },

        "opponent": {
            "name": opponent,
            "league": opponent_league,
            "season": opponent_season,
            "recent": opponent_recent,
            "venue": opponent_venue,
            "ranks": opponent_ranks,
        },

        "differences": {
            metric: round(
                team_value - opponent_value,
                2,
            )
            for metric, team_value, opponent_value in [
                (
                    "season_ppg",
                    team_season["ppg"],
                    opponent_season["ppg"],
                ),
                (
                    "recent_ppg",
                    team_recent["ppg"],
                    opponent_recent["ppg"],
                ),
                (
                    "venue_ppg",
                    team_venue["ppg"],
                    opponent_venue["ppg"],
                ),
                (
                    "goals_scored_per_game",
                    team_venue["goals_scored_per_game"],
                    opponent_venue["goals_scored_per_game"],
                ),
                (
                    "goals_conceded_per_game",
                    opponent_venue["goals_conceded_per_game"],
                    team_venue["goals_conceded_per_game"],
                ),
                (
                    "shots_per_game",
                    team_venue["shots_per_game"],
                    opponent_venue["shots_per_game"],
                ),
                (
                    "shots_on_target_per_game",
                    team_venue["shots_on_target_per_game"],
                    opponent_venue["shots_on_target_per_game"],
                ),
                (
                    "corners_per_game",
                    team_venue["corners_per_game"],
                    opponent_venue["corners_per_game"],
                ),
            ]
        },
    }


def identify_key_insights(
    comparison: dict,
) -> list[dict]:
    """
    Identify the most important statistical advantages
    from the perspective of the selected team.
    """

    insights = []

    differences = comparison["differences"]

    team = comparison["team"]["name"]
    opponent = comparison["opponent"]["name"]

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

        value = differences.get(metric)

        if value is None:
            continue

        if abs(value) < threshold:
            continue

        stronger_team = (
            team
            if value > 0
            else opponent
        )

        insights.append(
            {
                "metric": metric,
                "team": stronger_team,
                "difference": round(
                    abs(value),
                    2,
                ),
            }
        )

    return insights




