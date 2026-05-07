# coding=utf-8
####################################################
# Main View
#
# Author: Tobias Grupe
#
####################################################

from tkinter import Tk, Frame, LabelFrame, Label, Entry, Button, StringVar, BooleanVar, \
    OptionMenu, Menu, LEFT, RIGHT, TOP, BOTTOM, X, END, ttk, Checkbutton
from tkinter.ttk import Combobox

import GuiConstants
import Toolinfo
import dliveConstants
from gui.CheckboxGrid import CheckboxGrid


class MainView:
    def __init__(self):
        self.root = Tk()
        self.root.title(Toolinfo.tool_name + ' - v' + Toolinfo.version)
        self.root.geometry('1320x875')
        self.root.resizable(False, False)

        # String/bool vars
        self.var_midi_channel = StringVar(self.root)
        self.var_console = StringVar(self.root)

        # File output attributes (not on root)
        self.reaper_output_dir = ""
        self.reaper_file_prefix = ""

        self._build_ui()

    def _build_ui(self):
        self._create_menu()
        self._create_tabs()
        self._create_connection_settings()
        self._create_tab1_content()
        self._create_tab2_content()
        self._create_tab3_content()
        self._create_status_area()
        self._finalize_layout()

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------

    def _create_menu(self):
        menu_bar = Menu(self.root)

        self.file_menu = Menu(menu_bar, tearoff=0)
        self.file_menu.add_command(label="Documentation")  # index 0 – controller binds command
        self.file_menu.add_command(label="Donate ☕")      # index 1 – controller binds command
        self.file_menu.add_separator()
        self.file_menu.add_command(label="About")          # index 3 – controller binds command
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Close", command=self.root.destroy)

        menu_bar.add_cascade(label="Help", menu=self.file_menu)
        self.root.config(menu=menu_bar)

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------

    def _create_tabs(self):
        self.tab_control = ttk.Notebook(self.root)

        self.tab1 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text='Spreadsheet to Console / DAW')

        self.tab2 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab2, text='Console to DAW')

        self.tab3 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab3, text='Helpers')

        self.tab1_frame = LabelFrame(self.tab1, text='Spreadsheet to Console / DAW')
        self.tab2_frame = LabelFrame(self.tab2, text='Console to DAW')

    # ------------------------------------------------------------------
    # Connection Settings (packed side=TOP first)
    # ------------------------------------------------------------------

    def _create_connection_settings(self):
        config_frame = LabelFrame(self.root, text="Connection Settings")

        console_frame = Frame(config_frame)
        console_frame.grid(row=1, column=0, sticky="W")

        ip_frame = Frame(config_frame)
        ip_frame.grid(row=2, column=0, sticky="W")

        midi_channel_frame = Frame(config_frame)
        midi_channel_frame.grid(row=3, column=0, sticky="W")

        # --- Console dropdown ---
        Label(console_frame, text="Audio Console:", width=25).pack(side=LEFT)
        dropdown_console = OptionMenu(console_frame, self.var_console,
                                      dliveConstants.console_drop_down_dlive,
                                      dliveConstants.console_drop_down_avantis)
        dropdown_console.pack(side=RIGHT)

        # --- IP address row ---
        self.label_ip_address_text = Label(ip_frame, text="", width=25)
        self.label_ip_address_text.pack(side=LEFT)

        ip_field = Frame(ip_frame)
        self.ip_byte0 = Entry(ip_field, width=3)
        self.ip_byte1 = Entry(ip_field, width=3)
        self.ip_byte2 = Entry(ip_field, width=3)
        self.ip_byte3 = Entry(ip_field, width=3)

        self.ip_byte0.grid(row=0, column=0)
        Label(ip_field, text=".").grid(row=0, column=1)
        self.ip_byte1.grid(row=0, column=2)
        Label(ip_field, text=".").grid(row=0, column=3)
        self.ip_byte2.grid(row=0, column=4)
        Label(ip_field, text=".").grid(row=0, column=5)
        self.ip_byte3.grid(row=0, column=6)
        Label(ip_field, text="     ").grid(row=0, column=7)

        self.btn_save = Button(ip_field, text='Save')
        self.btn_save.grid(row=0, column=8)

        self.btn_director = Button(ip_field, text='Director')
        self.btn_director.grid(row=0, column=9)

        self.btn_default = Button(ip_field, text='Default')
        self.btn_default.grid(row=0, column=10)

        self.btn_test_connection = Button(ip_field, text='Test Connection')
        self.btn_test_connection.grid(row=0, column=11)

        ip_field.pack(side=RIGHT)

        # --- MIDI channel dropdown ---
        Label(midi_channel_frame, text="Midi Channel:", width=25).pack(side=LEFT)
        dropdown_midi_channel = OptionMenu(midi_channel_frame, self.var_midi_channel,
                                           dliveConstants.midi_channel_drop_down_string_1,
                                           dliveConstants.midi_channel_drop_down_string_2,
                                           dliveConstants.midi_channel_drop_down_string_3,
                                           dliveConstants.midi_channel_drop_down_string_4,
                                           dliveConstants.midi_channel_drop_down_string_5,
                                           dliveConstants.midi_channel_drop_down_string_6,
                                           dliveConstants.midi_channel_drop_down_string_7,
                                           dliveConstants.midi_channel_drop_down_string_8,
                                           dliveConstants.midi_channel_drop_down_string_9,
                                           dliveConstants.midi_channel_drop_down_string_10,
                                           dliveConstants.midi_channel_drop_down_string_11,
                                           dliveConstants.midi_channel_drop_down_string_12)
        dropdown_midi_channel.pack(side=RIGHT)

        config_frame.pack(side=TOP)

    # ------------------------------------------------------------------
    # Tab 1 – Spreadsheet to Console / DAW
    # ------------------------------------------------------------------

    def _create_tab1_content(self):
        parameter_lf = LabelFrame(self.tab1, text="Choose from given spreadsheet which column you want to write")

        headers = ["Channels", "Sockets / Preamps", "Auxes & Groups", "DCAs & Matrices", "FX Sends & Returns"]
        labels = [
            [GuiConstants.TEXT_NAME,
             GuiConstants.TEXT_COLOR,
             GuiConstants.TEXT_HPF_ON,
             GuiConstants.TEXT_HPF_VALUE,
             GuiConstants.TEXT_MUTE,
             GuiConstants.TEXT_FADER_LEVEL,
             GuiConstants.TEXT_DCA,
             GuiConstants.TEXT_MUTE_GROUPS,
             GuiConstants.TEXT_MAINMIX,
             GuiConstants.TEXT_MONO_GROUP_ASSIGN,
             GuiConstants.TEXT_STEREO_GROUP_ASSIGN
             ],
            [GuiConstants.TEXT_PHANTOM,
             GuiConstants.TEXT_PAD,
             GuiConstants.TEXT_GAIN
             ],
            [GuiConstants.TEXT_AUX_MONO_NAME,
             GuiConstants.TEXT_AUX_MONO_COLOR,
             GuiConstants.TEXT_AUX_STEREO_NAME,
             GuiConstants.TEXT_AUX_STEREO_COLOR,
             GuiConstants.TEXT_GRP_MONO_NAME,
             GuiConstants.TEXT_GRP_MONO_COLOR,
             GuiConstants.TEXT_GRP_STEREO_NAME,
             GuiConstants.TEXT_GRP_STEREO_COLOR
             ],
            [GuiConstants.TEXT_DCA_NAME,
             GuiConstants.TEXT_DCA_COLOR,
             GuiConstants.TEXT_MTX_MONO_NAME,
             GuiConstants.TEXT_MTX_MONO_COLOR,
             GuiConstants.TEXT_MTX_STEREO_NAME,
             GuiConstants.TEXT_MTX_STEREO_COLOR
             ],
            [GuiConstants.TEXT_FX_SEND_MONO_NAME,
             GuiConstants.TEXT_FX_SEND_MONO_COLOR,
             GuiConstants.TEXT_FX_SEND_STEREO_NAME,
             GuiConstants.TEXT_FX_SEND_STEREO_COLOR,
             GuiConstants.TEXT_FX_RETURN_NAME,
             GuiConstants.TEXT_FX_RETURN_COLOR,
             GuiConstants.TEXT_UFX_SEND_NAME,
             GuiConstants.TEXT_UFX_SEND_COLOR,
             GuiConstants.TEXT_UFX_RETURN_NAME,
             GuiConstants.TEXT_UFX_RETURN_COLOR
             ]
        ]

        self.grid = CheckboxGrid(parameter_lf, headers, labels)
        self.grid.pack(side=TOP)

        global_select_frame = Frame(parameter_lf)

        self.btn_select_all = Button(global_select_frame, text='Select All', width=8)
        self.btn_select_all.grid(row=0, column=0)

        self.btn_clear_all = Button(global_select_frame, text='Clear', width=8)
        self.btn_clear_all.grid(row=0, column=1)

        parameter_lf.pack(pady=10, side=TOP)
        global_select_frame.pack(side=TOP)

        # --- Output Options ---
        output_option_frame = LabelFrame(self.tab1, text="Output Options")

        self.var_write_to_csv = BooleanVar(value=False)
        write_to_csv = Checkbutton(output_option_frame,
                                   text="Generate Director CSV (Columns: Name, Color, Source, Socket, Gain, Pad, Phantom)",
                                   var=self.var_write_to_csv)

        self.var_write_to_console = BooleanVar(value=True)
        write_to_console = Checkbutton(output_option_frame,
                                       text="Write to Audio Console or Director",
                                       var=self.var_write_to_console)

        self.var_write_reaper = BooleanVar(value=False)
        self.cb_reaper_write = Checkbutton(output_option_frame,
                                           text="Generate Reaper Recording Session with Name & Color (In & Out 1:1 Patch)",
                                           var=self.var_write_reaper)

        self.var_write_trackslive = BooleanVar(value=False)
        self.cb_trackslive_write = Checkbutton(output_option_frame,
                                               text="Generate Tracks Live Template with Name & Color (In & Out 1:1 Patch)",
                                               var=self.var_write_trackslive)

        self.var_disable_track_numbering = BooleanVar(value=False)
        self.cb_reaper_disable_numbering = Checkbutton(output_option_frame,
                                                       text="Disable Track Numbering",
                                                       var=self.var_disable_track_numbering)

        self.var_disable_track_coloring = BooleanVar(value=False)
        self.cb_reaper_disable_track_coloring = Checkbutton(output_option_frame,
                                                            text="Disable Track Coloring",
                                                            var=self.var_disable_track_coloring)

        self.label_track_prefix = Label(output_option_frame, text="Example: Band_Date_City", width=30)

        self.var_reaper_additional_prefix = BooleanVar(value=False)
        self.cb_reaper_additional_prefix = Checkbutton(output_option_frame,
                                                       text="Add Custom Track Prefix",
                                                       var=self.var_reaper_additional_prefix)

        self.entry_additional_track_prefix = Entry(output_option_frame, width=20)

        self.var_reaper_additional_master_tracks = BooleanVar(value=False)
        self.cb_reaper_additional_master_tracks = Checkbutton(output_option_frame,
                                                              text="Add 2 Additional Master-Tracks",
                                                              var=self.var_reaper_additional_master_tracks)

        values = [f"{i}-{i + 1}" for i in range(1, 127, 2)]
        values.append("127-128")  # workaround
        self.var_master_recording_patch = StringVar()
        self.combobox_master_track = Combobox(output_option_frame,
                                              textvariable=self.var_master_recording_patch,
                                              values=values)
        self.combobox_master_track.set("Select DAW Input")

        # Layout grid for output options
        write_to_console.grid(row=0, column=0, sticky="W")
        self.cb_reaper_write.grid(row=1, column=0, sticky="W")
        self.cb_reaper_disable_numbering.grid(row=1, column=1, sticky="W")
        self.cb_reaper_disable_track_coloring.grid(row=2, column=1, sticky="W")
        self.cb_reaper_additional_prefix.grid(row=3, column=1, sticky="W")
        self.entry_additional_track_prefix.grid(row=3, column=2, sticky="W")
        self.label_track_prefix.grid(row=3, column=3, sticky="W")
        self.cb_reaper_additional_master_tracks.grid(row=4, column=1, sticky="W")
        self.combobox_master_track.grid(row=4, column=2, sticky="W")
        self.cb_trackslive_write.grid(row=2, column=0, sticky="W")
        write_to_csv.grid(row=5, column=0, sticky="W")

        output_option_frame.pack(side=TOP, fill=X)

        # --- Bottom frame with Open Spreadsheet button ---
        bottom_frame = Frame(self.tab1)

        self.btn_open_spreadsheet = Button(bottom_frame,
                                           text='Open spreadsheet and start writing process')
        self.btn_open_spreadsheet.grid(row=0, column=0)
        Label(bottom_frame, text=" ", width=30).grid(row=1)

        bottom_frame.pack(side=BOTTOM)

    # ------------------------------------------------------------------
    # Tab 2 – Console to DAW
    # ------------------------------------------------------------------

    def _create_tab2_content(self):
        console_to_daw_settings_lf = LabelFrame(self.tab2, text="Settings")
        console_to_daw_settings_lf.pack(side=TOP)

        start_end_channel_frame = Frame(console_to_daw_settings_lf)

        values_start = [f"{i}" for i in range(1, 129)]
        self.var_current_console_startChannel = StringVar()
        self.combobox_start = Combobox(start_end_channel_frame,
                                       textvariable=self.var_current_console_startChannel,
                                       values=values_start, width=3)
        self.combobox_start.set("1")

        Label(start_end_channel_frame, text="Channel Start").grid(row=0, column=0, sticky="w")
        self.combobox_start.grid(row=0, column=1)

        values_end = [f"{i}" for i in range(1, 129)]
        self.var_current_console_endChannel = StringVar()
        self.combobox_end = Combobox(start_end_channel_frame,
                                     textvariable=self.var_current_console_endChannel,
                                     values=values_end, width=3)
        self.combobox_end.set("128")
        Label(start_end_channel_frame, text="End").grid(row=0, column=2)
        self.combobox_end.grid(row=0, column=3)

        start_end_channel_frame.grid(row=0)

        self.var_console_to_daw_disable_track_numbering_daw = BooleanVar(value=False)
        cb_console_to_daw_disable_track_numbering_daw = Checkbutton(
            console_to_daw_settings_lf,
            text="Disable Track Numbering",
            var=self.var_console_to_daw_disable_track_numbering_daw)

        self.var_console_to_daw_disable_track_coloring_daw = BooleanVar(value=False)
        cb_console_to_daw_disable_track_coloring_daw = Checkbutton(
            console_to_daw_settings_lf,
            text="Disable Track Coloring",
            var=self.var_console_to_daw_disable_track_coloring_daw)

        self.var_console_to_daw_reaper_additional_prefix = BooleanVar(value=False)
        self.cb_console_to_daw_reaper_additional_prefix = Checkbutton(
            console_to_daw_settings_lf,
            text="Add Custom Track Prefix",
            var=self.var_console_to_daw_reaper_additional_prefix)

        self.entry_console_to_daw_additional_track_prefix = Entry(console_to_daw_settings_lf, width=20)

        self.label_console_to_daw_track_prefix = Label(console_to_daw_settings_lf,
                                                        text="Example: Band_Date_City", width=25)

        self.var_console_to_daw_additional_master_tracks = BooleanVar(value=False)
        self.cb_console_to_daw_additional_master_tracks = Checkbutton(
            console_to_daw_settings_lf,
            text="Add 2 Additional Master-Tracks",
            var=self.var_console_to_daw_additional_master_tracks)

        values = [f"{i}-{i + 1}" for i in range(1, 127, 2)]
        values.append("127-128")  # workaround
        self.var_console_to_daw_master_recording_patch = StringVar()
        self.combobox_console_to_daw_master_track = Combobox(
            console_to_daw_settings_lf,
            textvariable=self.var_console_to_daw_master_recording_patch,
            values=values)
        self.combobox_console_to_daw_master_track.set("Select DAW Input")

        # --- Output Options ---
        console_to_daw_output_options_lf = LabelFrame(self.tab2, text="Output Options")

        self.var_console_to_daw_reaper = BooleanVar(value=False)
        cb_console_to_daw_reaper = Checkbutton(console_to_daw_output_options_lf,
                                               text="Generate Reaper Session",
                                               var=self.var_console_to_daw_reaper)

        self.var_console_to_daw_trackslive = BooleanVar(value=False)
        cb_console_to_daw_trackslive = Checkbutton(console_to_daw_output_options_lf,
                                                   text="Generate Tracks Live Template",
                                                   var=self.var_console_to_daw_trackslive)

        label_space = Label(console_to_daw_output_options_lf, width=48)

        cb_console_to_daw_reaper.grid(row=0, column=0, sticky="w")
        label_space.grid(row=0, column=1, sticky="w")
        cb_console_to_daw_trackslive.grid(row=1, sticky="w")

        console_to_daw_output_options_lf.pack(side=TOP)

        # Settings grid (rows 1–4 come after start/end channel frame at row 0)
        cb_console_to_daw_disable_track_numbering_daw.grid(row=1, sticky="w")
        cb_console_to_daw_disable_track_coloring_daw.grid(row=2, sticky="w")
        self.cb_console_to_daw_reaper_additional_prefix.grid(row=3, column=0, sticky="w")
        self.entry_console_to_daw_additional_track_prefix.grid(row=3, column=1, sticky="w")
        self.label_console_to_daw_track_prefix.grid(row=3, column=2)
        self.cb_console_to_daw_additional_master_tracks.grid(row=4, column=0, sticky="w")
        self.combobox_console_to_daw_master_track.grid(row=4, column=1, sticky="w")

        # --- Console to DAW action button ---
        button_frame = Frame(self.tab2)

        self.btn_console_to_daw = Button(button_frame,
                                         text='Generate DAW session(s) from current console settings')
        self.btn_console_to_daw.pack(side=BOTTOM)

        button_frame.pack(side=TOP)

    # ------------------------------------------------------------------
    # Tab 3 – Helpers
    # ------------------------------------------------------------------

    def _create_tab3_content(self):
        reset_frame = LabelFrame(self.tab3, text="Reset")

        self.btn_reset_dca = Button(reset_frame, text='RESET all DCA Assignments', width=35)
        self.btn_reset_mute_groups = Button(reset_frame, text='RESET all Mute Group Assignments', width=35)
        self.btn_reset_main_mix = Button(reset_frame, text='RESET all Main Assignments', width=35)

        self.btn_reset_dca.grid(row=0, column=0, padx=10, pady=5, sticky='W')
        self.btn_reset_mute_groups.grid(row=0, column=1, padx=10, pady=5, sticky='W')
        self.btn_reset_main_mix.grid(row=0, column=2, padx=10, pady=5, sticky='W')

        reset_frame.pack(side=TOP, fill=X, padx=10, pady=10)

        mute_frame = LabelFrame(self.tab3, text="Mute")

        self.btn_mute_all_inputs = Button(mute_frame, text='MUTE all Inputs', width=35)
        self.btn_mute_all_outputs = Button(mute_frame, text='MUTE all Outputs', width=35)

        self.btn_mute_all_inputs.grid(row=0, column=0, padx=10, pady=5, sticky='W')
        self.btn_mute_all_outputs.grid(row=0, column=1, padx=10, pady=5, sticky='W')

        mute_frame.pack(side=TOP, fill=X, padx=10, pady=10)

    def disable_helpers_avantis(self):
        self.btn_reset_mute_groups.config(state='disabled')

    def enable_helpers_avantis(self):
        self.btn_reset_mute_groups.config(state='normal')

    # ------------------------------------------------------------------
    # Status Area (packed side=BOTTOM)
    # ------------------------------------------------------------------

    def _create_status_area(self):
        bottom4_frame = Frame(self.root)
        Button(bottom4_frame, text='Close', command=self.root.destroy).grid(row=6)
        Label(bottom4_frame, text=" ", width=30).grid(row=7)
        bottom4_frame.pack(side=BOTTOM)

        bottom3_frame = LabelFrame(self.root, text="Status")

        self.current_action_label = ttk.Label(bottom3_frame, text="")
        self.current_action_label.grid(row=3)
        Label(bottom3_frame, text=" ", width=30).grid(row=5)

        self.pb = ttk.Progressbar(
            bottom3_frame,
            orient='horizontal',
            mode='determinate',
            length=1250
        )
        self.pb.grid(row=4)

        self.value_label = ttk.Label(bottom3_frame, text=self._progress_label())
        self.value_label.grid(row=5)

        bottom3_frame.pack(side=BOTTOM)

    # ------------------------------------------------------------------
    # Finalize layout
    # ------------------------------------------------------------------

    def _finalize_layout(self):
        self.tab_control.pack(expand=1, fill='both', side=TOP)

    # ------------------------------------------------------------------
    # UI State Helpers
    # ------------------------------------------------------------------

    def _progress_label(self):
        return f"Current Progress: {round(self.pb['value'], 1)} %"

    def set_status(self, text):
        self.current_action_label['text'] = text
        self.root.update()

    def reset_status(self):
        self.current_action_label['text'] = ""
        self.root.update()

    def reset_progress(self):
        self.pb['value'] = 0.0
        self.value_label['text'] = self._progress_label()
        self.root.update()

    def advance_progress(self, actions):
        if actions == 0:
            self.pb['value'] += 90
        else:
            if self.pb['value'] < 100:
                self.pb['value'] += 90 / actions
                self.value_label['text'] = self._progress_label()

    def advance_progress_connection(self):
        """Adds 5% if below 100%, returns False.
        If already at 100%, shows nothing and returns True so the controller
        can display 'Writing completed!'."""
        if round(self.pb['value']) < 100.0:
            self.pb['value'] += 5.0
            if self.pb['value'] > 100.0:
                self.pb['value'] = 100.0
            self.value_label['text'] = self._progress_label()
            return False
        else:
            return True

    def set_ip(self, ip_string):
        parts = ip_string.split(".")
        for entry, value in zip(
                [self.ip_byte0, self.ip_byte1, self.ip_byte2, self.ip_byte3], parts):
            entry.delete(0, END)
            entry.insert(0, value)

    def get_ip(self):
        return (self.ip_byte0.get() + "." + self.ip_byte1.get() + "." +
                self.ip_byte2.get() + "." + self.ip_byte3.get())

    def enable_reaper_options(self):
        self.cb_reaper_disable_numbering.config(state="normal")
        self.cb_reaper_disable_track_coloring.config(state="normal")
        self.cb_reaper_additional_prefix.config(state="normal")
        self.label_track_prefix.config(state="normal")
        self.cb_reaper_additional_master_tracks.config(state="normal")
        self.entry_additional_track_prefix.config(state="normal")
        self.combobox_master_track.config(state="normal")

    def disable_reaper_options(self):
        self.cb_reaper_disable_numbering.config(state="disabled")
        self.cb_reaper_disable_track_coloring.config(state="disabled")
        self.cb_reaper_additional_prefix.config(state="disabled")
        self.label_track_prefix.config(state="disabled")
        self.cb_reaper_additional_master_tracks.config(state="disabled")
        self.entry_additional_track_prefix.config(state="disabled")
        self.combobox_master_track.config(state="disabled")

    def enable_console_to_daw_prefix(self):
        self.entry_console_to_daw_additional_track_prefix.config(state="normal")
        self.label_console_to_daw_track_prefix.config(state="normal")

    def disable_console_to_daw_prefix(self):
        self.entry_console_to_daw_additional_track_prefix.config(state="disabled")
        self.label_console_to_daw_track_prefix.config(state="disabled")

    def enable_console_to_daw_mastertracks(self):
        self.combobox_console_to_daw_master_track.config(state="normal")

    def disable_console_to_daw_mastertracks(self):
        self.combobox_console_to_daw_master_track.config(state="disabled")

    def disable_avantis_checkboxes(self):
        cb_to_disable = [
            GuiConstants.TEXT_HPF_ON,
            GuiConstants.TEXT_HPF_VALUE,
            GuiConstants.TEXT_MUTE_GROUPS,
            GuiConstants.TEXT_MONO_GROUP_ASSIGN,
            GuiConstants.TEXT_STEREO_GROUP_ASSIGN,
        ]
        for checkbox in self.grid.checkboxes:
            current_cb = checkbox.__getitem__("text")
            if current_cb in cb_to_disable:
                self._remove_tick(current_cb)
                checkbox.config(state="disabled")

    def reactivate_avantis_checkboxes(self):
        for checkbox in self.grid.checkboxes:
            checkbox.config(state="normal")

    def _remove_tick(self, var_name):
        for var in self.grid.vars:
            if var._name == var_name:
                var.set(False)

    def set_end_channel(self, n):
        self.combobox_end.set(str(n))
        self.root.update()

    def set_start_channel(self, n):
        self.combobox_start.set(str(n))
        self.root.update()

    def select_all_checkboxes(self):
        for var in self.grid.vars:
            var.set(True)

    def clear_all_checkboxes(self):
        for var in self.grid.vars:
            var.set(False)
