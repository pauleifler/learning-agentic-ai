def identify_team_strengths(
    team_summary: dict,
) -> list:
    """
    Identify statistically strong areas for a team.
    """

    strengths = []

    attack = team_summary["attack"]
    defence = team_summary["defence"]

    if attack["goals_rank"] <= 5:
        strengths.append(
            {
                "area": "goals scored",
                "evidence": (
                    f"{team_summary['team']} rank "
                    f"{attack['goals_rank']} for goals scored"
                ),
            }
        )

    if attack["shots_rank"] <= 5:
        strengths.append(
            {
                "area": "shot volume",
                "evidence": (
                    f"{team_summary['team']} rank "
                    f"{attack['shots_rank']} for shots"
                ),
            }
        )

    if attack["corners_rank"] <= 5:
        strengths.append(
            {
                "area": "territorial pressure",
                "evidence": (
                    f"{team_summary['team']} rank "
                    f"{attack['corners_rank']} for corners"
                ),
            }
        )

    if defence["defence_rank"] <= 5:
        strengths.append(
            {
                "area": "defensive record",
                "evidence": (
                    f"{team_summary['team']} rank "
                    f"{defence['defence_rank']} for "
                    "goals conceded"
                ),
            }
        )

    return strengths


def identify_team_weaknesses(
    team_summary: dict,
) -> list:
    """
    Identify statistically weaker areas.
    """

    weaknesses = []

    attack = team_summary["attack"]
    defence = team_summary["defence"]

    if attack["goals_rank"] >= 15:
        weaknesses.append(
            {
                "area": "goals scored",
                "evidence": (
                    f"{team_summary['team']} rank "
                    f"{attack['goals_rank']} for goals scored"
                ),
            }
        )

    if defence["defence_rank"] >= 15:
        weaknesses.append(
            {
                "area": "defensive record",
                "evidence": (
                    f"{team_summary['team']} rank "
                    f"{defence['defence_rank']} for goals conceded"
                ),
            }
        )

    return weaknesses


def calculate_performance_indicators(
    summary: dict,
) -> dict:
    """
    Add derived performance indicators
    to a team analysis summary.
    """

    attack = summary["attack"]
    defence = summary["defence"]

    indicators = {}

    if attack["shots_per_game"] > 0:
        indicators["shot_conversion_rate"] = (
            attack["goals_per_game"]
            /
            attack["shots_per_game"]
        )

        indicators["shot_accuracy"] = (
            attack["shots_on_target_per_game"]
            /
            attack["shots_per_game"]
        )

    if attack["shots_on_target_per_game"] > 0:
        indicators["shots_on_target_conversion_rate"] = (
            attack["goals_per_game"]
            /
            attack["shots_on_target_per_game"]
        )

    if defence["shots_conceded_per_game"] > 0:
        indicators["defensive_conversion_rate_conceded"] = (
            defence["goals_conceded_per_game"]
            /
            defence["shots_conceded_per_game"]
        )

    return indicators


def identify_performance_observations(
    summary: dict,
) -> list:
    """
    Identify meaningful relationships between
    performance metrics.
    """

    observations = []

    attack = summary["attack"]
    indicators = summary.get(
        "performance_indicators",
        {},
    )

    team = summary["team"]

    # High shots but lower goal output
    if (
        attack["shots_rank"] <= 10
        and attack["goals_rank"] >= 15
    ):
        observations.append(
            {
                "team": team,
                "area": "attacking efficiency",
                "observation": (
                    f"{team} create a relatively high "
                    "volume of shots but rank lower "
                    "for goals scored."
                ),
                "evidence": {
                    "shots_rank": attack["shots_rank"],
                    "goals_rank": attack["goals_rank"],
                },
            }
        )

    # Good finishing efficiency
    if (
        indicators.get("shot_conversion_rate", 0)
        > 0.15
    ):
        observations.append(
            {
                "team": team,
                "area": "finishing efficiency",
                "observation": (
                    f"{team} convert a high proportion "
                    "of their shots into goals."
                ),
                "evidence": {
                    "shot_conversion_rate": indicators[
                        "shot_conversion_rate"
                    ],
                },
            }
        )

    # Strong defensive suppression
    if (
        summary["defence"]["shots_conceded_rank"]
        <= 5
        and summary["defence"]["defence_rank"]
        <= 5
    ):
        observations.append(
            {
                "team": team,
                "area": "defensive control",
                "observation": (
                    f"{team} combine low opponent shot "
                    "volume with a strong defensive record."
                ),
                "evidence": {
                    "shots_conceded_rank": (
                        summary["defence"]
                        ["shots_conceded_rank"]
                    ),
                    "defence_rank": (
                        summary["defence"]
                        ["defence_rank"]
                    ),
                },
            }
        )

    return observations


def build_team_analysis_summary(
    team_context: dict,
) -> dict:

    profile = team_context["profile"]
    league = team_context["league"]
    ranks = team_context["ranks"]

    season = profile["season"]

    summary = {
        "team": team_context["team"],

        "league_position": league["position"],

        "results": {
            "played": league["played"],
            "points": league["points"],
            "ppg": season["ppg"],
            "goal_difference": league["goal_difference"],
        },

        "attack": {
            "goals_per_game": season["goals_scored_per_game"],
            "goals_rank": ranks["goals_scored_per_game_rank"],

            "shots_per_game": season["shots_per_game"],
            "shots_rank": ranks["shots_per_game_rank"],

            "shots_on_target_per_game": season["shots_on_target_per_game"],
            "shots_on_target_rank": ranks["shots_on_target_per_game_rank"],

            "corners_per_game": season["corners_per_game"],
            "corners_rank": ranks["corners_per_game_rank"],
        },

        "defence": {
            "goals_conceded_per_game": season["goals_conceded_per_game"],
            "defence_rank": ranks["goals_conceded_per_game_rank"],

            "shots_conceded_per_game": season["shots_conceded_per_game"],
            "shots_conceded_rank": ranks["shots_conceded_per_game_rank"],

            "shots_on_target_conceded_per_game": season["shots_on_target_conceded_per_game"],
            "shots_on_target_conceded_rank": ranks["shots_on_target_conceded_per_game_rank"],

            "corners_conceded_per_game": season["corners_conceded_per_game"],
            "corners_conceded_rank": ranks["corners_conceded_per_game_rank"],
        },
    }

    summary["strengths"] = identify_team_strengths(summary)

    summary["weaknesses"] = identify_team_weaknesses(summary)

    summary["performance_indicators"] = (
    calculate_performance_indicators(summary))

    summary["observations"] = (
    identify_performance_observations(summary)
    )

    return summary

def identify_key_battles(
    team: dict,
    opponent: dict,
) -> list:
    """
    Identify important statistical comparisons
    from the perspective of the selected team.
    """

    battles = []

    team_attack = team["attack"]
    team_defence = team["defence"]

    opponent_attack = opponent["attack"]
    opponent_defence = opponent["defence"]

    # Chance creation
    battles.append(
        {
            "area": "Chance creation",
            "comparison": [
                {
                    "team": team["team"],
                    "metric": "shots_per_game",
                    "value": round(
                        team_attack["shots_per_game"],
                        2,
                    ),
                    "rank": team_attack["shots_rank"],
                },
                {
                    "team": opponent["team"],
                    "metric": "shots_allowed_per_game",
                    "value": round(
                        opponent_defence["shots_conceded_per_game"],
                        2,
                    ),
                    "rank": opponent_defence["shots_conceded_rank"],
                },
            ],
        }
    )

    # Chance quality
    battles.append(
        {
            "area": "Chance quality",
            "comparison": [
                {
                    "team": team["team"],
                    "metric": "shots_on_target_per_game",
                    "value": round(
                        team_attack["shots_on_target_per_game"],
                        2,
                    ),
                    "rank": team_attack["shots_on_target_rank"],
                },
                {
                    "team": opponent["team"],
                    "metric": "shots_allowed_on_target_per_game",
                    "value": round(
                        opponent_defence[
                            "shots_on_target_conceded_per_game"
                        ],
                        2,
                    ),
                    "rank": opponent_defence[
                        "shots_on_target_conceded_rank"
                    ],
                },
            ],
        }
    )

    # Territorial pressure
    battles.append(
        {
            "area": "Territorial pressure",
            "comparison": [
                {
                    "team": team["team"],
                    "metric": "corners_per_game",
                    "value": round(
                        team_attack["corners_per_game"],
                        2,
                    ),
                    "rank": team_attack["corners_rank"],
                },
                {
                    "team": opponent["team"],
                    "metric": "corners_allowed_per_game",
                    "value": round(
                        opponent_defence[
                            "corners_conceded_per_game"
                        ],
                        2,
                    ),
                    "rank": opponent_defence[
                        "corners_conceded_rank"
                    ],
                },
            ],
        }
    )

    return battles

def build_opposition_analysis_context(
    match_context: dict,
) -> dict:

    fixture = match_context["fixture"]

    team = build_team_analysis_summary(
        match_context["team"]
    )

    opponent = build_team_analysis_summary(
        match_context["opponent"]
    )

    return {
        "report_type": "opposition_analysis",

        "perspective": (
            f"{team['team']} performance analyst "
            "assessing the upcoming opponent"
        ),

        "fixture": {
            "team": fixture["team"],
            "opponent": fixture["opponent"],
            "venue": fixture["venue"],
            "date": fixture["date"],
        },

        "team": team,

        "opponent": opponent,

        "key_statistical_differences": (
            match_context["insights"]
        ),

        "key_battles": identify_key_battles(
            team,
            opponent,
        ),
    }