from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def test_dashboard_accepts_csv_uploads_and_reports_missing_required_columns():
    valid_app = AppTest.from_file(str(APP_PATH), default_timeout=60).run()
    valid_app.radio[0].set_value("Upload a CSV").run()
    valid_app.get("file_uploader")[0].set_value(
        ("responses.csv", b"Response_ID,Question,Selected_Option\nR1,Q,A\n", "text/csv")
    ).run()
    assert not valid_app.exception
    assert valid_app.metric[0].label == "Valid responses"
    assert valid_app.metric[0].value == "1"

    invalid_app = AppTest.from_file(str(APP_PATH), default_timeout=60).run()
    invalid_app.radio[0].set_value("Upload a CSV").run()
    invalid_app.get("file_uploader")[0].set_value(
        ("invalid.csv", b"Other\nA\n", "text/csv")
    ).run()
    assert not invalid_app.exception
    assert any("missing required column" in item.value for item in invalid_app.error)
