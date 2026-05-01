# coding=utf-8
####################################################
# CheckboxGrid Widget
#
# Author: Tobias Grupe
#
####################################################

from tkinter import Frame, Checkbutton, LabelFrame, BooleanVar


class CheckboxGrid(Frame):
    def __init__(self, parent, headers, labels):
        super().__init__(parent)
        self.vars = []
        self.headers = headers
        self.labels = labels
        self.checkboxes = self.create_widgets()

    def create_widgets(self):
        self.checkboxes = []
        for i, header in enumerate(self.headers):
            frame = LabelFrame(self, text=header)
            frame.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            group_vars = []
            for j, label in enumerate(self.labels[i]):
                var = BooleanVar(value=False, name=label)
                self.vars.append(var)
                checkbox = Checkbutton(frame, text=label, variable=var)
                checkbox.grid(row=j + 1, column=0, sticky="w")
                self.checkboxes.append(checkbox)
                group_vars.append(var)
            self.create_group_checkbox(frame, group_vars)
        return self.checkboxes

    def create_group_checkbox(self, parent, group_vars):
        group_var = BooleanVar()
        group_checkbox = Checkbutton(parent, text="Select All", variable=group_var,
                                     command=lambda: self.toggle_group(group_vars, group_var.get()))
        group_checkbox.grid(row=0, column=1, sticky="e")
        for var in group_vars:
            var.trace_add("write", lambda *_: group_var.set(all(var.get() for var in group_vars)))

    def toggle_group(self, group_vars, state):
        for var in group_vars:
            var.set(state)
