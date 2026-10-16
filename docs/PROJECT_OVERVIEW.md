# Project overview

Poll Results Visualizer turns a CSV of poll responses into a cleaned dataset,
per-question count and percentage tables, charts, and plain-language descriptive
insights. It provides both a command-line workflow and a Streamlit dashboard.

## Intended use

Use the project to practice data validation, cleaning, exploratory analysis,
visualization, and dashboard development with classroom, event, product, or
feedback polls. The built-in dataset is reproducible synthetic data, not real
polling. Findings describe the supplied responses only and are not predictions
or population estimates.

## Workflow

1. Load the built-in sample or a CSV.
2. Validate the required response ID, question, and selected-option fields.
3. Standardize categories, remove invalid required records and duplicate IDs,
   parse dates, and mark ratings outside 1–5 as missing.
4. Aggregate counts and within-question percentages; inspect optional fields.
5. Render charts and calculate descriptive insights from the loaded data.
6. Display results interactively or export cleaned data and reports.

See [the README](../README.md) for setup and execution.
