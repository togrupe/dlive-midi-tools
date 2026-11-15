# coding=utf-8
####################################################
# Mixer Config - Dialog
# Lets the user type in the mixer config (amount of
# mono/stereo buses configured on the console).
# Buses beyond these amounts are not written.
# Configs can be stored as named presets per console.
#
# Author: Tobias Grupe
#
####################################################
import tkinter as tk
from tkinter import BOTTOM, TOP
from tkinter.messagebox import showerror, askyesno
from tkinter.simpledialog import askstring
from tkinter.ttk import Frame, Button, Combobox

from model.MixerConfig import MixerConfig, MIXER_CONFIG_ROWS, MIXER_CONFIG_RESERVED_BUSES, count_buses

COLOR_INVALID = "#F1948A"
COLOR_TEXT_INVALID = "#C0392B"

HINT_TEXT = ("This does not change the mixer config of the console, the amounts only\n"
             "serve as boundaries for the tool (the mixer config cannot be read out).\n"
             "Enter the amount of buses as configured on the mixer.\n"
             "Buses beyond these amounts are not written to the console.\n"
             "Mono buses are configured in pairs, so only even amounts are allowed.\n"
             "All fields are required, enter 0 for bus types which are not used.")


FIRST_WRITE_INTRO_TEXT = ("No mixer config saved for this console yet.\n"
                          "Please enter the amount of buses before writing,\n"
                          "it will be saved for the next writing process.")

PRESET_NAME_MAX_LENGTH = 40

EMPTY_FIELDS_TEXT = "Please fill in all fields (0 if a bus type is not used)."


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
        return "Mixer Config: not set (no limits)"

    def fmt(value):
        return "–" if value is None else str(value)

    rows = mixer_config_to_rows(mixer_config)
    return "Mixer Config: " + ", ".join(
        f"{label} {fmt(rows[label][0])}/{fmt(rows[label][1])}" for label in MIXER_CONFIG_ROWS)


class MixerConfigDialog(tk.Toplevel):
    """Modal dialog. After wait_window() returns, `result` holds the entered MixerConfig,
    or None if the user cancelled.

    `presets` gives access to the named presets of the console and provides
    names() -> [str], get(name) -> MixerConfig, save(name, MixerConfig) and delete(name)."""

    def __init__(self, parent, console_type, maxima, bus_pool, current, presets, intro=None):
        super().__init__(parent)
        self.title("Mixer Config - " + str(console_type))
        self.resizable(False, False)
        self.maxima = maxima
        self.bus_pool = bus_pool
        self.presets = presets
        self.result = None
        self.vars = {}
        self.entries = {}
        self.intro = intro
        self._create_widgets()
        if current is not None:
            self._fill(current)
            self._select_matching_preset(current)
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

        preset_frame = Frame(content_frame)
        tk.Label(preset_frame, text="Preset", font=("", 0, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.var_preset = tk.StringVar()
        self.combobox_preset = Combobox(preset_frame, textvariable=self.var_preset, state="readonly", width=24)
        self.combobox_preset.bind("<<ComboboxSelected>>", self._on_preset_selected)
        self.combobox_preset.pack(side=tk.LEFT, padx=5)
        self.btn_save_preset = Button(preset_frame, text="Save as Preset...", command=self._on_save_preset)
        self.btn_save_preset.pack(side=tk.LEFT, padx=5)
        self.btn_delete_preset = Button(preset_frame, text="Delete Preset", command=self._on_delete_preset)
        self.btn_delete_preset.pack(side=tk.LEFT, padx=5)
        preset_frame.grid(row=2, column=0, columnspan=4, padx=5, pady=(0, 10), sticky=tk.W)

        tk.Label(content_frame, text="Mono", font=("", 0, "bold")).grid(row=3, column=1, padx=5)
        tk.Label(content_frame, text="Stereo", font=("", 0, "bold")).grid(row=3, column=2, padx=5)

        for index, label in enumerate(MIXER_CONFIG_ROWS):
            row = index + 4
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
        self.bus_count_label.grid(row=len(MIXER_CONFIG_ROWS) + 4, column=0, columnspan=4,
                                  padx=5, pady=(8, 0), sticky=tk.W)
        self.default_label_fg = self.bus_count_label.cget("foreground")

        self.error_label = tk.Label(content_frame, justify=tk.LEFT, fg=COLOR_TEXT_INVALID)
        self.error_label.grid(row=len(MIXER_CONFIG_ROWS) + 5, column=0, columnspan=4,
                              padx=5, sticky=tk.W)

        tk.Label(content_frame, text=HINT_TEXT, justify=tk.LEFT).grid(
            row=len(MIXER_CONFIG_ROWS) + 6, column=0, columnspan=4, padx=5, pady=(10, 0), sticky=tk.W)

        content_frame.pack(side=TOP, padx=10)

        bottom_frame = Frame(self)
        Button(bottom_frame, text="Reset", command=self._on_reset).pack(side=tk.LEFT, padx=5)
        self.btn_ok = Button(bottom_frame, text="OK", command=self._on_ok)
        self.btn_ok.pack(side=tk.LEFT, padx=(20, 5))
        Button(bottom_frame, text="Cancel", command=self._on_cancel).pack(side=tk.LEFT, padx=5)
        bottom_frame.pack(side=BOTTOM, pady=10)

        self._refresh_presets()
        self._check_plausibility()

    def _field_value(self, label, kind, var, maximum):
        """(value, error) of an entry field. An empty field returns (None, None), the caller
        decides how to handle it. Mono amounts must be even, as mono buses are configured in pairs."""
        text = var.get().strip()
        if text == "":
            return None, None
        if not text.isdigit() or int(text) > maximum:
            return None, f"{label} {kind}: please enter a number between 0 and {maximum}."
        if kind == "Mono" and int(text) % 2 != 0:
            return None, f"{label} Mono: only even amounts are allowed (mono buses are configured in pairs)."
        return int(text), None

    def _on_value_changed(self, *args):
        self._check_plausibility()

    def _check_plausibility(self):
        """Marks invalid fields red. If more buses than the console provides are entered,
        all filled fields turn red. In both cases, and as long as a field is empty,
        "Save as Preset" and OK are disabled."""
        rows = {}
        invalid_fields = []
        errors = []
        empty_fields = 0
        for label in MIXER_CONFIG_ROWS:
            values = []
            for var, entry, maximum, kind in zip(self.vars[label], self.entries[label], self.maxima[label],
                                                 ("Mono", "Stereo")):
                value, error = self._field_value(label, kind, var, maximum)
                if error is not None:
                    invalid_fields.append(entry)
                    errors.append(error)
                elif value is None:
                    empty_fields += 1
                values.append(value)
            rows[label] = tuple(values)
        if empty_fields:
            errors.append(EMPTY_FIELDS_TEXT)
        self.error_label.configure(text="\n".join(errors))

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

        state = "disabled" if invalid_fields or empty_fields or pool_exceeded else "normal"
        self.btn_save_preset.configure(state=state)
        self.btn_ok.configure(state=state)

    def _parse(self):
        """Returns the entered MixerConfig or None (after showing an error) if invalid
        or a field is empty."""
        rows = {}
        for label in MIXER_CONFIG_ROWS:
            values = []
            for var, maximum, kind in zip(self.vars[label], self.maxima[label], ("Mono", "Stereo")):
                value, error = self._field_value(label, kind, var, maximum)
                if error is None and value is None:
                    error = EMPTY_FIELDS_TEXT
                if error is not None:
                    showerror(parent=self, message=error)
                    return None
                values.append(value)
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

    def _refresh_presets(self, selected=""):
        names = sorted(self.presets.names(), key=str.lower)
        self.combobox_preset.configure(values=names)
        self.var_preset.set(selected if selected in names else "")
        self.combobox_preset.configure(state="readonly" if names else "disabled")
        self.btn_delete_preset.configure(state="normal" if self.var_preset.get() else "disabled")

    def _select_matching_preset(self, mixer_config):
        rows = mixer_config_to_rows(mixer_config)
        for name in sorted(self.presets.names(), key=str.lower):
            preset = self.presets.get(name)
            if preset is not None and mixer_config_to_rows(preset) == rows:
                self._refresh_presets(selected=name)
                return

    def _on_preset_selected(self, *args):
        name = self.var_preset.get()
        mixer_config = self.presets.get(name)
        if mixer_config is not None:
            self._fill(mixer_config)
        self.btn_delete_preset.configure(state="normal" if name else "disabled")

    def _on_save_preset(self):
        mixer_config = self._parse()
        if mixer_config is None:
            return
        name = askstring("Save as Preset", "Preset name:", parent=self, initialvalue=self.var_preset.get())
        if name is None:
            return
        name = name.strip()
        if name == "" or len(name) > PRESET_NAME_MAX_LENGTH:
            showerror(parent=self, message=f"Please enter a preset name with 1 to {PRESET_NAME_MAX_LENGTH} characters.")
            return
        if name in self.presets.names() and not askyesno(
                parent=self, message=f"Preset \"{name}\" already exists. Overwrite it?"):
            return
        self.presets.save(name, mixer_config)
        self._refresh_presets(selected=name)

    def _on_delete_preset(self):
        name = self.var_preset.get()
        if not name or not askyesno(parent=self, message=f"Delete preset \"{name}\"?"):
            return
        self.presets.delete(name)
        self._refresh_presets()

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
