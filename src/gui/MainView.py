# coding=utf-8
####################################################
# Main View
#
# Author: Tobias Grupe
#
####################################################

import tkinter as tk
import customtkinter as ctk
from tkinter import BooleanVar, StringVar, Menu

import GuiConstants
import Toolinfo
import dliveConstants
from gui.CheckboxGrid import CheckboxGrid

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
ctk.set_widget_scaling(0.85)
ctk.set_window_scaling(0.85)


class MainView:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title(Toolinfo.tool_name + ' - v' + Toolinfo.version)
        self.root.geometry('1680x1000')
        self.root.minsize(1500, 840)
        self.root.resizable(True, True)

        self.var_midi_channel = StringVar(self.root)
        self.var_console = StringVar(self.root)
        self.var_ms_console = StringVar(self.root)
        self.var_ms_console.set(dliveConstants.console_drop_down_sq_mixing_station)

        self.reaper_output_dir = ""
        self.reaper_file_prefix = ""
        self._pb_value = 0.0

        self._build_ui()

    # ------------------------------------------------------------------
    # Section frame helper (replaces LabelFrame)
    # ------------------------------------------------------------------

    def _section(self, parent, title):
        """CTkFrame with a bold title at grid row=0. Add content at row=1+."""
        frame = ctk.CTkFrame(parent)
        ctk.CTkLabel(frame, text=f" {title}",
                     font=ctk.CTkFont(weight="bold"), anchor="w").grid(
            row=0, column=0, columnspan=20, sticky="w", padx=10, pady=(8, 2))
        return frame

    def _bi_scroll_frame(self, parent):
        """Scrollable frame with both vertical and horizontal scrollbars.
        Packs itself into parent and returns the inner content frame."""
        fg_colors = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        mode_idx = 1 if ctk.get_appearance_mode() == "Dark" else 0
        bg_color = fg_colors[mode_idx] if isinstance(fg_colors, (list, tuple)) else fg_colors

        outer = ctk.CTkFrame(parent, fg_color="transparent")
        outer.pack(fill="both", expand=True)
        outer.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)

        canvas = tk.Canvas(outer, bg=bg_color, highlightthickness=0, bd=0)
        v_scroll = ctk.CTkScrollbar(outer, orientation="vertical", command=canvas.yview)
        h_scroll = ctk.CTkScrollbar(outer, orientation="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        inner = ctk.CTkFrame(canvas, fg_color="transparent")
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfig(window_id, height=max(event.height, inner.winfo_reqheight()))

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * event.delta), "units")

        inner.bind("<Configure>", _on_inner_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.bind("<MouseWheel>", _on_mousewheel)
        inner.bind("<MouseWheel>", _on_mousewheel)

        return inner

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_ui(self):
        self._create_menu()
        self._create_tabs()
        self._create_connection_settings()
        self._create_tab1_content()
        self._create_tab2_content()
        self._create_tab3_content()
        self._create_tab4_content()
        self._create_status_area()
        self._finalize_layout()

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------

    def _create_menu(self):
        menu_bar = Menu(self.root)

        self.settings_menu = Menu(menu_bar, tearoff=0)
        self.var_dark_mode = BooleanVar(value=True)
        self.settings_menu.add_checkbutton(label="Dark Mode",
                                           variable=self.var_dark_mode,
                                           onvalue=True, offvalue=False)
        menu_bar.add_cascade(label="Settings", menu=self.settings_menu)

        self.file_menu = Menu(menu_bar, tearoff=0)
        self.file_menu.add_command(label="Documentation")  # index 0
        self.file_menu.add_command(label="Donate ☕")      # index 1
        self.file_menu.add_separator()
        self.file_menu.add_command(label="About")          # index 3
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Close", command=self.root.destroy)

        menu_bar.add_cascade(label="Help", menu=self.file_menu)
        self.root.config(menu=menu_bar)

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------

    def _create_tabs(self):
        self.tab_control = ctk.CTkTabview(self.root)
        self.tab1 = self.tab_control.add("Spreadsheet to Console / DAW")
        self.tab2 = self.tab_control.add("Console to DAW")
        self.tab3 = self.tab_control.add("Utilities")
        self.tab4 = self.tab_control.add("Export")

    # ------------------------------------------------------------------
    # Connection Settings
    # ------------------------------------------------------------------

    def _create_connection_settings(self):
        config_frame = self._section(self.root, "Connection Settings")

        # Single row: Console | MIDI | IP | Buttons
        single_row = ctk.CTkFrame(config_frame, fg_color="transparent")
        single_row.grid(row=1, column=0, sticky="W", padx=5, pady=3)

        console_section = ctk.CTkFrame(single_row, fg_color="transparent")
        ctk.CTkLabel(console_section, text="Audio Console:", width=120, anchor="w").pack(side="left")
        ctk.CTkOptionMenu(console_section, variable=self.var_console,
                          values=[dliveConstants.console_drop_down_dlive,
                                  dliveConstants.console_drop_down_avantis,
                                  dliveConstants.console_drop_down_mixing_station,
                                  ]).pack(side="left", padx=(0, 5))

        self._ms_console_selector = ctk.CTkFrame(console_section, fg_color="transparent")
        ctk.CTkLabel(self._ms_console_selector, text="Type:", width=40, anchor="w").pack(
            side="left", padx=(8, 0))
        self._ms_console_menu = ctk.CTkOptionMenu(
            self._ms_console_selector,
            variable=self.var_ms_console,
            values=[
                dliveConstants.console_drop_down_sq_mixing_station,
                dliveConstants.console_drop_down_dm7_mixing_station,
                dliveConstants.console_drop_down_wing_mixing_station,
                dliveConstants.console_drop_down_m32_mixing_station,
                dliveConstants.console_drop_down_qu16_mixing_station,
            ])
        self._ms_console_menu.pack(side="left")

        console_section.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(single_row, text="MIDI Channel:", width=100, anchor="w").pack(side="left")
        self._midi_channel_menu = ctk.CTkOptionMenu(single_row, variable=self.var_midi_channel,
                          values=[
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
                              dliveConstants.midi_channel_drop_down_string_12,
                          ])
        self._midi_channel_menu.pack(side="left", padx=(0, 20))

        self.label_ip_address_text = ctk.CTkLabel(single_row, text="", width=120, anchor="w")
        self.label_ip_address_text.pack(side="left")

        ip_field = ctk.CTkFrame(single_row, fg_color="transparent")
        self.ip_byte0 = ctk.CTkEntry(ip_field, width=45)
        self.ip_byte1 = ctk.CTkEntry(ip_field, width=45)
        self.ip_byte2 = ctk.CTkEntry(ip_field, width=45)
        self.ip_byte3 = ctk.CTkEntry(ip_field, width=45)

        self.ip_byte0.grid(row=0, column=0, padx=2)
        ctk.CTkLabel(ip_field, text=".").grid(row=0, column=1)
        self.ip_byte1.grid(row=0, column=2, padx=2)
        ctk.CTkLabel(ip_field, text=".").grid(row=0, column=3)
        self.ip_byte2.grid(row=0, column=4, padx=2)
        ctk.CTkLabel(ip_field, text=".").grid(row=0, column=5)
        self.ip_byte3.grid(row=0, column=6, padx=2)

        self._ms_port_frame = ctk.CTkFrame(ip_field, fg_color="transparent")
        ctk.CTkLabel(self._ms_port_frame, text=":").pack(side="left", padx=(5, 0))
        self.entry_ms_port = ctk.CTkEntry(self._ms_port_frame, width=65)
        self.entry_ms_port.insert(0, str(dliveConstants.mixing_station_default_port))
        self.entry_ms_port.pack(side="left", padx=(2, 0))
        self._ms_port_frame.grid(row=0, column=7, padx=(5, 0))
        self._ms_port_frame.grid_remove()

        self.btn_save = ctk.CTkButton(ip_field, text='Save', width=70)
        self.btn_save.grid(row=0, column=8, padx=5)
        self.btn_director = ctk.CTkButton(ip_field, text='Director', width=80)
        self.btn_director.grid(row=0, column=9, padx=5)
        self.btn_default = ctk.CTkButton(ip_field, text='Default', width=70)
        self.btn_default.grid(row=0, column=10, padx=5)
        self.btn_test_connection = ctk.CTkButton(ip_field, text='Test Connection', width=130)
        self.btn_test_connection.grid(row=0, column=11, padx=5)
        ip_field.pack(side="left")

        config_frame.configure(border_width=1, border_color="white")
        config_frame.pack(side="top", fill="x", padx=10, pady=(5, 8))

    # ------------------------------------------------------------------
    # Tab 1 – Spreadsheet to Console / DAW
    # ------------------------------------------------------------------

    def _create_tab1_content(self):
        outer = ctk.CTkFrame(self.tab1, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=5, pady=3)

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
             GuiConstants.TEXT_STEREO_GROUP_ASSIGN],
            [GuiConstants.TEXT_PHANTOM,
             GuiConstants.TEXT_PAD,
             GuiConstants.TEXT_GAIN],
            [GuiConstants.TEXT_AUX_MONO_NAME,
             GuiConstants.TEXT_AUX_MONO_COLOR,
             GuiConstants.TEXT_AUX_STEREO_NAME,
             GuiConstants.TEXT_AUX_STEREO_COLOR,
             GuiConstants.TEXT_GRP_MONO_NAME,
             GuiConstants.TEXT_GRP_MONO_COLOR,
             GuiConstants.TEXT_GRP_STEREO_NAME,
             GuiConstants.TEXT_GRP_STEREO_COLOR],
            [GuiConstants.TEXT_DCA_NAME,
             GuiConstants.TEXT_DCA_COLOR,
             GuiConstants.TEXT_MTX_MONO_NAME,
             GuiConstants.TEXT_MTX_MONO_COLOR,
             GuiConstants.TEXT_MTX_STEREO_NAME,
             GuiConstants.TEXT_MTX_STEREO_COLOR],
            [GuiConstants.TEXT_FX_SEND_MONO_NAME,
             GuiConstants.TEXT_FX_SEND_MONO_COLOR,
             GuiConstants.TEXT_FX_SEND_STEREO_NAME,
             GuiConstants.TEXT_FX_SEND_STEREO_COLOR,
             GuiConstants.TEXT_FX_RETURN_NAME,
             GuiConstants.TEXT_FX_RETURN_COLOR,
             GuiConstants.TEXT_UFX_SEND_NAME,
             GuiConstants.TEXT_UFX_SEND_COLOR,
             GuiConstants.TEXT_UFX_RETURN_NAME,
             GuiConstants.TEXT_UFX_RETURN_COLOR]
        ]

        parameter_lf = ctk.CTkFrame(outer, border_width=1, border_color="white")
        ctk.CTkLabel(parameter_lf,
                     text=" Select spreadsheet columns to apply",
                     font=ctk.CTkFont(weight="bold"), anchor="w").pack(
            fill="x", padx=10, pady=(6, 2))

        self.grid = CheckboxGrid(parameter_lf, headers, labels)
        self.grid.pack(side="top", padx=5, pady=3, fill="x")

        global_select_frame = ctk.CTkFrame(parameter_lf, fg_color="transparent")
        self.btn_select_all = ctk.CTkButton(global_select_frame, text='Select All', width=90)
        self.btn_select_all.grid(row=0, column=0, padx=5)
        self.btn_clear_all = ctk.CTkButton(global_select_frame, text='Clear', width=70)
        self.btn_clear_all.grid(row=0, column=1, padx=5)
        global_select_frame.pack(side="top", pady=(0, 10))

        # Output Options – compact 2-column layout
        output_option_frame = self._section(outer, "Output Options")
        output_option_frame.configure(border_width=1, border_color="white")

        self.var_write_to_csv = BooleanVar(value=False)
        write_to_csv = ctk.CTkCheckBox(output_option_frame,
                                       text="Generate Director CSV",
                                       variable=self.var_write_to_csv)

        self.var_write_to_console = BooleanVar(value=True)
        write_to_console = ctk.CTkCheckBox(output_option_frame,
                                           text="Write to Audio Console or Director",
                                           variable=self.var_write_to_console)

        self.var_write_reaper = BooleanVar(value=False)
        self.cb_reaper_write = ctk.CTkCheckBox(output_option_frame,
                                               text="Generate Reaper Session",
                                               variable=self.var_write_reaper)

        self.var_write_trackslive = BooleanVar(value=False)
        self.cb_trackslive_write = ctk.CTkCheckBox(output_option_frame,
                                                   text="Generate Tracks Live Template",
                                                   variable=self.var_write_trackslive)

        self.var_disable_track_numbering = BooleanVar(value=False)
        self.cb_reaper_disable_numbering = ctk.CTkCheckBox(output_option_frame,
                                                           text="Disable Track Numbering",
                                                           variable=self.var_disable_track_numbering)

        self.var_disable_track_coloring = BooleanVar(value=False)
        self.cb_reaper_disable_track_coloring = ctk.CTkCheckBox(output_option_frame,
                                                                 text="Disable Track Coloring",
                                                                 variable=self.var_disable_track_coloring)

        self.label_track_prefix = ctk.CTkLabel(output_option_frame,
                                               text="Example: Band_Date_City", width=200, anchor="w")

        self.var_reaper_additional_prefix = BooleanVar(value=False)
        self.cb_reaper_additional_prefix = ctk.CTkCheckBox(output_option_frame,
                                                           text="Add Custom Track Prefix",
                                                           variable=self.var_reaper_additional_prefix)

        self.entry_additional_track_prefix = ctk.CTkEntry(output_option_frame, width=160)

        self.var_reaper_additional_master_tracks = BooleanVar(value=False)
        self.cb_reaper_additional_master_tracks = ctk.CTkCheckBox(output_option_frame,
                                                                   text="Add 2 Additional Master-Tracks",
                                                                   variable=self.var_reaper_additional_master_tracks)

        values = [f"{i}-{i + 1}" for i in range(1, 127, 2)]
        values.append("127-128")  # workaround
        self.var_master_recording_patch = StringVar()
        self.combobox_master_track = ctk.CTkComboBox(output_option_frame,
                                                     variable=self.var_master_recording_patch,
                                                     values=values)
        self.combobox_master_track.set("Select DAW Input")

        # Row 0 = title label; content from row 1
        # col 0: main output targets  |  col 1+: DAW sub-options
        write_to_console.grid(row=1, column=0, sticky="W", padx=10, pady=2)
        write_to_csv.grid(row=1, column=1, sticky="W", padx=10, pady=2)
        self.cb_reaper_write.grid(row=2, column=0, sticky="W", padx=10, pady=2)
        self.cb_reaper_disable_numbering.grid(row=2, column=1, sticky="W", padx=10, pady=2)
        self.cb_trackslive_write.grid(row=3, column=0, sticky="W", padx=10, pady=2)
        self.cb_reaper_disable_track_coloring.grid(row=3, column=1, sticky="W", padx=10, pady=2)
        self.cb_reaper_additional_prefix.grid(row=4, column=1, sticky="W", padx=10, pady=2)
        self.entry_additional_track_prefix.grid(row=4, column=2, sticky="W", padx=5, pady=2)
        self.label_track_prefix.grid(row=4, column=3, sticky="W", padx=5, pady=2)
        self.cb_reaper_additional_master_tracks.grid(row=5, column=1, sticky="W", padx=10, pady=2)
        self.combobox_master_track.grid(row=5, column=2, sticky="W", padx=5, pady=2)

        bottom_frame = ctk.CTkFrame(outer, fg_color="transparent")
        self.btn_open_spreadsheet = ctk.CTkButton(
            bottom_frame,
            text='Open Spreadsheet and Start Writing Process',
            height=38, font=ctk.CTkFont(size=13))
        self.btn_open_spreadsheet.grid(row=0, column=0, padx=10, pady=6)

        # Grid layout on outer: CheckboxGrid row gets all extra space (weight=1),
        # the rest are fixed-height so they are always fully visible.
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)   # parameter_lf – expands
        outer.rowconfigure(1, weight=0)   # Output Options
        outer.rowconfigure(2, weight=0)   # Button

        parameter_lf.grid(row=0, column=0, sticky="nsew", pady=(0, 3))
        output_option_frame.grid(row=1, column=0, sticky="ew", pady=3)
        bottom_frame.grid(row=2, column=0, pady=3)

    # ------------------------------------------------------------------
    # Tab 2 – Console to DAW
    # ------------------------------------------------------------------

    def _create_tab2_content(self):
        scroll = ctk.CTkFrame(self.tab2, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=3)

        console_to_daw_settings_lf = self._section(scroll, "Settings")
        console_to_daw_settings_lf.configure(border_width=1, border_color="white")
        console_to_daw_settings_lf.pack(side="top", fill="x", padx=5, pady=5)

        start_end_channel_frame = ctk.CTkFrame(console_to_daw_settings_lf, fg_color="transparent")

        values_start = [f"{i}" for i in range(1, 129)]
        self.var_current_console_startChannel = StringVar()
        self.combobox_start = ctk.CTkComboBox(start_end_channel_frame,
                                              variable=self.var_current_console_startChannel,
                                              values=values_start, width=70)
        self.combobox_start.set("1")

        ctk.CTkLabel(start_end_channel_frame, text="Channel Start", anchor="w").grid(row=0, column=0, padx=5, sticky="w")
        self.combobox_start.grid(row=0, column=1, padx=5)

        values_end = [f"{i}" for i in range(1, 129)]
        self.var_current_console_endChannel = StringVar()
        self.combobox_end = ctk.CTkComboBox(start_end_channel_frame,
                                            variable=self.var_current_console_endChannel,
                                            values=values_end, width=70)
        self.combobox_end.set("128")
        ctk.CTkLabel(start_end_channel_frame, text="End", anchor="w").grid(row=0, column=2, padx=5)
        self.combobox_end.grid(row=0, column=3, padx=5)
        start_end_channel_frame.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.var_console_to_daw_disable_track_numbering_daw = BooleanVar(value=False)
        cb_console_to_daw_disable_track_numbering_daw = ctk.CTkCheckBox(
            console_to_daw_settings_lf,
            text="Disable Track Numbering",
            variable=self.var_console_to_daw_disable_track_numbering_daw)

        self.var_console_to_daw_disable_track_coloring_daw = BooleanVar(value=False)
        cb_console_to_daw_disable_track_coloring_daw = ctk.CTkCheckBox(
            console_to_daw_settings_lf,
            text="Disable Track Coloring",
            variable=self.var_console_to_daw_disable_track_coloring_daw)

        self.var_console_to_daw_reaper_additional_prefix = BooleanVar(value=False)
        self.cb_console_to_daw_reaper_additional_prefix = ctk.CTkCheckBox(
            console_to_daw_settings_lf,
            text="Add Custom Track Prefix",
            variable=self.var_console_to_daw_reaper_additional_prefix)

        self.entry_console_to_daw_additional_track_prefix = ctk.CTkEntry(
            console_to_daw_settings_lf, width=160)

        self.label_console_to_daw_track_prefix = ctk.CTkLabel(
            console_to_daw_settings_lf, text="Example: Band_Date_City", width=200, anchor="w")

        self.var_console_to_daw_additional_master_tracks = BooleanVar(value=False)
        self.cb_console_to_daw_additional_master_tracks = ctk.CTkCheckBox(
            console_to_daw_settings_lf,
            text="Add 2 Additional Master-Tracks",
            variable=self.var_console_to_daw_additional_master_tracks)

        values = [f"{i}-{i + 1}" for i in range(1, 127, 2)]
        values.append("127-128")  # workaround
        self.var_console_to_daw_master_recording_patch = StringVar()
        self.combobox_console_to_daw_master_track = ctk.CTkComboBox(
            console_to_daw_settings_lf,
            variable=self.var_console_to_daw_master_recording_patch,
            values=values)
        self.combobox_console_to_daw_master_track.set("Select DAW Input")

        # Output Options
        console_to_daw_output_options_lf = self._section(scroll, "Output Options")
        console_to_daw_output_options_lf.configure(border_width=1, border_color="white")

        self.var_console_to_daw_reaper = BooleanVar(value=False)
        cb_console_to_daw_reaper = ctk.CTkCheckBox(console_to_daw_output_options_lf,
                                                    text="Generate Reaper Session",
                                                    variable=self.var_console_to_daw_reaper)

        self.var_console_to_daw_trackslive = BooleanVar(value=False)
        cb_console_to_daw_trackslive = ctk.CTkCheckBox(console_to_daw_output_options_lf,
                                                       text="Generate Tracks Live Template",
                                                       variable=self.var_console_to_daw_trackslive)

        cb_console_to_daw_reaper.grid(row=1, column=0, sticky="w", padx=10, pady=3)
        cb_console_to_daw_trackslive.grid(row=2, column=0, sticky="w", padx=10, pady=3)
        console_to_daw_output_options_lf.pack(side="top", fill="x", padx=5, pady=5)

        # Settings grid (row 0 is title, content at row 2+)
        cb_console_to_daw_disable_track_numbering_daw.grid(row=2, column=0, sticky="w", padx=10, pady=3)
        cb_console_to_daw_disable_track_coloring_daw.grid(row=3, column=0, sticky="w", padx=10, pady=3)
        self.cb_console_to_daw_reaper_additional_prefix.grid(row=4, column=0, sticky="w", padx=10, pady=3)
        self.entry_console_to_daw_additional_track_prefix.grid(row=4, column=1, sticky="w", padx=5, pady=3)
        self.label_console_to_daw_track_prefix.grid(row=4, column=2, padx=5)
        self.cb_console_to_daw_additional_master_tracks.grid(row=5, column=0, sticky="w", padx=10, pady=3)
        self.combobox_console_to_daw_master_track.grid(row=5, column=1, sticky="w", padx=5, pady=3)

        button_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.btn_console_to_daw = ctk.CTkButton(
            button_frame,
            text='Generate DAW Session(s) from Current Console Settings',
            height=40, font=ctk.CTkFont(size=13))
        self.btn_console_to_daw.pack(pady=10)
        button_frame.pack(side="top", pady=5)

    # ------------------------------------------------------------------
    # Tab 3 – Utilities
    # ------------------------------------------------------------------

    def _create_tab3_content(self):
        reset_frame = self._section(self.tab3, "Reset")
        reset_frame.configure(border_width=1, border_color="white")

        self.btn_reset_dca = ctk.CTkButton(reset_frame, text='RESET all DCA Assignments', width=260,
                                           fg_color="#C0392B", hover_color="#922B21")
        self.btn_reset_mute_groups = ctk.CTkButton(reset_frame, text='RESET all Mute Group Assignments', width=280,
                                                   fg_color="#C0392B", hover_color="#922B21")
        self.btn_reset_main_mix = ctk.CTkButton(reset_frame, text='RESET all Main Assignments', width=260,
                                                fg_color="#C0392B", hover_color="#922B21")

        self.btn_reset_dca.grid(row=1, column=0, padx=10, pady=8)
        self.btn_reset_mute_groups.grid(row=1, column=1, padx=10, pady=8)
        self.btn_reset_main_mix.grid(row=1, column=2, padx=10, pady=8)
        reset_frame.pack(side="top", fill="x", padx=10, pady=8)

        mute_frame = self._section(self.tab3, "Mute")
        mute_frame.configure(border_width=1, border_color="white")

        self.btn_mute_all_inputs = ctk.CTkButton(mute_frame, text='MUTE all Inputs', width=260,
                                                 fg_color="#E67E22", hover_color="#CA6F1E")
        self.btn_mute_all_outputs = ctk.CTkButton(mute_frame, text='MUTE all Outputs', width=260,
                                                  fg_color="#E67E22", hover_color="#CA6F1E")
        self.btn_unmute_all_inputs = ctk.CTkButton(mute_frame, text='UNMUTE all Inputs', width=260,
                                                   fg_color="#27AE60", hover_color="#1E8449")
        self.btn_unmute_all_outputs = ctk.CTkButton(mute_frame, text='UNMUTE all Outputs', width=260,
                                                    fg_color="#27AE60", hover_color="#1E8449")

        self.btn_mute_all_inputs.grid(row=1, column=0, padx=10, pady=8)
        self.btn_mute_all_outputs.grid(row=1, column=1, padx=10, pady=8)
        self.btn_unmute_all_inputs.grid(row=2, column=0, padx=10, pady=8)
        self.btn_unmute_all_outputs.grid(row=2, column=1, padx=10, pady=8)
        mute_frame.pack(side="top", fill="x", padx=10, pady=8)

        fader_frame = self._section(self.tab3, "Fader")
        fader_frame.configure(border_width=1, border_color="white")

        self.btn_fader_all_to_zero = ctk.CTkButton(fader_frame, text='Set all Input Faders to 0 dB', width=260)
        self.btn_fader_all_to_minus_inf = ctk.CTkButton(fader_frame, text='Set all Input Faders to -inf', width=260)

        self.btn_fader_all_to_zero.grid(row=1, column=0, padx=10, pady=8)
        self.btn_fader_all_to_minus_inf.grid(row=1, column=1, padx=10, pady=8)
        fader_frame.pack(side="top", fill="x", padx=10, pady=8)

        preamp_frame = self._section(self.tab3, "Preamp Safety")
        preamp_frame.configure(border_width=1, border_color="white")

        self.btn_phantom_off_all = ctk.CTkButton(preamp_frame, text='Phantom Power OFF (all Sockets)', width=280,
                                                 fg_color="#C0392B", hover_color="#922B21")
        self.btn_phantom_off_all.grid(row=1, column=0, padx=10, pady=8)
        preamp_frame.pack(side="top", fill="x", padx=10, pady=8)

    # ------------------------------------------------------------------
    # Tab 4 – Export
    # ------------------------------------------------------------------

    def _create_tab4_content(self):
        outer = ctk.CTkFrame(self.tab4, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=5, pady=3)

        export_settings_lf = self._section(outer, "Settings")
        export_settings_lf.configure(border_width=1, border_color="white")
        export_settings_lf.pack(side="top", fill="x", padx=5, pady=5)

        source_frame = ctk.CTkFrame(export_settings_lf, fg_color="transparent")
        ctk.CTkLabel(source_frame, text="Read Channel Names From", anchor="w").grid(
            row=0, column=0, padx=5, sticky="w")

        self.var_export_source = StringVar(value=GuiConstants.TEXT_EXPORT_SOURCE_CONSOLE)
        ctk.CTkRadioButton(source_frame, text=GuiConstants.TEXT_EXPORT_SOURCE_CONSOLE,
                          variable=self.var_export_source,
                          value=GuiConstants.TEXT_EXPORT_SOURCE_CONSOLE).grid(
            row=0, column=1, padx=5)
        ctk.CTkRadioButton(source_frame, text=GuiConstants.TEXT_EXPORT_SOURCE_SPREADSHEET,
                          variable=self.var_export_source,
                          value=GuiConstants.TEXT_EXPORT_SOURCE_SPREADSHEET).grid(
            row=0, column=2, padx=5)
        source_frame.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        start_end_channel_frame = ctk.CTkFrame(export_settings_lf, fg_color="transparent")

        values_start = [f"{i}" for i in range(1, 129)]
        self.var_export_startChannel = StringVar()
        self.combobox_export_start = ctk.CTkComboBox(start_end_channel_frame,
                                                     variable=self.var_export_startChannel,
                                                     values=values_start, width=70)
        self.combobox_export_start.set("1")

        ctk.CTkLabel(start_end_channel_frame, text="Channel Start", anchor="w").grid(row=0, column=0, padx=5, sticky="w")
        self.combobox_export_start.grid(row=0, column=1, padx=5)

        values_end = [f"{i}" for i in range(1, 129)]
        self.var_export_endChannel = StringVar()
        self.combobox_export_end = ctk.CTkComboBox(start_end_channel_frame,
                                                    variable=self.var_export_endChannel,
                                                    values=values_end, width=70)
        self.combobox_export_end.set("128")
        ctk.CTkLabel(start_end_channel_frame, text="End", anchor="w").grid(row=0, column=2, padx=5)
        self.combobox_export_end.grid(row=0, column=3, padx=5)
        start_end_channel_frame.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        export_json_lf = self._section(outer, "Export to Dante Config Editor")
        export_json_lf.configure(border_width=1, border_color="white")

        btn_row = ctk.CTkFrame(export_json_lf, fg_color="transparent")
        self.btn_export_json = ctk.CTkButton(
            btn_row,
            text='Export Channel List as JSON',
            fg_color="#8E44AD", hover_color="#6C3483")
        self.btn_export_json.pack(side="left", padx=5)
        self.btn_export_csv = ctk.CTkButton(
            btn_row,
            text='Export Channel List as CSV',
            fg_color="#8E44AD", hover_color="#6C3483")
        self.btn_export_csv.pack(side="left", padx=5)
        btn_row.grid(row=1, column=0, padx=10, pady=8)

        export_json_lf.pack(side="top", fill="x", padx=5, pady=5)

        export_pdf_lf = self._section(outer, "Export / Print PDF")
        export_pdf_lf.configure(border_width=1, border_color="white")

        btn_row2 = ctk.CTkFrame(export_pdf_lf, fg_color="transparent")
        self.btn_export_pdf = ctk.CTkButton(
            btn_row2,
            text='Export Channel List as PDF',
            fg_color="#2980B9", hover_color="#21618C")
        self.btn_export_pdf.pack(side="left", padx=5)
        self.btn_print_channels = ctk.CTkButton(
            btn_row2,
            text='Print Channel List',
            fg_color="#2980B9", hover_color="#21618C")
        self.btn_print_channels.pack(side="left", padx=5)
        btn_row2.grid(row=1, column=0, padx=10, pady=8)

        export_pdf_lf.pack(side="top", fill="x", padx=5, pady=5)

    def set_export_max_channel(self, max_ch):
        values = [f"{i}" for i in range(1, max_ch + 1)]
        self.combobox_export_end.configure(values=values)
        current = int(self.var_export_endChannel.get())
        if current > max_ch:
            self.combobox_export_end.set(str(max_ch))
        self.root.update()

    def set_export_start_channel(self, n):
        self.combobox_export_start.set(str(n))

    def set_export_end_channel(self, n):
        self.combobox_export_end.set(str(n))

    def disable_helpers_avantis(self):
        self.btn_reset_mute_groups.configure(state='disabled')

    def enable_helpers_avantis(self):
        self.btn_reset_mute_groups.configure(state='normal')

    def disable_utilities(self):
        for btn in (self.btn_reset_dca, self.btn_reset_mute_groups, self.btn_reset_main_mix,
                    self.btn_mute_all_inputs, self.btn_mute_all_outputs,
                    self.btn_unmute_all_inputs, self.btn_unmute_all_outputs,
                    self.btn_fader_all_to_zero, self.btn_fader_all_to_minus_inf,
                    self.btn_phantom_off_all):
            btn.configure(state='disabled')

    def enable_utilities(self):
        for btn in (self.btn_reset_dca, self.btn_reset_mute_groups, self.btn_reset_main_mix,
                    self.btn_mute_all_inputs, self.btn_mute_all_outputs,
                    self.btn_unmute_all_inputs, self.btn_unmute_all_outputs,
                    self.btn_fader_all_to_zero, self.btn_fader_all_to_minus_inf,
                    self.btn_phantom_off_all):
            btn.configure(state='normal')

    # ------------------------------------------------------------------
    # Status Area
    # ------------------------------------------------------------------

    def _create_status_area(self):
        bottom4_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        ctk.CTkButton(bottom4_frame, text='Close', command=self.root.destroy, width=80).pack(pady=8)
        bottom4_frame.pack(side="bottom")

        bottom3_frame = ctk.CTkFrame(self.root, border_width=1, border_color="white")
        bottom3_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(bottom3_frame, text=" Status",
                     font=ctk.CTkFont(weight="bold"), anchor="w").grid(
            row=0, column=0, rowspan=3, padx=(10, 0), pady=8, sticky="ns")

        self.current_action_label = ctk.CTkLabel(bottom3_frame, text="")
        self.current_action_label.grid(row=0, column=1, padx=10, pady=(6, 1), sticky="w")

        self.pb = ctk.CTkProgressBar(bottom3_frame, mode='determinate')
        self.pb.set(0)
        self.pb.grid(row=1, column=1, padx=10, pady=1, sticky="ew")

        self.value_label = ctk.CTkLabel(bottom3_frame, text=self._progress_label())
        self.value_label.grid(row=2, column=1, padx=10, pady=(1, 6), sticky="w")

        bottom3_frame.pack(side="bottom", fill="x", padx=10, pady=5)

    # ------------------------------------------------------------------
    # Finalize layout
    # ------------------------------------------------------------------

    def _finalize_layout(self):
        self.tab_control.pack(expand=1, fill='both', side="top")

    # ------------------------------------------------------------------
    # UI State Helpers
    # ------------------------------------------------------------------

    def _progress_label(self):
        return f"Current Progress: {round(self._pb_value, 1)} %"

    def set_status(self, text):
        self.current_action_label.configure(text=text)
        self.root.update()

    def reset_status(self):
        self.current_action_label.configure(text="")
        self.root.update()

    def reset_progress(self):
        self._pb_value = 0.0
        self.pb.set(0.0)
        self.value_label.configure(text=self._progress_label())
        self.root.update()

    def advance_progress(self, actions):
        if actions == 0:
            self._pb_value += 90
        else:
            if self._pb_value < 100:
                self._pb_value += 90 / actions
                self.value_label.configure(text=self._progress_label())
        self.pb.set(min(self._pb_value, 100) / 100.0)

    def advance_progress_connection(self):
        """Adds 5% if below 100%, returns False.
        If already at 100%, returns True so the controller can display 'Writing completed!'."""
        if round(self._pb_value) < 100.0:
            self._pb_value += 5.0
            if self._pb_value > 100.0:
                self._pb_value = 100.0
            self.pb.set(self._pb_value / 100.0)
            self.value_label.configure(text=self._progress_label())
            return False
        else:
            return True

    def set_ip(self, ip_string):
        parts = ip_string.split(".")
        for entry, value in zip(
                [self.ip_byte0, self.ip_byte1, self.ip_byte2, self.ip_byte3], parts):
            entry.delete(0, 'end')
            entry.insert(0, value)

    def get_ip(self):
        return (self.ip_byte0.get() + "." + self.ip_byte1.get() + "." +
                self.ip_byte2.get() + "." + self.ip_byte3.get())

    def enable_reaper_options(self):
        self.cb_reaper_disable_numbering.configure(state="normal")
        self.cb_reaper_disable_track_coloring.configure(state="normal")
        self.cb_reaper_additional_prefix.configure(state="normal")
        self.label_track_prefix.configure(state="normal")
        self.cb_reaper_additional_master_tracks.configure(state="normal")
        self.entry_additional_track_prefix.configure(state="normal")
        self.combobox_master_track.configure(state="normal")

    def disable_reaper_options(self):
        self.cb_reaper_disable_numbering.configure(state="disabled")
        self.cb_reaper_disable_track_coloring.configure(state="disabled")
        self.cb_reaper_additional_prefix.configure(state="disabled")
        self.label_track_prefix.configure(state="disabled")
        self.cb_reaper_additional_master_tracks.configure(state="disabled")
        self.entry_additional_track_prefix.configure(state="disabled")
        self.combobox_master_track.configure(state="disabled")

    def enable_console_to_daw_prefix(self):
        self.entry_console_to_daw_additional_track_prefix.configure(state="normal")
        self.label_console_to_daw_track_prefix.configure(state="normal")

    def disable_console_to_daw_prefix(self):
        self.entry_console_to_daw_additional_track_prefix.configure(state="disabled")
        self.label_console_to_daw_track_prefix.configure(state="disabled")

    def enable_console_to_daw_mastertracks(self):
        self.combobox_console_to_daw_master_track.configure(state="normal")

    def disable_console_to_daw_mastertracks(self):
        self.combobox_console_to_daw_master_track.configure(state="disabled")

    def disable_avantis_checkboxes(self):
        cb_to_disable = [
            GuiConstants.TEXT_HPF_ON,
            GuiConstants.TEXT_HPF_VALUE,
            GuiConstants.TEXT_MUTE_GROUPS,
            GuiConstants.TEXT_MONO_GROUP_ASSIGN,
            GuiConstants.TEXT_STEREO_GROUP_ASSIGN,
        ]
        for checkbox in self.grid.checkboxes:
            current_cb = checkbox.cget("text")
            if current_cb in cb_to_disable:
                self._remove_tick(current_cb)
                checkbox.configure(state="disabled")

    def reactivate_avantis_checkboxes(self):
        for checkbox in self.grid.checkboxes:
            checkbox.configure(state="normal")

    _MS_SUPPORTED_PARAMS = {
        GuiConstants.TEXT_NAME,
        GuiConstants.TEXT_COLOR,
        GuiConstants.TEXT_MUTE,
        GuiConstants.TEXT_FADER_LEVEL,
    }

    def disable_mixing_station_checkboxes(self):
        for checkbox in self.grid.checkboxes:
            text = checkbox.cget("text")
            if text not in self._MS_SUPPORTED_PARAMS:
                self._remove_tick(text)
                checkbox.configure(state="disabled")

    def show_ms_port(self):
        self._ms_port_frame.grid()

    def hide_ms_port(self):
        self._ms_port_frame.grid_remove()

    def show_ms_console_selector(self):
        self._ms_console_selector.pack(side="left", padx=(5, 0))

    def hide_ms_console_selector(self):
        self._ms_console_selector.pack_forget()

    def get_effective_console(self):
        if self.var_console.get() == dliveConstants.console_drop_down_mixing_station:
            return self.var_ms_console.get()
        return self.var_console.get()

    def get_ms_port(self):
        return self.entry_ms_port.get()

    def set_ms_port(self, port):
        self.entry_ms_port.delete(0, 'end')
        self.entry_ms_port.insert(0, str(port))

    def enable_midi_channel(self):
        self._midi_channel_menu.configure(state="normal")

    def disable_midi_channel(self):
        self._midi_channel_menu.configure(state="disabled")

    def _remove_tick(self, var_name):
        for var in self.grid.vars:
            if var._name == var_name:
                var.set(False)

    def set_end_channel(self, n):
        self.combobox_end.set(str(n))

    def set_console_to_daw_max_channel(self, max_ch):
        values = [f"{i}" for i in range(1, max_ch + 1)]
        self.combobox_end.configure(values=values)
        current = int(self.var_current_console_endChannel.get())
        if current > max_ch:
            self.combobox_end.set(str(max_ch))
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
