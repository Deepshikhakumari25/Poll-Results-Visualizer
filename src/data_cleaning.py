"""Input cleaning with an auditable summary of changed and removed records."""

import pandas as pd

from src.data_loader import REQUIRED_COLUMNS, validate_columns


CATEGORY_COLUMNS = ("Question", "Selected_Option", "Age_Group", "Gender", "Region")


def _normalize_category(series: pd.Series, column: str) -> pd.Series:
    values = series.astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    values = values.mask(values.eq(""))
    canonical = {}
    if column == "Selected_Option":
        canonical = {name.casefold(): name for name in ("Python", "SQL", "Excel", "Power BI", "Tableau")}
    elif column == "Gender":
        canonical = {
            name.casefold(): name
            for name in ("Female", "Male", "Non-binary", "Prefer not to say")
        }
    elif column == "Region":
        canonical = {
            name.casefold(): name
            for name in ("North", "South", "East", "West", "Central")
        }

    first_seen = {}
    for value in values.dropna():
        key = value.casefold()
        first_seen.setdefault(key, canonical.get(key, value))
    return values.map(
        lambda value: first_seen.get(value.casefold(), pd.NA)
        if pd.notna(value)
        else pd.NA
    )


def clean_data(data: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean poll data and return it with a record of quality issues/actions."""
    validate_columns(data)
    cleaned = data.copy()
    original_rows = len(cleaned)
    missing_before = cleaned.isna().sum().astype(int).to_dict()
    exact_duplicates = int(cleaned.duplicated().sum())
    duplicate_ids = (
        int(cleaned["Response_ID"].dropna().duplicated().sum())
        if "Response_ID" in cleaned.columns
        else 0
    )

    for column in CATEGORY_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = _normalize_category(cleaned[column], column)

    for column in REQUIRED_COLUMNS:
        cleaned[column] = cleaned[column].astype("string").str.strip()
    missing_required = cleaned[list(REQUIRED_COLUMNS)].isna().any(axis=1)
    blank_required = cleaned[list(REQUIRED_COLUMNS)].apply(
        lambda column: column.eq("").fillna(False)
    ).any(axis=1)
    invalid_required_rows = int((missing_required | blank_required).sum())
    cleaned = cleaned.loc[~(missing_required | blank_required)].copy()

    before_exact = len(cleaned)
    cleaned = cleaned.drop_duplicates(keep="first")
    removed_exact = before_exact - len(cleaned)

    before_ids = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=["Response_ID"], keep="first")
    removed_duplicate_ids = before_ids - len(cleaned)

    invalid_ratings = 0
    if "Satisfaction_Rating" in cleaned.columns:
        original_ratings = cleaned["Satisfaction_Rating"]
        numeric_ratings = pd.to_numeric(original_ratings, errors="coerce")
        invalid_rating_mask = numeric_ratings.notna() & ~numeric_ratings.between(1, 5)
        originally_missing = original_ratings.isna() | original_ratings.astype(
            "string"
        ).str.strip().eq("")
        invalid_text_mask = numeric_ratings.isna() & ~originally_missing
        invalid_ratings = int((invalid_text_mask | invalid_rating_mask).sum())
        cleaned["Satisfaction_Rating"] = numeric_ratings.where(
            numeric_ratings.between(1, 5)
        )

    invalid_timestamps = 0
    if "Timestamp" in cleaned.columns:
        parsed = pd.to_datetime(cleaned["Timestamp"], errors="coerce", utc=True)
        invalid_timestamps = int((cleaned["Timestamp"].notna() & parsed.isna()).sum())
        cleaned["Timestamp"] = parsed

    if "Feedback" in cleaned.columns:
        feedback = cleaned["Feedback"].astype("string").str.strip()
        cleaned["Feedback"] = feedback.mask(feedback.eq(""), pd.NA)

    cleaned = cleaned.reset_index(drop=True)
    summary = {
        "input_rows": original_rows,
        "output_rows": len(cleaned),
        "removed_invalid_required_rows": invalid_required_rows,
        "removed_exact_duplicates": removed_exact,
        "removed_duplicate_response_ids": removed_duplicate_ids,
        "exact_duplicates_detected_before_cleaning": exact_duplicates,
        "duplicate_response_ids_detected_before_cleaning": duplicate_ids,
        "invalid_ratings_set_to_missing": invalid_ratings,
        "invalid_timestamps_set_to_missing": invalid_timestamps,
        "missing_values_before": missing_before,
        "missing_values_after": cleaned.isna().sum().astype(int).to_dict(),
    }
    return cleaned, summary
