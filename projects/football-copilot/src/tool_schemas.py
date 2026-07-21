analyse_team_fixture_tool = {
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
}

tools = [
    analyse_team_fixture_tool
]