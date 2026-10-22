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

    # Western US coordinates (wildfire-prone regions))
    # California boundary polygon (lon, lat) — closed loop
    # To move east/west add/subtract to lon
    # To move north/south add/subtract to lat
    california = [
        [-124.21, 42.00], # NW corner
        [-120.00, 42.00], # NE corner
        [-120.00, 39.00], # Lake Tahoe bend
        [-114.64, 35.00], # Colorado River area (NV/AZ)
        [-114.48, 34.20], # AZ border
        [-114.53, 33.30], # AZ border
        [-114.72, 32.72], # SE corner
        [-117.12, 32.53], # SW corner
        [-117.45, 33.30], # Southern coast
        [-118.45, 34.00], # Santa Monica/LA
        [-120.55, 34.55], # North SB
        [-120.70, 34.55], # South Santa Maria
        [-120.65, 35.10], # Santa Maria/Arroyo Grande
        [-121.50, 36.00], # SLO to Paso
        [-122.00, 36.60], # Paso to Monterey
        [-122.50, 37.75], # SF
        [-123.70, 38.80], # Santa Rosa/Mendocino
        [-123.85, 39.60], # Mendocino
        [-124.10, 40.10], # South Eureka bump
        [-124.35, 40.45], # Mid Eureka bump
        [-124.50, 40.60], # North Eureka bump
        [-124.22, 40.75], # South Eureka
        [-124.13, 41.10], # North Eureka
        [-124.15, 42.00]  # NW corner
    ]

    def point_in_polygon(lon, lat, polygon):
        """Ray-casting point-in-polygon test."""
        n = len(polygon)
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = polygon[i]
            xj, yj = polygon[j]
            if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi):
                inside = not inside
            j = i
        return inside

    latitudes = []
    longitudes = []
    while len(latitudes) < n:
        lat = np.random.uniform(32.5, 42.0)
        lon = np.random.uniform(-124.5, -114.0)
        if point_in_polygon(lon, lat, california):
            latitudes.append(lat)
            longitudes.append(lon)

    latitudes = np.array(latitudes)
    longitudes = np.array(longitudes)

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

    df["Acquired"] = pd.to_datetime(df["Acquired"])
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
        (df["Acquired"] >= pd.Timestamp(start_date))
        & (df["Acquired"] <= pd.Timestamp(end_date))
        & (df["Brightness"] >= min_brightness)
        & (df["Brightness"] <= max_brightness)
        & (df["Confidence"] >= min_confidence)
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
        "avg_brightness": float(df["Brightness"].mean()),
        "max_brightness": float(df["Brightness"].max()),
        "avg_frp": float(df["FRP"].mean()),
    }