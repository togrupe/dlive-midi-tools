# coding=utf-8
####################################################
# Main Script
#
# Author: Tobias Grupe
#
####################################################
import ipaddress
import json
import logging
import os
import re
import socket
import threading
import time
from tkinter import filedialog, Button, Tk, Checkbutton, Frame, LEFT, TOP, X, RIGHT, Label, \
    Entry, BOTTOM, StringVar, OptionMenu, ttk, LabelFrame, BooleanVar, END, Menu
from tkinter.messagebox import showinfo, showerror
from tkinter.ttk import Combobox

import mido
import numpy
import pandas as pd
from mido.sockets import connect

import GuiConstants
import Toolinfo
import dliveConstants
from dawsession import ReaperSessionCreator, TracksLiveSessionCreator
from gui.AboutDialog import AboutDialog
from model.Action import Action
from model.ChannelListEntry import ChannelListEntry
from model.DcaConfig import DcaConfig
from model.GroupSetup import GroupSetup
from model.GroupsListEntry import GroupsListEntry
from model.Misc import Misc
from model.MuteGroupConfig import MuteGroupConfig
from model.Sheet import Sheet
from model.SocketListEntry import SocketListEntry
from spreadsheet import SpreadsheetConstants

LABEL_IPADDRESS_AVANTIS = "IP-Address:"
LABEL_IPADDRESS_DLIVE = "Mixrack IP-Address:"

DEFAULT_SLEEP_AFTER_MIDI_COMMAND = 0.01
DEFAULT_SLEEP_GROUPS_AFTER_MIDI_COMMAND = 0.001

LOG_FILE = 'main.log'
CONFIG_FILE = 'config.json'

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)

is_network_communication_allowed = dliveConstants.allow_network_communication


def convert_return_value_to_readable_color(in_message):
    color = in_message.data[10]
    color_ret = SpreadsheetConstants.spreadsheet_color_black

    if color == dliveConstants.lcd_color_blue:
        color_ret = SpreadsheetConstants.spreadsheet_color_blue
    elif color == dliveConstants.lcd_color_ltblue:
        color_ret = SpreadsheetConstants.spreadsheet_color_light_blue
    elif color == dliveConstants.lcd_color_red:
        color_ret = SpreadsheetConstants.spreadsheet_color_red
    elif color == dliveConstants.lcd_color_yellow:
        color_ret = SpreadsheetConstants.spreadsheet_color_yellow
    elif color == dliveConstants.lcd_color_green:
        color_ret = SpreadsheetConstants.spreadsheet_color_green
    elif color == dliveConstants.lcd_color_purple:
        color_ret = SpreadsheetConstants.spreadsheet_color_purple
    elif color == dliveConstants.lcd_color_black:
        color_ret = SpreadsheetConstants.spreadsheet_color_black
    elif color == dliveConstants.lcd_color_white:
        color_ret = SpreadsheetConstants.spreadsheet_color_white
    return color_ret


def get_color_channel(output, start_channel, end_channel):
    color = []

    for channel in range(start_channel, end_channel):
        prefix = [determine_technical_midi_port(var_midi_channel.get()),
                  dliveConstants.sysex_message_get_channel_colour, channel]

        message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + prefix + dliveConstants.sysexhdrend)
        if is_network_communication_allowed:
            output.send(message)

            response = output.receive()

            thisdict = {
                "dliveChannel": channel + 1,
                "technicalChannel": channel,
                "color": convert_return_value_to_readable_color(response),
                "name": None
            }

            color.append(thisdict)

            time.sleep(.01)

    return color


def extract_name(original_array):
    name = original_array.data[10:]

    ascii_string = ''.join(chr(num) for num in name if num != 0)

    return ascii_string.rstrip()


def get_name_channel(output, data_color, start_channel, end_channel):
    for channel in range(start_channel, end_channel):
        prefix = [determine_technical_midi_port(var_midi_channel.get()), dliveConstants.sysex_message_get_channel_name,
                  channel]

        message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + prefix + dliveConstants.sysexhdrend)
        if is_network_communication_allowed:
            output.send(message)

            channel_name = extract_name(output.receive())

            for item in data_color:
                if item['technicalChannel'] == channel:
                    item['name'] = channel_name
                    break

            time.sleep(.01)
    return data_color


def get_data_from_console():
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

        if is_network_communication_allowed:
            output = connect_to_console(read_current_ui_ip_address())
            start_channel = int(var_current_console_startChannel.get()) - 1
            end_channel = int(var_current_console_endChannel.get())
            if start_channel > end_channel:
                error_msg = "Start Channel: " + str(start_channel + 1) + " is greater than End Channel: " + str(
                    end_channel)
                logging.error(error_msg)
                showerror(message=error_msg)
                return

            current_action_label["text"] = "Reading channel color from console"
            progress(actions)
            root.update()
            data_color = get_color_channel(output, start_channel, end_channel)

            current_action_label["text"] = "Reading channel name from console"
            progress(actions)
            root.update()
            data_fin = get_name_channel(output, data_color, start_channel, end_channel)

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
                    logging.info(text)

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
                    logging.info(text)

                output.close()
                progress_open_or_close_connection()

            except OSError:
                error = "Some thing went wrong during store, please choose a folder where you have write rights."
                logging.error(error)
                current_action_label["text"] = error
                showerror(message=error)
                return

            showinfo(message='Reading from console done, session(s) created!')
        else:
            output = None
    else:
        showerror(message="Nothing to do, please select at least one output option.")


def create_channel_list_content_from_console(data_fin):
    channel_list_entries = []
    index = 0

    for item in data_fin:
        cle = ChannelListEntry(item['dliveChannel'],
                               item['name'],
                               item['color'],
                               None,
                               None,
                               None,
                               None,
                               'yes',
                               'yes',
                               None,
                               None,
                               None)

        channel_list_entries.append(cle)
        index = index + 1

    return channel_list_entries


def name_channel(output, item, midi_channel_offset, channel_offset, bus_type):
    # Trim name if length of name > dliveConstants.trim_after_x_charactors
    if len(str(item.get_name())) > dliveConstants.trim_after_x_charactors:
        trimmed_name = str(item.get_name())[0:dliveConstants.trim_after_x_charactors]
        logging.info(
            "Channel name will be trimmed to 6 characters, before: " + str(item.get_name()) + " after: " + str(
                trimmed_name))
    else:
        trimmed_name = str(item.get_name())

    if trimmed_name == SpreadsheetConstants.spreadsheet_bypass_sign or trimmed_name == SpreadsheetConstants.spreadsheet_bypass_string:
        logging.info("Don´t care flag found, skipping name for channel: " + str(item.get_channel()))
        return

    if trimmed_name == 'nan':
        characters = [' ', ' ', ' ', ' ', ' ', ' ', '']
    else:
        characters = re.findall('.?', trimmed_name)

    payload = []

    for character in characters:
        if len(str(character)) != 0:
            value = ord(character)
            if value > 127:
                error_msg = "One of the characters in " + str(bus_type) + ": channel " + str(
                    item.get_channel_console() + 1) + " is not supported. Characters like ä, ö, ü, é are not supported."
                logging.error(error_msg)
                showerror(message=error_msg)
                reset_current_action_label()
                reset_progress_bar()
                output.close()
                exit(1)
            else:
                payload.append(value)

    prefix = [root.midi_channel + midi_channel_offset, dliveConstants.sysex_message_set_channel_name,
              channel_offset + item.get_channel_console()]
    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + prefix + payload + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
        time.sleep(DEFAULT_SLEEP_AFTER_MIDI_COMMAND)


def color_channel(output, item, midi_channel_offset, channel_offset):
    lower_color = item.get_color().lower()

    if lower_color == SpreadsheetConstants.spreadsheet_bypass_sign or lower_color == SpreadsheetConstants.spreadsheet_bypass_string:
        logging.info("Don´t care flag found, skipping channel color: " + str(item.get_channel()))
        return
    elif lower_color == SpreadsheetConstants.spreadsheet_color_blue:
        colour = dliveConstants.lcd_color_blue
    elif lower_color == SpreadsheetConstants.spreadsheet_color_red:
        colour = dliveConstants.lcd_color_red
    elif lower_color == SpreadsheetConstants.spreadsheet_color_light_blue:
        colour = dliveConstants.lcd_color_ltblue
    elif lower_color == SpreadsheetConstants.spreadsheet_color_purple:
        colour = dliveConstants.lcd_color_purple
    elif lower_color == SpreadsheetConstants.spreadsheet_color_green:
        colour = dliveConstants.lcd_color_green
    elif lower_color == SpreadsheetConstants.spreadsheet_color_yellow:
        colour = dliveConstants.lcd_color_yellow
    elif lower_color == SpreadsheetConstants.spreadsheet_color_black:
        colour = dliveConstants.lcd_color_black
    elif lower_color == SpreadsheetConstants.spreadsheet_color_white:
        colour = dliveConstants.lcd_color_white
    elif lower_color == 'nan':
        logging.info("Empty cell found, treating as don´t care, skipping channel")
        return
    else:
        logging.warning("Given color: " + lower_color + " is not supported, setting default color: black")
        colour = dliveConstants.lcd_color_black

    payload_array = [root.midi_channel + midi_channel_offset, dliveConstants.sysex_message_set_channel_colour,
                     channel_offset + item.get_channel_console(),
                     colour]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
        time.sleep(DEFAULT_SLEEP_AFTER_MIDI_COMMAND)


def mute_on_channel(output, item):
    midi_channel_tmp = root.midi_channel

    lower_mute_on = item.get_mute().lower()
    channel = item.get_channel_console()

    if lower_mute_on == SpreadsheetConstants.spreadsheet_bypass_sign or lower_mute_on == SpreadsheetConstants.spreadsheet_bypass_string:
        logging.info("Don´t care flag found, skipping channel")
        return
    elif lower_mute_on == "yes":
        message_on = mido.Message('note_on', channel=midi_channel_tmp, note=channel, velocity=dliveConstants.mute_on)
        message_off = mido.Message('note_on', channel=midi_channel_tmp, note=channel, velocity=dliveConstants.note_off)
    elif lower_mute_on == "no":
        message_on = mido.Message('note_on', channel=midi_channel_tmp, note=channel, velocity=dliveConstants.mute_off)
        message_off = mido.Message('note_on', channel=midi_channel_tmp, note=channel, velocity=dliveConstants.note_off)
    elif lower_mute_on == 'nan':
        logging.info("Empty cell found, treating as don´t care, skipping channel")
        return
    else:
        logging.warning("Unexpected input value found")
        return

    if is_network_communication_allowed:
        output.send(message_on)
        output.send(message_off)
        time.sleep(DEFAULT_SLEEP_AFTER_MIDI_COMMAND)


def phantom_socket(output, item, socket_type):
    socket_tmp = item.get_socket_number()
    socket_dlive_tmp = item.get_socket_number_dlive()

    if socket_type == "local":
        if socket_tmp <= dliveConstants.LOCAL_DLIVE_SOCKET_COUNT_MAX and root.console == dliveConstants.console_drop_down_dlive:
            lower_phantom = str(item.get_local_phantom()).lower()
            socket = socket_dlive_tmp
        elif socket_tmp <= dliveConstants.LOCAL_AVANTIS_SOCKET_COUNT_MAX and root.console == dliveConstants.console_drop_down_avantis:
            lower_phantom = str(item.get_local_phantom()).lower()
            socket = socket_dlive_tmp
        else:
            return

    elif socket_type == "DX1":
        if socket_tmp <= dliveConstants.DX1_SOCKET_COUNT_MAX:
            lower_phantom = str(item.get_dx1_phantom()).lower()
            socket = socket_dlive_tmp + 64
        else:
            return

    elif socket_type == "DX3":
        if socket_tmp <= dliveConstants.DX3_SOCKET_COUNT_MAX:
            lower_phantom = str(item.get_dx3_phantom()).lower()
            socket = socket_dlive_tmp + 96
        else:
            return

    elif socket_type == "Slink":
        if socket_tmp <= dliveConstants.SLINK_SOCKET_COUNT_MAX:
            lower_phantom = str(item.get_slink_phantom()).lower()
            socket = socket_dlive_tmp + 64
        else:
            return

    if lower_phantom == SpreadsheetConstants.spreadsheet_bypass_sign or lower_phantom == SpreadsheetConstants.spreadsheet_bypass_string:
        logging.info("Don´t care flag found, skipping socket: " + str(socket))
        return
    elif lower_phantom == "yes":
        res = dliveConstants.phantom_power_on
    elif lower_phantom == "no":
        res = dliveConstants.phantom_power_off
    else:
        logging.info("empty cell found, treating as don´t care, skipping socket: " + str(socket))
        return

    # TODO Currently required because value of socket cannot be higher than 127
    if socket > 127:
        return

    payload_array = [root.midi_channel, dliveConstants.sysex_message_set_socket_preamp_48V, socket,
                     res]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
        time.sleep(DEFAULT_SLEEP_AFTER_MIDI_COMMAND)


def hpf_on_channel(output, item):
    lower_hpf_on = str(item.get_hpf_on()).lower()

    if lower_hpf_on == SpreadsheetConstants.spreadsheet_bypass_sign or lower_hpf_on == SpreadsheetConstants.spreadsheet_bypass_string:
        logging.info("Don´t care flag found, skipping channel")
        return
    elif lower_hpf_on == "yes":
        res = dliveConstants.hpf_on
    elif lower_hpf_on == "no":
        res = dliveConstants.hpf_off
    elif lower_hpf_on == 'nan':
        logging.info("Empty cell found, treating as don´t care, skipping channel")
        return
    else:
        logging.warning("Unexpected input value found")
        return

    if is_network_communication_allowed:
        output.send(
            mido.Message('control_change', channel=root.midi_channel, control=0x63, value=item.get_channel_console()))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_hpf_on))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x6, value=res))
        time.sleep(DEFAULT_SLEEP_AFTER_MIDI_COMMAND)


def calculate_vv(hpf_value):
    return int(27.58 * numpy.log(float(hpf_value)) - 82.622)


def clamp(value, lower_limit, upper_limit):
    return max(lower_limit, min(value, upper_limit))


def hpf_value_channel(output, item):
    hpf_value = item.get_hpf_value()
    if hpf_value == 'nan' or hpf_value == SpreadsheetConstants.spreadsheet_bypass_sign or hpf_value == SpreadsheetConstants.spreadsheet_bypass_string:
        logging.info("Don´t care flag found, skipping channel")
        return
    if int(hpf_value) < dliveConstants.hpf_min_frequency or int(hpf_value) > dliveConstants.hpf_max_frequency:
        showerror(message="Highpass filter value of CH: " + str(item.get_channel()) +
                          " only allows values between " + str(dliveConstants.hpf_min_frequency) + " and "
                          + str(dliveConstants.hpf_max_frequency) + " Hz. Given value: " + hpf_value +
                          " has been clipped to the lower or upper limit.")

    value_freq = calculate_vv(clamp(int(hpf_value), 20, 2000))

    if is_network_communication_allowed:
        output.send(
            mido.Message('control_change', channel=root.midi_channel, control=0x63, value=item.get_channel_console()))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_hpf_frequency))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x6, value=value_freq))
        time.sleep(DEFAULT_SLEEP_AFTER_MIDI_COMMAND)


def fader_level_channel(output, item):
    lower_fader_level = str(item.get_fader_level())

    if lower_fader_level == 'nan':
        return

    switcher = {
        "10": dliveConstants.fader_level_plus10,
        "5": dliveConstants.fader_level_plus5,
        "0": dliveConstants.fader_level_zero,
        "-5": dliveConstants.fader_level_minus5,
        "-10": dliveConstants.fader_level_minus10,
        "-15": dliveConstants.fader_level_minus15,
        "-20": dliveConstants.fader_level_minus20,
        "-25": dliveConstants.fader_level_minus25,
        "-30": dliveConstants.fader_level_minus30,
        "-35": dliveConstants.fader_level_minus35,
        "-40": dliveConstants.fader_level_minus40,
        "-45": dliveConstants.fader_level_minus45,
        "-99": dliveConstants.fader_level_minus_inf,
        SpreadsheetConstants.spreadsheet_bypass_sign: -1,
        SpreadsheetConstants.spreadsheet_bypass_string: -1
    }
    fader_level = switcher.get(lower_fader_level, -2)

    if fader_level == -1:
        logging.info("Don´t care flag found, skipping fader level for channel: " + str(item.get_channel()))
        return

    if fader_level == -2:
        errormsg = "Invalid fader level: " + lower_fader_level + " at channel: " + \
                   str(item.get_channel()) + ". Please use the dropdown values. Channel will be skipped"
        logging.info(errormsg)
        showerror(message=errormsg)
        return

    logging.info("Set Fader to: " + str(lower_fader_level) + " at Channel: " + str(item.get_channel()))

    if is_network_communication_allowed:
        output.send(
            mido.Message('control_change', channel=root.midi_channel, control=0x63, value=item.get_channel_console()))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_fader_level))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x6, value=int(fader_level)))
        time.sleep(DEFAULT_SLEEP_AFTER_MIDI_COMMAND)


def handle_channels_parameter(message, output, channel_list_entries, action):
    logging.info(message)
    current_action_label["text"] = message

    if var_console.get() == dliveConstants.console_drop_down_avantis:
        max_count_dsp_channels = 64
    else:
        max_count_dsp_channels = 128

    for item in channel_list_entries:
        if item.get_channel_console() > max_count_dsp_channels - 1:
            logging.warning("Skipping Channel...current channel number: " + str(item.get_channel()) +
                            " is bigger than the console supports.")
            continue
        logging.info("Processing " + action + " for channel: " + str(item.get_channel_console() + 1))
        if action == "name":
            name_channel(output, item, dliveConstants.midi_channel_offset_channels,
                         dliveConstants.channel_offset_channels, "Input Channels")
        elif action == "color":
            color_channel(output, item, dliveConstants.midi_channel_offset_channels,
                          dliveConstants.channel_offset_channels)
        elif action == "mute":
            mute_on_channel(output, item)
        elif action == "fader_level":
            fader_level_channel(output, item)
        elif action == "hpf_on":
            hpf_on_channel(output, item)
        elif action == "hpf_value":
            hpf_value_channel(output, item)
        elif action == "dca":
            dca_channel(output, item)
        elif action == "mute_group":
            mg_channel(output, item)
        elif action == "assign_main_mix":
            assign_mainmix_channel(output, item)


def pad_socket(output, item, socket_type):
    socket_tmp = item.get_socket_number()
    socket_dlive_tmp = item.get_socket_number_dlive()

    if socket_type == "local":
        if socket_tmp <= dliveConstants.LOCAL_DLIVE_SOCKET_COUNT_MAX and root.console == dliveConstants.console_drop_down_dlive:
            lower_pad = str(item.get_local_pad()).lower()
            socket = socket_dlive_tmp
        elif socket_tmp <= dliveConstants.LOCAL_AVANTIS_SOCKET_COUNT_MAX and root.console == dliveConstants.console_drop_down_avantis:
            lower_pad = str(item.get_local_pad()).lower()
            socket = socket_dlive_tmp
        else:
            return

    elif socket_type == "DX1":
        if socket_tmp <= dliveConstants.DX1_SOCKET_COUNT_MAX:
            lower_pad = str(item.get_dx1_pad()).lower()
            socket = socket_dlive_tmp + 64
        else:
            return

    elif socket_type == "DX3":
        if socket_tmp <= dliveConstants.DX3_SOCKET_COUNT_MAX:
            lower_pad = str(item.get_dx3_pad()).lower()
            socket = socket_dlive_tmp + 96
        else:
            return

    elif socket_type == "Slink":
        if socket_tmp <= dliveConstants.SLINK_SOCKET_COUNT_MAX:
            lower_pad = str(item.get_slink_pad()).lower()
            socket = socket_dlive_tmp + 64
        else:
            return

    if lower_pad == SpreadsheetConstants.spreadsheet_bypass_sign:
        logging.info("Don´t care flag found, skipping socket: " + str(socket))
        return
    elif lower_pad == "yes":
        res = dliveConstants.pad_on
    elif lower_pad == "no":
        res = dliveConstants.pad_off
    elif lower_pad == 'nan':
        logging.info("empty cell found, treating as don´t care, skipping socket: " + str(socket))
        return
    else:
        logging.warning("unexpected input value found")
        return

    # TODO Currently required because value of socket cannot be higher than 127
    if socket > 127:
        return

    payload_array = [root.midi_channel, dliveConstants.sysex_message_set_socket_preamp_pad, socket, res]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
        time.sleep(DEFAULT_SLEEP_AFTER_MIDI_COMMAND)


def gain_socket(output, item, socket_type):
    socket_tmp = item.get_socket_number()
    socket_dlive_tmp = item.get_socket_number_dlive()

    if socket_type == "local":
        if socket_tmp <= dliveConstants.LOCAL_DLIVE_SOCKET_COUNT_MAX and root.console == dliveConstants.console_drop_down_dlive:
            gain_sheet_lower = str(item.get_local_gain())
            socket = socket_dlive_tmp
        elif socket_tmp <= dliveConstants.LOCAL_AVANTIS_SOCKET_COUNT_MAX and root.console == dliveConstants.console_drop_down_avantis:
            gain_sheet_lower = str(item.get_local_gain())
            socket = socket_dlive_tmp
        else:
            return

    elif socket_type == "DX1":
        if socket_tmp <= dliveConstants.DX1_SOCKET_COUNT_MAX:
            gain_sheet_lower = str(item.get_dx1_gain())
            socket = socket_dlive_tmp + 64
        else:
            return

    elif socket_type == "DX3":
        if socket_tmp <= dliveConstants.DX3_SOCKET_COUNT_MAX:
            gain_sheet_lower = str(item.get_dx3_gain())
            socket = socket_dlive_tmp + 96
        else:
            return

    elif socket_type == "Slink":
        if socket_tmp <= dliveConstants.SLINK_SOCKET_COUNT_MAX:
            gain_sheet_lower = str(item.get_slink_gain())
            socket = socket_dlive_tmp + 64
        else:
            return

    # TODO Currently required because value of socket cannot be higher than 127
    if socket > 127:
        return

    if gain_sheet_lower == 'nan' or gain_sheet_lower == 'byp':
        logging.info("empty cell found, treating as don´t care, skipping socket: " + str(socket))
        return

    switcher = {
        "60": dliveConstants.gain_level_plus60,
        "55": dliveConstants.gain_level_plus55,
        "50": dliveConstants.gain_level_plus50,
        "45": dliveConstants.gain_level_plus45,
        "40": dliveConstants.gain_level_plus40,
        "35": dliveConstants.gain_level_plus35,
        "30": dliveConstants.gain_level_plus30,
        "25": dliveConstants.gain_level_plus25,
        "20": dliveConstants.gain_level_plus20,
        "15": dliveConstants.gain_level_plus15,
        "10": dliveConstants.gain_level_plus10,
        "5": dliveConstants.gain_level_plus5,
        SpreadsheetConstants.spreadsheet_bypass_sign: -1
    }
    gain_level = switcher.get(gain_sheet_lower, "Invalid gain level")

    if gain_level == -1:
        logging.info("Don´t care flag found, skipping socket: " + str(socket))
        return

    if is_network_communication_allowed:
        logging.info("Set Gain Level " + str(gain_sheet_lower) + "dB/" + str(hex(gain_level)) + " to socket: " + str(
            socket_type) + ":" + str(socket))

        byte_1 = gain_level << 8
        byte_2 = socket << 1
        byte_all = byte_1 | byte_2
        byte_out = byte_all >> 1
        byte_out = byte_out - 8192

        output.send(mido.Message('pitchwheel', channel=root.midi_channel, pitch=byte_out))
        time.sleep(DEFAULT_SLEEP_AFTER_MIDI_COMMAND)


def handle_sockets_parameter(message, output, socket_list_entries, action):
    logging.info(message)
    current_action_label["text"] = message

    for item in socket_list_entries:
        logging.info("Processing " + action + " for socket: " + str(item.get_socket_number()))
        if action == "phantom":
            if root.console == dliveConstants.console_drop_down_dlive:
                phantom_socket(output, item, "local")
                phantom_socket(output, item, "DX1")
                phantom_socket(output, item, "DX3")
            elif root.console == dliveConstants.console_drop_down_avantis:
                phantom_socket(output, item, "local")
                phantom_socket(output, item, "Slink")
        elif action == "pad":
            if root.console == dliveConstants.console_drop_down_dlive:
                pad_socket(output, item, "local")
                pad_socket(output, item, "DX1")
                pad_socket(output, item, "DX3")
            elif root.console == dliveConstants.console_drop_down_avantis:
                pad_socket(output, item, "local")
                pad_socket(output, item, "Slink")
        elif action == "gain":
            if root.console == dliveConstants.console_drop_down_dlive:
                gain_socket(output, item, "local")
                gain_socket(output, item, "DX1")
                gain_socket(output, item, "DX3")
            elif root.console == dliveConstants.console_drop_down_avantis:
                gain_socket(output, item, "local")
                gain_socket(output, item, "Slink")


def assign_dca(output, channel, dca_value):
    if is_network_communication_allowed:
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x63, value=channel))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_dca_assign))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x6, value=dca_value))
        time.sleep(DEFAULT_SLEEP_GROUPS_AFTER_MIDI_COMMAND)


def assign_mainmix(output, channel, mainmix_value):
    if is_network_communication_allowed:
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x63, value=channel))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_mainmix_assign))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x6, value=mainmix_value))
        time.sleep(DEFAULT_SLEEP_GROUPS_AFTER_MIDI_COMMAND)


def dca_channel(output, item):
    channel = item.get_channel_console()

    for dca_index in range(0, 24):

        if root.console == dliveConstants.console_drop_down_avantis and dca_index > 15:
            return

        dca_config = item.get_dca_config()
        dca_array = dca_config.get_dca_array()

        dca_array_item_lower = dca_array.__getitem__(dca_index).lower()

        if dca_array_item_lower == SpreadsheetConstants.spreadsheet_bypass_sign or dca_array_item_lower == SpreadsheetConstants.spreadsheet_bypass_string:
            continue
        elif dca_array.__getitem__(dca_index).lower() == "x":
            assign_dca(output, channel, dliveConstants.dca_on_base_address + dca_index)
        else:
            assign_dca(output, channel, dliveConstants.dca_off_base_address + dca_index)


def assign_mainmix_channel(output, item):
    channel = item.get_channel_console()
    mainmix_value = item.get_assign_mainmix()

    if mainmix_value == 'nan' or mainmix_value == SpreadsheetConstants.spreadsheet_bypass_sign or mainmix_value == SpreadsheetConstants.spreadsheet_bypass_string:
        logging.info("Don´t care flag found, skipping channel")
        return

    if mainmix_value.lower() == "yes":
        assign_mainmix(output, channel, dliveConstants.mainmix_on)
    else:
        assign_mainmix(output, channel, dliveConstants.mainmix_off)


def assign_mg(output, channel, mg_value):
    if is_network_communication_allowed:
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x63, value=channel))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_mg_assign))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x6, value=mg_value))
        time.sleep(DEFAULT_SLEEP_GROUPS_AFTER_MIDI_COMMAND)


def mg_channel(output, item):
    channel = item.get_channel_console()

    for mg_index in range(0, 8):

        mg_config = item.get_mg_config()
        mg_array = mg_config.get_mg_array()

        mg_array_item_lower = mg_array.__getitem__(mg_index).lower()
        if mg_array_item_lower == SpreadsheetConstants.spreadsheet_bypass_sign or mg_array_item_lower == SpreadsheetConstants.spreadsheet_bypass_string:
            continue
        elif mg_array_item_lower == "x":
            assign_mg(output, channel, dliveConstants.mg_on_base_address + mg_index)
        else:
            assign_mg(output, channel, dliveConstants.mg_off_base_address + mg_index)


def is_valid_ip_address(ip_address):
    try:
        ipaddress.IPv4Address(ip_address)
        return True
    except ipaddress.AddressValueError:
        return False


def handle_groups_parameter(message, output, groups_model, action, bus_type):
    logging.info(message)
    current_action_label["text"] = message

    if bus_type == "dca":
        for item in groups_model.get_dca_config():
            if action == "name":
                name_channel(output, item, dliveConstants.midi_channel_offset_dca, dliveConstants.channel_offset_dca,
                             bus_type)
            elif action == "color":
                color_channel(output, item, dliveConstants.midi_channel_offset_dca, dliveConstants.channel_offset_dca)

    if bus_type == "aux_mono":
        for item in groups_model.get_auxes_mono_config():
            if action == "name":
                name_channel(output, item, dliveConstants.midi_channel_offset_auxes,
                             dliveConstants.channel_offset_auxes_mono, bus_type)
            elif action == "color":
                color_channel(output, item, dliveConstants.midi_channel_offset_auxes,
                              dliveConstants.channel_offset_auxes_mono)

    if bus_type == "aux_stereo":
        for item in groups_model.get_auxes_stereo_config():
            if action == "name":
                name_channel(output, item, dliveConstants.midi_channel_offset_auxes,
                             dliveConstants.channel_offset_auxes_stereo, bus_type)
            elif action == "color":
                color_channel(output, item, dliveConstants.midi_channel_offset_auxes,
                              dliveConstants.channel_offset_auxes_stereo)

    if bus_type == "group_mono":
        for item in groups_model.get_group_mono_config():
            if action == "name":
                name_channel(output, item, dliveConstants.midi_channel_offset_groups,
                             dliveConstants.channel_offset_groups_mono, bus_type)
            elif action == "color":
                color_channel(output, item, dliveConstants.midi_channel_offset_groups,
                              dliveConstants.channel_offset_groups_mono)

    if bus_type == "group_stereo":
        for item in groups_model.get_group_stereo_config():
            if action == "name":
                name_channel(output, item, dliveConstants.midi_channel_offset_groups,
                             dliveConstants.channel_offset_groups_stereo, bus_type)
            elif action == "color":
                color_channel(output, item, dliveConstants.midi_channel_offset_groups,
                              dliveConstants.channel_offset_groups_stereo)

    if bus_type == "matrix_mono":
        for item in groups_model.get_matrix_mono_config():
            if action == "name":
                name_channel(output, item, dliveConstants.midi_channel_offset_matrices,
                             dliveConstants.channel_offset_matrices_mono, bus_type)
            elif action == "color":
                color_channel(output, item, dliveConstants.midi_channel_offset_matrices,
                              dliveConstants.channel_offset_matrices_mono)

    if bus_type == "matrix_stereo":
        for item in groups_model.get_matrix_stereo_config():
            if action == "name":
                name_channel(output, item, dliveConstants.midi_channel_offset_matrices,
                             dliveConstants.channel_offset_matrices_stereo, bus_type)
            elif action == "color":
                color_channel(output, item, dliveConstants.midi_channel_offset_matrices,
                              dliveConstants.channel_offset_matrices_stereo)

    if bus_type == "fx_send_mono":
        for item in groups_model.get_fx_send_mono_config():
            if action == "name":
                name_channel(output, item, dliveConstants.midi_channel_offset_fx_send_mono,
                             dliveConstants.channel_offset_fx_send_mono, bus_type)
            elif action == "color":
                color_channel(output, item, dliveConstants.midi_channel_offset_fx_send_mono,
                              dliveConstants.channel_offset_fx_send_mono)

    if bus_type == "fx_send_stereo":
        for item in groups_model.get_fx_send_stereo_config():
            if action == "name":
                name_channel(output, item, dliveConstants.midi_channel_offset_fx_send_stereo,
                             dliveConstants.channel_offset_fx_send_stereo, bus_type)
            elif action == "color":
                color_channel(output, item, dliveConstants.midi_channel_offset_fx_send_stereo,
                              dliveConstants.channel_offset_fx_send_stereo)

    if bus_type == "fx_return":
        for item in groups_model.get_fx_return_config():
            if action == "name":
                name_channel(output, item, dliveConstants.midi_channel_offset_fx_return,
                             dliveConstants.channel_offset_fx_return, bus_type)
            elif action == "color":
                color_channel(output, item, dliveConstants.midi_channel_offset_fx_return,
                              dliveConstants.channel_offset_fx_return)


def read_document(filename, check_box_reaper, check_box_trackslive, check_box_write_to_console):
    logging.info('The following file will be read : ' + str(filename))

    sheet = Sheet()

    sheet.set_misc_model(create_misc_content(pd.read_excel(filename, sheet_name="Misc")))

    latest_spreadsheet_version = '10'

    read_version = sheet.get_misc_model().get_version()

    if read_version != latest_spreadsheet_version:
        error_msg = "Given spreadsheet version: " + str(
            read_version) + " is not compatible. Please use the latest spread " \
                            "sheet (Version " + latest_spreadsheet_version + \
                    "). You can see the version in the spreadsheet tab \"Misc\""
        logging.error(error_msg)
        showerror(message=error_msg)
        return root.quit()

    sheet.set_channel_model(create_channel_list_content(pd.read_excel(filename, sheet_name="Channels", dtype=str)))
    sheet.set_socket_model(create_socket_list_content(pd.read_excel(filename, sheet_name="Sockets", dtype=str)))
    sheet.set_group_model(create_groups_list_content(pd.read_excel(filename, sheet_name="Groups", dtype=str)))

    root.midi_channel = determine_technical_midi_port(var_midi_channel.get())
    root.console = determine_console_id(var_console.get())

    actions = 0

    if check_box_write_to_console:
        cb_write_to_console = True
    else:
        cb_write_to_console = False

    if var_console.get() == dliveConstants.console_drop_down_avantis:
        disable_avantis_checkboxes()
        root.update()

    action_list = []

    if cb_write_to_console:
        for var in grid.vars:
            logging.info("Current checkbox name: " + str(var._name) + " State=" + str(var.get()))

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
            elif var._name == GuiConstants.TEXT_AUX_STERE0_COLOR and var.get() is True:
                action = Action(GuiConstants.TEXT_AUX_STERE0_COLOR, "groups",
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

    if check_box_reaper:
        actions = increment_actions(actions)
        cb_reaper = True
    else:
        cb_reaper = False

    if check_box_trackslive:
        actions = increment_actions(actions)
        cb_trackslive = True
    else:
        cb_trackslive = False

    if check_box_write_to_console and actions == 0:
        showinfo(message="No spreadsheet column(s) selected. Please select at least one column")
        return

    action = "Start Processing..."
    logging.info(action)
    current_action_label["text"] = action

    if is_network_communication_allowed & check_box_write_to_console:
        output = connect_to_console(read_current_ui_ip_address())
    else:
        output = None
    progress_open_or_close_connection()
    root.update()

    if cb_write_to_console:
        for action in action_list:
            if action.get_sheet_tab() == "channels":
                handle_channels_parameter(action.get_message(), output, sheet.get_channel_model(),
                                          action.get_action())

            elif action.get_sheet_tab() == "sockets":
                handle_sockets_parameter(action.get_message(), output, sheet.get_socket_model(),
                                         action.get_action())

            elif action.get_sheet_tab() == "groups":
                handle_groups_parameter(action.get_message(), output, sheet.get_group_model(),
                                        action.get_action(), action.get_bus_type())

            progress(actions)
            root.update()

    if cb_reaper:
        action = "Creating Reaper Recording Session Template file..."
        logging.info(action)
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
        logging.info("Reaper Recording Session Template created")

        progress(actions)
        root.update()

    if cb_trackslive:
        action = "Creating Tracks Live Recording Session Template file..."
        logging.info(action)
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
        logging.info("Tracks Live Recording Session Template created")

        progress(actions)
        root.update()

    if actions == 0:
        progress(actions)
        root.update()

    action = "Processing done"
    logging.info(action)
    current_action_label["text"] = ""

    if is_network_communication_allowed & check_box_write_to_console:
        if output is not None:
            output.close()
    progress_open_or_close_connection()
    progress_open_or_close_connection()
    root.update()


def increment_actions(actions):
    actions = actions + 1
    return actions


def read_current_ui_ip_address():
    return ip_byte0.get() + "." + ip_byte1.get() + "." + ip_byte2.get() + "." + ip_byte3.get()


def create_channel_list_content(sheet_channels):
    channel_list_entries = []
    index = 0

    for channel in sheet_channels['Channel']:

        dca_array = []
        for dca_number in range(1, 25):
            dca_array.append(str(sheet_channels["DCA" + str(dca_number)].__getitem__(index)))

        dca_config_tmp = DcaConfig(dca_array)

        mg_array = []
        for mg_number in range(1, 9):
            mg_array.append(str(sheet_channels["Mute" + str(mg_number)].__getitem__(index)))

        mg_config_tmp = MuteGroupConfig(mg_array)

        cle = ChannelListEntry(int(channel),
                               str(sheet_channels['Name'].__getitem__(index)),
                               str(sheet_channels['Color'].__getitem__(index)),
                               str(sheet_channels['HPF On'].__getitem__(index)),
                               str(sheet_channels['HPF Value'].__getitem__(index)),
                               str(sheet_channels['Fader Level'].__getitem__(index)),
                               str(sheet_channels['Mute'].__getitem__(index)),
                               str(sheet_channels['Recording'].__getitem__(index)),
                               str(sheet_channels['Record Arm'].__getitem__(index)),
                               dca_config_tmp,
                               mg_config_tmp,
                               str(sheet_channels['Main Mix'].__getitem__(index))
                               )
        channel_list_entries.append(cle)
        index = index + 1
    return channel_list_entries


def create_misc_content(sheet_misc):
    misc = Misc()
    sheet_version = None
    index = 0
    for property_item in sheet_misc['Property']:
        if str(property_item).strip() == "Version":
            sheet_version = str(sheet_misc['Value'].__getitem__(index)).strip()

    misc.set_version(sheet_version)
    return misc


def create_socket_list_content(sheet_sockets):
    socket_list_entries = []
    index = 0

    for socket in sheet_sockets['Socket Number']:
        ple = SocketListEntry(int(socket),
                              str(sheet_sockets['Local Phantom'].__getitem__(index)),
                              str(sheet_sockets['DX1 Phantom'].__getitem__(index)),
                              str(sheet_sockets['DX3 Phantom'].__getitem__(index)),
                              str(sheet_sockets['Local Pad'].__getitem__(index)),
                              str(sheet_sockets['DX1 Pad'].__getitem__(index)),
                              str(sheet_sockets['DX3 Pad'].__getitem__(index)),
                              str(sheet_sockets['Slink Phantom'].__getitem__(index)),
                              str(sheet_sockets['Slink Pad'].__getitem__(index)),
                              str(sheet_sockets['Local Gain'].__getitem__(index)),
                              str(sheet_sockets['DX1 Gain'].__getitem__(index)),
                              str(sheet_sockets['DX3 Gain'].__getitem__(index)),
                              str(sheet_sockets['Slink Gain'].__getitem__(index)),
                              )

        socket_list_entries.append(ple)
        index = index + 1
    return socket_list_entries


def create_groups_list_content(sheet_groups):
    dca_list_entries = []
    extract_data(dca_list_entries, sheet_groups, 'DCA', 'DCA Name', 'DCA Color')

    aux_mono_list_entries = []
    extract_data(aux_mono_list_entries, sheet_groups, 'Mono Auxes', 'Aux Name', 'Aux Color')

    aux_stereo_list_entries = []
    extract_data(aux_stereo_list_entries, sheet_groups, 'Stereo Auxes', 'StAux Name', 'StAux Color')

    grp_mono_list_entries = []
    extract_data(grp_mono_list_entries, sheet_groups, 'Mono Group', 'Group Name', 'Group Color')

    grp_stereo_list_entries = []
    extract_data(grp_stereo_list_entries, sheet_groups, 'Stereo Group', 'StGroup Name', 'StGroup Color')

    mtx_mono_list_entries = []
    extract_data(mtx_mono_list_entries, sheet_groups, 'Mono Matrix', 'Matrix Name', 'Matrix Color')

    mtx_stereo_list_entries = []
    extract_data(mtx_stereo_list_entries, sheet_groups, 'Stereo Matrix', 'StMatrix Name', 'StMatrix Color')

    fx_send_mono_list_entries = []
    extract_data(fx_send_mono_list_entries, sheet_groups, 'Mono FX Send', 'FX Name', 'FX Color')

    fx_send_stereo_list_entries = []
    extract_data(fx_send_stereo_list_entries, sheet_groups, 'Stereo FX Send', 'StFX Name', 'StFX Color')

    fx_return_list_entries = []
    extract_data(fx_return_list_entries, sheet_groups, 'FX Return', 'FX Return Name', 'FX Return Color')

    return GroupsListEntry(dca_list_entries,
                           aux_mono_list_entries,
                           aux_stereo_list_entries,
                           grp_mono_list_entries,
                           grp_stereo_list_entries,
                           mtx_mono_list_entries,
                           mtx_stereo_list_entries,
                           fx_send_mono_list_entries,
                           fx_send_stereo_list_entries,
                           fx_return_list_entries)


def extract_data(list_entries, sheet_groups, type_name, name, color):
    index = 0
    for item in sheet_groups[type_name]:
        if str(item) != 'nan':
            gse = GroupSetup(int(item),
                             str(sheet_groups[name].__getitem__(index)),
                             str(sheet_groups[color].__getitem__(index))
                             )

            list_entries.append(gse)
            index = index + 1


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

    cb_reaper = var_write_reaper.get()
    cb_trackslive = var_write_trackslive.get()
    cb_console_write = var_write_to_console.get()

    if cb_reaper or cb_trackslive or cb_console_write:
        input_file_path = filedialog.askopenfilename()
        if input_file_path == "":
            # Nothing to do
            return

        root.reaper_output_dir = os.path.dirname(input_file_path)
        root.reaper_file_prefix = os.path.splitext(os.path.basename(input_file_path))[0]
        try:
            read_document(input_file_path, cb_reaper, cb_trackslive, cb_console_write)
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


def trigger_background_process():
    bg_thread = threading.Thread(target=browse_files)
    bg_thread.start()


def save_current_ui_settings():
    file = CONFIG_FILE
    current_ip = ip_byte0.get() + "." + ip_byte1.get() + "." + ip_byte2.get() + "." + ip_byte3.get()

    data = {
        'version': 1,
        'ip': str(current_ip),
        'console': dropdown_console.getvar(str(var_console)),
        'midi-port': dropdown_midi_channel.getvar(str(var_midi_channel))
    }

    json_str = json.dumps(data)

    data = json.loads(json_str)
    with open(file, 'w') as file:
        json.dump(data, file)
        logging.info("Following data has be persisted: " + str(json_str) + " into file: " + str(file) + ".")


def read_persisted_ip():
    filename = CONFIG_FILE
    if os.path.exists(filename):
        logging.info("Try to read persisted ip from " + str(filename) + " file.")
        with open(filename, 'r') as file:
            data = json.load(file)
            try:
                ip_ret = data['ip']
                logging.info("Using ip: " + str(ip_ret) + " from config file: " + str(filename))
            except KeyError:
                logging.error("No key: ip found, using default ip: " +
                              dliveConstants.ip +
                              " from dliveConstants instead.")
                ip_ret = dliveConstants.ip
    else:
        logging.info("No config file found, using default ip: "
                     + dliveConstants.ip +
                     " from dliveConstants instead")
        ip_ret = dliveConstants.ip

    return ip_ret


def read_persisted_console():
    filename = CONFIG_FILE
    if os.path.exists(filename):
        logging.info("Try to read persisted console from " + str(filename) + " file.")
        with open(filename, 'r') as file:
            data = json.load(file)
            try:
                console_ret = data['console']
                logging.info("Using console: " + str(console_ret) + " from config file: " + str(filename))
            except KeyError:
                logging.error("No key: console found, Using default console: " +
                              dliveConstants.console_drop_down_default +
                              " from dliveConstants instead.")

                console_ret = dliveConstants.console_drop_down_default
    else:
        logging.info("No config file found, using default console: " +
                     dliveConstants.console_drop_down_default +
                     " from dliveConstants instead.")

        console_ret = dliveConstants.console_drop_down_default

    return console_ret


def read_persisted_midi_port():
    filename = CONFIG_FILE
    if os.path.exists(filename):
        logging.info("Try to read persisted midi-port from " + str(filename) + " file.")
        with open(filename, 'r') as file:
            data = json.load(file)
            try:
                midi_port_ret = data['midi-port']
                logging.info("Using midi-port: " + str(midi_port_ret) + " from config file: " + str(filename))
            except KeyError:
                logging.info("Use default midi-port: " +
                             dliveConstants.midi_channel_drop_down_string_default +
                             " from dliveConstants instead.")

                midi_port_ret = dliveConstants.midi_channel_drop_down_string_default
    else:
        logging.info("No config file found, using default midi-port: " +
                     dliveConstants.midi_channel_drop_down_string_default +
                     " from dliveConstants instead.")

        midi_port_ret = dliveConstants.midi_channel_drop_down_string_default

    return midi_port_ret


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
    cb_to_disable = [GuiConstants.TEXT_HPF_ON, GuiConstants.TEXT_HPF_VALUE, GuiConstants.TEXT_MUTE_GROUPS]
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


def on_console_selected(*args):
    print("The selected console is:", var_console.get())
    if var_console.get() == dliveConstants.console_drop_down_avantis:
        label_ip_address_text["text"] = LABEL_IPADDRESS_AVANTIS
        root.update()
        showinfo(
            message='Info: "' + GuiConstants.TEXT_HPF_ON +
                    '", "' + GuiConstants.TEXT_HPF_VALUE +
                    '" and "' + GuiConstants.TEXT_MUTE_GROUPS +
                    '" are currently not supported by the API of Avantis!')
        disable_avantis_checkboxes()
        root.update()

    elif var_console.get() == dliveConstants.console_drop_down_dlive:
        label_ip_address_text["text"] = LABEL_IPADDRESS_DLIVE
        reactivate_avantis_checkboxes()
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


root = Tk()
ip_address_label = StringVar(root)
current_action_label = StringVar(root)


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
    logging.info("Open connection to console on ip: " + mix_rack_ip_tmp + ":" + str(dliveConstants.port) + " ...")
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


if __name__ == '__main__':
    logging.info("dlive-midi-tool version: " + Toolinfo.version)
    root.title(Toolinfo.tool_name + ' - v' + Toolinfo.version)
    root.geometry('1300x800')
    root.resizable(False, False)

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

    tab_control = ttk.Notebook(root)

    # Tab 1 erstellen
    tab1 = ttk.Frame(tab_control)
    tab_control.add(tab1, text='Spreadsheet to Console / DAW')

    # Tab 2 erstellen
    tab2 = ttk.Frame(tab_control)
    tab_control.add(tab2, text='Console to DAW')

    tab1_frame = LabelFrame(tab1, text='Spreadsheet to Console / DAW')
    tab2_frame = LabelFrame(tab2, text='Console to DAW')

    config_frame = LabelFrame(root, text="Connection Settings")
    ip_frame = Frame(config_frame)
    console_frame = Frame(config_frame)
    console_frame.grid(row=1, column=0, sticky="W")

    ip_frame.grid(row=2, column=0, sticky="W")
    midi_channel_frame = Frame(config_frame)
    midi_channel_frame.grid(row=3, column=0, sticky="W")

    config_frame.pack(side=TOP)

    output_option_frame = LabelFrame(tab1, text="Output Options")
    var_write_to_console = BooleanVar(value=True)
    write_to_console = Checkbutton(output_option_frame, text="Write to Audio Console or Director",
                                   var=var_write_to_console)
    var_write_reaper = BooleanVar(value=False)
    cb_reaper_write = Checkbutton(output_option_frame,
                                  text="Generate Reaper Recording Session with Name & Color (In & Out 1:1 Patch)",
                                  var=var_write_reaper, command=on_reaper_write_changed)

    var_write_trackslive = BooleanVar(value=False)
    cb_trackslive_write = Checkbutton(output_option_frame,
                                      text="Generate Tracks Live (v1.3) Template with Name & Color (In & Out 1:1 Patch)",
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

    ip_field = Frame(ip_frame)
    ip_byte0 = Entry(ip_field, width=3)
    ip_byte1 = Entry(ip_field, width=3)
    ip_byte2 = Entry(ip_field, width=3)
    ip_byte3 = Entry(ip_field, width=3)
    mixrack_ip = ""
    midi_channel = None
    var_midi_channel = StringVar(root)
    var_console = StringVar(root)

    reaper_output_dir = ""
    reaper_file_prefix = ""

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
         GuiConstants.TEXT_AUX_STERE0_COLOR,
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
         GuiConstants.TEXT_FX_RETURN_COLOR
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

    output_option_frame.pack(side=TOP, fill=X)

    var_console.set(read_persisted_console())

    Label(console_frame, text="Audio Console:", width=25).pack(side=LEFT)

    dropdown_console = OptionMenu(console_frame, var_console,
                                  dliveConstants.console_drop_down_dlive,
                                  dliveConstants.console_drop_down_avantis,
                                  )
    dropdown_console.pack(side=RIGHT)

    label_ip_address_text = Label(ip_frame, text=ip_address_label.get(), width=25)
    if var_console.get() == dliveConstants.console_drop_down_avantis:
        label_ip_address_text["text"] = LABEL_IPADDRESS_AVANTIS
        disable_avantis_checkboxes()
        root.update()
        root.focus()
    elif var_console.get() == dliveConstants.console_drop_down_dlive:
        label_ip_address_text["text"] = LABEL_IPADDRESS_DLIVE
        reactivate_avantis_checkboxes()
        root.update()
        root.focus()
    label_ip_address_text.pack(side=LEFT)

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

    var_midi_channel.set(read_persisted_midi_port())  # default value

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

    ip = read_persisted_ip()
    ip_from_config_file = ip.split(".")

    ip_byte0.insert(10, ip_from_config_file.__getitem__(0))
    ip_byte1.insert(11, ip_from_config_file.__getitem__(1))
    ip_byte2.insert(12, ip_from_config_file.__getitem__(2))
    ip_byte3.insert(13, ip_from_config_file.__getitem__(3))

    bottom_frame = Frame(tab1)

    Button(bottom_frame, text='Open spreadsheet and start writing process', command=trigger_background_process).grid(
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
           command=get_data_from_console).pack(side=BOTTOM)

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

    tab_control.pack(expand=1, fill='both', side=TOP)

    root.mainloop()
