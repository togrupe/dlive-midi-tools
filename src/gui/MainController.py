# coding=utf-8
####################################################
# Main Controller
#
# Author: Tobias Grupe
#
####################################################

import logging
import os
import socket
import threading
from tkinter import filedialog
from tkinter.messagebox import showinfo, showerror

import pandas as pd
from mido.sockets import connect

import GuiConstants
import dliveConstants
from directorcsv import CsvCreator
from dawsession import ReaperSessionCreator, TracksLiveSessionCreator
from gui.AboutDialog import AboutDialog
from helper.Networking import is_valid_ip_address
from model.Action import Action
from model.Sheet import Sheet
from parameters.channels.ChannelsCommon import handle_channels_parameter
from parameters.channels.Color import get_color_channel
from parameters.channels.GroupsCommon import handle_groups_parameter
from parameters.channels.Name import get_name_channel
from parameters.sockets.SocketsCommon import handle_sockets_parameter
from persistence.Persistence import (persist_current_ui_settings,
                                     read_persisted_console,
                                     read_persisted_midi_port,
                                     read_persisted_ip)
from spreadsheet.Spreadsheet import (create_channel_list_content,
                                     create_socket_list_content,
                                     create_groups_list_content,
                                     create_misc_content,
                                     create_channel_list_content_from_console)
from spreadsheet.Validator import validate


class MainController:
    def __init__(self, view, context):
        self.view = view
        self.context = context
        self.log = context.get_logger()

        self._load_persisted_settings()
        self._bind_commands()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _load_persisted_settings(self):
        self.view.var_console.set(read_persisted_console(self.context))
        self.view.var_midi_channel.set(read_persisted_midi_port(self.context))

        ip = read_persisted_ip(self.context)
        self.view.set_ip(ip)

        # Set the IP-label text based on the persisted console type
        if self.view.var_console.get() == dliveConstants.console_drop_down_avantis:
            self.view.label_ip_address_text["text"] = GuiConstants.LABEL_IPADDRESS_AVANTIS
        else:
            self.view.label_ip_address_text["text"] = GuiConstants.LABEL_IPADDRESS_DLIVE
        self.view.root.update()
        self.view.root.focus()

        self.view.disable_reaper_options()
        self.view.disable_console_to_daw_prefix()
        self.view.disable_console_to_daw_mastertracks()

    def _bind_commands(self):
        # Menu
        self.view.file_menu.entryconfig(0, command=self.on_about)

        # Connection buttons
        self.view.btn_save.config(command=self.on_save_settings)
        self.view.btn_director.config(command=self.on_director_ip)
        self.view.btn_default.config(command=self.on_reset_ip)
        self.view.btn_test_connection.config(command=self.on_test_connection)

        # Checkbox / combobox commands
        self.view.cb_reaper_write.config(command=self.on_reaper_write_changed)
        self.view.cb_trackslive_write.config(command=self.on_reaper_write_changed)
        self.view.cb_console_to_daw_reaper_additional_prefix.config(
            command=self.on_console_to_daw_prefix_changed)
        self.view.cb_console_to_daw_additional_master_tracks.config(
            command=self.on_console_to_daw_mastertracks_changed)

        # Tab 1 action buttons
        self.view.btn_select_all.config(command=self.view.select_all_checkboxes)
        self.view.btn_clear_all.config(command=self.view.clear_all_checkboxes)
        self.view.btn_open_spreadsheet.config(command=self.on_browse_files_thread)

        # Tab 2 action button
        self.view.btn_console_to_daw.config(command=self.on_console_to_daw_thread)

        # Variable traces
        self.view.var_console.trace("w", self.on_console_selected)
        self.view.var_current_console_endChannel.trace("w", self.on_endchannel_selected)
        self.view.var_current_console_startChannel.trace("w", self.on_startchannel_selected)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def on_about(self):
        about = AboutDialog(self.view.root)
        about.mainloop()

    def on_save_settings(self):
        current_ip = self.view.get_ip()
        self.context.get_app_data().set_console(
            self._determine_console_id(self.view.var_console.get()))
        self.context.get_app_data().set_midi_channel(self.view.var_midi_channel.get())
        self.context.get_app_data().set_current_ip(current_ip)
        persist_current_ui_settings(self.context)

    def on_reset_ip(self):
        default_ip = dliveConstants.ip
        self.view.set_ip(default_ip)
        logging.info("Default ip: " + default_ip + " was set.")

    def on_director_ip(self):
        director_ip = "127.0.0.1"
        self.view.set_ip(director_ip)
        logging.info("Director ip: " + director_ip + " was set.")

    def on_test_connection(self):
        self.view.reset_status()
        test_ip = self.view.get_ip()

        if not is_valid_ip_address(test_ip):
            error_message = "Invalid IP-Address"
            self.view.set_status(error_message)
            showerror(message=error_message)
            return

        logging.info("Test connection to " + str(test_ip))
        try:
            ret = self._connect_to_console(test_ip, test=True)
            if ret is not None:
                ret.close()
                showinfo(message="Connection Test successful")
        except OSError:
            action = "Connection Test failed"
            logging.error(action)
            self.view.set_status(action)
            showerror(message=action)

    def on_console_selected(self, *args):
        self.context.get_app_data().set_console(self.view.var_console.get())
        self.log.info("The selected console is: " + self.view.var_console.get())

        if self.view.var_console.get() == dliveConstants.console_drop_down_avantis:
            self.view.label_ip_address_text["text"] = GuiConstants.LABEL_IPADDRESS_AVANTIS
            self.view.root.update()

            if self.view.tab_control.index(self.view.tab_control.select()) == 0:
                showinfo(
                    message='Info: "' + GuiConstants.TEXT_HPF_ON +
                            '", "' + GuiConstants.TEXT_HPF_VALUE +
                            '", "' + GuiConstants.TEXT_MUTE_GROUPS +
                            '", "' + GuiConstants.TEXT_MONO_GROUP_ASSIGN +
                            '" and  "' + GuiConstants.TEXT_STEREO_GROUP_ASSIGN +
                            '" are currently not supported by the API of Avantis!')

            self.view.disable_avantis_checkboxes()
            self.view.set_end_channel(dliveConstants.AVANTIS_MAX_CHANNELS)
            self.view.root.update()

        elif self.view.var_console.get() == dliveConstants.console_drop_down_dlive:
            self.view.label_ip_address_text["text"] = GuiConstants.LABEL_IPADDRESS_DLIVE
            self.view.reactivate_avantis_checkboxes()
            self.view.set_end_channel(dliveConstants.DLIVE_MAX_CHANNELS)
            self.view.root.update()

    def on_reaper_write_changed(self):
        if self.view.var_write_reaper.get() or self.view.var_write_trackslive.get():
            self.view.enable_reaper_options()
        else:
            self.view.disable_reaper_options()

    def on_console_to_daw_prefix_changed(self):
        if self.view.var_console_to_daw_reaper_additional_prefix.get():
            self.view.enable_console_to_daw_prefix()
        else:
            self.view.disable_console_to_daw_prefix()

    def on_console_to_daw_mastertracks_changed(self):
        if self.view.var_console_to_daw_additional_master_tracks.get():
            self.view.enable_console_to_daw_mastertracks()
        else:
            self.view.disable_console_to_daw_mastertracks()

    def on_endchannel_selected(self, *args):
        if (self.view.var_console.get() == dliveConstants.console_drop_down_avantis and
                int(self.view.var_current_console_endChannel.get()) > dliveConstants.AVANTIS_MAX_CHANNELS):
            showerror(message="Avantis supports up to " + str(dliveConstants.AVANTIS_MAX_CHANNELS) + " Channels")
            self.view.set_end_channel(dliveConstants.AVANTIS_MAX_CHANNELS)

    def on_startchannel_selected(self, *args):
        if (self.view.var_console.get() == dliveConstants.console_drop_down_avantis and
                int(self.view.var_current_console_startChannel.get()) > dliveConstants.AVANTIS_MAX_CHANNELS):
            showerror(message="Avantis supports up to " + str(dliveConstants.AVANTIS_MAX_CHANNELS) + " Channels")
            self.view.set_start_channel(dliveConstants.AVANTIS_MAX_CHANNELS)

    def on_browse_files_thread(self):
        bg_thread = threading.Thread(target=self._browse_files)
        bg_thread.start()

    def on_console_to_daw_thread(self):
        bg_thread = threading.Thread(target=self._get_data_from_console)
        bg_thread.start()

    # ------------------------------------------------------------------
    # Business logic – Console to DAW
    # ------------------------------------------------------------------

    def _get_data_from_console(self):
        app_data = self.context.get_app_data()
        app_data.set_midi_channel(
            self._determine_technical_midi_port(self.view.var_midi_channel.get()))
        self.context.set_app_data(app_data)

        if self.view.var_console_to_daw_reaper.get() or self.view.var_console_to_daw_trackslive.get():

            if (self.view.var_console_to_daw_additional_master_tracks.get() and
                    self.view.var_console_to_daw_master_recording_patch.get() == "Select DAW Input"):
                showerror(message="DAW Inputs for additional master tracks must to be chosen.")
                return

            self.view.reset_status()
            self.view.reset_progress()
            self.view.advance_progress_connection()
            self.view.root.update()
            actions = 2

            if self.view.var_console_to_daw_reaper.get():
                actions += 1

            if self.view.var_console_to_daw_trackslive.get():
                actions += 1

            self.view.set_status("Choose a directory...")
            directory_path = filedialog.askdirectory(title="Please select a directory")

            if directory_path.__len__() == 0:
                return

            if self.context.get_network_connection_allowed():
                ip_address = self.view.get_ip()
                if not is_valid_ip_address(ip_address):
                    error_message = "Invalid IP-Address"
                    self.view.set_status(error_message)
                    showerror(message=error_message)
                    return

                self.context.set_output(self._connect_to_console(ip_address))
                output = self.context.get_output()
                start_channel = int(self.view.var_current_console_startChannel.get()) - 1
                end_channel = int(self.view.var_current_console_endChannel.get())

                if start_channel > end_channel:
                    error_msg = ("Start Channel: " + str(start_channel + 1) +
                                 " is greater than End Channel: " + str(end_channel))
                    self.log.error(error_msg)
                    showerror(message=error_msg)
                    return

                self.view.set_status("Reading channel color from console")
                self.view.advance_progress(actions)
                self.view.root.update()
                data_color = get_color_channel(self.context, start_channel, end_channel)

                self.view.set_status("Reading channel name from console")
                self.view.advance_progress(actions)
                self.view.root.update()
                data_fin = get_name_channel(self.context, data_color, start_channel, end_channel)

                sheet = Sheet()
                sheet.set_channel_model(create_channel_list_content_from_console(data_fin))

                try:
                    if self.view.var_console_to_daw_reaper.get():
                        self.view.set_status("Generating Reaper Session...")
                        self.view.advance_progress(actions)
                        self.view.root.update()
                        ReaperSessionCreator.create_session(
                            sheet, directory_path, "current-console",
                            self.view.var_console_to_daw_disable_track_numbering_daw.get(),
                            self.view.var_console_to_daw_reaper_additional_prefix.get(),
                            self.view.entry_console_to_daw_additional_track_prefix.get(),
                            self.view.var_console_to_daw_additional_master_tracks.get(),
                            self.view.var_console_to_daw_master_recording_patch.get(),
                            self.view.var_console_to_daw_disable_track_coloring_daw.get())
                        text = "Reaper Recording Session Template created"
                        self.view.set_status(text)
                        self.log.info(text)

                    if self.view.var_console_to_daw_trackslive.get():
                        self.view.set_status("Generating Tracks Live Template...")
                        self.view.advance_progress(actions)
                        self.view.root.update()
                        TracksLiveSessionCreator.create_session(
                            sheet, directory_path, "current-console",
                            self.view.var_console_to_daw_disable_track_numbering_daw.get(),
                            self.view.var_console_to_daw_reaper_additional_prefix.get(),
                            self.view.entry_console_to_daw_additional_track_prefix.get(),
                            self.view.var_console_to_daw_additional_master_tracks.get(),
                            self.view.var_console_to_daw_master_recording_patch.get(),
                            self.view.var_console_to_daw_disable_track_coloring_daw.get())
                        text = "Tracks Live Recording Session Template created"
                        self.view.set_status(text)
                        self.log.info(text)

                    output.close()
                    self.view.advance_progress_connection()

                except OSError:
                    error = ("Some thing went wrong during store, please choose a folder "
                             "where you have write rights.")
                    self.log.error(error)
                    self.view.set_status(error)
                    showerror(message=error)
                    return

                showinfo(message='Reading from console done, session(s) created!')
            else:
                pass  # network not allowed; nothing to do
        else:
            showerror(message="Nothing to do, please select at least one output option.")

    # ------------------------------------------------------------------
    # Business logic – Spreadsheet to Console / DAW
    # ------------------------------------------------------------------

    def _browse_files(self):
        self.view.reset_progress()

        self.view.set_status("Choose channel list spreadsheet...")

        app_data = self.context.get_app_data()
        cb_reaper = self.view.var_write_reaper.get()
        app_data.set_output_reaper(cb_reaper)

        cb_trackslive = self.view.var_write_trackslive.get()
        app_data.set_output_trackslive(cb_trackslive)

        cb_console_write = self.view.var_write_to_console.get()
        app_data.set_output_write_to_console(cb_console_write)

        cb_write_to_csv = self.view.var_write_to_csv.get()
        app_data.set_output_write_to_csv(cb_write_to_csv)

        if cb_reaper or cb_trackslive or cb_console_write or cb_write_to_csv:
            input_file_path = filedialog.askopenfilename()
            if input_file_path == "":
                return

            self.view.reaper_output_dir = os.path.dirname(input_file_path)
            self.view.reaper_file_prefix = os.path.splitext(os.path.basename(input_file_path))[0]

            try:
                self._read_document(input_file_path)
            except TypeError as exc:
                error_message = ("An error happened, probably an empty line could be the issue. "
                                 "Empty lines in spreadsheet are not supported.")
                showerror(message=error_message)
                logging.error(error_message)
                logging.error(exc)
                self.view.reset_progress()
                self.view.reset_status()
                exit(1)

            except ValueError as exc:
                error_message = (
                    "One of the following columns have unexpected characters. "
                    "(Mono Auxes, Stereo Auxes, Mono Groups, Stereo Group, \n"
                    "Mono Matrix, Stereo Matrix, \n"
                    "Mono FX Send, Stereo FX Send, FX Return), the should only contain integer numbers. \n"
                    "Please use the Name columns.")
                showerror(message=error_message)
                logging.error(error_message)
                logging.error(exc)
                self.view.reset_progress()
                self.view.reset_status()
                exit(1)
        else:
            showerror(message="Nothing to do, please select at least one output option.")

    def _read_document(self, filename):
        self.log.info('The following file will be read : ' + str(filename))

        sheet = Sheet()
        sheet.set_misc_model(create_misc_content(pd.read_excel(filename, sheet_name="Misc")))

        latest_spreadsheet_version = '14'
        read_version = sheet.get_misc_model().get_version()

        if read_version != latest_spreadsheet_version:
            error_msg = ("Given spreadsheet version: " + str(read_version) +
                         " is not compatible. Please use the latest spread "
                         "sheet (Version " + latest_spreadsheet_version +
                         "). You can see the version in the spreadsheet tab \"Misc\"")
            self.log.error(error_msg)
            showerror(message=error_msg)
            return self.view.root.quit()

        self.context.get_app_data().set_console(self.view.var_console.get())

        sheet.set_channel_model(
            create_channel_list_content(
                pd.read_excel(filename, sheet_name="Channels", dtype=str), self.context))
        sheet.set_socket_model(
            create_socket_list_content(
                pd.read_excel(filename, sheet_name="Sockets", dtype=str)))
        sheet.set_group_model(
            create_groups_list_content(
                pd.read_excel(filename, sheet_name="Groups", dtype=str)))

        app_data = self.context.get_app_data()
        app_data.set_midi_channel(
            self._determine_technical_midi_port(self.view.var_midi_channel.get()))

        if self.context.get_app_data().get_console() == dliveConstants.console_drop_down_avantis:
            self.view.disable_avantis_checkboxes()
            self.view.root.update()

        validation_errors = validate(sheet, self.context.get_app_data().get_console())
        if validation_errors:
            MAX_SHOWN = 20
            shown = validation_errors[:MAX_SHOWN]
            suffix = (f"\n\n... and {len(validation_errors) - MAX_SHOWN} more error(s). See log for full list."
                      if len(validation_errors) > MAX_SHOWN else "")
            msg = "Spreadsheet validation failed:\n\n" + "\n".join(shown) + suffix
            for err in validation_errors:
                self.log.error("Validation: " + err)
            showerror(message=msg)
            self.view.reset_progress()
            self.view.reset_status()
            return

        actions = 0
        action_list = []

        if self.context.get_app_data().get_output_write_to_console():
            actions = self._fill_actions(action_list, actions)
            if actions == 0:
                text = "No spreadsheet column(s) selected. Please select at least one column"
                showinfo(message=text)
                logging.info(text)
                self.view.set_status(text)
                return

        if self.context.get_app_data().get_output_reaper():
            actions += 1

        if self.context.get_app_data().get_output_trackslive():
            actions += 1

        if self.context.get_app_data().get_output_write_to_csv():
            actions += 1

        action = "Start Processing..."
        self.log.info(action)
        self.view.set_status(action)

        current_ip = self.view.get_ip()

        if (self.context.get_network_connection_allowed() and
                self.context.get_app_data().get_output_write_to_console()):
            if not is_valid_ip_address(current_ip):
                error_message = "Invalid IP-Address"
                self.view.set_status(error_message)
                showerror(message=error_message)
                return
            self.context.set_output(self._connect_to_console(current_ip))
        else:
            self.context.set_output(None)

        self.view.advance_progress_connection()
        self.view.root.update()

        if self.context.get_app_data().get_output_write_to_console():
            if not self.context.get_csv_patching_hint_already_seen():
                showinfo(
                    message='Hint: Input patching (Source, Socket) can be applied by using Director´s CSV Import function.')
                self.context.set_csv_patching_hint_already_seen(True)

            if self.context.get_output() is None:
                self.view.reset_progress()
                self.view.root.update()
                return

            self._process_actions(action_list, actions, sheet)

        if self.context.get_app_data().get_output_reaper():
            action = "Creating Reaper Recording Session Template file..."
            self.log.info(action)
            self.view.set_status(action)

            if (self.view.var_reaper_additional_master_tracks.get() and
                    self.view.var_master_recording_patch.get() == "Select DAW Input"):
                self.view.advance_progress(actions)
                self.view.root.update()
                showerror(message="DAW Inputs for additional master tracks must to be chosen.")
                return

            ReaperSessionCreator.create_session(
                sheet,
                self.view.reaper_output_dir,
                self.view.reaper_file_prefix,
                self.view.var_disable_track_numbering.get(),
                self.view.var_reaper_additional_prefix.get(),
                self.view.entry_additional_track_prefix.get(),
                self.view.var_reaper_additional_master_tracks.get(),
                self.view.var_master_recording_patch.get(),
                self.view.var_disable_track_coloring.get())
            self.log.info("Reaper Recording Session Template created")

            self.view.advance_progress(actions)
            self.view.root.update()

        if self.context.get_app_data().get_output_trackslive():
            action = "Creating Tracks Live Recording Session Template file..."
            self.log.info(action)
            self.view.set_status(action)

            if (self.view.var_reaper_additional_master_tracks.get() and
                    self.view.var_master_recording_patch.get() == "Select DAW Input"):
                self.view.advance_progress(actions)
                self.view.root.update()
                showerror(message="DAW Inputs for additional master tracks must to be chosen.")
                return

            TracksLiveSessionCreator.create_session(
                sheet,
                self.view.reaper_output_dir,
                self.view.reaper_file_prefix,
                self.view.var_disable_track_numbering.get(),
                self.view.var_reaper_additional_prefix.get(),
                self.view.entry_additional_track_prefix.get(),
                self.view.var_reaper_additional_master_tracks.get(),
                self.view.var_master_recording_patch.get(),
                self.view.var_disable_track_coloring.get())
            self.log.info("Tracks Live Recording Session Template created")

            self.view.advance_progress(actions)
            self.view.root.update()

        if self.context.get_app_data().get_output_write_to_csv():
            showinfo(
                message='Info: You have selected the CSV Export Feature, Please use Directors Import CSV Feature to '
                        'import Name, Color, Patching, Gain, Pad, Phantom (48V)')

            action = "Creating Director CSV file..."
            self.log.info(action)
            self.view.set_status(action)

            CsvCreator.create(sheet, self.view.reaper_output_dir, self.view.reaper_file_prefix)
            self.log.info("Director CSV file created")

            self.view.advance_progress(actions)
            self.view.root.update()

        if actions == 0:
            self.view.advance_progress(actions)
            self.view.root.update()

        action = "Processing done"
        self.log.info(action)
        self.view.current_action_label['text'] = ""

        if (self.context.get_network_connection_allowed() and
                self.context.get_app_data().get_output_write_to_console()):
            output = self.context.get_output()
            if output is not None:
                output.close()

        # Call advance_progress_connection twice; second call returns True when at 100%
        self.view.advance_progress_connection()
        if self.view.advance_progress_connection():
            showinfo(message='Writing completed!')

        self.view.root.update()

    def _process_actions(self, action_list, actions, sheet):
        for action in action_list:
            action_message = action.get_message()
            if action.get_sheet_tab() == "channels":
                self.view.set_status(action_message)
                if handle_channels_parameter(action_message, self.context,
                                             sheet.get_channel_model(),
                                             action.get_action()) == 1:
                    self.view.reset_status()
                    self.view.reset_progress()
                    exit(1)
            elif action.get_sheet_tab() == "sockets":
                self.view.set_status(action_message)
                handle_sockets_parameter(action_message, self.context,
                                         sheet.get_socket_model(),
                                         action.get_action())
            elif action.get_sheet_tab() == "groups":
                self.view.set_status(action_message)
                if handle_groups_parameter(action_message, self.context,
                                           sheet.get_group_model(),
                                           action.get_action(),
                                           action.get_bus_type()) == 1:
                    self.view.reset_status()
                    self.view.reset_progress()
                    exit(1)

            self.view.advance_progress(actions)
            self.view.root.update()

    def _fill_actions(self, action_list, actions):
        checkbox_action_map = {
            GuiConstants.TEXT_NAME:              ("channels", "Set Names to channels...",                  "name",                None),
            GuiConstants.TEXT_COLOR:             ("channels", "Set Color to channels...",                  "color",               None),
            GuiConstants.TEXT_MUTE:              ("channels", "Set Mute to channels...",                   "mute",                None),
            GuiConstants.TEXT_FADER_LEVEL:       ("channels", "Set Fader Level to channels...",            "fader_level",         None),
            GuiConstants.TEXT_HPF_ON:            ("channels", "Set HPF On to channels...",                 "hpf_on",              None),
            GuiConstants.TEXT_HPF_VALUE:         ("channels", "Set HPF Value to channels...",              "hpf_value",           None),
            GuiConstants.TEXT_DCA:               ("channels", "Set DCA Assignments to channels...",        "dca",                 None),
            GuiConstants.TEXT_MUTE_GROUPS:       ("channels", "Set Mute Group Assignments to channels...", "mute_group",          None),
            GuiConstants.TEXT_MAINMIX:           ("channels", "Set Main Mix Assignments to channels...",   "assign_main_mix",     None),
            GuiConstants.TEXT_MONO_GROUP_ASSIGN: ("channels", "Set Mono Group Assignments to channels...", "assign_mono_group",   None),
            GuiConstants.TEXT_STEREO_GROUP_ASSIGN:("channels","Set Stereo Group Assignments to channels...","assign_stereo_group", None),
            GuiConstants.TEXT_PHANTOM:           ("sockets",  "Set Phantom Power to sockets...",           "phantom",             None),
            GuiConstants.TEXT_PAD:               ("sockets",  "Set Pad to sockets...",                     "pad",                 None),
            GuiConstants.TEXT_GAIN:              ("sockets",  "Set Gain to sockets...",                    "gain",                None),
            GuiConstants.TEXT_DCA_NAME:          ("groups",   "Set DCA Names...",                          "name",                "dca"),
            GuiConstants.TEXT_DCA_COLOR:         ("groups",   "Set DCA Color...",                          "color",               "dca"),
            GuiConstants.TEXT_AUX_MONO_NAME:     ("groups",   "Set Aux Mono Name...",                      "name",                "aux_mono"),
            GuiConstants.TEXT_AUX_MONO_COLOR:    ("groups",   "Set Aux Mono Color...",                     "color",               "aux_mono"),
            GuiConstants.TEXT_AUX_STEREO_NAME:   ("groups",   "Set Aux Stereo Name...",                    "name",                "aux_stereo"),
            GuiConstants.TEXT_AUX_STEREO_COLOR:  ("groups",   "Set Aux Stereo Color...",                   "color",               "aux_stereo"),
            GuiConstants.TEXT_GRP_MONO_NAME:     ("groups",   "Set Group Mono Name...",                    "name",                "group_mono"),
            GuiConstants.TEXT_GRP_MONO_COLOR:    ("groups",   "Set Group Mono Color...",                   "color",               "group_mono"),
            GuiConstants.TEXT_GRP_STEREO_NAME:   ("groups",   "Set Group Stereo Name...",                  "name",                "group_stereo"),
            GuiConstants.TEXT_GRP_STEREO_COLOR:  ("groups",   "Set Group Stereo Color...",                 "color",               "group_stereo"),
            GuiConstants.TEXT_MTX_MONO_NAME:     ("groups",   "Set Matrix Mono Name...",                   "name",                "matrix_mono"),
            GuiConstants.TEXT_MTX_MONO_COLOR:    ("groups",   "Set Matrix Mono Color...",                  "color",               "matrix_mono"),
            GuiConstants.TEXT_MTX_STEREO_NAME:   ("groups",   "Set Matrix Stereo Name...",                 "name",                "matrix_stereo"),
            GuiConstants.TEXT_MTX_STEREO_COLOR:  ("groups",   "Set Matrix Stereo Color...",                "color",               "matrix_stereo"),
            GuiConstants.TEXT_FX_SEND_MONO_NAME: ("groups",   "Set FX Send Mono Name...",                  "name",                "fx_send_mono"),
            GuiConstants.TEXT_FX_SEND_MONO_COLOR:("groups",   "Set FX Send Mono Color...",                 "color",               "fx_send_mono"),
            GuiConstants.TEXT_FX_SEND_STEREO_NAME:("groups",  "Set FX Send Stereo Name...",                "name",                "fx_send_stereo"),
            GuiConstants.TEXT_FX_SEND_STEREO_COLOR:("groups", "Set FX Send Stereo Color...",               "color",               "fx_send_stereo"),
            GuiConstants.TEXT_FX_RETURN_NAME:    ("groups",   "Set FX Return Name...",                     "name",                "fx_return"),
            GuiConstants.TEXT_FX_RETURN_COLOR:   ("groups",   "Set FX Return Color...",                    "color",               "fx_return"),
            GuiConstants.TEXT_UFX_SEND_NAME:     ("groups",   "Set UFX Send Name...",                      "name",                "ufx_send"),
            GuiConstants.TEXT_UFX_SEND_COLOR:    ("groups",   "Set UFX Send Color...",                     "color",               "ufx_send"),
            GuiConstants.TEXT_UFX_RETURN_NAME:   ("groups",   "Set UFX Return Name...",                    "name",                "ufx_return"),
            GuiConstants.TEXT_UFX_RETURN_COLOR:  ("groups",   "Set UFX Return Color...",                   "color",               "ufx_return"),
        }

        for var in self.view.grid.vars:
            self.log.info("Current checkbox name: " + str(var._name) + " State=" + str(var.get()))
            if var.get() and var._name in checkbox_action_map:
                tab, message, action_type, bus_type = checkbox_action_map[var._name]
                action = Action(var._name, tab, message, action_type, bus_type=bus_type)
                action_list.append(action)
                actions += 1

        return actions

    def _connect_to_console(self, ip, test=False):
        text = ("Try to open connection to console on ip: " + ip + ":" +
                str(dliveConstants.port) + " ...")
        logging.info(text)
        self.view.set_status(text)

        try:
            output = connect(ip, dliveConstants.port)
            action = "Connection Test Successful" if test else "Connection successful"
            logging.info(action)
            self.view.set_status(action)
            return output
        except socket.timeout:
            connect_err_message = ("Connection to IP-Address: " + ip + " could not be "
                                   "established. Are you in the same subnet?")
            action = "Connection failed"
            logging.error(action)
            self.view.set_status(action)
            logging.error(connect_err_message)
            showerror(message=connect_err_message)
            self.view.reset_progress()
            return None

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _determine_technical_midi_port(selected_midi_port_as_string):
        switcher = {
            dliveConstants.midi_channel_drop_down_string_1: 0,
            dliveConstants.midi_channel_drop_down_string_2: 1,
            dliveConstants.midi_channel_drop_down_string_3: 2,
            dliveConstants.midi_channel_drop_down_string_4: 3,
            dliveConstants.midi_channel_drop_down_string_5: 4,
            dliveConstants.midi_channel_drop_down_string_6: 5,
            dliveConstants.midi_channel_drop_down_string_7: 6,
            dliveConstants.midi_channel_drop_down_string_8: 7,
            dliveConstants.midi_channel_drop_down_string_9: 8,
            dliveConstants.midi_channel_drop_down_string_10: 9,
            dliveConstants.midi_channel_drop_down_string_11: 10,
            dliveConstants.midi_channel_drop_down_string_12: 11,
        }
        return switcher.get(selected_midi_port_as_string, "Invalid port")

    @staticmethod
    def _determine_console_id(selected_console_as_string):
        switcher = {
            dliveConstants.console_drop_down_dlive: dliveConstants.console_drop_down_dlive,
            dliveConstants.console_drop_down_avantis: dliveConstants.console_drop_down_avantis,
        }
        return switcher.get(selected_console_as_string, "Invalid console")
