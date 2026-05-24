# coding=utf-8
####################################################
# CheckboxGrid Widget
#
# Author: Tobias Grupe
#
####################################################

import customtkinter as ctk
from tkinter import BooleanVar


class CheckboxGrid(ctk.CTkFrame):
    def __init__(self, parent, headers, labels):
        super().__init__(parent, fg_color="transparent")
        self.vars = []
        self.headers = headers
        self.labels = labels
        self.checkboxes = self.create_widgets()

    def create_widgets(self):
        self.checkboxes = []
        for i, header in enumerate(self.headers):
            self.columnconfigure(i, weight=1)
            frame = ctk.CTkFrame(self, border_width=1, border_color="white")
            frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

            ctk.CTkLabel(frame, text=header,
                         font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=0, padx=10, pady=(8, 4), sticky="w")

            group_vars = []
            for j, label in enumerate(self.labels[i]):
                var = BooleanVar(value=False, name=label)
                self.vars.append(var)
                checkbox = ctk.CTkCheckBox(frame, text=label, variable=var)
                checkbox.grid(row=j + 1, column=0, padx=10, pady=2, sticky="w")
                self.checkboxes.append(checkbox)
                group_vars.append(var)
            self.create_group_checkbox(frame, group_vars)
        return self.checkboxes

    def create_group_checkbox(self, parent, group_vars):
        group_var = BooleanVar()
        group_checkbox = ctk.CTkCheckBox(parent, text="Select All", variable=group_var,
                                         command=lambda: self.toggle_group(group_vars, group_var.get()))
        group_checkbox.grid(row=0, column=1, padx=8, pady=(8, 4), sticky="e")
        for var in group_vars:
            var.trace_add("write", lambda *_: group_var.set(all(v.get() for v in group_vars)))

    def toggle_group(self, group_vars, state):
        for var in group_vars:
            var.set(state)
