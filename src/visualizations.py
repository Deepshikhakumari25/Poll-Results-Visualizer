"""Labeled matplotlib charts that can be embedded or saved as PNG files."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

from src.analysis import option_summary


PALETTE = ("#2E6F95", "#52A675", "#F2A541", "#8E6CBE", "#D66A6A", "#58A6A6")


def _empty_figure(title: str, message: str = "No valid data available.") -> plt.Figure:
    figure, axis = plt.subplots(figsize=(8, 4.5))
    axis.set_title(title, fontsize=14, fontweight="bold")
    axis.text(0.5, 0.5, message, ha="center", va="center", transform=axis.transAxes)
    axis.set_axis_off()
    figure.tight_layout()
    return figure


def _categorical_bar(
    data: pd.DataFrame, column: str, title: str
) -> plt.Figure:
    if column not in data.columns:
        return _empty_figure(title, f"{column} is not available in this dataset.")
    counts = data[column].dropna().value_counts().sort_values(ascending=False)
    if counts.empty:
        return _empty_figure(title)
    figure, axis = plt.subplots(figsize=(8, 4.5))
    colors = [PALETTE[index % len(PALETTE)] for index in range(len(counts))]
    counts.plot.bar(ax=axis, color=colors)
    axis.set(title=title, xlabel=column.replace("_", " "), ylabel="Responses")
    axis.tick_params(axis="x", labelrotation=25)
    axis.grid(axis="y", alpha=0.2)
    figure.tight_layout()
    return figure


def category_bar_chart(data: pd.DataFrame, column: str, title: str) -> plt.Figure:
    """Create a categorical response-count chart for any available field."""
    return _categorical_bar(data, column, title)


def option_bar_chart(data: pd.DataFrame, question: str | None = None) -> plt.Figure:
    summary = option_summary(data, question)
    if summary.empty:
        return _empty_figure("Responses by poll option")
    if question is None:
        question = str(summary.iloc[0]["Question"])
    selected = summary.loc[summary["Question"].eq(question)]
    if selected.empty:
        return _empty_figure("Responses by poll option", "No responses for this question.")
    figure, axis = plt.subplots(figsize=(8, 4.5))
    colors = [PALETTE[index % len(PALETTE)] for index in range(len(selected))]
    bars = axis.bar(
        selected["Selected_Option"],
        selected["Response_Count"],
        color=colors,
    )
    axis.bar_label(bars, padding=3)
    axis.set(
        title=f"Responses by option: {question}",
        xlabel="Selected option",
        ylabel="Responses",
    )
    axis.grid(axis="y", alpha=0.2)
    figure.tight_layout()
    return figure


def option_donut_chart(data: pd.DataFrame, question: str | None = None) -> plt.Figure:
    summary = option_summary(data, question)
    if summary.empty:
        return _empty_figure("Share of poll options")
    if question is None:
        question = str(summary.iloc[0]["Question"])
    selected = summary.loc[summary["Question"].eq(question)]
    if selected.empty:
        return _empty_figure("Share of poll options", "No responses for this question.")
    figure, axis = plt.subplots(figsize=(7, 5))
    colors = [PALETTE[index % len(PALETTE)] for index in range(len(selected))]
    axis.pie(
        selected["Response_Count"],
        labels=selected["Selected_Option"],
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        wedgeprops={"width": 0.48, "edgecolor": "white"},
    )
    axis.set_title(f"Share of options: {question}", fontsize=13)
    figure.tight_layout()
    return figure


def rating_chart(data: pd.DataFrame) -> plt.Figure:
    if "Satisfaction_Rating" not in data.columns:
        return _empty_figure(
            "Satisfaction rating distribution",
            "Satisfaction_Rating is not available in this dataset.",
        )
    ratings = pd.to_numeric(data["Satisfaction_Rating"], errors="coerce").dropna()
    if ratings.empty:
        return _empty_figure("Satisfaction rating distribution")
    counts = ratings.value_counts().sort_index()
    figure, axis = plt.subplots(figsize=(7, 4.5))
    bars = axis.bar(counts.index.astype(str), counts.values, color="#52A675")
    axis.bar_label(bars, padding=3)
    axis.set(
        title="Satisfaction rating distribution",
        xlabel="Rating (1 = low, 5 = high)",
        ylabel="Responses",
    )
    axis.grid(axis="y", alpha=0.2)
    figure.tight_layout()
    return figure


def time_chart(data: pd.DataFrame) -> plt.Figure:
    if "Timestamp" not in data.columns:
        return _empty_figure("Responses over time", "Timestamp is not available.")
    dates = pd.to_datetime(data["Timestamp"], errors="coerce", utc=True).dropna()
    if dates.empty:
        return _empty_figure("Responses over time")
    counts = dates.dt.floor("D").value_counts().sort_index()
    figure, axis = plt.subplots(figsize=(9, 4.5))
    axis.plot(counts.index, counts.values, color="#2E6F95", marker="o", linewidth=1.7)
    axis.set(title="Recorded responses over time", xlabel="Date", ylabel="Responses")
    axis.tick_params(axis="x", rotation=25)
    axis.grid(alpha=0.2)
    figure.tight_layout()
    return figure


def feedback_wordcloud(data: pd.DataFrame) -> plt.Figure:
    if "Feedback" not in data.columns:
        return _empty_figure("Feedback word cloud", "Feedback is not available.")
    text = " ".join(data["Feedback"].dropna().astype(str).tolist()).strip()
    if not text:
        return _empty_figure("Feedback word cloud", "No written feedback is available.")
    cloud = WordCloud(
        width=1000, height=480, background_color="white", colormap="viridis",
        collocations=False, random_state=42,
    ).generate(text)
    figure, axis = plt.subplots(figsize=(9, 4.5))
    axis.imshow(cloud, interpolation="bilinear")
    axis.set_title("Words appearing in written feedback", fontsize=13)
    axis.set_axis_off()
    figure.tight_layout()
    return figure


def feedback_rating_chart(data: pd.DataFrame) -> plt.Figure:
    required = ("Feedback", "Satisfaction_Rating")
    if any(column not in data.columns for column in required):
        return _empty_figure(
            "Feedback length vs. satisfaction",
            "Feedback and Satisfaction_Rating are both required.",
        )
    chart_data = data.loc[:, required].dropna().copy()
    chart_data["Satisfaction_Rating"] = pd.to_numeric(
        chart_data["Satisfaction_Rating"], errors="coerce"
    )
    chart_data["Feedback_Length"] = chart_data["Feedback"].astype(str).str.len()
    chart_data = chart_data.dropna(subset=["Satisfaction_Rating"])
    if chart_data.empty:
        return _empty_figure("Feedback length vs. satisfaction")
    figure, axis = plt.subplots(figsize=(7, 4.5))
    axis.scatter(
        chart_data["Feedback_Length"],
        chart_data["Satisfaction_Rating"],
        alpha=0.55,
        color="#8E6CBE",
    )
    axis.set(
        title="Feedback length vs. satisfaction (descriptive only)",
        xlabel="Feedback length (characters)",
        ylabel="Satisfaction rating",
    )
    axis.grid(alpha=0.2)
    figure.tight_layout()
    return figure


def save_visualizations(
    data: pd.DataFrame, output_dir: str | Path, question: str | None = None
) -> dict[str, Path]:
    """Save available charts as PNGs and return their paths by chart name."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    charts = {
        "option_bar": option_bar_chart(data, question),
        "option_donut": option_donut_chart(data, question),
    }
    if "Satisfaction_Rating" in data.columns:
        charts["rating_distribution"] = rating_chart(data)
    if "Timestamp" in data.columns:
        charts["responses_over_time"] = time_chart(data)
    for column, name, title in (
        ("Region", "region_comparison", "Responses by region"),
        ("Age_Group", "age_group_comparison", "Responses by age group"),
        ("Gender", "gender_comparison", "Responses by gender category"),
    ):
        if column in data.columns:
            charts[name] = _categorical_bar(data, column, title)
    if "Feedback" in data.columns:
        charts["feedback_wordcloud"] = feedback_wordcloud(data)
    if {"Feedback", "Satisfaction_Rating"}.issubset(data.columns):
        charts["feedback_vs_satisfaction"] = feedback_rating_chart(data)

    paths = {}
    for name, figure in charts.items():
        path = destination / f"{name}.png"
        figure.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(figure)
        paths[name] = path
    return paths
