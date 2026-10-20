"""Unit tests for src.data_utils."""

import pandas as pd
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from src.data_utils import (
    filter_data,
    generate_sample_data,
    get_summary_stats,
    load_or_generate_data,
)

@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Deterministic sample data for tests."""
    return generate_sample_data(n=100, seed=42)

def test_generate_sample_data_schema(sample_df: pd.DataFrame) -> None:
    expected_columns = {
        "latitude",
        "longitude",
        "brightness",
        "confidence",
        "acq_date",
        "frp",
        "satellite",
    }
    assert set(sample_df.columns) == expected_columns
    assert len(sample_df) == 100

def test_generate_sample_data_ranges(sample_df: pd.DataFrame) -> None:
    assert sample_df["latitude"].between(32.0, 42.0).all()
    assert sample_df["longitude"].between(-125.0, -114.0).all()
    assert sample_df["brightness"].between(300.0, 480.0).all()
    assert sample_df["confidence"].between(40, 99).all()
    assert sample_df["frp"].between(5.0, 150.0).all()
    assert set(sample_df["satellite"].unique()).issubset({"Terra", "Aqua"})

def test_generate_sample_data_is_deterministic() -> None:
    df1 = generate_sample_data(n=50, seed=123)
    df2 = generate_sample_data(n=50, seed=123)
    pd.testing.assert_frame_equal(df1, df2)


def test_load_or_generate_data_creates_file(tmp_path: Path) -> None:
    data_path = tmp_path / "sample_firms.csv"
    assert not data_path.exists()

    df = load_or_generate_data(str(data_path))

    assert data_path.exists()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert pd.api.types.is_datetime64_any_dtype(df["acq_date"])


def test_filter_data_basic(sample_df: pd.DataFrame) -> None:
    # Ensure datetime for filtering
    sample_df = sample_df.copy()
    sample_df["acq_date"] = pd.to_datetime(sample_df["acq_date"])

    start = sample_df["acq_date"].min()
    end = sample_df["acq_date"].max()

    filtered = filter_data(
        sample_df,
        start_date=start,
        end_date=end,
        min_brightness=300.0,
        max_brightness=500.0,
        min_confidence=0,
    )
    assert len(filtered) == len(sample_df)


def test_filter_data_restrictive(sample_df: pd.DataFrame) -> None:
    sample_df = sample_df.copy()
    sample_df["acq_date"] = pd.to_datetime(sample_df["acq_date"])

    filtered = filter_data(
        sample_df,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=1),
        min_brightness=1000.0,  # impossible
        max_brightness=2000.0,
        min_confidence=100,
    )
    assert filtered.empty


def test_filter_data_empty_input() -> None:
    empty = pd.DataFrame(columns=["Latitude", "Longitude", "Brightness", "Confidence", "Acquired", "FRP", "Satellite"])
    result = filter_data(
        empty,
        start_date=datetime.now(),
        end_date=datetime.now(),
        min_brightness=0,
        max_brightness=1000,
        min_confidence=0,
    )
    assert result.empty


def test_get_summary_stats_empty() -> None:
    empty = pd.DataFrame()
    stats = get_summary_stats(empty)
    assert stats == {
        "total": 0,
        "avg_brightness": 0.0,
        "max_brightness": 0.0,
        "avg_frp": 0.0,
    }


def test_get_summary_stats_non_empty(sample_df: pd.DataFrame) -> None:
    sample_df = sample_df.copy()
    sample_df["acq_date"] = pd.to_datetime(sample_df["acq_date"])

    stats = get_summary_stats(sample_df)
    assert stats["total"] == len(sample_df)
    assert stats["avg_brightness"] == pytest.approx(sample_df["brightness"].mean())
    assert stats["max_brightness"] == sample_df["brightness"].max()
    assert stats["avg_frp"] == pytest.approx(sample_df["frp"].mean())
