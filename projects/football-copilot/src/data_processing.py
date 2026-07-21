import pandas as pd


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

