# coding=utf-8
####################################################
# Update Dialog
#
# Author: Tobias Grupe
#
####################################################
import webbrowser
import tkinter as tk
from tkinter import BOTTOM, TOP
from tkinter.ttk import Frame, Button


class UpdateDialog(tk.Toplevel):
    def __init__(self, parent, current_version, latest_version, download_url):
        super().__init__(parent)
        self.title("Check for Updates")
        self.resizable(False, False)
        self._download_url = download_url
        self._create_widgets(current_version, latest_version)
        self.update_idletasks()
        self.geometry(f"{self.winfo_reqwidth() + 40}x{self.winfo_reqheight() + 20}")

    def _create_widgets(self, current_version, latest_version):
        content_frame = Frame(self)
        update_available = self._download_url is not None

        if update_available:
            heading = "A New Version Is Available"
            body = f"Installed version: {current_version}\nLatest version:    {latest_version}"
        else:
            heading = "You're Up to Date"
            body = f"Installed version: {current_version}\nThis is the latest version."

        tk.Label(content_frame, text=heading, font=("", 14, "bold")).grid(
            row=0, column=0, pady=(10, 4))
        tk.Label(content_frame, text=body, justify=tk.LEFT).grid(
            row=1, column=0, padx=10, pady=(0, 10))
        content_frame.pack(side=TOP, padx=10)

        bottom_frame = Frame(self)
        if update_available:
            Button(bottom_frame, text="Download",
                   command=lambda: webbrowser.open(self._download_url)).pack(side=tk.LEFT, padx=5)
        Button(bottom_frame, text="Close", command=self.destroy).pack(side=tk.LEFT, padx=5)
        bottom_frame.pack(side=BOTTOM, pady=10)
