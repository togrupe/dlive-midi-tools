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
import tkinter
from tkinter import filedialog, Button, Tk, Checkbutton, IntVar, W, Frame, LEFT, YES, TOP, X, RIGHT, Label, \
    Entry, BOTTOM, StringVar, OptionMenu, ttk
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
from model.PhantomListEntry import PhantomListEntry
from model.Sheet import Sheet

LOCAL_DLIVE_SOCKET_COUNT_MAX = 64
LOCAL_AVANTIS_SOCKET_COUNT_MAX = 12
DX1_SOCKET_COUNT_MAX = 32
DX3_SOCKET_COUNT_MAX = 32
SLINK_SOCKET_COUNT_MAX = 128

logging.basicConfig(filename='main.log', level=logging.DEBUG)

version = "2.3.0-alpha1"

is_network_communication_allowed = dliveConstants.allow_network_communication


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
        if socket_tmp <= LOCAL_DLIVE_SOCKET_COUNT_MAX and root.console == dliveConstants.console_drop_down_dlive:
            lower_phantom = str(item.get_local_phantom()).lower()
            socket = socket_dlive_tmp
        elif socket_tmp <= LOCAL_AVANTIS_SOCKET_COUNT_MAX and root.console == dliveConstants.console_drop_down_avantis:
            lower_phantom = str(item.get_local_phantom()).lower()
            socket = socket_dlive_tmp
        else:
            return

    elif socket_type == "DX1":
        if socket_tmp <= DX1_SOCKET_COUNT_MAX:
            lower_phantom = str(item.get_dx1_phantom()).lower()
            socket = socket_dlive_tmp + 64
        else:
            return

    elif socket_type == "DX3":
        if socket_tmp <= DX3_SOCKET_COUNT_MAX:
            lower_phantom = str(item.get_dx3_phantom()).lower()
            socket = socket_dlive_tmp + 96
        else:
            return

    elif socket_type == "Slink":
        if socket_tmp <= SLINK_SOCKET_COUNT_MAX:
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
    # TODO: NRPN is currently not supported from mido
    lower_hpf_on = str(item.get_hpf_on()).lower()
    if lower_hpf_on == "yes":
        res = dliveConstants.hpf_on
    else:
        res = dliveConstants.hpf_off

    midi_channel_tmp = 0xB << 4
    midi_channel_tmp = midi_channel_tmp + root.midi_channel

    select_channel = [midi_channel_tmp, 0x63, item.get_channel_dlive()]
    parameter = [midi_channel_tmp, 0x62, dliveConstants.nrpn_parameter_id_hpf_on]
    set_value = [midi_channel_tmp, 0x06, res]

    if is_network_communication_allowed:
        message = mido.Message.from_bytes(select_channel + parameter + set_value)
        output.send(message)
        time.sleep(.1)


def calculate_vv(hpf_value):
    return int(127 * ((4608 * numpy.log10(hpf_value / 4) / numpy.log10(2)) - 10699) / 41314)


def hpf_value_channel(output, item):
    # TODO: NRPN is currently not supported from mido
    midi_channel_tmp = 0xB << 4
    midi_channel_tmp = midi_channel_tmp + root.midi_channel

    select_channel = [midi_channel_tmp, 0x63, item.get_channel_dlive()]
    parameter = [midi_channel_tmp, 0x62, dliveConstants.nrpn_parameter_id_hpf_frequency]
    set_value = [midi_channel_tmp, 0x06, calculate_vv(item.get_hpf_value())]

    if is_network_communication_allowed:
        message = mido.Message.from_bytes(select_channel + parameter + set_value)
        output.send(message)
        time.sleep(.1)


def fader_level_channel(output, item):
    # TODO: NRPN is currently not supported by mido
    lower_fader_level = str(item.get_fader_level()).lower()

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

    midi_channel_tmp = 0xB << 4
    midi_channel_tmp = midi_channel_tmp + root.midi_channel

    select_channel = [midi_channel_tmp, 0x63, item.get_channel_dlive()]
    parameter = [midi_channel_tmp, 0x62, dliveConstants.nrpn_parameter_id_fader_level]
    set_value = [midi_channel_tmp, 0x06, fader_level]

    if is_network_communication_allowed:
        message = mido.Message.from_bytes(select_channel + parameter + set_value)
        output.send(message)
        time.sleep(.1)


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
        if socket_tmp <= LOCAL_DLIVE_SOCKET_COUNT_MAX and root.console == dliveConstants.console_drop_down_dlive:
            lower_pad = str(item.get_local_pad()).lower()
            socket = socket_dlive_tmp
        elif socket_tmp <= LOCAL_AVANTIS_SOCKET_COUNT_MAX and root.console == dliveConstants.console_drop_down_avantis:
            lower_pad = str(item.get_local_pad()).lower()
            socket = socket_dlive_tmp
        else:
            return

    elif socket_type == "DX1":
        if socket_tmp <= DX1_SOCKET_COUNT_MAX:
            lower_pad = str(item.get_dx1_pad()).lower()
            socket = socket_dlive_tmp + 64
        else:
            return

    elif socket_type == "DX3":
        if socket_tmp <= DX3_SOCKET_COUNT_MAX:
            lower_pad = str(item.get_dx3_pad()).lower()
            socket = socket_dlive_tmp + 96
        else:
            return

    elif socket_type == "Slink":
        if socket_tmp <= SLINK_SOCKET_COUNT_MAX:
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


def assign_dca(output, channel, dca_value):
    midi_channel_tmp = 0xB << 4
    midi_channel_tmp = midi_channel_tmp + root.midi_channel

    select_channel = [midi_channel_tmp, 0x63, channel]
    parameter = [midi_channel_tmp, 0x62, dliveConstants.nrpn_parameter_id_dca_assign]
    set_value = [midi_channel_tmp, 0x06, dca_value]

    if is_network_communication_allowed:
        message = mido.Message.from_bytes(select_channel + parameter + set_value)
        output.send(message)
        time.sleep(.1)


def dca_channel(output, item):
    # TODO: NRPN is currently not supported from mido
    channel = item.get_channel_dlive()

    for dca_index in range(0, 24):

        dca_config = item.get_dca_config()
        dca_array = dca_config.get_dca_array()

        if dca_array.__getitem__(dca_index).lower() == "x":
            assign_dca(output, channel, dliveConstants.dca_on_base_address + dca_index)
        else:
            assign_dca(output, channel, dliveConstants.dca_off_base_address + dca_index)


def handle_dca_parameter(message, output, dca_list, action):
    logging.info(message)
    for item in dca_list:
        if action == "dca":
            dca_channel(output, item)


def is_valid_ip_address(ip_address):
    try:
        ipaddress.IPv4Address(ip_address)
        return True
    except ipaddress.AddressValueError:
        return False


def read_document(filename, check_box_states, check_box_reaper, check_box_write_to_dlive):
    logging.info('The following file will be read : ' + str(filename))

    sheet = Sheet()

    sheet.set_misc_model(create_misc_content(pd.read_excel(filename, sheet_name="Misc")))

    latest_spreadsheet_version = '4'

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

    time.sleep(2)

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

    if check_box_states.__getitem__(0):  # Names
        actions = actions + 1
        cb_names = True
    else:
        cb_names = False

    if check_box_states.__getitem__(1):  # Colors
        actions = actions + 1
        cb_color = True
    else:
        cb_color = False

    if check_box_states.__getitem__(2):  # Mute
        actions = actions + 1
        cb_mute = True
    else:
        cb_mute = False

    if check_box_states.__getitem__(3):  # Phantom value
        actions = actions + 1
        cb_phantom = True
    else:
        cb_phantom = False

    if check_box_states.__getitem__(4):  # Pad value
        actions = actions + 1
        cb_pad = True
    else:
        cb_pad = False

    if check_box_reaper.__getitem__(0):
        actions = actions + 1
        cb_reaper = True
    else:
        cb_reaper = False

    if check_box_write_to_dlive.__getitem__(0):
        cb_write_to_dlive = True
    else:
        cb_write_to_dlive = False

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
                               None,
                               None,
                               None,
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
                               str(sheet_48V_and_pad['Slink Pad'].__getitem__(index)))

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
    read_document(input_file_path, get_checkbox_states(), get_reaper_state(), get_dlive_write_state())


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


root = Tk()
config_frame = Frame(root)
ip_frame = Frame(config_frame)
console_frame = Frame(config_frame)
console_frame.grid(row=1, column=0, sticky="W")
Label(config_frame, text="       ").grid(row=0, column=0)
ip_frame.grid(row=2, column=0, sticky="W")
midi_channel_frame = Frame(config_frame)
midi_channel_frame.grid(row=3, column=0, sticky="W")

config_frame.pack(side=TOP)

columns = Checkbar(root, ['Name', 'Color', 'Mute', '48V Phantom', 'Pad'])
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


def get_checkbox_states():
    return list(columns.state())


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

    # Ein Python-Dictionary in einen JSON-String umwandeln
    json_str = json.dumps(data)

    data = json.loads(json_str)
    with open(file, 'w') as file:
        json.dump(data, file)
        logging.info("Following data has be persisted: " + str(json_str) + " into file: " + str(file) + ".")


def read_perstisted_ip():
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


def read_perstisted_console():
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


def read_perstisted_midi_port():
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
    ip_byte0.delete(0, tkinter.END)
    ip_byte0.insert(0, "192")
    ip_byte1.delete(0, tkinter.END)
    ip_byte1.insert(0, "168")
    ip_byte2.delete(0, tkinter.END)
    ip_byte2.insert(0, "1")
    ip_byte3.delete(0, tkinter.END)
    ip_byte3.insert(0, "70")
    logging.info("Default ip: " + dliveConstants.ip + " was set.")


def set_ip_field_to_local_director_ip():
    ip_byte0.delete(0, tkinter.END)
    ip_byte0.insert(0, "127")
    ip_byte1.delete(0, tkinter.END)
    ip_byte1.insert(0, "0")
    ip_byte2.delete(0, tkinter.END)
    ip_byte2.insert(0, "0")
    ip_byte3.delete(0, tkinter.END)
    ip_byte3.insert(0, "1")
    logging.info("Director ip: 127.0.0.1 was set.")


if __name__ == '__main__':
    root.title('Channel List Manager for Allen & Heath dLive and Avantis - v' + version)
    root.geometry('700x400')
    root.resizable(False, False)
    Label(root, text=" ").pack(side=TOP)
    Label(root, text="Choose from the given spreadsheet which column you want to write.").pack(side=TOP)

    columns.pack(side=TOP, fill=X)
    columns.config(bd=2)
    Label(root, text=" ").pack(side=TOP)
    Label(root, text=" ").pack(side=TOP)
    write_to_dlive.pack(side=TOP, fill=X)
    write_to_dlive.config(bd=2)
    reaper.pack(side=TOP, fill=X)
    reaper.config(bd=2)

    var_console.set(read_perstisted_console())

    Label(console_frame, text="Console:", width=25).pack(side=LEFT)

    dropdown_console = OptionMenu(console_frame, var_console,
                                  dliveConstants.console_drop_down_dlive,
                                  dliveConstants.console_drop_down_avantis,
                                  )
    dropdown_console.pack(side=RIGHT)

    Label(ip_frame, text="(Mixrack-) IP Address:", width=25).pack(side=LEFT)

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

    var_midi_channel.set(read_perstisted_midi_port())  # default value

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

    ip = read_perstisted_ip()
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
        length=600
    )

    pb.grid(row=2)


    def update_progress_label():
        return f"Current Progress: {pb['value']}%"


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


    # label to show current value in percent
    value_label = ttk.Label(bottom_frame, text=update_progress_label())
    value_label.grid(row=3)

    Button(bottom_frame, text='Quit', command=root.quit).grid(row=4)
    bottom_frame.pack(side=BOTTOM)

    root.mainloop()
