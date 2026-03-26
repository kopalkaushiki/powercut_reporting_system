import tkinter as tk
from tkinter import ttk

import analytics
import dashboard
import report


class PowerCutApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Power Cut Reporting System")
        self.geometry("900x600")

        self._build_ui()

    def _build_ui(self) -> None:
        # Top navigation
        nav = ttk.Frame(self, padding=10)
        nav.grid(row=0, column=0, sticky="ew")
        nav.grid_columnconfigure(0, weight=1)

        report_btn = ttk.Button(nav, text="Report Power Cut", command=self.show_report)
        report_btn.grid(row=0, column=0, padx=(0, 8), sticky="w")

        view_btn = ttk.Button(nav, text="View Reports", command=self.show_reports)
        view_btn.grid(row=0, column=1, padx=(0, 8), sticky="w")

        analytics_btn = ttk.Button(nav, text="Analytics Dashboard", command=self.show_analytics)
        analytics_btn.grid(row=0, column=2, padx=(0, 8), sticky="w")

        exit_btn = ttk.Button(nav, text="Exit", command=self.destroy)
        exit_btn.grid(row=0, column=3, padx=(0, 8), sticky="w")

        # Container for pages (frames)
        container = ttk.Frame(self, padding=(10, 0, 10, 10))
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.report_frame = report.ReportPowerCutFrame(container)
        self.reports_frame = dashboard.ViewReportsFrame(container)

        for frame in (self.report_frame, self.reports_frame):
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_reports()

    def show_report(self) -> None:
        self.report_frame.tkraise()

    def show_reports(self) -> None:
        self.reports_frame.tkraise()
        # Ensure the latest data is shown
        try:
            self.reports_frame.load_records()
        except Exception:
            pass

    def show_analytics(self) -> None:
        analytics.open_analytics_dashboard(self)


if __name__ == "__main__":
    app = PowerCutApp()
    app.mainloop()

