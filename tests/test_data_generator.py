import pandas as pd
import pytest

from src.data_generator import generate_synthetic_data, save_synthetic_data
from src.data_loader import REQUIRED_COLUMNS


def test_generation_is_reproducible_and_has_expected_columns():
    first = generate_synthetic_data(30, seed=17)
    second = generate_synthetic_data(30, seed=17)
    pd.testing.assert_frame_equal(first, second)
    assert set(REQUIRED_COLUMNS).issubset(first.columns)
    assert len(first) == 30


def test_sample_writer_overwrites_instead_of_appending(tmp_path):
    destination = tmp_path / "raw" / "sample.csv"
    save_synthetic_data(destination, n_responses=4)
    save_synthetic_data(destination, n_responses=4)
    assert len(pd.read_csv(destination)) == 4


def test_negative_sample_size_is_rejected():
    with pytest.raises(ValueError, match="zero or greater"):
        generate_synthetic_data(-1)
