"""
Data utilities for NASA FIRMS Wildfire Detection Viewer.
Handles sample data generation, loading, filtering, and summary statistics.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any

def generate_sample_data(n: int = 800, seed: int = 42) -> pd.DataFrame:
    """Generate realistic sample MODIS wildfire detection data.
    
    Focused on Western united States (California and surrounding areas) to simulate typical wildfire activity.
    """

    np.random.seed(seed)

    # Western US coordinates (wildfire-prone regions)
    latitudes = np.random.uniform(32.0, 42.0, n)
    longitudes = np.random.uniform(-125.0, -114.0, n)

    # Brightness temperature (Kelvin) - typical MODIS range for fires
    brightness = np.random.uniform(300.0, 480.0, n)

    # Confidence (0-100)
    confidence = np.random.randint(40, 100, n)

    # Acquisition dates over the last 45 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=45)
    random_days = np.random.randint(0, 45, n)
    acq_dates = [(start_date + timedelta(days=int(d))).strftime("%Y-%m-%d") for d in random_days]

    # Fire Radiative Power (MW)
    frp = np.random.uniform(5.0, 150.0, n)

    # Satellite
    satellites = np.random.choice(["Terra", "Aqua"], n)

    df = pd.DataFrame({
        "Latitude": latitudes.round(4),
        "Longitude": longitudes.round(4),
        "Brightness": brightness.round(1),
        "Confidence": confidence,
        "Acquired": acq_dates,
        "FRP": frp.round(1),
        "Satellite": satellites,
    })
    return df

def load_or_generate_data(data_path: str = "data/sample_firms.csv") -> pd.DataFrame:
    """Load exisitng sample data or generate and save it if missing."""
    os.makedirs(os.path.dirname(data_path) or ".", exist_ok=True)

    if not os.path.exists(data_path):
        df = generate_sample_data()
        df.to_csv(data_path, index=False)
    else:
        df = pd.read_csv(data_path)

    df["acq_date"] = pd.to_datetime(df["acq_date"])
    return df

def filter_data(
        df: pd.DataFrame,
        start_date: datetime,
        end_date: datetime,
        min_brightness: float,
        max_brightness: float,
        min_confidence: int,
) -> pd.DataFrame:
    """Filter detections by date range, brightness, and confidence."""
    if df.empty:
        return df.copy()

    mask = (
        (df["acq_date"] >= pd.Timestamp(start_date))
        & (df["acq_date"] <= pd.Timestamp(end_date))
        & (df["brightness"] >= min_brightness)
        & (df["brightness"] <= max_brightness)
        & (df["confidence"] >= min_confidence)
    )
    return df.loc[mask].copy()

def get_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute summary statistics for the filtered detections."""
    if df.empty:
        return {
            "total": 0,
            "avg_brightness": 0.0,
            "max_brightness": 0.0,
            "avg_frp": 0.0,
        }
    
    return {
        "total": int(len(df)),
        "avg_brightness": float(df["brightness"].mean()),
        "max_brightness": float(df["brightness"].max()),
        "avg_frp": float(df["frp"].mean()),
    }