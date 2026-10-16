"""Descriptive statistics and per-question poll summaries."""

import pandas as pd

from src.data_loader import REQUIRED_COLUMNS, validate_columns


def _group_counts(data: pd.DataFrame, column: str) -> pd.DataFrame:
    if column not in data.columns:
        return pd.DataFrame(columns=[column, "Response_Count"])
    counts = (
        data[column]
        .dropna()
        .value_counts()
        .rename_axis(column)
        .reset_index(name="Response_Count")
    )
    return counts


def option_summary(
    data: pd.DataFrame, question: str | None = None
) -> pd.DataFrame:
    """Calculate each option's count and share within its own poll question."""
    validate_columns(data)
    valid = data.dropna(subset=["Question", "Selected_Option"]).copy()
    if question is not None:
        valid = valid.loc[valid["Question"].eq(question)]
    columns = ["Question", "Selected_Option", "Response_Count", "Percentage"]
    if valid.empty:
        return pd.DataFrame(columns=columns)
    counts = (
        valid.groupby(["Question", "Selected_Option"], dropna=False)
        .size()
        .rename("Response_Count")
        .reset_index()
    )
    denominator = counts.groupby("Question")["Response_Count"].transform("sum")
    counts["Percentage"] = counts["Response_Count"].div(denominator).mul(100)
    return counts[columns].sort_values(
        ["Question", "Response_Count", "Selected_Option"],
        ascending=[True, False, True],
    ).reset_index(drop=True)


def summarize_data(data: pd.DataFrame) -> dict:
    """Return descriptive metrics and optional-column summaries for ``data``."""
    validate_columns(data)
    valid_poll_responses = data.dropna(subset=["Question", "Selected_Option"])
    rating_values = (
        pd.to_numeric(data["Satisfaction_Rating"], errors="coerce").dropna()
        if "Satisfaction_Rating" in data.columns
        else pd.Series(dtype=float)
    )
    result = {
        "total_responses": len(data),
        "valid_poll_responses": len(valid_poll_responses),
        "unique_questions": int(data["Question"].nunique(dropna=True)),
        "unique_options": int(data["Selected_Option"].nunique(dropna=True)),
        "missing_values": data.isna().sum().astype(int).to_dict(),
        "duplicate_records": int(data.duplicated().sum()),
        "option_summary": option_summary(data),
        "average_satisfaction": (
            float(rating_values.mean()) if not rating_values.empty else None
        ),
        "rating_distribution": _group_counts(
            data.assign(
                Satisfaction_Rating=(
                    pd.to_numeric(data["Satisfaction_Rating"], errors="coerce")
                    if "Satisfaction_Rating" in data.columns
                    else pd.Series(index=data.index, dtype=float)
                )
            ),
            "Satisfaction_Rating",
        ),
        "region_counts": _group_counts(data, "Region"),
        "age_group_counts": _group_counts(data, "Age_Group"),
        "gender_counts": _group_counts(data, "Gender"),
        "responses_over_time": _responses_over_time(data),
        "feedback_length_stats": _feedback_length_stats(data),
    }
    return result


def _responses_over_time(data: pd.DataFrame) -> pd.DataFrame:
    if "Timestamp" not in data.columns:
        return pd.DataFrame(columns=["Date", "Response_Count"])
    timestamps = pd.to_datetime(data["Timestamp"], errors="coerce", utc=True)
    valid = timestamps.dropna().dt.floor("D")
    return (
        valid.value_counts()
        .sort_index()
        .rename_axis("Date")
        .reset_index(name="Response_Count")
    )


def _feedback_length_stats(data: pd.DataFrame) -> dict | None:
    if "Feedback" not in data.columns:
        return None
    lengths = data["Feedback"].dropna().astype(str).str.len()
    if lengths.empty:
        return {"responses_with_feedback": 0, "mean_characters": None, "median_characters": None}
    return {
        "responses_with_feedback": int(len(lengths)),
        "mean_characters": float(lengths.mean()),
        "median_characters": float(lengths.median()),
    }
