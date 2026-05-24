# coding=utf-8
####################################################
# About - Dialog
#
# Author: Tobias Grupe
#
####################################################
import tkinter as tk
from tkinter import BOTTOM, TOP
from tkinter.ttk import Frame, Button

import Toolinfo

ABOUT_CONTENT = [
    {"type": "spacer"},
    {"type": "row",      "label": "Toolname:",           "value": Toolinfo.tool_name},
    {"type": "row",      "label": "GitHub Project:",     "value": "https://github.com/togrupe/dlive-midi-tools"},
    {"type": "spacer"},
    {"type": "row",      "label": "Version:",            "value": Toolinfo.version},
    {"type": "row",      "label": "Build-Date:",         "value": Toolinfo.build_date},
    {"type": "row",      "label": "License:",            "value": "MIT License"},
    {"type": "spacer"},
    {"type": "row",      "label": "Idea & Development:", "value": "Tobias Grupe"},
    {"type": "row",      "label": "Testing Avantis:",    "value": "Matthieu Pochon"},
    {"type": "multirow", "label": "Testing dLive:",      "values": ["Tobias Grupe", "Zac Paton", "Tim-Lukas Arold", "Nathan May", "Günter Hellstern"]},
    {"type": "spacer"},
    {"type": "full",     "text": "Powered by Open Source"},
    {"type": "spacer"},
    {"type": "multirow", "label": "Used Python Modules:", "values": ["mido", "pandas", "openpyxl", "odfpy", "reathon", "pyinstaller"]},
    {"type": "spacer"},
    {"type": "row",      "label": "Contact/Feedback:",   "value": "dmt@liveworks-vt.de"},
]


class AboutDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About")
        self.resizable(False, False)
        self.create_widgets()
        self.update_idletasks()
        self.geometry(f"{self.winfo_reqwidth() + 40}x{self.winfo_reqheight() + 20}")

    def create_widgets(self):
        content_frame = Frame(self)
        row = 0

        for entry in ABOUT_CONTENT:
            kind = entry["type"]

            if kind == "spacer":
                tk.Label(content_frame, text="").grid(row=row, column=0, sticky=tk.W)
                row += 1

            elif kind == "row":
                tk.Label(content_frame, text=entry["label"]).grid(row=row, column=0, sticky=tk.W)
                tk.Label(content_frame, text=entry["value"]).grid(row=row, column=1, sticky=tk.W)
                row += 1

            elif kind == "multirow":
                tk.Label(content_frame, text=entry["label"]).grid(row=row, column=0, sticky=tk.W)
                for value in entry["values"]:
                    tk.Label(content_frame, text=value).grid(row=row, column=1, sticky=tk.W)
                    row += 1

            elif kind == "full":
                tk.Label(content_frame, text=entry["text"]).grid(row=row, column=0, columnspan=2, sticky=tk.W)
                row += 1

        content_frame.pack(side=TOP)

        bottom_frame = Frame(self)
        Button(bottom_frame, text="Close", command=self.destroy).pack(side=TOP)
        bottom_frame.pack(side=BOTTOM)
