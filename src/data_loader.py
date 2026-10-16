"""CSV loading and validation helpers."""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = ("Response_ID", "Question", "Selected_Option")


def validate_columns(
    data: pd.DataFrame, required_columns: tuple[str, ...] = REQUIRED_COLUMNS
) -> None:
    """Raise a helpful error listing required columns absent from ``data``."""
    missing = [column for column in required_columns if column not in data.columns]
    if missing:
        required = ", ".join(required_columns)
        raise ValueError(
            f"CSV is missing required column(s): {', '.join(missing)}. "
            f"Include these required columns: {required}."
        )


def load_csv(path: str | Path) -> pd.DataFrame:
    """Read a CSV, rejecting missing paths, non-CSV files, and invalid schemas."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"CSV file not found: {source}")
    if source.suffix.lower() != ".csv":
        raise ValueError("The input file must have a .csv extension.")
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except pd.errors.EmptyDataError as error:
        raise ValueError("The CSV file is empty or has no column headers.") from error
    except (UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Could not read this CSV file: {error}") from error
    validate_columns(data)
    return data
