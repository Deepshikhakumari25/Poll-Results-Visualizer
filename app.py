"""Interactive Streamlit dashboard for exploratory poll analysis."""

from pathlib import Path

import pandas as pd
import streamlit as st

from src.analysis import option_summary, summarize_data
from src.data_cleaning import clean_data
from src.data_generator import DEFAULT_SEED, DEFAULT_SAMPLE_SIZE, SAMPLE_DATA_PATH, save_synthetic_data
from src.data_loader import load_csv
from src.insights import generate_insights
from src.visualizations import (
    category_bar_chart,
    feedback_rating_chart,
    feedback_wordcloud,
    option_bar_chart,
    option_donut_chart,
    rating_chart,
    save_visualizations,
    time_chart,
)


st.set_page_config(page_title="Poll Results Visualizer", page_icon="📊", layout="wide")
st.title("Poll Results Visualizer")
st.caption(
    "Explore, clean, and summarize poll responses. Results describe only the data "
    "you load; they do not estimate wider population opinion."
)

with st.sidebar:
    st.header("Data source")
    source_choice = st.radio("Choose a dataset", ("Built-in sample", "Upload a CSV"))
    uploaded_file = None
    if source_choice == "Upload a CSV":
        uploaded_file = st.file_uploader("Upload poll responses (.csv)", type=["csv"])

try:
    if source_choice == "Built-in sample":
        sample_path = save_synthetic_data(SAMPLE_DATA_PATH, DEFAULT_SAMPLE_SIZE, DEFAULT_SEED)
        raw_data = load_csv(sample_path)
        st.info(
            "Built-in data is synthetic and fictional (1,000 reproducible responses); "
            "it is not real-world polling."
        )
    elif uploaded_file is not None:
        raw_data = pd.read_csv(uploaded_file)
    else:
        st.info("Upload a CSV to explore it. Required columns: Response_ID, Question, Selected_Option.")
        st.stop()

    cleaned_data, quality = clean_data(raw_data)
except (ValueError, FileNotFoundError, pd.errors.ParserError, UnicodeDecodeError) as error:
    st.error(f"Could not load or clean this dataset: {error}")
    st.info(
        "Provide a readable CSV with Response_ID, Question, and Selected_Option columns. "
        "Optional columns include Timestamp, Region, Age_Group, Gender, "
        "Satisfaction_Rating, and Feedback."
    )
    st.stop()

with st.sidebar:
    st.header("Filters")
    available_questions = cleaned_data["Question"].dropna().unique().tolist()
    selected_question = None
    if available_questions:
        selected_question = st.selectbox("Poll question", available_questions)

    filtered = cleaned_data.copy()
    if selected_question is not None:
        filtered = filtered.loc[filtered["Question"].eq(selected_question)]

    for column, label in (("Region", "Region"), ("Age_Group", "Age group"), ("Gender", "Gender")):
        if column in filtered.columns:
            choices = sorted(filtered[column].dropna().astype(str).unique().tolist())
            selected_values = st.multiselect(label, choices, default=choices)
            if len(selected_values) != len(choices):
                filtered = filtered.loc[filtered[column].astype(str).isin(selected_values)]

    if "Timestamp" in filtered.columns:
        valid_dates = pd.to_datetime(filtered["Timestamp"], errors="coerce", utc=True).dropna()
        if not valid_dates.empty:
            minimum, maximum = valid_dates.min().date(), valid_dates.max().date()
            date_range = st.date_input("Date range", value=(minimum, maximum))
            if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
                start_date, end_date = date_range
                parsed = pd.to_datetime(filtered["Timestamp"], errors="coerce", utc=True)
                keep = parsed.dt.date.between(start_date, end_date)
                filtered = filtered.loc[keep.fillna(False)]

st.subheader("Summary")
metrics = summarize_data(filtered)
first, second, third, fourth = st.columns(4)
first.metric("Valid responses", f"{metrics['valid_poll_responses']:,}")
second.metric("Poll questions", f"{metrics['unique_questions']:,}")
third.metric("Available options", f"{metrics['unique_options']:,}")
fourth.metric(
    "Average satisfaction",
    f"{metrics['average_satisfaction']:.2f} / 5"
    if metrics["average_satisfaction"] is not None
    else "Not available",
)

st.subheader("Poll results")
if selected_question is not None:
    left, right = st.columns(2)
    with left:
        st.pyplot(option_bar_chart(filtered, selected_question), width="stretch")
    with right:
        st.pyplot(option_donut_chart(filtered, selected_question), width="stretch")
else:
    st.info("No valid question is available for a poll-options chart.")

st.subheader("Response patterns")
optional_charts = []
if "Satisfaction_Rating" in filtered.columns:
    optional_charts.append(("Satisfaction", rating_chart(filtered)))
if "Region" in filtered.columns:
    optional_charts.append(("Region", None))
if "Age_Group" in filtered.columns:
    optional_charts.append(("Age group", None))
if "Gender" in filtered.columns:
    optional_charts.append(("Gender", None))
if "Timestamp" in filtered.columns:
    optional_charts.append(("Time trend", time_chart(filtered)))

chart_functions = {
    "Region": ("Region", "Responses by region"),
    "Age group": ("Age_Group", "Responses by age group"),
    "Gender": ("Gender", "Responses by gender category"),
}
for index in range(0, len(optional_charts), 2):
    columns = st.columns(2)
    for column, item in zip(columns, optional_charts[index : index + 2]):
        label, figure = item
        if figure is None:
            data_column, title = chart_functions[label]
            figure = category_bar_chart(filtered, data_column, title)
        with column:
            st.pyplot(figure, width="stretch")

if "Feedback" in filtered.columns:
    st.subheader("Written feedback (descriptive)")
    left, right = st.columns(2)
    with left:
        st.pyplot(feedback_wordcloud(filtered), width="stretch")
    if "Satisfaction_Rating" in filtered.columns:
        with right:
            st.pyplot(feedback_rating_chart(filtered), width="stretch")
    st.caption("A word cloud shows word frequency only; it does not measure sentiment.")

st.subheader("Data quality")
st.write(
    f"Input rows: **{quality['input_rows']:,}** · "
    f"Cleaned rows: **{quality['output_rows']:,}** · "
    f"Removed rows: **{quality['input_rows'] - quality['output_rows']:,}** · "
    f"Invalid ratings set to missing: **{quality['invalid_ratings_set_to_missing']:,}** · "
    f"Invalid timestamps set to missing: **{quality['invalid_timestamps_set_to_missing']:,}**"
)
with st.expander("Missing values before cleaning"):
    st.dataframe(
        pd.DataFrame(
            {"Column": quality["missing_values_before"].keys(),
             "Missing": quality["missing_values_before"].values()},
        ),
        hide_index=True,
        width="stretch",
    )

st.subheader("Generated insights")
for insight in generate_insights(filtered):
    st.markdown(f"- {insight}")

st.subheader("Response data")
with st.expander("Cleaned data preview", expanded=True):
    st.dataframe(filtered.head(50), hide_index=True, width="stretch")
    st.caption(f"Showing up to 50 of {len(filtered):,} filtered cleaned records.")

st.subheader("Downloads")
download_left, download_right = st.columns(2)
download_left.download_button(
    "Download filtered cleaned CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="cleaned_poll_responses.csv",
    mime="text/csv",
)
download_right.download_button(
    "Download option summary CSV",
    data=option_summary(filtered).to_csv(index=False).encode("utf-8"),
    file_name="poll_option_summary.csv",
    mime="text/csv",
)
report_text = "\n".join(f"- {insight}" for insight in generate_insights(filtered))
st.download_button(
    "Download insights report",
    data=report_text,
    file_name="poll_insights.txt",
    mime="text/plain",
)

if st.button("Save filtered charts to outputs/charts"):
    saved = save_visualizations(filtered, Path("outputs") / "charts", selected_question)
    st.success(f"Saved {len(saved)} charts to outputs/charts.")
