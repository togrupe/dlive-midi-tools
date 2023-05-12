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


class AboutDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About")
        self.geometry('600x500')
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        content_frame = Frame(self)

        space_label0 = tk.Label(content_frame, text="")
        space_label1 = tk.Label(content_frame, text="")
        space_label2 = tk.Label(content_frame, text="")
        space_label3 = tk.Label(content_frame, text="")

        # create labels for the about dialog
        toolname_label = tk.Label(content_frame, text="Toolname:")
        toolname_value = tk.Label(content_frame, text=Toolinfo.tool_name)

        github_project_label = tk.Label(content_frame, text="GitHub Project:")
        github_project_value = tk.Label(content_frame, text="https://github.com/togrupe/dlive-midi-tools")

        version_label = tk.Label(content_frame, text="Version:")
        version_value = tk.Label(content_frame, text=Toolinfo.version)

        build_label = tk.Label(content_frame, text="Build-Date:")
        build_value = tk.Label(content_frame, text=Toolinfo.build_date)

        license_label = tk.Label(content_frame, text="License:")
        license_value = tk.Label(content_frame, text="MIT License")

        team0_label = tk.Label(content_frame, text="Idea & Development:")
        team0_value = tk.Label(content_frame, text="Tobias Grupe")

        team1_label = tk.Label(content_frame, text="Testing Avantis:")
        team1_value = tk.Label(content_frame, text="Matthieu Pochon")

        team2_label = tk.Label(content_frame, text="Testing dLive:")
        team2_value = tk.Label(content_frame, text="Tobias Grupe")

        opensource_label = tk.Label(content_frame, text="Powered by Open Source")

        python_modules_label = tk.Label(content_frame, text="Used Python Modules:")
        python_modules_value0 = tk.Label(content_frame, text="mido")
        python_modules_value1 = tk.Label(content_frame, text="pandas")
        python_modules_value2 = tk.Label(content_frame, text="openpyxl")
        python_modules_value3 = tk.Label(content_frame, text="odfpy")
        python_modules_value4 = tk.Label(content_frame, text="reathon")
        python_modules_value5 = tk.Label(content_frame, text="pyinstaller")

        # set the grid layout for the labels
        toolname_label.grid(row=0, column=0, sticky=tk.W)
        github_project_label.grid(row=1, column=0, sticky=tk.W)
        space_label0.grid(row=2, column=0, sticky=tk.W)
        version_label.grid(row=3, column=0, sticky=tk.W)
        build_label.grid(row=4, column=0, sticky=tk.W)
        license_label.grid(row=5, column=0, sticky=tk.W)
        space_label1.grid(row=6, column=0, sticky=tk.W)
        team0_label.grid(row=7, column=0, sticky=tk.W)
        team1_label.grid(row=8, column=0, sticky=tk.W)
        team2_label.grid(row=9, column=0, sticky=tk.W)
        space_label2.grid(row=10, column=0, sticky=tk.W)
        opensource_label.grid(row=11, column=0, sticky=tk.W)
        space_label3.grid(row=12, column=0, sticky=tk.W)
        python_modules_label.grid(row=13, column=0, sticky=tk.W)

        # set the grid layout for the values
        toolname_value.grid(row=0, column=1, sticky=tk.W)
        github_project_value.grid(row=1, column=1, sticky=tk.W)

        version_value.grid(row=3, column=1, sticky=tk.W)
        build_value.grid(row=4, column=1, sticky=tk.W)
        license_value.grid(row=5, column=1, sticky=tk.W)

        team0_value.grid(row=7, column=1, sticky=tk.W)
        team1_value.grid(row=8, column=1, sticky=tk.W)
        team2_value.grid(row=9, column=1, sticky=tk.W)

        python_modules_value0.grid(row=13, column=1, sticky=tk.W)
        python_modules_value1.grid(row=14, column=1, sticky=tk.W)
        python_modules_value2.grid(row=15, column=1, sticky=tk.W)
        python_modules_value3.grid(row=16, column=1, sticky=tk.W)
        python_modules_value4.grid(row=17, column=1, sticky=tk.W)
        python_modules_value5.grid(row=18, column=1, sticky=tk.W)

        content_frame.pack(side=TOP)

        bottom_frame = Frame(self)
        Button(bottom_frame, text="Close", command=self.destroy).pack(side=TOP)
        bottom_frame.pack(side=BOTTOM)
