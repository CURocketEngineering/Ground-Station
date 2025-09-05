# … existing imports …
import os

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from cure_ground.core.protocols.data_names.data_name_loader import DataNames
from cure_ground.core.protocols.states.states_loader import States

FT_PER_M = 3.28084  # handy constant


def plot_stacked_summary_figure(
    launch_df: pd.DataFrame,
    states: States,
    units: dict,
    save_path: str,
    key_state_event_labels: dict,
    data_names: DataNames,
) -> None:

    # ── 1. Pre-compute total acceleration ───────────────────────────────────
    accel_cols = {
        data_names["ACCELEROMETER_X"].name,
        data_names["ACCELEROMETER_Y"].name,
        data_names["ACCELEROMETER_Z"].name,
    }
    if accel_cols.issubset(launch_df.columns):
        launch_df["total_acceleration"] = (
            launch_df[data_names["ACCELEROMETER_X"].name] ** 2
            + launch_df[data_names["ACCELEROMETER_Y"].name] ** 2
            + launch_df[data_names["ACCELEROMETER_Z"].name] ** 2
        ) ** 0.5
    else:
        launch_df["total_acceleration"] = None

    # ── 1 b.  ✓  QUICK SUMMARY VALUES  ──────────────────────────────────────
    max_alt_m = launch_df[data_names["ALTITUDE"].name].max()
    min_alt_m = launch_df[data_names["ALTITUDE"].name].min()
    apogee_ft = (max_alt_m - min_alt_m) * FT_PER_M
    max_accel = launch_df["total_acceleration"].max()

    # Find the first continuous segment where acceleration > 2.0 m/s² + gravity
    threshold = 9.8 + 2.0
    first_above_2 = launch_df[launch_df["total_acceleration"] > threshold].index.min()
    first_below_2_after_first_above_2 = (
        launch_df[launch_df["total_acceleration"] <= threshold]
        .index[launch_df.index.get_loc(first_above_2) + 1 :]
        .min()
    )

    burn_time = (
        (first_below_2_after_first_above_2 - first_above_2)
        if first_above_2 and first_below_2_after_first_above_2
        else 0.0
    )

    launch_detection_delay = -first_above_2

    # ── 2. Figure setup (unchanged) ─────────────────────────────────────────
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.025,
        row_heights=[0.6, 0.4],
        #   subplot_titles=("Altitude", "Total Acceleration")
    )

    # ── 3. Altitude trace (row 1) ────────────────────────────────────────────
    if data_names["ALTITUDE"].name in launch_df.columns:
        fig.add_trace(
            go.Scatter(
                x=launch_df.index,
                y=launch_df[data_names["ALTITUDE"].name].interpolate(),
                mode="lines",
                name="Altitude",
            ),
            row=1,
            col=1,
        )

    # Estimated apogee (optional) — row 1
    if (
        data_names["EST_APOGEE"].name in launch_df.columns
        and not launch_df[data_names["EST_APOGEE"].name].isnull().all()
    ):
        fig.add_trace(
            go.Scatter(
                x=launch_df.index,
                y=launch_df[data_names["EST_APOGEE"].name].interpolate(),
                mode="lines",
                name="Estimated Apogee",
                line=dict(dash="dot"),
            ),
            row=1,
            col=1,
        )

    # ── 4. Total acceleration trace (row 2) ─────────────────────────────────
    if "total_acceleration" in launch_df.columns:
        fig.add_trace(
            go.Scatter(
                x=launch_df.index,
                y=launch_df["total_acceleration"].interpolate(),
                mode="lines",
                name="Total Acceleration",
            ),
            row=2,
            col=1,
        )

    # ── 5. Vertical lines for each state change (draw across both rows) ─────
    apogee_detection_delay = float("inf")
    if data_names["STATE_CHANGE"].name in launch_df.columns:
        state_changes = launch_df[data_names["STATE_CHANGE"].name].dropna()
        color_cycle = ["red", "lime", "blue", "cyan", "magenta", "yellow", "white", "orange"]
        for i, (x_pos, state_val) in enumerate(state_changes.items()):
            color = color_cycle[i % len(color_cycle)]

            # Label lookup
            try:
                label = states.get_by_id(state_val).name
            except Exception:
                label = f"State {state_val}"

            anno_text = key_state_event_labels.get(state_val, label)

            # If its apogee, then calculate apogee detection delay
            if state_val == states["STATE_DESCENT"].id:
                # x_pos - max altitude index

                # Get the max altitude between launch and the x_pos
                max_altitude_idx = launch_df[data_names["ALTITUDE"].name].loc[:x_pos].idxmax()

                apogee_detection_delay = pd.to_numeric(x_pos, errors="coerce") - pd.to_numeric(
                    max_altitude_idx, errors="coerce"
                )
                apogee_detection_delay = float(apogee_detection_delay)

            # Draw the vertical line through all subplots
            fig.add_vline(
                x=x_pos, line_width=2, line_dash="dash", line_color=color, row="all", col=1
            )

            # Add the annotation once at the top
            fig.add_annotation(
                x=x_pos,
                y=1.02,  # slightly above the top subplot
                xref="x",  # bind x to the data axis
                yref="paper",  # y is relative to figure height (0–1)
                text=anno_text,
                showarrow=False,
                font=dict(color="white"),
                bgcolor="black",
                bordercolor="white",
                borderwidth=1,
                borderpad=4,
                xanchor="left",
            )

    # ── 3. Layout tweaks (unchanged) ────────────────────────────────────────
    fig.update_layout(
        template="plotly_dark",
        height=700,
        width=1000,
        title_text="Launch Window Summary: Altitude & Total Acceleration",
        showlegend=True,
        legend=dict(orientation="h", x=0, y=-0.15),
    )

    # Y-axis labels for each subplot
    fig.update_yaxes(
        title_text=f"Altitude ({units.get(data_names['ALTITUDE'].name, 'm')})",
        row=1,
        col=1,
        range=[0, max_alt_m * 1.1],  # Add some padding above max altitude
    )
    fig.update_yaxes(
        title_text=f"Total Acceleration ({units.get(data_names['ACCELEROMETER_X'].name, 'm/s²')})",
        row=2,
        col=1,
    )

    fig.update_xaxes(title_text="Time from Detected Launch (s)", row=2, col=1)

    # ──────────────────  4.  NEW SUMMARY BLOCK  ────────────────────────────
    summary_text = (
        f"<b>Launch Stats</b><br>"
        f"Max Acc   : {max_accel:4.1f} m/s²<br>"
        f"Apogee    : {apogee_ft:4.0f} ft AGL<br>"
        f"Burn Time : {burn_time:4.2f} s<br>"
        f"LCH Dly   : {launch_detection_delay:.2f} s<br>"
        f"APOG Dly  : {apogee_detection_delay:.2f} s<br>"
    )

    fig.add_annotation(
        x=0.5,  # just outside right edge
        y=0.5,
        xref="paper",
        yref="paper",
        text=summary_text,
        align="left",
        showarrow=False,
        bordercolor="white",
        borderwidth=1,
        borderpad=8,
        bgcolor="black",
        font=dict(
            family="Courier New, monospace",  # swap for Orbitron, Audiowide, etc.
            size=12,
            color="lightcyan",
        ),
    )
    # ───────────────────────────────────────────────────────────────────────

    # ── 5. Save & display ───────────────────────────────────────────────────
    out_path = os.path.join(save_path, "launch_summary_stacked.png")
    fig.write_image(out_path, scale=2)
    print(f"Saved stacked-axis summary to {out_path}")
    fig.show()
