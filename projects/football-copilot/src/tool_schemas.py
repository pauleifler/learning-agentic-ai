tools = [
    {
        "type": "function",
        "function": {
            "name": "analyse_team_fixture",
            "description": (
                "Analyse a football team's upcoming fixture "
                "and return structured opposition analysis."
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
                        "description": "The league the team plays in."
                    },
                    "analysis_date": {
                        "type": "string",
                        "description": (
                            "The date the analysis should be based on."
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
}
]