import matplotlib.pyplot as plt
import pandas as pd

from src.visualizations import (
    feedback_wordcloud,
    option_bar_chart,
    option_donut_chart,
    save_visualizations,
)


def test_charts_handle_empty_data_and_create_saved_pngs(tmp_path):
    empty = pd.DataFrame(columns=["Response_ID", "Question", "Selected_Option"])
    bar = option_bar_chart(empty)
    donut = option_donut_chart(empty)
    assert bar.axes and donut.axes
    plt.close(bar)
    plt.close(donut)

    data = pd.DataFrame(
        {
            "Response_ID": ["1", "2", "3"],
            "Question": ["Q", "Q", "Q"],
            "Selected_Option": ["A", "A", "B"],
            "Satisfaction_Rating": [3, 4, 5],
            "Timestamp": ["2025-01-01", "2025-01-02", "2025-01-03"],
            "Region": ["North", "South", "North"],
            "Age_Group": ["18-24", "25-34", "18-24"],
            "Gender": ["Female", "Male", "Female"],
            "Feedback": ["Helpful charts", "clear examples", "nice tool"],
        }
    )
    paths = save_visualizations(data, tmp_path)
    assert {"option_bar", "option_donut", "rating_distribution", "region_comparison"} <= set(paths)
    assert all(path.is_file() and path.stat().st_size > 0 for path in paths.values())


def test_wordcloud_handles_missing_feedback():
    figure = feedback_wordcloud(pd.DataFrame({"Response_ID": ["1"]}))
    assert figure.axes
    plt.close(figure)
