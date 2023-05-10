####################################################
# Main Script
#
# Author: Tobias Grupe
#
####################################################
# coding=utf-8
import ipaddress
import json
import logging
import os
import re
import socket
import threading
import time
from tkinter import filedialog, Button, Tk, Checkbutton, IntVar, W, Frame, LEFT, YES, TOP, X, RIGHT, Label, \
    Entry, BOTTOM, StringVar, OptionMenu, ttk, LabelFrame, BooleanVar, END
from tkinter.messagebox import showinfo, showerror

import mido
import numpy
import pandas as pd
from mido.sockets import connect

import dliveConstants
from dawsession import SessionCreator
from model.ChannelListEntry import ChannelListEntry
from model.DcaConfig import DcaConfig
from model.DcaListEntry import DcaListEntry
from model.Misc import Misc
from model.MuteGroupConfig import MuteGroupConfig
from model.MuteGroupListEntry import MuteGroupListEntry
from model.PhantomListEntry import PhantomListEntry
from model.Sheet import Sheet

LABEL_IPADDRESS_AVANTIS = "IP-Address:"
LABEL_IPADDRESS_DLIVE = "Mixrack IP-Address:"

logging.basicConfig(filename='main.log', level=logging.DEBUG)

version = "2.3.0-alpha7"

is_network_communication_allowed = dliveConstants.allow_network_communication


def convert_return_value_to_readable_color(in_message):
    color = in_message[11]
    color_ret = "black"

    if color == dliveConstants.lcd_color_blue:
        color_ret = "blue"
    elif color == dliveConstants.lcd_color_ltblue:
        color_ret = "light blue"
    elif color == dliveConstants.lcd_color_red:
        color_ret = "red"
    elif color == dliveConstants.lcd_color_yellow:
        color_ret = "yellow"
    elif color == dliveConstants.lcd_color_green:
        color_ret = "green"
    elif color == dliveConstants.lcd_color_purple:
        color_ret = "purple"
    elif color == dliveConstants.lcd_color_black:
        color_ret = "black"
    elif color == dliveConstants.lcd_color_white:
        color_ret = "white"
    return color_ret


def get_color_channel(output):
    # TODO: Not yet implemented fully
    color = []

    for channel in range(0, 127):
        prefix = [root.midi_channel, dliveConstants.sysex_message_get_channel_colour, channel]

        message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + prefix + dliveConstants.sysexhdrend)
        if is_network_communication_allowed:
            color.append(output.send(message))

            inport = mido.open_input()
            in_message = inport.receive()

            thisdict = {
                "channel": channel,
                "color": convert_return_value_to_readable_color(in_message)
            }

            color.append(thisdict)

            print(in_message)
            time.sleep(.1)
    return color


def get_name_channel(output):
    # TODO: Not yet implemented fully
    names = []

    for channel in range(0, 127):
        prefix = [root.midi_channel, dliveConstants.sysex_message_get_channel_name, channel]

        message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + prefix + dliveConstants.sysexhdrend)
        if is_network_communication_allowed:
            names.append(output.send(message))
            time.sleep(.1)


def name_channel(output, item):
    # Trim name if length of name > dliveConstants.trim_after_x_charactors
    if len(str(item.get_name())) > dliveConstants.trim_after_x_charactors:
        trimmed_name = str(item.get_name())[0:dliveConstants.trim_after_x_charactors]
        logging.info(
            "Channel name will be trimmed to 6 characters, before: " + str(item.get_name()) + " after: " + str(
                trimmed_name))
    else:
        trimmed_name = str(item.get_name())

    if trimmed_name == 'nan':
        characters = [' ', ' ', ' ', ' ', ' ', ' ', '']
    else:
        characters = re.findall('.?', trimmed_name)

    payload = []

    for character in characters:
        if len(str(character)) != 0:
            value = ord(character)
            if value > 127:
                error_msg = "One of the characters in Channel " + str(
                    item.get_channel_dlive() + 1) + " is not supported. Characters like ä, ö, ü are not supported."
                logging.error(error_msg)
                showerror(message=error_msg)
                exit(1)
            else:
                payload.append(value)

    prefix = [root.midi_channel, dliveConstants.sysex_message_set_channel_name,
              item.get_channel_dlive()]
    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + prefix + payload + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
        time.sleep(.1)


def color_channel(output, item):
    lower_color = item.get_color().lower()

    if lower_color == "blue":
        colour = dliveConstants.lcd_color_blue
    elif lower_color == "red":
        colour = dliveConstants.lcd_color_red
    elif lower_color == "light blue":
        colour = dliveConstants.lcd_color_ltblue
    elif lower_color == 'purple':
        colour = dliveConstants.lcd_color_purple
    elif lower_color == 'green':
        colour = dliveConstants.lcd_color_green
    elif lower_color == 'yellow':
        colour = dliveConstants.lcd_color_yellow
    elif lower_color == 'black':
        colour = dliveConstants.lcd_color_black
    elif lower_color == 'white':
        colour = dliveConstants.lcd_color_white
    else:
        logging.warning("Given color: " + lower_color + " is not supported, setting default color: black")
        colour = dliveConstants.lcd_color_black

    payload_array = [root.midi_channel, dliveConstants.sysex_message_set_channel_colour, item.get_channel_dlive(),
                     colour]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
        time.sleep(.1)


def mute_on_channel(output, item):
    midi_channel_tmp = root.midi_channel

    lower_mute_on = item.get_mute().lower()
    channel = item.get_channel_dlive()

    if lower_mute_on == "yes":
        message_on = mido.Message('note_on', channel=midi_channel_tmp, note=channel, velocity=dliveConstants.mute_on)
        message_off = mido.Message('note_on', channel=midi_channel_tmp, note=channel, velocity=dliveConstants.note_off)
    else:
        message_on = mido.Message('note_on', channel=midi_channel_tmp, note=channel, velocity=dliveConstants.mute_off)
        message_off = mido.Message('note_on', channel=midi_channel_tmp, note=channel, velocity=dliveConstants.note_off)

    if is_network_communication_allowed:
        output.send(message_on)
        output.send(message_off)
        time.sleep(.1)


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

    if lower_phantom == "yes":
        res = dliveConstants.phantom_power_on
    else:
        res = dliveConstants.phantom_power_off

    # TODO Currently required because value of socket cannot be higher than 127
    if socket > 127:
        return

    payload_array = [root.midi_channel, dliveConstants.sysex_message_set_socket_preamp_48V, socket,
                     res]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
        time.sleep(.1)


def hpf_on_channel(output, item):
    lower_hpf_on = str(item.get_hpf_on()).lower()
    if lower_hpf_on == "yes":
        res = dliveConstants.hpf_on
    else:
        res = dliveConstants.hpf_off

    if is_network_communication_allowed:
        output.send(
            mido.Message('control_change', channel=root.midi_channel, control=0x63, value=item.get_channel_dlive()))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_hpf_on))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x6, value=res))
        time.sleep(.001)


def calculate_vv(hpf_value):
    return int(127 * ((4608 * numpy.log10(float(hpf_value) / 4) / numpy.log10(2)) - 10699) / 41314)


def hpf_value_channel(output, item):
    value_freq = calculate_vv(item.get_hpf_value())

    if is_network_communication_allowed:
        output.send(
            mido.Message('control_change', channel=root.midi_channel, control=0x63, value=item.get_channel_dlive()))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_hpf_frequency))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x6, value=value_freq))
        time.sleep(.001)


def fader_level_channel(output, item):
    lower_fader_level = str(float(str(item.get_fader_level())))

    switcher = {
        "10.0": dliveConstants.fader_level_plus10,
        "5.0": dliveConstants.fader_level_plus5,
        "0.0": dliveConstants.fader_level_zero,
        "-5.0": dliveConstants.fader_level_minus5,
        "-10.0": dliveConstants.fader_level_minus10,
        "-15.0": dliveConstants.fader_level_minus15,
        "-20.0": dliveConstants.fader_level_minus20,
        "-25.0": dliveConstants.fader_level_minus25,
        "-30.0": dliveConstants.fader_level_minus30,
        "-35.0": dliveConstants.fader_level_minus35,
        "-40.0": dliveConstants.fader_level_minus40,
        "-45.0": dliveConstants.fader_level_minus45,
        "-inf": dliveConstants.fader_level_minus_inf
    }
    fader_level = switcher.get(lower_fader_level, "Invalid Fader level")

    logging.info("Set Fader to: " + str(lower_fader_level) + " at Channel: " + str(item.get_channel()))

    if is_network_communication_allowed:
        output.send(
            mido.Message('control_change', channel=root.midi_channel, control=0x63, value=item.get_channel_dlive()))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_fader_level))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x6, value=int(fader_level)))
        time.sleep(.001)


def handle_channels_parameter(message, output, channel_list_entries, action):
    logging.info(message)
    for item in channel_list_entries:
        logging.info("Processing " + action + " for channel: " + str(item.get_channel_dlive() + 1))
        if action == "name":
            name_channel(output, item)
        elif action == "color":
            color_channel(output, item)
        elif action == "mute":
            mute_on_channel(output, item)
        elif action == "fader_level":
            fader_level_channel(output, item)
        elif action == "hpf_on":
            hpf_on_channel(output, item)
        elif action == "hpf_value":
            hpf_value_channel(output, item)


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

    if lower_pad == "yes":
        res = dliveConstants.pad_on
    else:
        res = dliveConstants.pad_off

    # TODO Currently required because value of socket cannot be higher than 127
    if socket > 127:
        return

    payload_array = [root.midi_channel, dliveConstants.sysex_message_set_socket_preamp_pad, socket, res]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
        time.sleep(.1)


def gain_socket(output, item, socket_type):
    socket_tmp = item.get_socket_number()
    socket_dlive_tmp = item.get_socket_number_dlive()

    if socket_type == "local":
        if socket_tmp <= dliveConstants.LOCAL_DLIVE_SOCKET_COUNT_MAX and root.console == dliveConstants.console_drop_down_dlive:
            gain_sheet_lower = str(float(str(item.get_local_gain())))
            socket = socket_dlive_tmp
        elif socket_tmp <= dliveConstants.LOCAL_AVANTIS_SOCKET_COUNT_MAX and root.console == dliveConstants.console_drop_down_avantis:
            gain_sheet_lower = str(float(str(item.get_local_gain())))
            socket = socket_dlive_tmp
        else:
            return

    elif socket_type == "DX1":
        if socket_tmp <= dliveConstants.DX1_SOCKET_COUNT_MAX:
            gain_sheet_lower = str(float(str(item.get_dx1_gain())))
            socket = socket_dlive_tmp + 64
        else:
            return

    elif socket_type == "DX3":
        if socket_tmp <= dliveConstants.DX3_SOCKET_COUNT_MAX:
            gain_sheet_lower = str(float(str(item.get_dx3_gain())))
            socket = socket_dlive_tmp + 96
        else:
            return

    elif socket_type == "Slink":
        if socket_tmp <= dliveConstants.SLINK_SOCKET_COUNT_MAX:
            gain_sheet_lower = str(float(str(item.get_slink_gain())))
            socket = socket_dlive_tmp + 64
        else:
            return

    # TODO Currently required because value of socket cannot be higher than 127
    if socket > 127:
        return

    switcher = {
        "60.0": dliveConstants.gain_level_plus60,
        "55.0": dliveConstants.gain_level_plus55,
        "50.0": dliveConstants.gain_level_plus50,
        "45.0": dliveConstants.gain_level_plus45,
        "40.0": dliveConstants.gain_level_plus40,
        "35.0": dliveConstants.gain_level_plus35,
        "30.0": dliveConstants.gain_level_plus30,
        "25.0": dliveConstants.gain_level_plus25,
        "20.0": dliveConstants.gain_level_plus20,
        "15.0": dliveConstants.gain_level_plus15,
        "10.0": dliveConstants.gain_level_plus10,
        "5.0": dliveConstants.gain_level_plus5
    }
    gain_level = switcher.get(gain_sheet_lower, "Invalid gain level")

    if is_network_communication_allowed:
        logging.info("Set Gain Level " + str(gain_sheet_lower) + "dB/" + str(hex(gain_level)) + " to socket: " + str(
            socket_type) + ":" + str(socket))

        byte_1 = gain_level << 8
        byte_2 = socket << 1
        byte_all = byte_1 | byte_2
        byte_out = byte_all >> 1
        byte_out = byte_out - 8192

        output.send(mido.Message('pitchwheel', channel=root.midi_channel, pitch=byte_out))
        time.sleep(.01)


def handle_phantom_and_pad_parameter(message, output, phantom_list_entries, action):
    logging.info(message)
    for item in phantom_list_entries:
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
        time.sleep(.001)


def assign_mg(output, channel, mg_value):
    if is_network_communication_allowed:
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x63, value=channel))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_mg_assign))
        output.send(mido.Message('control_change', channel=root.midi_channel, control=0x6, value=mg_value))
        time.sleep(.001)


def dca_channel(output, item):
    channel = item.get_channel_dlive()

    for dca_index in range(0, 24):

        if root.console == dliveConstants.console_drop_down_avantis and dca_index > 15:
            return

        dca_config = item.get_dca_config()
        dca_array = dca_config.get_dca_array()

        if dca_array.__getitem__(dca_index).lower() == "x":
            assign_dca(output, channel, dliveConstants.dca_on_base_address + dca_index)
        else:
            assign_dca(output, channel, dliveConstants.dca_off_base_address + dca_index)


def mg_channel(output, item):
    channel = item.get_channel_dlive()

    for mg_index in range(0, 8):

        mg_config = item.get_mg_config()
        mg_array = mg_config.get_mg_array()

        if mg_array.__getitem__(mg_index).lower() == "x":
            assign_mg(output, channel, dliveConstants.mg_on_base_address + mg_index)
        else:
            assign_mg(output, channel, dliveConstants.mg_off_base_address + mg_index)


def handle_dca_mg_parameter(message, output, content_list, action):
    logging.info(message)
    for item in content_list:
        if action == "dca":
            dca_channel(output, item)
        elif action == "mg":
            mg_channel(output, item)


def is_valid_ip_address(ip_address):
    try:
        ipaddress.IPv4Address(ip_address)
        return True
    except ipaddress.AddressValueError:
        return False


def read_document(filename, check_box_reaper, check_box_write_to_dlive):
    logging.info('The following file will be read : ' + str(filename))

    sheet = Sheet()

    sheet.set_misc_model(create_misc_content(pd.read_excel(filename, sheet_name="Misc")))

    latest_spreadsheet_version = '5'

    read_version = sheet.get_misc_model().get_version()

    if read_version != latest_spreadsheet_version:
        error_msg = "Given spreadsheet version: " + str(
            read_version) + " is not compatible. Please use the latest excel " \
                            "sheet (Version " + latest_spreadsheet_version + \
                    "). You can see the version in the spreadsheet tab \"Misc\""
        logging.error(error_msg)
        showerror(message=error_msg)
        return root.quit()

    sheet.set_channel_model(create_channel_list_content(pd.read_excel(filename, sheet_name="Channels")))
    sheet.set_phantom_pad_model(create_phantom_pad_content(pd.read_excel(filename, sheet_name="48V & Pad")))
    sheet.set_dca_model(create_dca_content(pd.read_excel(filename, sheet_name="Channels")))
    sheet.set_mg_model(create_mg_content(pd.read_excel(filename, sheet_name="Channels")))

    if is_network_communication_allowed & check_box_write_to_dlive.__getitem__(0):
        mix_rack_ip_tmp = ip_byte0.get() + "." + ip_byte1.get() + "." + ip_byte2.get() + "." + ip_byte3.get()

        if not is_valid_ip_address(mix_rack_ip_tmp):
            error_msg_invalid_ip = "Given ip: " + mix_rack_ip_tmp + " " + "is invalid. Ip has to be in the following " \
                                                                          "format: e.g. 192.168.1.70. Each ip subpart can " \
                                                                          "only be between 0-255"
            logging.error(error_msg_invalid_ip)
            showerror(message=error_msg_invalid_ip)
            reset_progress_bar()
            return

        logging.info("Open connection to dlive on ip: " + mix_rack_ip_tmp + ":" + str(dliveConstants.port) + " ...")
        try:
            output = connect(mix_rack_ip_tmp, dliveConstants.port)
            logging.info("Connection successful.")
        except socket.timeout:
            connect_err_message = "Connection to given ip: " + mix_rack_ip_tmp + " " + "could not be " \
                                                                                       "established. " \
                                                                                       "Are you in the same " \
                                                                                       "subnet?"

            logging.error(connect_err_message)
            showerror(message=connect_err_message)
            reset_progress_bar()
            return
    else:
        output = None
    progress_open_or_close_connection()
    root.update()

    root.midi_channel = determine_technical_midi_port(var_midi_channel.get())
    root.console = determine_console_id(var_console.get())

    actions = 0

    if check_box_write_to_dlive.__getitem__(0):
        cb_write_to_dlive = True
    else:
        cb_write_to_dlive = False

    if cb_write_to_dlive:
        for var in grid.vars:
            # Name
            if var._name == "Name":
                actions = actions + 1
                cb_names = True
            # Colors
            elif var._name == "Color":
                actions = actions + 1
                cb_color = True

            # Mute
            elif var._name == "Mute":
                actions = actions + 1
                cb_mute = True

            # Fader Level
            elif var._name == "Fader Level":  #
                actions = actions + 1
                cb_fader_level = True

            # HPF On
            elif var._name == "HPF On" and var_console.get() == dliveConstants.console_drop_down_dlive:
                actions = actions + 1
                cb_hpf_on = True

            # HPF value
            elif var._name == "HPF Value" and var_console.get() == dliveConstants.console_drop_down_dlive:
                actions = actions + 1
                cb_hpf_value = True

            # DCAs
            elif var._name == "DCAs":
                actions = actions + 1
                cb_dca = True

            # Mute Groups
            elif var._name == "Mute Groups" and var_console.get() == dliveConstants.console_drop_down_dlive:
                actions = actions + 1
                cb_mg = True

            # Phantom
            elif var._name == "48V Phantom":
                actions = actions + 1
                cb_phantom = True

            # Pad
            elif var._name == "PAD":
                actions = actions + 1
                cb_pad = True

            # Gain
            elif var._name == "Gain":
                actions = actions + 1
                cb_gain = True

    if check_box_reaper.__getitem__(0):
        actions = actions + 1
        cb_reaper = True
    else:
        cb_reaper = False

    logging.info("Start Processing...")

    if cb_write_to_dlive:
        if cb_names:
            handle_channels_parameter("Set Name to channels...", output, sheet.get_channel_model(),
                                      action="name")
            progress(actions)
            root.update()

        if cb_color:
            handle_channels_parameter("Set Colors to channels...", output, sheet.get_channel_model(),
                                      action="color")
            progress(actions)
            root.update()

        if cb_mute:
            handle_channels_parameter("Set Mute to channels...", output, sheet.get_channel_model(),
                                      action="mute")
            progress(actions)
            root.update()

        if cb_phantom:
            handle_phantom_and_pad_parameter("Set Phantom Power to channels...", output,
                                             sheet.get_phantom_pad_model(),
                                             action="phantom")
            progress(actions)
            root.update()

        if cb_pad:
            handle_phantom_and_pad_parameter("Set Pad to channels...", output, sheet.get_phantom_pad_model(),
                                             action="pad")
            progress(actions)
            root.update()

        if cb_hpf_on:
            handle_channels_parameter("Set HPF On to the channels...", output, sheet.get_channel_model(),
                                      action="hpf_on")
            progress(actions)
            root.update()

        if cb_hpf_value:
            handle_channels_parameter("Set HPF Value to the channels...", output, sheet.get_channel_model(),
                                      action="hpf_value")
            progress(actions)
            root.update()

        if cb_fader_level:
            handle_channels_parameter("Set Fader Level to the channels...", output, sheet.get_channel_model(),
                                      action="fader_level")
            progress(actions)
            root.update()

        if cb_dca:
            handle_dca_mg_parameter("Set DCA Assignments to the channels...", output, sheet.get_dca_model(),
                                    action="dca")
            progress(actions)
            root.update()

        if cb_mg:
            handle_dca_mg_parameter("Set Mute Group Assignments to the channels...", output, sheet.get_mg_model(),
                                    action="mg")
            progress(actions)
            root.update()

        if cb_gain:
            handle_phantom_and_pad_parameter("Set Gain to the channels...", output, sheet.get_phantom_pad_model(),
                                             action="gain")
            progress(actions)
            root.update()

    if cb_reaper:
        logging.info("Creating Reaper Recording Session Template file...")
        SessionCreator.create_reaper_session(sheet, root.reaper_output_dir, root.reaper_file_prefix)
        logging.info("Reaper Recording Session Template created")

        progress(actions)
        root.update()

    if actions == 0:
        progress(actions)
        root.update()

    logging.info("Processing done")

    if is_network_communication_allowed & check_box_write_to_dlive.__getitem__(0):
        output.close()
    progress_open_or_close_connection()
    progress_open_or_close_connection()
    root.update()


def create_channel_list_content(sheet_channels):
    channel_list_entries = []
    index = 0

    for channel in sheet_channels['Channel']:
        cle = ChannelListEntry(channel,
                               str(sheet_channels['Name'].__getitem__(index)),
                               str(sheet_channels['Color'].__getitem__(index)),
                               str(sheet_channels['HPF On'].__getitem__(index)),
                               str(sheet_channels['HPF Value'].__getitem__(index)),
                               str(sheet_channels['Fader Level'].__getitem__(index)),
                               str(sheet_channels['Mute'].__getitem__(index)),
                               str(sheet_channels['Recording'].__getitem__(index)),
                               str(sheet_channels['Record Arm'].__getitem__(index))
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


def create_dca_content(sheet_dcas):
    dca_list_entries = []
    index = 0

    for channel in sheet_dcas['Channel']:
        dca_array = []
        for dca_number in range(1, 25):
            dca_array.append(str(sheet_dcas["DCA" + str(dca_number)].__getitem__(index)))

        dca_config_tmp = DcaConfig(dca_array)

        dle = DcaListEntry(channel, dca_config_tmp)
        dca_list_entries.append(dle)
        index = index + 1
    return dca_list_entries


def create_mg_content(sheet_mg):
    mg_list_entries = []
    index = 0

    for channel in sheet_mg['Channel']:
        mg_array = []
        for mg_number in range(1, 9):
            mg_array.append(str(sheet_mg["Mute" + str(mg_number)].__getitem__(index)))

        mg_config_tmp = MuteGroupConfig(mg_array)

        mgle = MuteGroupListEntry(channel, mg_config_tmp)
        mg_list_entries.append(mgle)
        index = index + 1
    return mg_list_entries


def create_phantom_pad_content(sheet_48V_and_pad):
    phantom_and_pad_list_entries = []
    index = 0

    for socket in sheet_48V_and_pad['Socket Number']:
        ple = PhantomListEntry(socket,
                               str(sheet_48V_and_pad['Local Phantom'].__getitem__(index)),
                               str(sheet_48V_and_pad['DX1 Phantom'].__getitem__(index)),
                               str(sheet_48V_and_pad['DX3 Phantom'].__getitem__(index)),
                               str(sheet_48V_and_pad['Local Pad'].__getitem__(index)),
                               str(sheet_48V_and_pad['DX1 Pad'].__getitem__(index)),
                               str(sheet_48V_and_pad['DX3 Pad'].__getitem__(index)),
                               str(sheet_48V_and_pad['Slink Phantom'].__getitem__(index)),
                               str(sheet_48V_and_pad['Slink Pad'].__getitem__(index)),
                               str(sheet_48V_and_pad['Local Gain'].__getitem__(index)),
                               str(sheet_48V_and_pad['DX1 Gain'].__getitem__(index)),
                               str(sheet_48V_and_pad['DX3 Gain'].__getitem__(index)),
                               str(sheet_48V_and_pad['Slink Gain'].__getitem__(index)),
                               )

        phantom_and_pad_list_entries.append(ple)
        index = index + 1
    return phantom_and_pad_list_entries


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
    pb['value'] = 0
    root.update()


def browse_files():
    reset_progress_bar()
    input_file_path = filedialog.askopenfilename()
    root.reaper_output_dir = os.path.dirname(input_file_path)
    root.reaper_file_prefix = os.path.splitext(os.path.basename(input_file_path))[0]
    read_document(input_file_path, get_reaper_state(), get_dlive_write_state())


def trigger_background_process():
    bg_thread = threading.Thread(target=browse_files)
    bg_thread.start()


class Checkbar(Frame):
    def __init__(self, parent=None, picks=[], side=LEFT, anchor=W):
        Frame.__init__(self, parent)
        self.vars = []
        for pick in picks:
            var = IntVar()
            chk = Checkbutton(self, text=pick, variable=var)
            chk.pack(side=side, anchor=anchor, expand=YES)
            self.vars.append(var)

    def state(self):
        return map((lambda var: var.get()), self.vars)


def get_reaper_state():
    return list(reaper.state())


def get_dlive_write_state():
    return list(write_to_dlive.state())


def save_current_ui_settings():
    file = dliveConstants.config_file
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
    filename = dliveConstants.config_file
    if os.path.exists(filename):
        logging.info("Try to read persisted ip from " + dliveConstants.config_file + " file.")
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
    filename = dliveConstants.config_file
    if os.path.exists(filename):
        logging.info("Try to read persisted console from " + dliveConstants.config_file + " file.")
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
    filename = dliveConstants.config_file
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
                             "from dliveConstants instead.")

                midi_port_ret = dliveConstants.midi_channel_drop_down_string_default
    else:
        logging.info("No config file found, using default midi-port: " +
                     dliveConstants.midi_channel_drop_down_string_default +
                     "from dliveConstants instead.")

        midi_port_ret = dliveConstants.midi_channel_drop_down_string_default

    return midi_port_ret


def reset_ip_field_to_default_ip():
    ip_byte0.delete(0, END)
    ip_byte0.insert(0, "192")
    ip_byte1.delete(0, END)
    ip_byte1.insert(0, "168")
    ip_byte2.delete(0, END)
    ip_byte2.insert(0, "1")
    ip_byte3.delete(0, END)
    ip_byte3.insert(0, "70")
    logging.info("Default ip: " + dliveConstants.ip + " was set.")


def set_ip_field_to_local_director_ip():
    ip_byte0.delete(0, END)
    ip_byte0.insert(0, "127")
    ip_byte1.delete(0, END)
    ip_byte1.insert(0, "0")
    ip_byte2.delete(0, END)
    ip_byte2.insert(0, "0")
    ip_byte3.delete(0, END)
    ip_byte3.insert(0, "1")
    logging.info("Director ip: 127.0.0.1 was set.")


def on_console_selected(*args):
    print("The selected console is:", var_console.get())
    if var_console.get() == dliveConstants.console_drop_down_avantis:
        label_ip_address_text["text"] = LABEL_IPADDRESS_AVANTIS
        root.update()
        showinfo(
            message='Info: "HPF On", "HPF Value" and "Mute Groups" are currently not supported by the API of Avantis!')
    elif var_console.get() == dliveConstants.console_drop_down_dlive:
        label_ip_address_text["text"] = LABEL_IPADDRESS_DLIVE


def update_progress_label():
    return f"Current Progress: {round(pb['value'], 1)} %"


def progress(actions=None):
    if actions == 0:
        pb['value'] += 90
    else:
        if pb['value'] < 100:
            pb['value'] += 90 / actions
            value_label['text'] = update_progress_label()
        else:
            showinfo(message='Writing completed!')


def progress_open_or_close_connection():
    if pb['value'] < 100:
        pb['value'] += 5
        value_label['text'] = update_progress_label()
    else:
        showinfo(message='Writing completed!')


class CheckboxGrid(Frame):
    def __init__(self, parent, headers, labels):
        super().__init__(parent)
        self.vars = []
        self.headers = headers
        self.labels = labels
        self.create_widgets()

    def create_widgets(self):
        for i, header in enumerate(self.headers):
            frame = LabelFrame(self, text=header)
            frame.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            group_vars = []
            for j, label in enumerate(self.labels[i]):
                var = BooleanVar(value=False, name=label)
                self.vars.append(var)
                checkbox = Checkbutton(frame, text=label, variable=var)
                checkbox.grid(row=j + 1, column=0, sticky="w")
                group_vars.append(var)
            self.create_group_checkbox(frame, group_vars)

    def create_group_checkbox(self, parent, group_vars):
        group_var = BooleanVar()
        group_checkbox = Checkbutton(parent, text="Select all", variable=group_var,
                                     command=lambda: self.toggle_group(group_vars, group_var.get()))
        group_checkbox.grid(row=0, column=1, sticky="e")
        for var in group_vars:
            var.trace_add("write", lambda *_: group_var.set(all(var.get() for var in group_vars)))

    def toggle_group(self, group_vars, state):
        for var in group_vars:
            var.set(state)


root = Tk()
ip_address_label = StringVar(root)

if __name__ == '__main__':
    root.title('Channel List Manager for Allen & Heath dLive and Avantis - v' + version)
    root.geometry('900x550')
    root.resizable(False, False)

    config_frame = Frame(root)
    ip_frame = Frame(config_frame)
    console_frame = Frame(config_frame)
    console_frame.grid(row=1, column=0, sticky="W")
    Label(config_frame, text="       ").grid(row=0, column=0)
    ip_frame.grid(row=2, column=0, sticky="W")
    midi_channel_frame = Frame(config_frame)
    midi_channel_frame.grid(row=3, column=0, sticky="W")

    config_frame.pack(side=TOP)

    write_to_dlive = Checkbar(root, ['Write to console'])
    reaper = Checkbar(root, ['Generate Reaper recording session (In & Out 1:1 Patch)'])

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

    Label(root, text=" ").pack(side=TOP)
    Label(root, text="Choose from the given spreadsheet which column you want to write.").pack(side=TOP)

    headers = ["Channel", "Preamp", "Processing", "Attribute"]
    labels = [["Name", "Color"], ["48V Phantom", "PAD", "Gain"], ["Mute", "Fader Level", "HPF On", "HPF Value"],
              ["DCAs", "Mute Groups"]]
    grid = CheckboxGrid(root, headers, labels)
    grid.pack(side=TOP)

    Label(root, text=" ").pack(side=TOP)
    Label(root, text=" ").pack(side=TOP)
    write_to_dlive.pack(side=TOP, fill=X)
    write_to_dlive.config(bd=2)
    reaper.pack(side=TOP, fill=X)
    reaper.config(bd=2)

    var_console.set(read_persisted_console())

    Label(console_frame, text="Console:", width=25).pack(side=LEFT)

    dropdown_console = OptionMenu(console_frame, var_console,
                                  dliveConstants.console_drop_down_dlive,
                                  dliveConstants.console_drop_down_avantis,
                                  )
    dropdown_console.pack(side=RIGHT)

    label_ip_address_text = Label(ip_frame, text=ip_address_label.get(), width=25)
    if var_console.get() == dliveConstants.console_drop_down_avantis:
        label_ip_address_text["text"] = LABEL_IPADDRESS_AVANTIS
    elif var_console.get() == dliveConstants.console_drop_down_dlive:
        label_ip_address_text["text"] = LABEL_IPADDRESS_DLIVE
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

    bottom_frame = Frame(root)

    Button(bottom_frame, text='Open spreadsheet and trigger writing process', command=trigger_background_process).grid(
        row=0)
    Label(bottom_frame, text=" ", width=30).grid(row=1)

    pb = ttk.Progressbar(
        bottom_frame,
        orient='horizontal',
        mode='determinate',
        length=850
    )

    pb.grid(row=2)

    # label to show current value in percent
    value_label = ttk.Label(bottom_frame, text=update_progress_label())
    value_label.grid(row=3)

    Button(bottom_frame, text='Quit', command=root.quit).grid(row=4)
    bottom_frame.pack(side=BOTTOM)

    var_console.trace("w", on_console_selected)

    root.mainloop()
