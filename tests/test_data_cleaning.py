import pandas as pd
import pytest

from src.data_cleaning import clean_data
from src.data_loader import load_csv


def sample_data():
    return pd.DataFrame(
        {
            "Response_ID": ["1", "2", "2", "3", "4"],
            "Question": [" Tool? ", "Tool?", "Tool?", "Tool?", "Tool?"],
            "Selected_Option": [" python  ", "SQL", "SQL", "Excel", "Python"],
            "Timestamp": ["2025-01-01", "invalid", "invalid", "2025-01-02", "2025-01-03"],
            "Satisfaction_Rating": ["5", "9", "9", "not a rating", "4"],
            "Region": [" north ", "South", "South", "East", "west"],
            "Feedback": [" good ", "", "", "fine", "nice"],
        }
    )


def test_cleaning_standardizes_categories_deduplicates_and_validates_ratings():
    cleaned, report = clean_data(sample_data())
    assert cleaned["Selected_Option"].tolist() == ["Python", "SQL", "Excel", "Python"]
    assert cleaned["Region"].tolist() == ["North", "South", "East", "West"]
    assert cleaned["Satisfaction_Rating"].iloc[0] == 5
    assert pd.isna(cleaned["Satisfaction_Rating"].iloc[1])
    assert report["removed_exact_duplicates"] == 1
    assert report["duplicate_response_ids_detected_before_cleaning"] == 1
    assert report["invalid_ratings_set_to_missing"] == 2
    assert report["invalid_timestamps_set_to_missing"] == 1
    assert pd.isna(cleaned.loc[0, "Feedback"]) is False


def test_rows_missing_required_values_are_removed_and_optional_columns_can_be_absent():
    source = pd.DataFrame(
        {
            "Response_ID": ["1", None, "3"],
            "Question": ["Q", "Q", "Q"],
            "Selected_Option": ["A", "B", "  "],
        }
    )
    cleaned, report = clean_data(source)
    assert len(cleaned) == 1
    assert cleaned.loc[0, "Response_ID"] == "1"
    assert report["removed_invalid_required_rows"] == 2


def test_csv_loader_reads_csv_and_explains_missing_required_columns(tmp_path):
    source = tmp_path / "valid.csv"
    sample_data().to_csv(source, index=False)
    assert len(load_csv(source)) == 5

    invalid = tmp_path / "invalid.csv"
    pd.DataFrame({"other": [1]}).to_csv(invalid, index=False)
    with pytest.raises(ValueError, match="missing required"):
        load_csv(invalid)


def test_csv_loader_rejects_missing_and_non_csv_paths(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_csv(tmp_path / "missing.csv")
    text_file = tmp_path / "input.txt"
    text_file.write_text("not a csv", encoding="utf-8")
    with pytest.raises(ValueError, match=".csv"):
        load_csv(text_file)
