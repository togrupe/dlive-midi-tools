# coding=utf-8
####################################################
# Donate - Dialog
#
# Author: Tobias Grupe
#
####################################################
import webbrowser
import tkinter as tk
from tkinter import BOTTOM, TOP
from tkinter.ttk import Frame, Button

DONATE_URL = 'https://buymeacoffee.com/togrupe'

DONATE_TEXT = (
    "dlive-midi-tools is a free, open-source project developed and\n"
    "maintained in my spare time. If it saves you time at your gigs\n"
    "or studio sessions, consider buying me a coffee — it keeps the\n"
    "project alive and motivates future development.\n\n"
    "Every contribution, no matter how small, is deeply appreciated!\n"
    "Thank you for your support. ♥"
)


class DonateDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Support dlive-midi-tools")
        self.resizable(False, False)
        self._create_widgets()
        self.update_idletasks()
        self.geometry(f"{self.winfo_reqwidth() + 40}x{self.winfo_reqheight() + 20}")

    def _create_widgets(self):
        content_frame = Frame(self)

        tk.Label(content_frame, text="☕  Buy Me a Coffee", font=("", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(10, 4))

        tk.Label(content_frame, text=DONATE_TEXT, justify=tk.LEFT).grid(
            row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky=tk.W)

        tk.Label(content_frame, text=DONATE_URL, foreground="blue", cursor="hand2").grid(
            row=2, column=0, columnspan=2, pady=(0, 10))

        content_frame.pack(side=TOP, padx=10)

        bottom_frame = Frame(self)
        Button(bottom_frame, text="☕  Donate Now",
               command=lambda: webbrowser.open(DONATE_URL)).pack(side=tk.LEFT, padx=5)
        Button(bottom_frame, text="Close", command=self.destroy).pack(side=tk.LEFT, padx=5)
        bottom_frame.pack(side=BOTTOM, pady=10)
