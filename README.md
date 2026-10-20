# NASA FIRMS Wildfire Detection Viewer

A polished, interactive Streamlit web application that visualizes sample wildfire detection data modeled on NASA FIRMS MODIS active fire products. Built as a portfolio project to demonstrate data engineering, software engineering, and interactive data application skills.

## Overview

This application loads (or automatically generates) realistic sample wildfire detections with the standard NASA FIRMS columns:

- `latitude`, `longitude`
- `brightness` (temperature in Kelvin)
- `confidence` (0–100)
- `acq_date`
- `frp` (Fire Radiative Power in MW)
- `satellite` (Terra / Aqua)

Users can filter the data interactively and explore results through summary metrics, a color-coded interactive map (powered by pydeck), and a detailed data table.

## Features

- **Automatic sample data generation** — creates realistic MODIS-style detections on first run and persists them to `data/sample_firms.csv`
- **Interactive sidebar filters** — date range, minimum/maximum brightness, and minimum confidence
- **Summary metrics** — total detections, average brightness, maximum brightness, and average FRP
- **Interactive map** — pydeck ScatterplotLayer with points colored by brightness intensity
- **Expandable data table** — full filtered results with clean formatting
- **Modular architecture** — data logic cleanly separated from the UI

## Project Structure

```
.
├── app.py                  # Main Streamlit application
├── src/
│   └── data_utils.py       # Data generation, loading, filtering, and summary stats
├── data/
│   └── sample_firms.csv    # Generated sample data (created automatically)
├── requirements.txt
└── README.md
```

## Installation & Running

1. Clone this repository (or download the project files).

2. (Recommended) Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   Then activate it:

   - **Windows (PowerShell):**
     ```powershell
     .venv\Scripts\activate
     ```

   - **Windows (Command Prompt):**
     ```cmd
     .venv\Scripts\activate.bat
     ```

   - **macOS / Linux / Git Bash:**
     ```bash
     source .venv/bin/activate
     ```

   You should see `(.venv)` at the start of your prompt.

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Launch the app:

   ```bash
   streamlit run app.py
   ```

On the first run, sample data is generated automatically and saved to `data/sample_firms.csv`. Subsequent runs load the existing file.

## Running Tests

The project includes unit tests for the data utilities.

```bash
pip install -r requirements.txt   # includes pytest
pytest tests/ -v
```

Tests cover data generation, loading, filtering, and summary statistics (including edge cases).

- **Python 3.9+**
- **Streamlit** — interactive web application framework
- **pandas** — data manipulation and filtering
- **pydeck** — high-performance geospatial visualization
- **numpy** — sample data generation

## What This Project Demonstrates

- Clean, modular project structure suitable for GitHub and code review
- Separation of concerns (data utilities vs. presentation layer)
- Realistic data pipeline patterns: generation → persistence → filtering → aggregation
- Production-quality Streamlit patterns (`st.cache_data`, column metrics, expanders, column configs)
- Geospatial data visualization with dynamic coloring
- Professional documentation and reproducible setup

This project is intentionally scoped as a self-contained portfolio piece that can be extended (e.g., live NASA FIRMS API integration, additional layers, deployment to Streamlit Community Cloud).