# coding=utf-8
####################################################
# Main Script
#
# Author: Tobias Grupe
#
####################################################

import logging
import os
import socket
import threading
from tkinter import filedialog, Button, Tk, Checkbutton, Frame, LEFT, TOP, X, RIGHT, Label, \
    Entry, BOTTOM, StringVar, OptionMenu, ttk, LabelFrame, BooleanVar, END, Menu
from tkinter.messagebox import showinfo, showerror
from tkinter.ttk import Combobox

import pandas as pd
from mido.sockets import connect

import GuiConstants
import Toolinfo
import dliveConstants
from directorcsv import CsvCreator
from dawsession import ReaperSessionCreator, TracksLiveSessionCreator
from gui.AboutDialog import AboutDialog
from helper.Networking import is_valid_ip_address
from model.Action import Action
from model.AppData import AppData
from model.Context import Context
from model.Sheet import Sheet
from parameters.channels.ChannelsCommon import handle_channels_parameter
from parameters.channels.Color import get_color_channel
from parameters.channels.GroupsCommon import handle_groups_parameter
from parameters.channels.Name import get_name_channel
from parameters.sockets.SocketsCommon import handle_sockets_parameter
from persistence.Persistence import persist_current_ui_settings, read_persisted_console, read_persisted_midi_port, \
    read_persisted_ip
from spreadsheet.Spreadsheet import create_channel_list_content, create_socket_list_content, create_groups_list_content, \
    create_misc_content, create_channel_list_content_from_console

LOG_FILE = 'main.log'
CONFIG_FILE = 'config.json'


def get_data_from_console():
    log = context.get_logger()

    app_data.set_midi_channel(determine_technical_midi_port(var_midi_channel.get()))
    context.set_app_data(app_data)

    if var_console_to_daw_reaper.get() or var_console_to_daw_trackslive.get():

        if var_console_to_daw_additional_master_tracks.get() and var_console_to_daw_master_recording_patch.get() == "Select DAW Input":
            showerror(message="DAW Inputs for additional master tracks must to be chosen.")
            return

        reset_current_action_label()
        reset_progress_bar()
        progress_open_or_close_connection()
        root.update()
        actions = 2

        if var_console_to_daw_reaper.get():
            actions = increment_actions(actions)

        if var_console_to_daw_trackslive.get():
            actions = increment_actions(actions)

        current_action_label["text"] = "Choose a directory..."
        root.update()
        directory_path = filedialog.askdirectory(title="Please select a directory")

        if directory_path.__len__() == 0:
            return

        if context.get_network_connection_allowed():
            ip_address = read_current_ui_ip_address()
            if not is_valid_ip_address(ip_address):
                error_message = "Invalid IP-Address"
                current_action_label["text"] = error_message
                root.update()
                showerror(message=error_message)
                return

            context.set_output(connect_to_console(ip_address))
            output = context.get_output()
            start_channel = int(var_current_console_startChannel.get()) - 1
            end_channel = int(var_current_console_endChannel.get())
            if start_channel > end_channel:
                error_msg = "Start Channel: " + str(start_channel + 1) + " is greater than End Channel: " + str(
                    end_channel)
                log.error(error_msg)
                showerror(message=error_msg)
                return

            current_action_label["text"] = "Reading channel color from console"
            progress(actions)
            root.update()
            data_color = get_color_channel(context, start_channel, end_channel)

            current_action_label["text"] = "Reading channel name from console"
            progress(actions)
            root.update()
            data_fin = get_name_channel(context, data_color, start_channel, end_channel)

            sheet = Sheet()

            sheet.set_channel_model(create_channel_list_content_from_console(data_fin))

            try:
                if var_console_to_daw_reaper.get():
                    current_action_label["text"] = "Generating Reaper Session..."
                    progress(actions)
                    root.update()
                    ReaperSessionCreator.create_session(sheet, directory_path, "current-console",
                                                        var_console_to_daw_disable_track_numbering_daw.get(),
                                                        var_console_to_daw_reaper_additional_prefix.get(),
                                                        entry_console_to_daw_additional_track_prefix.get(),
                                                        var_console_to_daw_additional_master_tracks.get(),
                                                        var_console_to_daw_master_recording_patch.get(),
                                                        var_console_to_daw_disable_track_coloring_daw.get())
                    text = "Reaper Recording Session Template created"
                    current_action_label["text"] = text
                    root.update()
                    log.info(text)

                if var_console_to_daw_trackslive.get():
                    current_action_label["text"] = "Generating Tracks Live Template..."
                    progress(actions)
                    root.update()
                    TracksLiveSessionCreator.create_session(sheet, directory_path, "current-console",
                                                            var_console_to_daw_disable_track_numbering_daw.get(),
                                                            var_console_to_daw_reaper_additional_prefix.get(),
                                                            entry_console_to_daw_additional_track_prefix.get(),
                                                            var_console_to_daw_additional_master_tracks.get(),
                                                            var_console_to_daw_master_recording_patch.get(),
                                                            var_console_to_daw_disable_track_coloring_daw.get())
                    text = "Tracks Live Recording Session Template created"
                    current_action_label["text"] = text
                    root.update()
                    log.info(text)

                disconnect_from_console(output)
                progress_open_or_close_connection()

            except OSError:
                error = "Some thing went wrong during store, please choose a folder where you have write rights."
                log.error(error)
                current_action_label["text"] = error
                showerror(message=error)
                return

            showinfo(message='Reading from console done, session(s) created!')
        else:
            output = None
    else:
        showerror(message="Nothing to do, please select at least one output option.")


def fill_actions(action_list, actions):
    for var in grid.vars:
        log.info("Current checkbox name: " + str(var._name) + " State=" + str(var.get()))

        # Name
        if var._name == GuiConstants.TEXT_NAME and var.get() is True:
            action = Action(GuiConstants.TEXT_NAME, "channels",
                            "Set Names to channels...", "name")
            action_list.append(action)
            actions = increment_actions(actions)

        # Color
        elif var._name == GuiConstants.TEXT_COLOR and var.get() is True:
            action = Action(GuiConstants.TEXT_COLOR, "channels",
                            "Set Color to channels...", "color")
            action_list.append(action)
            actions = increment_actions(actions)

        # Mute
        elif var._name == GuiConstants.TEXT_MUTE and var.get() is True:
            action = Action(GuiConstants.TEXT_MUTE, "channels",
                            "Set Mute to channels...", "mute")
            action_list.append(action)
            actions = increment_actions(actions)

        # Fader Level
        elif var._name == GuiConstants.TEXT_FADER_LEVEL and var.get() is True:
            action = Action(GuiConstants.TEXT_FADER_LEVEL, "channels",
                            "Set Fader Level to channels...", "fader_level")
            action_list.append(action)
            actions = increment_actions(actions)

        # HPF On
        elif var._name == GuiConstants.TEXT_HPF_ON and var.get() is True:
            action = Action(GuiConstants.TEXT_HPF_ON, "channels",
                            "Set HPF On to channels...", "hpf_on")
            action_list.append(action)
            actions = increment_actions(actions)

        # HPF value
        elif var._name == GuiConstants.TEXT_HPF_VALUE and var.get() is True:
            action = Action(GuiConstants.TEXT_HPF_VALUE, "channels",
                            "Set HPF Value to channels...", "hpf_value")
            action_list.append(action)
            actions = increment_actions(actions)

        # DCAs
        elif var._name == GuiConstants.TEXT_DCA and var.get() is True:
            action = Action(GuiConstants.TEXT_DCA, "channels",
                            "Set DCA Assignments to channels...", "dca")
            action_list.append(action)
            actions = increment_actions(actions)

        # Mute Groups
        elif var._name == GuiConstants.TEXT_MUTE_GROUPS and var.get() is True:
            action = Action(GuiConstants.TEXT_MUTE_GROUPS, "channels",
                            "Set Mute Group Assignments to channels...", "mute_group")
            action_list.append(action)
            actions = increment_actions(actions)

        # Assign to Main Mix
        elif var._name == GuiConstants.TEXT_MAINMIX and var.get() is True:
            action = Action(GuiConstants.TEXT_MAINMIX, "channels",
                            "Set Main Mix Assignments to channels...", "assign_main_mix")
            action_list.append(action)
            actions = increment_actions(actions)

        # Phantom
        elif var._name == GuiConstants.TEXT_PHANTOM and var.get() is True:
            action = Action(GuiConstants.TEXT_PHANTOM, "sockets",
                            "Set Phantom Power to sockets...", "phantom")
            action_list.append(action)
            actions = increment_actions(actions)

        # Pad
        elif var._name == GuiConstants.TEXT_PAD and var.get() is True:
            action = Action(GuiConstants.TEXT_PAD, "sockets",
                            "Set Pad to sockets...", "pad")
            action_list.append(action)
            actions = increment_actions(actions)

        # Gain
        elif var._name == GuiConstants.TEXT_GAIN and var.get() is True:
            action = Action(GuiConstants.TEXT_GAIN, "sockets",
                            "Set Gain to sockets...", "gain")
            action_list.append(action)
            actions = increment_actions(actions)

        # DCA Name
        elif var._name == GuiConstants.TEXT_DCA_NAME and var.get() is True:
            action = Action(GuiConstants.TEXT_DCA_NAME, "groups",
                            "Set DCA Names...", "name", bus_type="dca")
            action_list.append(action)
            actions = increment_actions(actions)

        # DCA Color
        elif var._name == GuiConstants.TEXT_DCA_COLOR and var.get() is True:
            action = Action(GuiConstants.TEXT_DCA_COLOR, "groups",
                            "Set DCA Color...", "color", bus_type="dca")
            action_list.append(action)
            actions = increment_actions(actions)

        # Aux Mono Name
        elif var._name == GuiConstants.TEXT_AUX_MONO_NAME and var.get() is True:
            action = Action(GuiConstants.TEXT_AUX_MONO_NAME, "groups",
                            "Set Aux Mono Name...", "name", bus_type="aux_mono")
            action_list.append(action)
            actions = increment_actions(actions)

        # Aux Mono Color
        elif var._name == GuiConstants.TEXT_AUX_MONO_COLOR and var.get() is True:
            action = Action(GuiConstants.TEXT_AUX_MONO_COLOR, "groups",
                            "Set Aux Mono Color...", "color", bus_type="aux_mono")
            action_list.append(action)
            actions = increment_actions(actions)

        # Aux Stereo Name
        elif var._name == GuiConstants.TEXT_AUX_STEREO_NAME and var.get() is True:
            action = Action(GuiConstants.TEXT_AUX_STEREO_NAME, "groups",
                            "Set Aux Stereo Name...", "name", bus_type="aux_stereo")
            action_list.append(action)
            actions = increment_actions(actions)

        # Aux Stereo Color
        elif var._name == GuiConstants.TEXT_AUX_STEREO_COLOR and var.get() is True:
            action = Action(GuiConstants.TEXT_AUX_STEREO_COLOR, "groups",
                            "Set Aux Stereo Color...", "color", bus_type="aux_stereo")
            action_list.append(action)
            actions = increment_actions(actions)

        # Group Mono Name
        elif var._name == GuiConstants.TEXT_GRP_MONO_NAME and var.get() is True:
            action = Action(GuiConstants.TEXT_GRP_MONO_NAME, "groups",
                            "Set Group Mono Name...", "name", bus_type="group_mono")
            action_list.append(action)
            actions = increment_actions(actions)

        # Group Mono Color
        elif var._name == GuiConstants.TEXT_GRP_MONO_COLOR and var.get() is True:
            action = Action(GuiConstants.TEXT_GRP_MONO_COLOR, "groups",
                            "Set Group Mono Color...", "color", bus_type="group_mono")
            action_list.append(action)
            actions = increment_actions(actions)

        # Group Stereo Name
        elif var._name == GuiConstants.TEXT_GRP_STEREO_NAME and var.get() is True:
            action = Action(GuiConstants.TEXT_GRP_STEREO_NAME, "groups",
                            "Set Group Stereo Name...", "name", bus_type="group_stereo")
            action_list.append(action)
            actions = increment_actions(actions)

        # Group Stereo Color
        elif var._name == GuiConstants.TEXT_GRP_STEREO_COLOR and var.get() is True:
            action = Action(GuiConstants.TEXT_GRP_STEREO_COLOR, "groups",
                            "Set Group Stereo Color...", "color", bus_type="group_stereo")
            action_list.append(action)
            actions = increment_actions(actions)

        # Matrix Mono Name
        elif var._name == GuiConstants.TEXT_MTX_MONO_NAME and var.get() is True:
            action = Action(GuiConstants.TEXT_MTX_MONO_NAME, "groups",
                            "Set Matrix Mono Name...", "name", bus_type="matrix_mono")
            action_list.append(action)
            actions = increment_actions(actions)

        # Matrix Mono Color
        elif var._name == GuiConstants.TEXT_MTX_MONO_COLOR and var.get() is True:
            action = Action(GuiConstants.TEXT_MTX_MONO_COLOR, "groups",
                            "Set Matrix Mono Color...", "color", bus_type="matrix_mono")
            action_list.append(action)
            actions = increment_actions(actions)

        # Matrix Stereo Name
        elif var._name == GuiConstants.TEXT_MTX_STEREO_NAME and var.get() is True:
            action = Action(GuiConstants.TEXT_MTX_STEREO_NAME, "groups",
                            "Set Matrix Stereo Name...", "name", bus_type="matrix_stereo")
            action_list.append(action)
            actions = increment_actions(actions)

        # Matrix Stereo Color
        elif var._name == GuiConstants.TEXT_MTX_STEREO_COLOR and var.get() is True:
            action = Action(GuiConstants.TEXT_MTX_STEREO_COLOR, "groups",
                            "Set Matrix Stereo Color...", "color", bus_type="matrix_stereo")
            action_list.append(action)
            actions = increment_actions(actions)

        # FX Send Mono Name
        elif var._name == GuiConstants.TEXT_FX_SEND_MONO_NAME and var.get() is True:
            action = Action(GuiConstants.TEXT_FX_SEND_MONO_NAME, "groups",
                            "Set FX Send Mono Name...", "name", bus_type="fx_send_mono")
            action_list.append(action)
            actions = increment_actions(actions)

        # FX Send Mono Color
        elif var._name == GuiConstants.TEXT_FX_SEND_MONO_COLOR and var.get() is True:
            action = Action(GuiConstants.TEXT_FX_SEND_MONO_COLOR, "groups",
                            "Set FX Send Mono Color...", "color", bus_type="fx_send_mono")
            action_list.append(action)
            actions = increment_actions(actions)

        # FX Send Stereo Name
        elif var._name == GuiConstants.TEXT_FX_SEND_STEREO_NAME and var.get() is True:
            action = Action(GuiConstants.TEXT_FX_SEND_STEREO_NAME, "groups",
                            "Set FX Send Stereo Name...", "name", bus_type="fx_send_stereo")
            action_list.append(action)
            actions = increment_actions(actions)

        # FX Send Stereo Color
        elif var._name == GuiConstants.TEXT_FX_SEND_STEREO_COLOR and var.get() is True:
            action = Action(GuiConstants.TEXT_FX_SEND_STEREO_COLOR, "groups",
                            "Set FX Send Stereo Color...", "color", bus_type="fx_send_stereo")
            action_list.append(action)
            actions = increment_actions(actions)

        # FX Return Name
        elif var._name == GuiConstants.TEXT_FX_RETURN_NAME and var.get() is True:
            action = Action(GuiConstants.TEXT_FX_RETURN_NAME, "groups",
                            "Set FX Return Name...", "name", bus_type="fx_return")
            action_list.append(action)
            actions = increment_actions(actions)

        # FX Return Color
        elif var._name == GuiConstants.TEXT_FX_RETURN_COLOR and var.get() is True:
            action = Action(GuiConstants.TEXT_FX_RETURN_COLOR, "groups",
                            "Set FX Return Color...", "color", bus_type="fx_return")
            action_list.append(action)
            actions = increment_actions(actions)

        # UFX Send Name
        elif var._name == GuiConstants.TEXT_UFX_SEND_NAME and var.get() is True:
            action = Action(GuiConstants.TEXT_UFX_SEND_NAME, "groups",
                        "Set UFX Send Name...", "name", bus_type="ufx_send")
            action_list.append(action)
            actions = increment_actions(actions)

        # UFX Send Color
        elif var._name == GuiConstants.TEXT_UFX_SEND_COLOR and var.get() is True:
            action = Action(GuiConstants.TEXT_UFX_SEND_COLOR, "groups",
                        "Set UFX Send Color...", "color", bus_type="ufx_send")
            action_list.append(action)
            actions = increment_actions(actions)

        # UFX Return Name
        elif var._name == GuiConstants.TEXT_UFX_RETURN_NAME and var.get() is True:
            action = Action(GuiConstants.TEXT_UFX_RETURN_NAME, "groups",
                        "Set UFX Return Name...", "name", bus_type="ufx_return")
            action_list.append(action)
            actions = increment_actions(actions)

        # UFX Return Color
        elif var._name == GuiConstants.TEXT_UFX_RETURN_COLOR and var.get() is True:
            action = Action(GuiConstants.TEXT_UFX_RETURN_COLOR, "groups",
                            "Set UFX Return Color...", "color", bus_type="ufx_return")
            action_list.append(action)
            actions = increment_actions(actions)

    return actions


def read_document(filename):
    log = context.get_logger()

    log.info('The following file will be read : ' + str(filename))

    sheet = Sheet()

    sheet.set_misc_model(create_misc_content(pd.read_excel(filename, sheet_name="Misc")))

    latest_spreadsheet_version = '12'

    read_version = sheet.get_misc_model().get_version()

    if read_version != latest_spreadsheet_version:
        error_msg = "Given spreadsheet version: " + str(
            read_version) + " is not compatible. Please use the latest spread " \
                            "sheet (Version " + latest_spreadsheet_version + \
                    "). You can see the version in the spreadsheet tab \"Misc\""
        log.error(error_msg)
        showerror(message=error_msg)
        return root.quit()

    sheet.set_channel_model(create_channel_list_content(pd.read_excel(filename, sheet_name="Channels", dtype=str)))
    sheet.set_socket_model(create_socket_list_content(pd.read_excel(filename, sheet_name="Sockets", dtype=str)))
    sheet.set_group_model(create_groups_list_content(pd.read_excel(filename, sheet_name="Groups", dtype=str)))

    app_data.set_midi_channel(determine_technical_midi_port(var_midi_channel.get()))

    context.get_app_data().set_console(var_console.get())

    if context.get_app_data().get_console() == dliveConstants.console_drop_down_avantis:
        disable_avantis_checkboxes()
        root.update()
    actions = 0
    action_list = []

    if context.get_app_data().get_output_write_to_console():
        actions = fill_actions(action_list, actions)
        if actions == 0:
            text = "No spreadsheet column(s) selected. Please select at least one column"
            showinfo(message=text)
            logging.info(text)
            current_action_label["text"] = text
            root.update()
            return

    if context.get_app_data().get_output_reaper():
        actions = increment_actions(actions)

    if context.get_app_data().get_output_trackslive():
        actions = increment_actions(actions)

    if context.get_app_data().get_output_write_to_csv():
        actions = increment_actions(actions)

    action = "Start Processing..."
    log.info(action)
    current_action_label["text"] = action

    current_ip = read_current_ui_ip_address()

    if context.get_network_connection_allowed() and context.get_app_data().get_output_write_to_console():
        if not is_valid_ip_address(current_ip):
            error_message = "Invalid IP-Address"
            current_action_label["text"] = error_message
            root.update()
            showerror(message=error_message)
            return
        context.set_output(connect_to_console(current_ip))
    else:
        context.set_output(None)
    progress_open_or_close_connection()
    root.update()

    if context.get_app_data().get_output_write_to_console():
        if not context.get_csv_patching_hint_already_seen():
            showinfo(
                message='Hint: Input patching (Source, Socket) can be applied by using Director´s CSV Import function.')
            context.set_csv_patching_hint_already_seen(True)

        if context.get_output() is None:
            reset_progress_bar()
            root.update()
            return
        process_actions(action_list, actions, sheet)

    if context.get_app_data().get_output_reaper():
        action = "Creating Reaper Recording Session Template file..."
        log.info(action)
        current_action_label["text"] = action

        if var_reaper_additional_master_tracks.get() and var_master_recording_patch.get() == "Select DAW Input":
            progress(actions)
            root.update()
            showerror(message="DAW Inputs for additional master tracks must to be chosen.")
            return

        ReaperSessionCreator.create_session(sheet, root.reaper_output_dir, root.reaper_file_prefix,
                                            var_disable_track_numbering.get(), var_reaper_additional_prefix.get(),
                                            entry_additional_track_prefix.get(),
                                            var_reaper_additional_master_tracks.get(),
                                            var_master_recording_patch.get(), var_disable_track_coloring.get())
        log.info("Reaper Recording Session Template created")

        progress(actions)
        root.update()

    if context.get_app_data().get_output_trackslive():
        action = "Creating Tracks Live Recording Session Template file..."
        log.info(action)
        current_action_label["text"] = action

        if var_reaper_additional_master_tracks.get() and var_master_recording_patch.get() == "Select DAW Input":
            progress(actions)
            root.update()
            showerror(message="DAW Inputs for additional master tracks must to be chosen.")
            return

        TracksLiveSessionCreator.create_session(sheet, root.reaper_output_dir, root.reaper_file_prefix,
                                                var_disable_track_numbering.get(), var_reaper_additional_prefix.get(),
                                                entry_additional_track_prefix.get(),
                                                var_reaper_additional_master_tracks.get(),
                                                var_master_recording_patch.get(), var_disable_track_coloring.get())
        log.info("Tracks Live Recording Session Template created")

        progress(actions)
        root.update()

    if context.get_app_data().get_output_write_to_csv():
        showinfo(
            message='Info: You have selected the CSV Export Feature, Please use Directors Import CSV Feature to '
                    'import Name, Color, Patching, Gain, Pad, Phantom (48V)')

        action = "Creating Director CSV file..."
        log.info(action)
        current_action_label["text"] = action

        CsvCreator.create(sheet, root.reaper_output_dir, root.reaper_file_prefix)
        log.info("Director CSV file created")

        progress(actions)
        root.update()

    if actions == 0:
        progress(actions)
        root.update()

    action = "Processing done"
    log.info(action)
    current_action_label["text"] = ""

    if context.get_network_connection_allowed() & context.get_app_data().get_output_write_to_console():
        output = context.get_output()
        if output is not None:
            output.close()
    progress_open_or_close_connection()
    progress_open_or_close_connection()
    root.update()


def process_actions(action_list, actions, sheet):
    for action in action_list:
        action_message = action.get_message()
        if action.get_sheet_tab() == "channels":
            current_action_label["text"] = action_message
            if handle_channels_parameter(action_message, context, sheet.get_channel_model(),
                                         action.get_action()) == 1:
                reset_current_action_label()
                reset_progress_bar()
                exit(1)
        elif action.get_sheet_tab() == "sockets":
            current_action_label["text"] = action_message
            handle_sockets_parameter(action_message, context, sheet.get_socket_model(),
                                     action.get_action())

        elif action.get_sheet_tab() == "groups":
            current_action_label["text"] = action_message
            if handle_groups_parameter(action_message, context, sheet.get_group_model(),
                                       action.get_action(), action.get_bus_type()) == 1:
                reset_current_action_label()
                reset_progress_bar()
                exit(1)

        progress(actions)
        root.update()


def increment_actions(actions):
    actions = actions + 1
    return actions


def read_current_ui_ip_address():
    return ip_byte0.get() + "." + ip_byte1.get() + "." + ip_byte2.get() + "." + ip_byte3.get()


def determine_technical_midi_port(selected_midi_port_as_string):
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
        dliveConstants.midi_channel_drop_down_string_12: 11
    }
    return switcher.get(selected_midi_port_as_string, "Invalid port")


def determine_console_id(selected_console_as_string):
    switcher = {
        dliveConstants.console_drop_down_dlive: dliveConstants.console_drop_down_dlive,
        dliveConstants.console_drop_down_avantis: dliveConstants.console_drop_down_avantis
    }
    return switcher.get(selected_console_as_string, "Invalid console")


def reset_progress_bar():
    pb['value'] = 0.0
    value_label['text'] = update_progress_label()
    root.update()


def browse_files():
    reset_progress_bar()

    current_action_label["text"] = "Choose channel list spreadsheet..."
    root.update()

    cb_reaper = var_write_reaper.get()
    context.get_app_data().set_output_reaper(cb_reaper)

    cb_trackslive = var_write_trackslive.get()
    context.get_app_data().set_output_trackslive(cb_trackslive)

    cb_console_write = var_write_to_console.get()
    context.get_app_data().set_output_write_to_console(cb_console_write)

    cb_write_to_csv = var_write_to_csv.get()
    context.get_app_data().set_output_write_to_csv(cb_write_to_csv)

    if cb_reaper or cb_trackslive or cb_console_write or cb_write_to_csv:
        input_file_path = filedialog.askopenfilename()
        if input_file_path == "":
            # Nothing to do
            return

        root.reaper_output_dir = os.path.dirname(input_file_path)
        root.reaper_file_prefix = os.path.splitext(os.path.basename(input_file_path))[0]
        try:
            read_document(input_file_path)
        except TypeError as exc:

            error_message = "An error happened, probably an empty line could be the issue. " \
                            "Empty lines in spreadsheet are not supported."

            showerror(message=error_message)

            logging.error(error_message)
            logging.error(exc)

            reset_progress_bar()
            reset_current_action_label()

            exit(1)

        except ValueError as exc:

            error_message = "One of the following columns have unexpected characters. " \
                            "(Mono Auxes, Stereo Auxes, Mono Groups, Stereo Group, \n" \
                            "Mono Matrix, Stereo Matrix, \n" \
                            "Mono FX Send, Stereo FX Send, FX Return), the should only contain integer numbers. \n" \
                            "Please use the Name columns."

            showerror(message=error_message)
            logging.error(error_message)
            logging.error(exc)

            reset_progress_bar()
            reset_current_action_label()

            exit(1)

    else:
        showerror(message="Nothing to do, please select at least one output option.")


def trigger_background_process_spread_to_console():
    bg_thread = threading.Thread(target=browse_files)
    bg_thread.start()


def trigger_background_process_console_to_daw():
    bg_thread = threading.Thread(target=get_data_from_console)
    bg_thread.start()


def save_current_ui_settings():
    current_ip = ip_byte0.get() + "." + ip_byte1.get() + "." + ip_byte2.get() + "." + ip_byte3.get()
    context.get_app_data().set_console(determine_console_id(var_console.get()))
    context.get_app_data().set_midi_channel(var_midi_channel.get())
    context.get_app_data().set_current_ip(current_ip)
    persist_current_ui_settings(context)


def reset_ip_field_to_default_ip():
    default_ip = dliveConstants.ip
    set_ip_fields(default_ip)
    logging.info("Default ip: " + default_ip + " was set.")


def set_ip_field_to_local_director_ip():
    director_ip = "127.0.0.1"
    set_ip_fields(director_ip)
    logging.info("Director ip: " + director_ip + " was set.")


def set_ip_fields(ip_to_set):
    ip_byte0.delete(0, END)
    ip_byte0.insert(0, ip_to_set.split(".")[0])
    ip_byte1.delete(0, END)
    ip_byte1.insert(0, ip_to_set.split(".")[1])
    ip_byte2.delete(0, END)
    ip_byte2.insert(0, ip_to_set.split(".")[2])
    ip_byte3.delete(0, END)
    ip_byte3.insert(0, ip_to_set.split(".")[3])


def remove_tick(var_name):
    for var in grid.vars:
        if var._name == var_name:
            var.set(False)


def disable_avantis_checkboxes():
    cb_to_disable = [GuiConstants.TEXT_HPF_ON, GuiConstants.TEXT_HPF_VALUE, GuiConstants.TEXT_MUTE_GROUPS, GuiConstants.TEXT_UFX_SEND_NAME, GuiConstants.TEXT_UFX_SEND_COLOR, GuiConstants.TEXT_UFX_RETURN_NAME, GuiConstants.TEXT_UFX_RETURN_COLOR]
    for checkbox in grid.checkboxes:
        current_cb = checkbox.__getitem__("text")
        if current_cb in cb_to_disable:
            remove_tick(current_cb)
            checkbox.config(state="disabled")


def reactivate_avantis_checkboxes():
    for checkbox in grid.checkboxes:
        checkbox.config(state="normal")


def select_all_checkboxes():
    for var in grid.vars:
        var.set(True)


def clear_all_checkboxes():
    for var in grid.vars:
        var.set(False)


def set_limit_console_to_daw_end_channel(param):
    combobox_end.set(str(param))
    root.update()


def set_limit_console_to_daw_start_channel(param):
    combobox_start.set(str(param))
    root.update()


def on_endchannel_selected(*args):
    if var_console.get() == dliveConstants.console_drop_down_avantis and int(
            var_current_console_endChannel.get()) > dliveConstants.AVANTIS_MAX_CHANNELS:
        showerror(message="Avantis supports up to " + str(dliveConstants.AVANTIS_MAX_CHANNELS) + " Channels")
        set_limit_console_to_daw_end_channel(dliveConstants.AVANTIS_MAX_CHANNELS)


def on_startchannel_selected(*args):
    if var_console.get() == dliveConstants.console_drop_down_avantis and int(
            var_current_console_startChannel.get()) > dliveConstants.AVANTIS_MAX_CHANNELS:
        showerror(message="Avantis supports up to " + str(dliveConstants.AVANTIS_MAX_CHANNELS) + " Channels")
        set_limit_console_to_daw_start_channel(dliveConstants.AVANTIS_MAX_CHANNELS)


def on_console_selected(*args):
    context.get_app_data().set_console(var_console.get())
    print("The selected console is:", var_console.get())
    if var_console.get() == dliveConstants.console_drop_down_avantis:
        label_ip_address_text["text"] = GuiConstants.LABEL_IPADDRESS_AVANTIS
        root.update()

        if tab_control.index(tab_control.select()) == 0:  # = Spreadsheet to Console / DAW
            showinfo(
                message='Info: "' + GuiConstants.TEXT_HPF_ON +
                        '", "' + GuiConstants.TEXT_HPF_VALUE +
                        '" and "' + GuiConstants.TEXT_MUTE_GROUPS +

                        '" are currently not supported by the API of Avantis!')
        disable_avantis_checkboxes()
        set_limit_console_to_daw_end_channel(dliveConstants.AVANTIS_MAX_CHANNELS)
        root.update()

    elif var_console.get() == dliveConstants.console_drop_down_dlive:
        label_ip_address_text["text"] = GuiConstants.LABEL_IPADDRESS_DLIVE
        reactivate_avantis_checkboxes()
        set_limit_console_to_daw_end_channel(dliveConstants.DLIVE_MAX_CHANNELS)
        root.update()


def enable_reaper_options_ui_elements():
    cb_reaper_disable_numbering.config(state="normal")
    cb_reaper_disable_track_coloring.config(state="normal")
    cb_reaper_additional_prefix.config(state="normal")
    label_track_prefix.config(state="normal")
    cb_reaper_additional_master_tracks.config(state="normal")
    entry_additional_track_prefix.config(state="normal")
    combobox_master_track.config(state="normal")


def disable_reaper_options_ui_elements():
    cb_reaper_disable_numbering.config(state="disabled")
    cb_reaper_disable_track_coloring.config(state="disabled")
    cb_reaper_additional_prefix.config(state="disabled")
    label_track_prefix.config(state="disabled")
    cb_reaper_additional_master_tracks.config(state="disabled")
    entry_additional_track_prefix.config(state="disabled")
    combobox_master_track.config(state="disabled")


def on_reaper_write_changed():
    if var_write_reaper.get() or var_write_trackslive.get():
        enable_reaper_options_ui_elements()
    else:
        disable_reaper_options_ui_elements()


def enable_console_to_daw_prefix_ui_elements():
    entry_console_to_daw_additional_track_prefix.config(state="normal")
    label_console_to_daw_track_prefix.config(state="normal")


def disable_console_to_daw_prefix_ui_elements():
    entry_console_to_daw_additional_track_prefix.config(state="disabled")
    label_console_to_daw_track_prefix.config(state="disabled")


def on_console_to_daw_prefix_changed():
    if var_console_to_daw_reaper_additional_prefix.get():
        enable_console_to_daw_prefix_ui_elements()
    else:
        disable_console_to_daw_prefix_ui_elements()


def enable_console_to_daw_mastertracks_ui_elements():
    combobox_console_to_daw_master_track.config(state="normal")


def disable_console_to_daw_mastertracks_ui_elements():
    combobox_console_to_daw_master_track.config(state="disabled")


def on_console_to_daw_mastertracks_changed():
    if var_console_to_daw_additional_master_tracks.get():
        enable_console_to_daw_mastertracks_ui_elements()
    else:
        disable_console_to_daw_mastertracks_ui_elements()


def update_progress_label():
    return f"Current Progress: {round(pb['value'], 1)} %"


def progress(actions=None):
    if actions == 0:
        pb['value'] += 90
    else:
        if pb['value'] < 100:
            pb['value'] += 90 / actions
            value_label['text'] = update_progress_label()


def progress_open_or_close_connection():
    if round(pb['value']) < 100.0:
        pb['value'] += 5.0
        if pb['value'] > 100.0:
            pb['value'] = 100.0
        value_label['text'] = update_progress_label()
    else:
        showinfo(message='Writing completed!')


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


def about_dialog():
    about = AboutDialog(root)
    about.resizable(False, False)
    about.mainloop()


def update_current_action():
    current_action_label['text'] = update_current_action_label()


def reset_current_action_label():
    current_action_label['text'] = ""
    root.update()


def update_current_action_label():
    return f"Current Action:"


def connect_to_console(mix_rack_ip_tmp, test=False):
    text = "Try to open connection to console on ip: " + mix_rack_ip_tmp + ":" + str(dliveConstants.port) + " ..."

    logging.info(text)
    current_action_label["text"] = text
    try:
        output = connect(mix_rack_ip_tmp, dliveConstants.port)
        if test:
            action = "Connection Test Successful"
        else:
            action = "Connection successful"
        logging.info(action)
        current_action_label["text"] = action
        return output
    except socket.timeout:
        connect_err_message = "Connection to IP-Address: " + mix_rack_ip_tmp + " " + "could not be " \
                                                                                     "established. " \
                                                                                     "Are you in the same " \
                                                                                     "subnet?"
        action = "Connection failed"
        logging.error(action)
        current_action_label["text"] = action

        logging.error(connect_err_message)
        showerror(message=connect_err_message)
        reset_progress_bar()
        return None


def disconnect_from_console(output):
    output.close()


def test_ip_connection():
    reset_current_action_label()
    test_ip = read_current_ui_ip_address()

    if not is_valid_ip_address(test_ip):
        error_message = "Invalid IP-Address"
        current_action_label["text"] = error_message
        root.update()
        showerror(message=error_message)
        return

    logging.info("Test connection to " + str(test_ip))
    try:
        ret = connect_to_console(test_ip, test=True)

        if ret is not None:
            disconnect_from_console(ret)
            showinfo(message="Connection Test successful")
    except OSError:
        action = "Connection Test failed"
        logging.error(action)
        current_action_label["text"] = action
        showerror(message=action)


root = Tk()
ip_address_label = StringVar(root)
current_action_label = StringVar(root)
var_midi_channel = StringVar(root)
var_console = StringVar(root)
reaper_output_dir = ""
reaper_file_prefix = ""

csv_patching_hint_already_seen = False;

if __name__ == '__main__':

    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
    logger_instance = logging.getLogger(__name__)
    context = Context(logger_instance, None, None,
                      dliveConstants.allow_network_communication, CONFIG_FILE,
                      not GuiConstants.SHOW_CSV_PATCHING_HINT_ONCE_A_RUN)
    app_data = AppData(None, None, None)
    context.set_app_data(app_data)

    log = context.get_logger()
    log.info("dlive-midi-tool version: " + Toolinfo.version)
    root.title(Toolinfo.tool_name + ' - v' + Toolinfo.version)
    root.geometry('1300x840')
    root.resizable(False, False)



    # ----------------- Menu Area ------------------

    menu_bar = Menu(root)

    # Create the file menu
    file_menu = Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="About", command=about_dialog)
    file_menu.add_separator()
    file_menu.add_command(label="Close", command=root.destroy)

    # Add the file menu to the menu bar
    menu_bar.add_cascade(label="Help", menu=file_menu)

    # Display the menu bar
    root.config(menu=menu_bar)

    # ----------------- Tab Area ------------------

    tab_control = ttk.Notebook(root)

    # Tab 1 erstellen
    tab1 = ttk.Frame(tab_control)
    tab_control.add(tab1, text='Spreadsheet to Console / DAW')

    # Tab 2 erstellen
    tab2 = ttk.Frame(tab_control)
    tab_control.add(tab2, text='Console to DAW')

    tab1_frame = LabelFrame(tab1, text='Spreadsheet to Console / DAW')
    tab2_frame = LabelFrame(tab2, text='Console to DAW')

    # ----------------- Global Connection Settings ------------------

    config_frame = LabelFrame(root, text="Connection Settings")
    ip_frame = Frame(config_frame)
    console_frame = Frame(config_frame)
    console_frame.grid(row=1, column=0, sticky="W")

    ip_frame.grid(row=2, column=0, sticky="W")
    midi_channel_frame = Frame(config_frame)
    midi_channel_frame.grid(row=3, column=0, sticky="W")

    Label(console_frame, text="Audio Console:", width=25).pack(side=LEFT)

    dropdown_console = OptionMenu(console_frame, var_console,
                                  dliveConstants.console_drop_down_dlive,
                                  dliveConstants.console_drop_down_avantis,
                                  )

    dropdown_console.pack(side=RIGHT)

    var_console.set(read_persisted_console(context))

    label_ip_address_text = Label(ip_frame, text=ip_address_label.get(), width=25)
    if var_console.get() == dliveConstants.console_drop_down_avantis:
        label_ip_address_text["text"] = GuiConstants.LABEL_IPADDRESS_AVANTIS
        root.update()
        root.focus()
    elif var_console.get() == dliveConstants.console_drop_down_dlive:
        label_ip_address_text["text"] = GuiConstants.LABEL_IPADDRESS_DLIVE
        root.update()
        root.focus()
    label_ip_address_text.pack(side=LEFT)

    ip_field = Frame(ip_frame)
    ip_byte0 = Entry(ip_field, width=3)
    ip_byte1 = Entry(ip_field, width=3)
    ip_byte2 = Entry(ip_field, width=3)
    ip_byte3 = Entry(ip_field, width=3)

    ip_byte0.grid(row=0, column=0)
    Label(ip_field, text=".").grid(row=0, column=1)
    ip_byte1.grid(row=0, column=2)
    Label(ip_field, text=".").grid(row=0, column=3)
    ip_byte2.grid(row=0, column=4)
    Label(ip_field, text=".").grid(row=0, column=5)
    ip_byte3.grid(row=0, column=6)
    Label(ip_field, text="     ").grid(row=0, column=7)
    Button(ip_field, text='Save', command=save_current_ui_settings).grid(row=0, column=8)
    Button(ip_field, text='Director', command=set_ip_field_to_local_director_ip).grid(row=0, column=9)
    Button(ip_field, text='Default', command=reset_ip_field_to_default_ip).grid(row=0, column=10)
    Button(ip_field, text='Test Connection', command=test_ip_connection).grid(row=0, column=11)
    ip_field.pack(side=RIGHT)

    var_midi_channel.set(read_persisted_midi_port(context))  # default value

    Label(midi_channel_frame, text="Midi Channel:", width=25).pack(side=LEFT)

    dropdown_midi_channel = OptionMenu(midi_channel_frame, var_midi_channel,
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

    ip = read_persisted_ip(context)
    ip_from_config_file = ip.split(".")

    ip_byte0.insert(10, ip_from_config_file.__getitem__(0))
    ip_byte1.insert(11, ip_from_config_file.__getitem__(1))
    ip_byte2.insert(12, ip_from_config_file.__getitem__(2))
    ip_byte3.insert(13, ip_from_config_file.__getitem__(3))

    config_frame.pack(side=TOP)

    # ----------------- Spreadsheet to Console / DAW Area-------------------

    parameter_lf = LabelFrame(tab1, text="Choose from given spreadsheet which column you want to write", )

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
         GuiConstants.TEXT_MAINMIX
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

    grid = CheckboxGrid(parameter_lf, headers, labels)
    grid.pack(side=TOP)

    global_select_frame = Frame(parameter_lf)

    button_select_all = Button(global_select_frame, text='Select All', command=select_all_checkboxes, width=8)
    button_select_all.grid(row=0, column=0)
    button_clear_all = Button(global_select_frame, text='Clear', command=clear_all_checkboxes, width=8)
    button_clear_all.grid(row=0, column=1)

    parameter_lf.pack(pady=10, side=TOP)

    global_select_frame.pack(side=TOP)

    output_option_frame = LabelFrame(tab1, text="Output Options")

    var_write_to_csv = BooleanVar(value=False)
    write_to_csv = Checkbutton(output_option_frame, text="Generate Director CSV (Columns: Name, Color, Source, Socket, Gain, Pad, Phantom)",
                               var=var_write_to_csv)

    var_write_to_console = BooleanVar(value=True)
    write_to_console = Checkbutton(output_option_frame, text="Write to Audio Console or Director",
                                   var=var_write_to_console)

    var_write_reaper = BooleanVar(value=False)
    cb_reaper_write = Checkbutton(output_option_frame,
                                  text="Generate Reaper Recording Session with Name & Color (In & Out 1:1 Patch)",
                                  var=var_write_reaper, command=on_reaper_write_changed)

    var_write_trackslive = BooleanVar(value=False)
    cb_trackslive_write = Checkbutton(output_option_frame,
                                      text="Generate Tracks Live Template with Name & Color (In & Out 1:1 Patch)",
                                      var=var_write_trackslive, command=on_reaper_write_changed)

    var_disable_track_numbering = BooleanVar(value=False)
    cb_reaper_disable_numbering = Checkbutton(output_option_frame,
                                              text="Disable Track Numbering",
                                              var=var_disable_track_numbering)

    var_disable_track_coloring = BooleanVar(value=False)
    cb_reaper_disable_track_coloring = Checkbutton(output_option_frame,
                                                   text="Disable Track Coloring",
                                                   var=var_disable_track_coloring)

    label_track_prefix = Label(output_option_frame, text="Example: Band_Date_City", width=30)

    var_reaper_additional_prefix = BooleanVar(value=False)
    cb_reaper_additional_prefix = Checkbutton(output_option_frame,
                                              text="Add Custom Track Prefix",
                                              var=var_reaper_additional_prefix)

    entry_additional_track_prefix = Entry(output_option_frame, width=20)

    var_reaper_additional_master_tracks = BooleanVar(value=False)
    cb_reaper_additional_master_tracks = Checkbutton(output_option_frame,
                                                     text="Add 2 Additional Master-Tracks",
                                                     var=var_reaper_additional_master_tracks)

    values = [f"{i}-{i + 1}" for i in range(1, 127, 2)]
    values.append("127-128")  # workaround
    var_master_recording_patch = StringVar()
    combobox_master_track = Combobox(output_option_frame, textvariable=var_master_recording_patch, values=values)
    combobox_master_track.set("Select DAW Input")

    disable_reaper_options_ui_elements()

    write_to_console.grid(row=0, column=0, sticky="W")
    cb_reaper_write.grid(row=1, column=0, sticky="W")
    cb_reaper_disable_numbering.grid(row=1, column=1, sticky="W")
    cb_reaper_disable_track_coloring.grid(row=2, column=1, sticky="W")
    cb_reaper_additional_prefix.grid(row=3, column=1, sticky="W")
    entry_additional_track_prefix.grid(row=3, column=2, sticky="W")
    label_track_prefix.grid(row=3, column=3, sticky="W")
    cb_reaper_additional_master_tracks.grid(row=4, column=1, sticky="W")
    combobox_master_track.grid(row=4, column=2, sticky="W")
    cb_trackslive_write.grid(row=2, column=0, sticky="W")
    write_to_csv.grid(row=5, column=0, sticky="W")

    output_option_frame.pack(side=TOP, fill=X)

    bottom_frame = Frame(tab1)

    Button(bottom_frame, text='Open spreadsheet and start writing process',
           command=trigger_background_process_spread_to_console).grid(
        row=0, column=0)
    Label(bottom_frame, text=" ", width=30).grid(row=1)

    # ----------------- Console to DAW Area-------------------

    console_to_daw_settings_lf = LabelFrame(tab2, text="Settings")

    console_to_daw_settings_lf.pack(side=TOP)

    start_end_channel_frame = Frame(console_to_daw_settings_lf)

    values_start = [f"{i}" for i in range(1, 129)]
    var_current_console_startChannel = StringVar()
    combobox_start = Combobox(start_end_channel_frame, textvariable=var_current_console_startChannel,
                              values=values_start, width=3)
    combobox_start.set("1")

    Label(start_end_channel_frame, text="Channel Start").grid(row=0, column=0, sticky="w")
    combobox_start.grid(row=0, column=1)

    values_end = [f"{i}" for i in range(1, 129)]
    var_current_console_endChannel = StringVar()
    combobox_end = Combobox(start_end_channel_frame, textvariable=var_current_console_endChannel,
                            values=values_end, width=3)
    combobox_end.set("128")
    Label(start_end_channel_frame, text="End").grid(row=0, column=2)
    combobox_end.grid(row=0, column=3)

    start_end_channel_frame.grid(row=0)

    var_console_to_daw_disable_track_numbering_daw = BooleanVar(value=False)
    cb_console_to_daw_disable_track_numbering_daw = Checkbutton(console_to_daw_settings_lf,
                                                                text="Disable Track Numbering",
                                                                var=var_console_to_daw_disable_track_numbering_daw)

    var_console_to_daw_disable_track_coloring_daw = BooleanVar(value=False)
    cb_console_to_daw_disable_track_coloring_daw = Checkbutton(console_to_daw_settings_lf,
                                                               text="Disable Track Coloring",
                                                               var=var_console_to_daw_disable_track_coloring_daw)

    var_console_to_daw_reaper_additional_prefix = BooleanVar(value=False)
    cb_console_to_daw_reaper_additional_prefix = Checkbutton(console_to_daw_settings_lf,
                                                             text="Add Custom Track Prefix",
                                                             var=var_console_to_daw_reaper_additional_prefix,
                                                             command=on_console_to_daw_prefix_changed)

    entry_console_to_daw_additional_track_prefix = Entry(console_to_daw_settings_lf, width=20)

    label_console_to_daw_track_prefix = Label(console_to_daw_settings_lf, text="Example: Band_Date_City", width=25)

    var_console_to_daw_additional_master_tracks = BooleanVar(value=False)
    cb_console_to_daw_additional_master_tracks = Checkbutton(console_to_daw_settings_lf,
                                                             text="Add 2 Additional Master-Tracks",
                                                             var=var_console_to_daw_additional_master_tracks,
                                                             command=on_console_to_daw_mastertracks_changed)

    values = [f"{i}-{i + 1}" for i in range(1, 127, 2)]
    values.append("127-128")  # workaround
    var_console_to_daw_master_recording_patch = StringVar()
    combobox_console_to_daw_master_track = Combobox(console_to_daw_settings_lf,
                                                    textvariable=var_console_to_daw_master_recording_patch,
                                                    values=values)
    combobox_console_to_daw_master_track.set("Select DAW Input")

    disable_console_to_daw_prefix_ui_elements()
    disable_console_to_daw_mastertracks_ui_elements()

    console_to_daw_output_options_lf = LabelFrame(tab2, text="Output Options")

    var_console_to_daw_reaper = BooleanVar(value=False)
    cb_console_to_daw_reaper = Checkbutton(console_to_daw_output_options_lf,
                                           text="Generate Reaper Session",
                                           var=var_console_to_daw_reaper)

    var_console_to_daw_trackslive = BooleanVar(value=False)
    cb_console_to_daw_trackslive = Checkbutton(console_to_daw_output_options_lf,
                                               text="Generate Tracks Live Template",
                                               var=var_console_to_daw_trackslive)

    label_space = Label(console_to_daw_output_options_lf, width=48)

    cb_console_to_daw_reaper.grid(row=0, column=0, sticky="w")
    label_space.grid(row=0, column=1, sticky="w")
    cb_console_to_daw_trackslive.grid(row=1, sticky="w")

    console_to_daw_output_options_lf.pack(side=TOP)

    cb_console_to_daw_disable_track_numbering_daw.grid(row=1, sticky="w")
    cb_console_to_daw_disable_track_coloring_daw.grid(row=2, sticky="w")
    cb_console_to_daw_reaper_additional_prefix.grid(row=3, column=0, sticky="w")
    entry_console_to_daw_additional_track_prefix.grid(row=3, column=1, sticky="w")
    label_console_to_daw_track_prefix.grid(row=3, column=2)
    cb_console_to_daw_additional_master_tracks.grid(row=4, column=0, sticky="w")
    combobox_console_to_daw_master_track.grid(row=4, column=1, sticky="w")

    button_frame = Frame(tab2)

    Button(button_frame, text='Generate DAW session(s) from current console settings',
           command=trigger_background_process_console_to_daw).pack(side=BOTTOM)

    # ----------------- Status Area-------------------

    bottom3_frame = LabelFrame(root, text="Status")

    current_action_label = ttk.Label(bottom3_frame, text=current_action_label.get())
    current_action_label.grid(row=3)
    Label(bottom3_frame, text=" ", width=30).grid(row=5)

    pb = ttk.Progressbar(
        bottom3_frame,
        orient='horizontal',
        mode='determinate',
        length=1250
    )

    pb.grid(row=4)

    # label to show current value in percent
    value_label = ttk.Label(bottom3_frame, text=update_progress_label())
    value_label.grid(row=5)

    bottom4_frame = Frame(root)

    Button(bottom4_frame, text='Close', command=root.destroy).grid(row=6)
    Label(bottom4_frame, text=" ", width=30).grid(row=7)

    bottom4_frame.pack(side=BOTTOM)
    bottom3_frame.pack(side=BOTTOM)
    button_frame.pack(side=TOP)
    bottom_frame.pack(side=BOTTOM)

    var_console.trace("w", on_console_selected)
    var_current_console_endChannel.trace("w", on_endchannel_selected)
    var_current_console_startChannel.trace("w", on_startchannel_selected)

    tab_control.pack(expand=1, fill='both', side=TOP)

    root.mainloop()
