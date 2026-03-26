from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from typing import Optional

import db


DATETIME_FMT = "%Y-%m-%d %H:%M"


class ReportPowerCutFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        pad = 12

        title = ttk.Label(self, text="Report Power Cut", font=("TkDefaultFont", 14, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=pad, pady=(pad, 10))

        # Location
        ttk.Label(self, text="Location:").grid(row=1, column=0, sticky="e", padx=pad, pady=6)
        self.location_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.location_var, width=35).grid(row=1, column=1, sticky="w", pady=6)

        # Start Time
        ttk.Label(self, text=f"Start Time ({DATETIME_FMT}):").grid(row=2, column=0, sticky="e", padx=pad, pady=6)
        self.start_time_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.start_time_var, width=35).grid(
            row=2, column=1, sticky="w", pady=6
        )

        # End Time
        ttk.Label(self, text=f"End Time ({DATETIME_FMT}) [optional]:").grid(
            row=3, column=0, sticky="e", padx=pad, pady=6
        )
        self.end_time_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.end_time_var, width=35).grid(row=3, column=1, sticky="w", pady=6)

        # Status
        ttk.Label(self, text="Status:").grid(row=4, column=0, sticky="e", padx=pad, pady=6)
        self.status_var = tk.StringVar(value="Ongoing")
        self.status_combo = ttk.Combobox(
            self,
            textvariable=self.status_var,
            values=["Ongoing", "Resolved"],
            state="readonly",
            width=33,
        )
        self.status_combo.grid(row=4, column=1, sticky="w", pady=6)

        # Type
        ttk.Label(self, text="Type:").grid(row=5, column=0, sticky="e", padx=pad, pady=6)
        self.type_var = tk.StringVar(value="Sudden")
        self.type_combo = ttk.Combobox(
            self,
            textvariable=self.type_var,
            values=["Planned", "Sudden"],
            state="readonly",
            width=33,
        )
        self.type_combo.grid(row=5, column=1, sticky="w", pady=6)

        # Severity
        ttk.Label(self, text="Severity:").grid(row=6, column=0, sticky="e", padx=pad, pady=6)
        self.severity_var = tk.StringVar(value="Medium")
        self.severity_combo = ttk.Combobox(
            self,
            textvariable=self.severity_var,
            values=["Low", "Medium", "High"],
            state="readonly",
            width=33,
        )
        self.severity_combo.grid(row=6, column=1, sticky="w", pady=6)

        # Submit
        submit_btn = ttk.Button(self, text="Submit", command=self._on_submit)
        submit_btn.grid(row=7, column=0, columnspan=2, sticky="w", padx=pad, pady=(14, pad))

        # Small UX note
        note = ttk.Label(
            self,
            text=f"Tip: Use the format {DATETIME_FMT}. For ongoing outages, leave End Time blank.",
            foreground="#555",
        )
        note.grid(row=8, column=0, columnspan=2, sticky="w", padx=pad, pady=(0, pad))

        self.columnconfigure()

    def columnconfigure(self) -> None:
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

    def _parse_datetime_or_none(self, value: str) -> Optional[datetime]:
        value = (value or "").strip()
        if not value:
            return None
        return datetime.strptime(value, DATETIME_FMT)

    def _on_submit(self) -> None:
        location = (self.location_var.get() or "").strip()
        start_str = (self.start_time_var.get() or "").strip()
        end_str = (self.end_time_var.get() or "").strip()

        if not location:
            messagebox.showerror("Validation error", "Location is required.")
            return
        if not start_str:
            messagebox.showerror("Validation error", "Start Time is required.")
            return

        try:
            start_time = datetime.strptime(start_str, DATETIME_FMT)
        except ValueError:
            messagebox.showerror(
                "Validation error",
                f"Invalid Start Time. Use format: {DATETIME_FMT}",
            )
            return

        status = self.status_var.get()
        type_value = self.type_var.get()
        severity = self.severity_var.get()

        end_time = None
        if status == "Resolved":
            if not end_str:
                messagebox.showerror("Validation error", "End Time is required for Resolved outages.")
                return
            try:
                end_time = datetime.strptime(end_str, DATETIME_FMT)
            except ValueError:
                messagebox.showerror(
                    "Validation error",
                    f"Invalid End Time. Use format: {DATETIME_FMT}",
                )
                return
            if end_time < start_time:
                messagebox.showerror("Validation error", "End Time must be after Start Time.")
                return
        else:
            # Ongoing: ignore end time even if user filled it
            end_time = None

        try:
            db.insert_powercut(
                location=location,
                start_time=start_time,
                end_time=end_time,
                status=status,
                type_value=type_value,
                severity=severity,
            )
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return

        messagebox.showinfo("Success", "Power cut report saved to database.")
        self._clear_form()

    def _clear_form(self) -> None:
        self.location_var.set("")
        self.start_time_var.set("")
        self.end_time_var.set("")
        self.status_var.set("Ongoing")
        self.type_var.set("Sudden")
        self.severity_var.set("Medium")

