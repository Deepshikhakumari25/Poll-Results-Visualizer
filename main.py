"""Run the independent command-line analysis pipeline."""

import argparse
import json
from pathlib import Path

from src.analysis import option_summary, summarize_data
from src.data_cleaning import clean_data
from src.data_generator import DEFAULT_SAMPLE_SIZE, DEFAULT_SEED, SAMPLE_DATA_PATH, save_synthetic_data
from src.data_loader import load_csv
from src.insights import generate_insights, save_insight_report
from src.visualizations import save_visualizations


def run_pipeline(
    input_path: str | Path | None = None,
    output_dir: str | Path = "outputs",
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    seed: int = DEFAULT_SEED,
) -> dict:
    """Load or generate responses and save cleaned data, summaries, charts, and insights."""
    if input_path is None:
        source = save_synthetic_data(SAMPLE_DATA_PATH, sample_size, seed)
        print(f"Generated {sample_size:,} synthetic responses: {source}")
    else:
        source = Path(input_path)

    raw = load_csv(source)
    cleaned, quality = clean_data(raw)
    root = Path(output_dir)
    cleaned_dir = root / "cleaned_data"
    reports_dir = root / "reports"
    charts_dir = root / "charts"
    cleaned_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    cleaned_path = cleaned_dir / "cleaned_poll_responses.csv"
    cleaned.to_csv(cleaned_path, index=False)
    options_path = reports_dir / "option_summary.csv"
    option_summary(cleaned).to_csv(options_path, index=False)
    summary = summarize_data(cleaned)
    quality_path = reports_dir / "data_quality.json"
    quality_path.write_text(json.dumps(quality, indent=2, default=str), encoding="utf-8")
    report_path = save_insight_report(cleaned, reports_dir / "insights.txt")
    charts = save_visualizations(cleaned, charts_dir)

    print(f"Valid responses: {summary['valid_poll_responses']:,}")
    print(f"Questions: {summary['unique_questions']:,}")
    print(f"Removed rows: {quality['input_rows'] - quality['output_rows']:,}")
    print(f"Cleaned CSV: {cleaned_path}")
    print(f"Option summary: {options_path}")
    print(f"Quality report: {quality_path}")
    print(f"Insight report: {report_path}")
    print(f"Charts generated: {len(charts)} ({charts_dir})")
    for insight in generate_insights(cleaned):
        print(f"- {insight}")
    return {
        "source": source,
        "cleaned_data": cleaned_path,
        "option_summary": options_path,
        "quality_report": quality_path,
        "insight_report": report_path,
        "charts": charts,
        "quality": quality,
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean, analyze, and visualize illustrative or user-provided poll data."
    )
    parser.add_argument("--input", type=Path, help="Use an existing input CSV.")
    parser.add_argument(
        "--output-dir", type=Path, default=Path("outputs"),
        help="Directory for charts, reports, and cleaned data (default: outputs).",
    )
    parser.add_argument(
        "--sample-size", type=int, default=DEFAULT_SAMPLE_SIZE,
        help="Synthetic rows when --input is not supplied (default: 1000).",
    )
    parser.add_argument(
        "--seed", type=int, default=DEFAULT_SEED,
        help="Random seed for reproducible synthetic responses (default: 42).",
    )
    args = parser.parse_args()
    run_pipeline(args.input, args.output_dir, args.sample_size, args.seed)


if __name__ == "__main__":
    main()
