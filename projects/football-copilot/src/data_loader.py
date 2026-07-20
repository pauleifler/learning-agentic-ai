import pandas as pd
from pathlib import Path

from config import (
    COLUMN_MAP,
    LEAGUE_NAMES,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIRECTORY = PROJECT_ROOT / "data"

def load_match_data(
    data_directory: Path = DATA_DIRECTORY,
) -> pd.DataFrame:
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

