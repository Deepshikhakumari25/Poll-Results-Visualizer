"""Plain-language insights grounded in the current dataset's calculated values."""

from pathlib import Path

from src.analysis import option_summary, summarize_data


def generate_insights(data) -> list[str]:
    """Describe observed response counts without implying population inference."""
    summary = summarize_data(data)
    insights = [
        (
            f"This dataset contains {summary['valid_poll_responses']:,} valid poll "
            f"responses across {summary['unique_questions']:,} question(s)."
        ),
        "These are recorded responses in this dataset, not estimates of wider public opinion.",
    ]
    options = option_summary(data)
    if not options.empty:
        for question, group in options.groupby("Question", sort=False):
            ranked = group.sort_values(
                ["Response_Count", "Selected_Option"], ascending=[False, True]
            )
            first = ranked.iloc[0]
            last = ranked.iloc[-1]
            insights.append(
                f'For "{question}", {first["Selected_Option"]} received the most '
                f"responses ({int(first['Response_Count']):,}; "
                f"{first['Percentage']:.1f}% of {int(group['Response_Count'].sum()):,} "
                "valid answers)."
            )
            if len(ranked) > 1:
                insights.append(
                    f'{last["Selected_Option"]} received the fewest responses '
                    f"({int(last['Response_Count']):,}; {last['Percentage']:.1f}%)."
                )
    if summary["average_satisfaction"] is not None:
        insights.append(
            f"Mean satisfaction rating: {summary['average_satisfaction']:.2f} "
            "out of 5 across records with a valid rating."
        )
    regions = summary["region_counts"]
    if not regions.empty:
        leaders = regions.loc[regions["Response_Count"].eq(regions["Response_Count"].max())]
        names = ", ".join(leaders["Region"].astype(str))
        insights.append(
            f"{names} recorded the most responses ({int(regions['Response_Count'].max()):,}); "
            "response volume does not establish regional preference."
        )
    if not summary["valid_poll_responses"]:
        insights.append("No valid question-and-option pairs are available for comparison.")
    return insights


def save_insight_report(data, path: str | Path) -> Path:
    """Write a fresh, dated-data-independent text report and return its path."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Poll Results Visualizer — Descriptive Insights",
        "=" * 48,
        "Dataset results are descriptive and apply only to the loaded responses.",
        "Synthetic sample responses, when used, are fictional and not population estimates.",
        "",
    ]
    lines.extend(f"- {insight}" for insight in generate_insights(data))
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return destination
