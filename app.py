"""
NASA FIRMS Wildfire Detection Viewer
A polished Streamlit application for exploring sample MODIS wildfire detections.
"""

from datetime import datetime
import pandas as pd
import pydeck as pdk
import streamlit as st
from src.data_utils import filter_data, get_summary_stats, load_or_generate_data

def brightness_to_color(brightness: float, min_b: float, max_b: float) -> list:
    """Map brightness to an RGBA color (higher brightness = more intense red/orange)"""
    if max_b <= min_b:
        norm = 0.5
    else:
        norm = (brightness - min_b) / (max_b - min_b)
        norm = max(0.0, min(1.0, norm))
    r = int(180 + 75 * norm)
    g = int(40 + 60 * (1 - norm))
    b = int(20)
    return [r, g, b, 200]

# Only generating the data once
@st.cache_data
def load_data() -> pd.DataFrame:
    """Cached data loader."""
    return load_or_generate_data()

def main() -> None:
    st.set_page_config(
        page_title="NASA FIRMS Wildfire Detection Viewer",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("🔥 NASA FIRMS Wildfire Detection Viewer")
    st.markdown("Interactive portfolio project visualizing sample wildfire detections"
                "modeled on NASA FIRMS MODIS active fire data."
                "Filter by date, brightness, and confidence to explore detections on an interactive map."
                )

    # loading data
    df = load_data()

    # Sidebar filters
    st.sidebar.header("Filters")
    st.sidebar.markdown("Adjust parameters to filter detections.")

    min_date = df["acq_date"].min().date()
    max_date = df["acq_date"].max().date()

    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    bright_min = float(df["brightness"].min())
    bright_max = float(df["brightness"].max())

    min_brightness = st.sidebar.slider(
        "Minimum Brightness (K)",
        min_value=bright_min,
        max_value=bright_max,
        value=bright_min,
        step=1.0,
    )
    max_brightness = st.sidebar.slider(
        "Maximum Brightness (K)",
        min_value=bright_min,
        max_value=bright_max,
        value=bright_max,
        step=1.0,
    )

    # Ensuring a logical range
    if min_brightness > max_brightness:
        min_brightness, max_brightness = max_brightness, min_brightness

    min_confidence = st.sidebar.slider(
        "Minimum Confidence",
        min_value=0,
        max_value=100,
        value=50,
        step=1,
    )

    # Filtering
    filtered_df = filter_data(
        df,
        start_date=datetime.combine(start_date, datetime.min.time()),
        end_date=datetime.combine(end_date, datetime.max.time()),
        min_brightness=min_brightness,
        max_brightness=max_brightness,
        min_confidence=min_confidence,
    )

    # Summary metrics
    stats = get_summary_stats(filtered_df)

    st.subheader("Summary Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Detections", f"{stats['total']:,}")
    col2.metric("Avg Brightness", f"{stats['avg_brightness']:.1f} K")
    col3.metric("Max Brightness", f"{stats['max_brightness']:.1f} K")
    col4.metric("Avg FRP", f"{stats['avg_frp']:.1f} MW")

    # Interactive map
    st.subheader("Fire Detection Map")
    st.caption("Points are colored by brightness (darker red/orange = higher intensity). Hover for details.")

    if filtered_df.empty:
        st.info("No detections match the current filters. Try widening the date range or lowering thresholds.")
    else:
        # Add color column for pydeck
        map_df = filtered_df.copy()
        map_df["acq_date"] = map_df["acq_date"].dt.strftime("%Y-%m-%d")
        map_df["color"] = map_df["brightness"].apply(
            lambda b: brightness_to_color(b, min_brightness, max_brightness)
        )
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position=["longitude", "latitude"],
            get_fill_color="color",
            get_radius=8000,
            radius_min_pixels=3,
            radius_max_pixels=15,
            pickable=True,
            auto_highlight=True,
        )

        # Center view on data
        view_state = pdk.ViewState(
            latitude=float(map_df["latitude"].mean()),
            longitude=float(map_df["longitude"].mean()),
            zoom=5.5,
            pitch=0,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "html": """
                <b>Brightness:</b> {brightness} K<br/>
                <b>Confidence:</b> {confidence}%<br/>
                <b>FRP:</b> {frp} MW<br/>
                <b>Satellite:</b> {satellite}<br/>
                <b>Date:</b> {acq_date}
                """,
                "style": {"backgroundColor": "steelblue", "color": "white"},
            },
            map_style="mapbox://styles/mapbox/dark-v10",
        )

        st.pydeck_chart(deck, use_container_width=True)

    # Data table
    with st.expander("View Filtered Detections", expanded=False):
        if filtered_df.empty:
            st.write("No data to display.")
        else:
            display_df = filtered_df.copy()
            display_df["acq_date"] = display_df["acq_date"].dt.strftime("%Y-%m-%d")
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "latitude": st.column_config.NumberColumn("Latitude", format="%.4f"),
                    "longitude": st.column_config.NumberColumn("Longitude", format="%.4f"),
                    "brightness": st.column_config.NumberColumn("Brightness", format="%.1f"),
                    "confidence": st.column_config.NumberColumn("Confidence"),
                    "acq_date": st.column_config.TextColumn("Date"),
                    "frp": st.column_config.NumberColumn("FRP (MW)", format="%.1f"),
                    "satellite": st.column_config.TextColumn("Satellite"),
                },
            )
            st.caption(f"Showing {len(display_df):,} of {len(df):,} total sample detections.")
if __name__ == "__main__":main()