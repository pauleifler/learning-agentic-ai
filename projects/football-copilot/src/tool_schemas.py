tools = [
    {
        "type": "function",
        "function": {
            "name": "compare_teams",
            "description": (
                "Compare the performance of any two football teams "
                "at a specified point in time."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "team": {
                        "type": "string",
                        "description": "The first team."
                    },
                    "opponent": {
                        "type": "string",
                        "description": "The second team."
                    },
                    "league": {
                        "type": "string",
                        "enum": [
                            "Premier League",
                            "Championship",
                            "League One",
                            "League Two"
                        ]
                    },
                    "analysis_date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format."
                    }
                },
                "required": [
                    "team",
                    "opponent",
                    "league",
                    "analysis_date"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_next_fixture",
            "description": (
                "Find a team's next fixture and compare it with "
                "the upcoming opponent using the correct venue."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "team": {
                        "type": "string",
                        "description": "The team to analyse."
                    },
                    "league": {
                        "type": "string",
                        "enum": [
                            "Premier League",
                            "Championship",
                            "League One",
                            "League Two"
                        ]
                    },
                    "analysis_date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format."
                    }
                },
                "required": [
                    "team",
                    "league",
                    "analysis_date"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_team_profile",
            "description": (
                "Retrieve the statistical profile of a football team "
                "including attacking, defensive, home, and away metrics."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "team": {
                        "type": "string",
                        "description": "The football team to analyse."
                    },
                    "league": {
                        "type": "string",
                        "enum": [
                            "Premier League",
                            "Championship",
                            "League One",
                            "League Two"
                        ],
                        "description": "The league containing the team."
                    },
                    "analysis_date": {
                        "type": "string",
                        "description": (
                            "The date up to which matches should be analysed "
                            "in YYYY-MM-DD format."
                        )
                    }
                },
                "required": [
                    "team",
                    "league",
                    "analysis_date"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_league_table",
            "description": (
                "Return the league table for a specified league "
                "and analysis date."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "league": {
                        "type": "string",
                        "enum": [
                            "Premier League",
                            "Championship",
                            "League One",
                            "League Two",
                        ],
                    },
                    "analysis_date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format.",
                    },
                },
                "required": [
                    "league",
                    "analysis_date",
                ],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_team_at_position",
            "description": "Compare the team occupying a specified league position with another team.",
            "parameters": {
                "type": "object",
                "properties": {
                    "league": {
                        "type": "string"
                    },
                    "position": {
                        "type": "integer"
                    },
                    "opponent": {
                        "type": "string"
                    },
                    "analysis_date": {
                        "type": "string"
                    }
                },
                "required": [
                    "league",
                    "position",
                    "opponent",
                    "analysis_date"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_metric_rankings",
            "description": (
                "Rank teams within a league using a supported performance "
                "metric. Use this for questions about the best attack, best "
                "defence, most shots, best recent form, highest points total "
                "or similar league-wide rankings."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "league": {
                        "type": "string",
                        "description": (
                            "The league to analyse, for example Premier League."
                        ),
                    },
                    "metric": {
                        "type": "string",
                        "enum": [
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
                        ],
                        "description": (
                            "The performance metric used to rank the teams."
                        ),
                    },
                    "analysis_date": {
                        "type": "string",
                        "description": (
                            "The analysis cut-off date in YYYY-MM-DD format."
                        ),
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 20,
                        "description": (
                            "Maximum number of teams to return. Defaults to 5."
                        ),
                    },
                },
                "required": [
                    "league",
                    "metric",
                    "analysis_date",
                ],
                "additionalProperties": False,
            },
        },
    },
    
]