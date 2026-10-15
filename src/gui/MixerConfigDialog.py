# coding=utf-8
####################################################
# Mixer Config - Dialog
# Lets the user type in the mixer config (amount of
# mono/stereo buses configured on the console).
# Buses beyond these amounts are not written.
#
# Author: Tobias Grupe
#
####################################################
import tkinter as tk
from tkinter import BOTTOM, TOP
from tkinter.messagebox import showerror, showinfo
from tkinter.ttk import Frame, Button

from model.MixerConfig import MixerConfig, MIXER_CONFIG_ROWS, MIXER_CONFIG_RESERVED_BUSES, count_buses

COLOR_INVALID = "#F1948A"
COLOR_TEXT_INVALID = "#C0392B"

HINT_TEXT = ("Enter the amount of buses as configured on the mixer.\n"
             "Buses beyond these amounts are not written to the console.\n"
             "Leave a field empty to use the console maximum.")


FIRST_WRITE_INTRO_TEXT = ("No mixer config saved for this console yet.\n"
                          "Please enter the amount of buses before writing,\n"
                          "it will be saved for the next writing process.")


def mixer_config_to_rows(mixer_config):
    return {
        "Group": (mixer_config.get_group_mono(), mixer_config.get_group_stereo()),
        "FX": (mixer_config.get_fx_mono(), mixer_config.get_fx_stereo()),
        "Aux": (mixer_config.get_aux_mono(), mixer_config.get_aux_stereo()),
        "Matrix": (mixer_config.get_matrix_mono(), mixer_config.get_matrix_stereo()),
    }


def mixer_config_from_rows(rows):
    return MixerConfig(rows["Group"][0], rows["Group"][1], rows["FX"][0], rows["FX"][1],
                       rows["Aux"][0], rows["Aux"][1], rows["Matrix"][0], rows["Matrix"][1])


def mixer_config_summary(mixer_config):
    if mixer_config is None:
        return "Mixer Config: console maximum"

    def fmt(value):
        return "max" if value is None else str(value)

    rows = mixer_config_to_rows(mixer_config)
    return "Mixer Config: " + ", ".join(
        f"{label} {fmt(rows[label][0])}/{fmt(rows[label][1])}" for label in MIXER_CONFIG_ROWS)


class MixerConfigDialog(tk.Toplevel):
    """Modal dialog. After wait_window() returns, `result` holds the entered MixerConfig,
    or None if the user cancelled."""

    def __init__(self, parent, console_type, maxima, bus_pool, current, on_save, on_recall, intro=None):
        super().__init__(parent)
        self.title("Mixer Config - " + str(console_type))
        self.resizable(False, False)
        self.maxima = maxima
        self.bus_pool = bus_pool
        self.on_save = on_save
        self.on_recall = on_recall
        self.result = None
        self.vars = {}
        self.entries = {}
        self.intro = intro
        self._create_widgets()
        if current is not None:
            self._fill(current)
        self.update_idletasks()
        self.geometry(f"{self.winfo_reqwidth() + 40}x{self.winfo_reqheight() + 20}")

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.transient(parent)
        self.wait_visibility()
        self.grab_set()
        self.focus_set()

    def _create_widgets(self):
        content_frame = Frame(self)

        tk.Label(content_frame, text="Mixer Config", font=("", 14, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(10, 4))

        if self.intro is not None:
            tk.Label(content_frame, text=self.intro, justify=tk.LEFT, fg="#C0392B").grid(
                row=1, column=0, columnspan=4, padx=5, pady=(0, 8), sticky=tk.W)

        tk.Label(content_frame, text="Mono", font=("", 0, "bold")).grid(row=2, column=1, padx=5)
        tk.Label(content_frame, text="Stereo", font=("", 0, "bold")).grid(row=2, column=2, padx=5)

        for index, label in enumerate(MIXER_CONFIG_ROWS):
            row = index + 3
            mono_max, stereo_max = self.maxima[label]
            tk.Label(content_frame, text=label, font=("", 0, "bold")).grid(
                row=row, column=0, padx=5, pady=2, sticky=tk.W)
            mono_var = tk.StringVar()
            stereo_var = tk.StringVar()
            mono_entry = tk.Entry(content_frame, textvariable=mono_var, width=6, justify=tk.CENTER)
            mono_entry.grid(row=row, column=1, padx=5, pady=2)
            stereo_entry = tk.Entry(content_frame, textvariable=stereo_var, width=6, justify=tk.CENTER)
            stereo_entry.grid(row=row, column=2, padx=5, pady=2)
            tk.Label(content_frame, text=f"(max {mono_max} / {stereo_max})").grid(
                row=row, column=3, padx=5, pady=2, sticky=tk.W)
            self.vars[label] = (mono_var, stereo_var)
            self.entries[label] = (mono_entry, stereo_entry)
            mono_var.trace_add("write", self._on_value_changed)
            stereo_var.trace_add("write", self._on_value_changed)

        self.default_entry_bg = mono_entry.cget("background")
        self.default_entry_fg = mono_entry.cget("foreground")

        self.bus_count_label = tk.Label(content_frame, font=("", 0, "bold"))
        self.bus_count_label.grid(row=len(MIXER_CONFIG_ROWS) + 3, column=0, columnspan=4,
                                  padx=5, pady=(8, 0), sticky=tk.W)
        self.default_label_fg = self.bus_count_label.cget("foreground")

        tk.Label(content_frame, text=HINT_TEXT, justify=tk.LEFT).grid(
            row=len(MIXER_CONFIG_ROWS) + 4, column=0, columnspan=4, padx=5, pady=(10, 0), sticky=tk.W)

        content_frame.pack(side=TOP, padx=10)

        bottom_frame = Frame(self)
        Button(bottom_frame, text="Recall", command=self._on_recall).pack(side=tk.LEFT, padx=5)
        self.btn_save = Button(bottom_frame, text="Save", command=self._on_save)
        self.btn_save.pack(side=tk.LEFT, padx=5)
        Button(bottom_frame, text="Reset", command=self._on_reset).pack(side=tk.LEFT, padx=5)
        self.btn_ok = Button(bottom_frame, text="OK", command=self._on_ok)
        self.btn_ok.pack(side=tk.LEFT, padx=(20, 5))
        Button(bottom_frame, text="Cancel", command=self._on_cancel).pack(side=tk.LEFT, padx=5)
        bottom_frame.pack(side=BOTTOM, pady=10)

        self._check_plausibility()

    def _field_value(self, var, maximum):
        """(value, valid) of an entry field. Empty is valid with value None."""
        text = var.get().strip()
        if text == "":
            return None, True
        if not text.isdigit() or int(text) > maximum:
            return None, False
        return int(text), True

    def _on_value_changed(self, *args):
        self._check_plausibility()

    def _check_plausibility(self):
        """Marks invalid fields red. If more buses than the console provides are entered,
        all filled fields turn red. In both cases Save and OK are disabled."""
        rows = {}
        invalid_fields = []
        for label in MIXER_CONFIG_ROWS:
            values = []
            for var, entry, maximum in zip(self.vars[label], self.entries[label], self.maxima[label]):
                value, valid = self._field_value(var, maximum)
                if not valid:
                    invalid_fields.append(entry)
                values.append(value)
            rows[label] = tuple(values)

        bus_count = count_buses(rows)
        pool_exceeded = self.bus_pool is not None and bus_count > self.bus_pool

        for label in MIXER_CONFIG_ROWS:
            for var, entry in zip(self.vars[label], self.entries[label]):
                mark = entry in invalid_fields or (pool_exceeded and var.get().strip() != "")
                entry.configure(background=COLOR_INVALID if mark else self.default_entry_bg,
                                foreground="black" if mark else self.default_entry_fg)

        if self.bus_pool is None:
            self.bus_count_label.configure(text=f"Buses: {bus_count}")
        else:
            text = (f"Buses: {bus_count} / {self.bus_pool}  "
                    f"(+{MIXER_CONFIG_RESERVED_BUSES} for LR & PAFL, stereo counts twice)")
            if pool_exceeded:
                text += f" - {bus_count - self.bus_pool} too many"
            self.bus_count_label.configure(text=text,
                                           fg=COLOR_TEXT_INVALID if pool_exceeded else self.default_label_fg)

        state = "disabled" if invalid_fields or pool_exceeded else "normal"
        self.btn_save.configure(state=state)
        self.btn_ok.configure(state=state)

    def _parse(self):
        """Returns the entered MixerConfig or None (after showing an error) if invalid.
        Empty fields mean "not limited"."""
        rows = {}
        for label in MIXER_CONFIG_ROWS:
            values = []
            for var, maximum, kind in zip(self.vars[label], self.maxima[label], ("Mono", "Stereo")):
                text = var.get().strip()
                if text == "":
                    values.append(None)
                    continue
                if not text.isdigit() or int(text) > maximum:
                    showerror(parent=self, message=f"{label} {kind}: please enter a number between 0 and {maximum}"
                                                   f" or leave the field empty.")
                    return None
                values.append(int(text))
            rows[label] = tuple(values)
        if self.bus_pool is not None and count_buses(rows) > self.bus_pool:
            showerror(parent=self, message=f"{count_buses(rows)} buses entered, the console provides "
                                           f"{self.bus_pool} buses besides LR and PAFL "
                                           f"(a stereo bus counts twice).")
            return None
        return mixer_config_from_rows(rows)

    def _fill(self, mixer_config):
        rows = mixer_config_to_rows(mixer_config)
        for label in MIXER_CONFIG_ROWS:
            for var, value in zip(self.vars[label], rows[label]):
                var.set("" if value is None else str(value))

    def _on_recall(self):
        mixer_config = self.on_recall()
        if mixer_config is None:
            showinfo(parent=self, message="No saved mixer config found for this console.")
            return
        self._fill(mixer_config)

    def _on_save(self):
        mixer_config = self._parse()
        if mixer_config is None:
            return
        self.on_save(mixer_config)
        showinfo(parent=self, message="Mixer config saved.")

    def _on_reset(self):
        for mono_var, stereo_var in self.vars.values():
            mono_var.set("")
            stereo_var.set("")

    def _on_ok(self):
        mixer_config = self._parse()
        if mixer_config is None:
            return
        self.result = mixer_config
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()
