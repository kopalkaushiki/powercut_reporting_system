import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import db


def open_analytics_dashboard(parent) -> None:
    try:
        records = db.fetch_all()
    except Exception as e:
        messagebox.showerror("Database error", str(e))
        return

    df = _records_to_dataframe(records)

    win = tk.Toplevel(parent)
    win.title("Analytics Dashboard")
    win.geometry("1100x800")

    shell = ttk.Frame(win, padding=12)
    shell.grid(row=0, column=0, sticky="nsew")

    win.grid_rowconfigure(0, weight=1)
    win.grid_columnconfigure(0, weight=1)
    shell.grid_rowconfigure(1, weight=1)
    shell.grid_columnconfigure(0, weight=1)

    header = ttk.Label(shell, text="Analytics Dashboard", font=("TkDefaultFont", 14, "bold"))
    header.grid(row=0, column=0, sticky="w", pady=(0, 10))

    avg_label = ttk.Label(shell, text="", foreground="#333")
    avg_label.grid(row=2, column=0, sticky="w", pady=(8, 10))

    if df.empty:
        ttk.Label(shell, text="No data found. Report a power cut first.").grid(
            row=1, column=0, sticky="w"
        )
        return

    # Calculations
    df_resolved = df[df["end_time"].notna()].copy()
    if not df_resolved.empty:
        df_resolved["duration_minutes"] = (
            (df_resolved["end_time"] - df_resolved["start_time"]).dt.total_seconds() / 60.0
        )
        overall_avg_minutes = df_resolved["duration_minutes"].mean()
        avg_label.config(
            text=f"Average resolved outage duration: {overall_avg_minutes:.1f} minutes"
        )
    else:
        avg_label.config(text="Average resolved outage duration: N/A (no resolved records).")

    most_affected = df["location"].value_counts().head(10)

    if not df_resolved.empty:
        avg_duration_by_location = (
            df_resolved.groupby("location")["duration_minutes"].mean().sort_values(ascending=False)
        ).head(10)
    else:
        avg_duration_by_location = pd.Series(dtype=float)

    peak_hour = df["start_time"].dt.hour.value_counts().sort_index()
    daily = df.groupby("date_reported").size().sort_index()

    # Layout charts: 2x2
    fig = Figure(figsize=(10.8, 7.2), dpi=100)
    axes = fig.subplots(2, 2).flatten()

    # Bar: Most affected areas
    axes[0].bar(most_affected.index.astype(str), most_affected.values)
    axes[0].set_title("Most Affected Areas (Top 10)")
    axes[0].set_xlabel("Location")
    axes[0].set_ylabel("Count")
    axes[0].tick_params(axis="x", rotation=30)

    # Bar: Average outage duration by location
    if not avg_duration_by_location.empty:
        axes[1].bar(avg_duration_by_location.index.astype(str), avg_duration_by_location.values)
        axes[1].set_title("Average Resolved Duration by Location (Top 10)")
        axes[1].set_xlabel("Location")
        axes[1].set_ylabel("Average Duration (minutes)")
        axes[1].tick_params(axis="x", rotation=30)
    else:
        axes[1].text(0.5, 0.5, "No resolved data to compute durations.", ha="center", va="center")
        axes[1].set_title("Average Resolved Duration by Location")
        axes[1].set_axis_off()

    # Line: Peak outage time (hour frequency)
    # Ensure hours 0-23 appear in order (even if frequency is 0)
    all_hours = pd.Series(0, index=range(24))
    all_hours.update(peak_hour)
    axes[2].plot(all_hours.index, all_hours.values, marker="o")
    axes[2].set_title("Peak Outage Time (Hour Frequency)")
    axes[2].set_xlabel("Hour (0-23)")
    axes[2].set_ylabel("Count")
    axes[2].set_xticks(range(0, 24, 2))
    axes[2].grid(True, alpha=0.25)

    # Line: Daily trends (using date_reported)
    if not daily.empty:
        axes[3].plot(daily.index.astype(str), daily.values, marker="o")
        axes[3].set_title("Daily Trends (Outages per Reported Date)")
        axes[3].set_xlabel("Date")
        axes[3].set_ylabel("Count")
        axes[3].tick_params(axis="x", rotation=30)
        axes[3].grid(True, alpha=0.25)
    else:
        axes[3].text(0.5, 0.5, "No daily trend data found.", ha="center", va="center")
        axes[3].set_title("Daily Trends")
        axes[3].set_axis_off()

    canvas = FigureCanvasTkAgg(fig, master=shell)
    canvas.draw()
    canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")

    # Optional toolbar
    try:
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

        toolbar = NavigationToolbar2Tk(canvas, shell)
        toolbar.update()
        toolbar.grid(row=0, column=1, sticky="nsew")
    except Exception:
        pass


def _records_to_dataframe(records: list[dict]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame.from_records(records)

    # Ensure datetime types for analytics
    if "start_time" in df.columns:
        df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
    if "end_time" in df.columns:
        df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")

    if "date_reported" in df.columns:
        df["date_reported"] = pd.to_datetime(df["date_reported"], errors="coerce").dt.date

    # Normalize location
    if "location" in df.columns:
        df["location"] = df["location"].fillna("").astype(str).str.strip()

    return df

