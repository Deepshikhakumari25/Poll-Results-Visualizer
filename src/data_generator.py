"""Reproducible generation of clearly illustrative poll responses."""

from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_SEED = 42
DEFAULT_SAMPLE_SIZE = 1_000
SAMPLE_DATA_PATH = Path("data") / "raw" / "poll_responses.csv"
OPTIONS = ("Python", "SQL", "Excel", "Power BI", "Tableau")


def generate_synthetic_data(
    n_responses: int = DEFAULT_SAMPLE_SIZE,
    seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    """Return a reproducible, fictional poll dataset with ``n_responses`` rows."""
    if n_responses < 0:
        raise ValueError("n_responses must be zero or greater.")

    rng = np.random.default_rng(seed)
    start = np.datetime64("2025-01-01T00:00:00")
    end = np.datetime64("2025-03-31T23:59:59")
    seconds = int((end - start) / np.timedelta64(1, "s"))
    timestamps = start + rng.integers(0, seconds + 1, size=n_responses).astype(
        "timedelta64[s]"
    )
    options = rng.choice(
        OPTIONS, size=n_responses, p=(0.30, 0.24, 0.15, 0.19, 0.12)
    )
    feedback_templates = (
        "Easy to learn and useful for my projects.",
        "I like the flexibility and helpful tutorials.",
        "A practical tool for working with data.",
        "The interface could be clearer for beginners.",
        "Good features, though I would like more practice.",
        "It saves time when I understand the workflow.",
        "Helpful for sharing results with my team.",
        "I would like to explore more examples.",
    )
    feedback = rng.choice(feedback_templates, size=n_responses)

    return pd.DataFrame(
        {
            "Response_ID": [f"R{i:05d}" for i in range(1, n_responses + 1)],
            "Timestamp": pd.to_datetime(timestamps),
            "Age_Group": rng.choice(
                ("18-24", "25-34", "35-44", "45-54", "55+"),
                size=n_responses,
                p=(0.32, 0.30, 0.19, 0.12, 0.07),
            ),
            "Gender": rng.choice(
                ("Female", "Male", "Non-binary", "Prefer not to say"),
                size=n_responses,
                p=(0.46, 0.43, 0.04, 0.07),
            ),
            "Region": rng.choice(
                ("North", "South", "East", "West", "Central"),
                size=n_responses,
                p=(0.22, 0.20, 0.19, 0.22, 0.17),
            ),
            "Question": "Which technology tool do you prefer?",
            "Selected_Option": options,
            "Satisfaction_Rating": rng.choice(
                (1, 2, 3, 4, 5), size=n_responses, p=(0.04, 0.09, 0.22, 0.39, 0.26)
            ),
            "Feedback": feedback,
        }
    )


def save_synthetic_data(
    path: str | Path = SAMPLE_DATA_PATH,
    n_responses: int = DEFAULT_SAMPLE_SIZE,
    seed: int = DEFAULT_SEED,
) -> Path:
    """Generate and overwrite one CSV; repeated runs never append duplicate rows."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    generate_synthetic_data(n_responses=n_responses, seed=seed).to_csv(
        destination, index=False
    )
    return destination


if __name__ == "__main__":
    print(f"Generated sample CSV: {save_synthetic_data()}")
