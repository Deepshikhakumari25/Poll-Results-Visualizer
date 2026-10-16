import math

import pandas as pd

from src.analysis import option_summary, summarize_data
from src.insights import generate_insights, save_insight_report


def test_option_counts_and_percentages_are_calculated_per_question():
    data = pd.DataFrame(
        {
            "Response_ID": ["1", "2", "3", "4", "5"],
            "Question": ["Q1", "Q1", "Q1", "Q2", "Q2"],
            "Selected_Option": ["A", "A", "B", "X", "Y"],
        }
    )
    summary = option_summary(data)
    q1 = summary.loc[summary["Question"].eq("Q1")]
    q2 = summary.loc[summary["Question"].eq("Q2")]
    assert math.isclose(q1["Percentage"].sum(), 100)
    assert math.isclose(q2["Percentage"].sum(), 100)
    assert q1.set_index("Selected_Option").loc["A", "Response_Count"] == 2
    assert math.isclose(
        q1.set_index("Selected_Option").loc["A", "Percentage"], 200 / 3
    )


def test_summary_handles_missing_optional_columns_and_empty_dataset():
    empty = pd.DataFrame(columns=["Response_ID", "Question", "Selected_Option"])
    result = summarize_data(empty)
    assert result["total_responses"] == 0
    assert result["average_satisfaction"] is None
    assert result["region_counts"].empty
    assert option_summary(empty).empty
    assert generate_insights(empty)[0].startswith("This dataset contains 0")


def test_insight_report_uses_actual_counts_and_is_saved(tmp_path):
    data = pd.DataFrame(
        {
            "Response_ID": ["1", "2", "3"],
            "Question": ["Q", "Q", "Q"],
            "Selected_Option": ["Actual leader", "Actual leader", "Other"],
            "Satisfaction_Rating": [4, 5, 3],
            "Region": ["North", "North", "South"],
        }
    )
    insights = generate_insights(data)
    assert any("Actual leader" in line and "66.7%" in line for line in insights)
    assert any("3 valid poll responses" in line for line in insights)
    report = save_insight_report(data, tmp_path / "reports" / "insights.txt")
    assert report.is_file()
    assert "Actual leader" in report.read_text(encoding="utf-8")
