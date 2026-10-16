# Architecture

```text
CSV / reproducible sample generator
              |
       src/data_loader.py
              |
       src/data_cleaning.py
              |
       src/analysis.py ------ src/insights.py
              |                      |
       src/visualizations.py         |
            /       \                |
     main.py       app.py -----------+
        |             |
  outputs/        Streamlit UI
```

- `src/data_generator.py` creates and overwrites a seeded illustrative CSV.
- `src/data_loader.py` validates CSV paths and required columns.
- `src/data_cleaning.py` returns cleaned rows and a quality-change summary.
- `src/analysis.py` computes counts and percentages per question, plus optional
  rating, demographic, temporal, and feedback summaries.
- `src/visualizations.py` creates charts for use in the UI and saved PNG files.
- `src/insights.py` builds descriptive statements from calculated results.
- `main.py` runs the analysis pipeline without Streamlit.
- `app.py` applies interactive filters and offers downloads.

Optional fields are checked before use. The required fields are
`Response_ID`, `Question`, and `Selected_Option`.
