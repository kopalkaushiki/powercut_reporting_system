import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

import db


class ViewReportsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        pad = 12

        title = ttk.Label(self, text="View Reports", font=("TkDefaultFont", 14, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=pad, pady=(pad, 10))

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="w", padx=pad)

        refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.load_records)
        refresh_btn.grid(row=0, column=0, padx=(0, 8), pady=(0, pad))

        delete_btn = ttk.Button(btn_frame, text="Delete Selected", command=self._delete_selected)
        delete_btn.grid(row=0, column=1, padx=(0, 8), pady=(0, pad))

        # Treeview + scrollbar
        columns = ["id", "location", "start_time", "end_time", "status", "type", "severity"]
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)

        self.tree.heading("id", text="ID")
        self.tree.heading("location", text="Location")
        self.tree.heading("start_time", text="Start Time")
        self.tree.heading("end_time", text="End Time")
        self.tree.heading("status", text="Status")
        self.tree.heading("type", text="Type")
        self.tree.heading("severity", text="Severity")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("location", width=180)
        self.tree.column("start_time", width=150)
        self.tree.column("end_time", width=150)
        self.tree.column("status", width=90, anchor="center")
        self.tree.column("type", width=90, anchor="center")
        self.tree.column("severity", width=90, anchor="center")

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=2, column=0, sticky="nsew", padx=pad, pady=(0, pad))
        vsb.grid(row=2, column=1, sticky="ns", pady=(0, pad))

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initial load
        self.load_records()

    def load_records(self) -> None:
        for row_id in self.tree.get_children():
            self.tree.delete(row_id)

        try:
            records = db.fetch_all()
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return

        for r in records:
            self.tree.insert(
                "",
                "end",
                values=(
                    r["id"],
                    r["location"],
                    self._fmt_dt(r["start_time"]),
                    self._fmt_dt(r["end_time"]),
                    r["status"],
                    r["type"],
                    r["severity"],
                ),
            )

    def _fmt_dt(self, dt_value) -> str:
        if dt_value is None:
            return ""
        # mysql-connector returns datetime objects
        if isinstance(dt_value, datetime):
            return dt_value.strftime("%Y-%m-%d %H:%M")
        return str(dt_value)

    def _delete_selected(self) -> None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No selection", "Select a row to delete.")
            return

        item_id = selection[0]
        values = self.tree.item(item_id, "values")
        if not values:
            return
        record_id = int(values[0])

        if not messagebox.askyesno("Confirm delete", f"Delete record ID {record_id}?"):
            return

        try:
            db.delete_record(record_id)
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return

        self.load_records()

