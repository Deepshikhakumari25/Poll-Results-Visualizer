# Testing

Run the automated tests from the project root:

```powershell
python -m pytest -v
```

Tests use small in-memory or temporary files to verify reproducible generation,
CSV validation, duplicate handling, category normalization, invalid ratings,
per-question percentage denominators, insight content, empty data, and PNG chart
creation. They do not depend on the full sample dataset.
The dashboard upload test uses Streamlit `AppTest` to exercise a valid CSV with
optional columns omitted and an invalid CSV missing required columns.

## Verified environment and results

- Python: 3.13.9 (64-bit)
- pandas: 3.0.6
- NumPy: 2.5.4
- Matplotlib: 3.11.2
- Streamlit: 1.66.0
- WordCloud: 1.9.6
- pytest: 9.1.1
- Latest full run: **13 passed**.
- Streamlit `AppTest` smoke run: **0 exceptions**; dashboard title, summary
  metrics, three download controls, valid CSV upload, and missing-required-column
  validation rendered.
- Streamlit server health endpoint: **HTTP 200**.

The dashboard server returned HTTP 200 and the app was opened in a browser.
