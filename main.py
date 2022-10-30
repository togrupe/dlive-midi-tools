# coding=utf-8
import logging
import re
import time
from tkinter import filedialog, Button, Tk, Checkbutton, IntVar, W, Frame, LEFT, YES, TOP, X, GROOVE, RIGHT, Label, \
    Entry, BOTTOM, StringVar, OptionMenu, ttk
from tkinter.messagebox import showinfo

import mido
import numpy
import pandas as pd
from mido.sockets import connect

import dliveConstants
from model.ChannelListEntry import ChannelListEntry
from model.DcaConfig import DcaConfig
from model.DcaListEntry import DcaListEntry
from model.Misc import Misc
from model.PhantomListEntry import PhantomListEntry
from model.Sheet import Sheet

logging.basicConfig(filename='main.log', level=logging.DEBUG)

version = "2.0.0"

is_network_communication_allowed = dliveConstants.allow_network_communication


def name_channel(output, item):
    # Trim name if length of name > 6
    if len(str(item.get_name())) > 6:
        trimmed_name = str(item.get_name())[0:6]
        logging.info(
            "Channel name will be trimmed to 6 characters, before: " + str(item.get_name()) + " after: " + str(
                trimmed_name))
    else:
        trimmed_name = str(item.get_name())

    characters = re.findall('.?', trimmed_name)

    payload = []

    for character in characters:
        if len(str(character)) != 0:
            payload.append(ord(character))

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


def phantom_socket(output, item, type):
    socket_tmp = item.get_socket_number()
    socket_dlive_tmp = item.get_socket_number_dlive()
    if type == "local":
        lower_phantom = str(item.get_local_phantom()).lower()
        socket = socket_dlive_tmp
    elif type == "DX1":
        lower_phantom = str(item.get_dx1_phantom()).lower()
        if (socket_tmp <= 32):
            socket = socket_dlive_tmp + 64
        else:
            return
    elif type == "DX3":
        lower_phantom = str(item.get_dx3_phantom()).lower()
        if (socket_tmp <= 32):
            socket = socket_dlive_tmp + 96
        else:
            return

    if lower_phantom == "yes":
        res = dliveConstants.phantom_power_on
    elif lower_phantom == "no":
        res = dliveConstants.phantom_power_off
    else:
        res = dliveConstants.phantom_power_off

    payload_array = [root.midi_channel, dliveConstants.sysex_message_set_socket_preamp_48V, socket,
                     res]

    if is_network_communication_allowed:
        message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
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
    parameter = [midi_channel_tmp, 0x62, dliveConstants.nrpn_message_hpf_on]
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
    parameter = [midi_channel_tmp, 0x62, dliveConstants.nrpn_message_hpf_frequency]
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
    parameter = [midi_channel_tmp, 0x62, dliveConstants.nrpn_message_fader_level]
    set_value = [midi_channel_tmp, 0x06, fader_level]

    if is_network_communication_allowed:
        message = mido.Message.from_bytes(select_channel + parameter + set_value)
        output.send(message)
        time.sleep(.1)


def handle_channels_parameter(message, output, channel_list_entries, action):
    logging.info(message)
    for item in channel_list_entries:
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


def pad_socket(output, item, type):
    socket_tmp = item.get_socket_number_dlive()

    if type == "local":
        lower_pad = str(item.get_local_pad()).lower()
        socket = item.get_socket_number_dlive()
    elif type == "DX1":
        lower_pad = str(item.get_dx1_pad()).lower()
        if item.socket_number <= 32:
            socket = socket_tmp + 64
        else:
            return
    elif type == "DX3":
        lower_pad = str(item.get_dx3_pad()).lower()
        if item.socket_number <= 32:
            socket = socket_tmp + 96
        else:
            return

    if lower_pad == "yes":
        res = dliveConstants.pad_on
    else:
        res = dliveConstants.pad_off

    payload_array = [root.midi_channel, dliveConstants.sysex_message_set_socket_preamp_pad, socket, res]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
        time.sleep(.1)


def handle_phantom_and_pad_parameter(message, output, phantom_list_entries, action):
    logging.info(message)
    for item in phantom_list_entries:
        if action == "phantom":
            phantom_socket(output, item, "local")
            phantom_socket(output, item, "DX1")
            phantom_socket(output, item, "DX3")
        elif action == "pad":
            pad_socket(output, item, "local")
            pad_socket(output, item, "DX1")
            pad_socket(output, item, "DX3")


class SheetVersionNotCompatible:
    pass


def assign_dca(output, channel, dca_value):
    midi_channel_tmp = 0xB << 4
    midi_channel_tmp = midi_channel_tmp + root.midi_channel

    select_channel = [midi_channel_tmp, 0x63, channel]
    parameter = [midi_channel_tmp, 0x62, dliveConstants.nrpn_message_dca_assign]
    set_value = [midi_channel_tmp, 0x06, dca_value]

    if is_network_communication_allowed:
        message = mido.Message.from_bytes(select_channel + parameter + set_value)
        output.send(message)
        time.sleep(.1)


def dca_channel(output, item):
    # TODO: NRPN is currently not supported from mido
    channel = item.get_channel_dlive()

    if str(item.get_dca_config().get_dca1()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on)
    else:
        assign_dca(output, channel, dliveConstants.dca_off)

    if str(item.get_dca_config().get_dca2()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 1)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 1)

    if str(item.get_dca_config().get_dca3()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 2)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 2)

    if str(item.get_dca_config().get_dca4()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 3)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 3)

    if str(item.get_dca_config().get_dca5()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 4)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 4)

    if str(item.get_dca_config().get_dca6()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 5)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 5)

    if str(item.get_dca_config().get_dca7()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 6)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 6)

    if str(item.get_dca_config().get_dca8()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 7)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 7)

    if str(item.get_dca_config().get_dca9()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 8)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 8)

    if str(item.get_dca_config().get_dca10()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 9)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 9)

    if str(item.get_dca_config().get_dca11()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 10)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 10)

    if str(item.get_dca_config().get_dca12()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 11)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 11)

    if str(item.get_dca_config().get_dca13()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 12)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 12)

    if str(item.get_dca_config().get_dca14()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 13)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 13)

    if str(item.get_dca_config().get_dca15()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 14)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 14)

    if str(item.get_dca_config().get_dca16()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 15)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 15)

    if str(item.get_dca_config().get_dca17()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 16)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 16)

    if str(item.get_dca_config().get_dca18()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 17)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 17)

    if str(item.get_dca_config().get_dca19()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 18)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 18)

    if str(item.get_dca_config().get_dca20()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 19)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 19)

    if str(item.get_dca_config().get_dca21()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 20)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 20)

    if str(item.get_dca_config().get_dca22()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 21)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 21)

    if str(item.get_dca_config().get_dca23()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 22)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 22)

    if str(item.get_dca_config().get_dca24()).lower() == "x":
        assign_dca(output, channel, dliveConstants.dca_on + 23)
    else:
        assign_dca(output, channel, dliveConstants.dca_off + 23)


def handle_dca_parameter(message, output, dca_list, action):
    logging.info(message)
    for item in dca_list:
        if action == "dca":
            dca_channel(output, item)


def read_document(filename, check_box_states):
    logging.info('The following file will be read : ' + str(filename))

    sheet = Sheet()

    sheet.set_channel_model(create_channel_list_content(pd.read_excel(filename, sheet_name="Channels")))
    sheet.set_phantom_pad_model(create_phantom_pad_content(pd.read_excel(filename, sheet_name="48V & Pad")))
    sheet.set_dca_model(create_dca_content(pd.read_excel(filename, sheet_name="DCAs")))
    sheet.set_misc_model(create_misc_content(pd.read_excel(filename, sheet_name="Misc")))

    if sheet.get_misc_model().get_version() != '2':
        raise SheetVersionNotCompatible

    time.sleep(2)

    if is_network_communication_allowed:
        mixrack_ip_tmp = ip_byte0.get() + "." + ip_byte1.get() + "." + ip_byte2.get() + "." + ip_byte3.get()
        logging.info("Open connection to dlive on ip: " + mixrack_ip_tmp + ":" + str(dliveConstants.port) + " ...")
        output = connect(mixrack_ip_tmp, dliveConstants.port)
        logging.info("Connection successful.")
    else:
        output = None
    progress_open_or_close_connection()
    root.update()

    root.midi_channel = determine_technical_midi_port(var_midi_channel.get())

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

    if check_box_states.__getitem__(3):  # Fader Level
        actions = actions + 1
        cb_fader_level = True
    else:
        cb_fader_level = False

    if check_box_states.__getitem__(4):  # HPF On
        actions = actions + 1
        cb_hpf_on = True
    else:
        cb_hpf_on = False

    if check_box_states.__getitem__(5):  # HPF value
        actions = actions + 1
        cb_hpf_value = True
    else:
        cb_hpf_value = False

    if check_box_states.__getitem__(6):  # Phantom value
        actions = actions + 1
        cb_phantom = True
    else:
        cb_phantom = False

    if check_box_states.__getitem__(7):  # Pad value
        actions = actions + 1
        cb_pad = True
    else:
        cb_pad = False

    if check_box_states.__getitem__(8):  # DCA values
        actions = actions + 1
        cb_dca = True
    else:
        cb_dca = False

    logging.info("Start Processing...")

    if cb_names:
        handle_channels_parameter("Set Name on to the channels...", output, sheet.get_channel_model(), action="name")
        progress(actions)
        root.update()

    if cb_color:
        handle_channels_parameter("Set Colors on to the channels...", output, sheet.get_channel_model(), action="color")
        progress(actions)
        root.update()

    if cb_mute:
        handle_channels_parameter("Set Mute on to the channels...", output, sheet.get_channel_model(), action="mute")
        progress(actions)
        root.update()

    if cb_fader_level:
        handle_channels_parameter("Set Fader Level on to the channels...", output, sheet.get_channel_model(),
                                  action="fader_level")
        progress(actions)
        root.update()

    if cb_hpf_on:
        handle_channels_parameter("Set HPF On to the channels...", output, sheet.get_channel_model(), action="hpf_on")
        progress(actions)
        root.update()

    if cb_hpf_value:
        handle_channels_parameter("Set HPF Value to the channels...", output, sheet.get_channel_model(), action="hpf_value")
        progress(actions)
        root.update()

    if cb_phantom:
        handle_phantom_and_pad_parameter("Set Phantom Power to the channels...", output, sheet.get_phantom_pad_model(),
                                         action="phantom")
        progress(actions)
        root.update()

    if cb_pad:
        handle_phantom_and_pad_parameter("Set Pad to the channels...", output, sheet.get_phantom_pad_model(),
                                         action="pad")
        progress(actions)
        root.update()

    if cb_dca:
        handle_dca_parameter("Set DCA assignments to the channels...", output, sheet.get_dca_model(),
                             action="dca")
        progress(actions)
        root.update()

    if actions == 0:
        progress(actions)
        root.update()

    logging.info("Processing done")

    if is_network_communication_allowed:
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
                               sheet_channels['HPF Value'].__getitem__(index),
                               str(sheet_channels['Fader Level'].__getitem__(index)),
                               str(sheet_channels['Mute'].__getitem__(index))
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
        dca_config_tmp = DcaConfig(str(sheet_dcas['DCA1'].__getitem__(index)),
                                   str(sheet_dcas['DCA2'].__getitem__(index)),
                                   str(sheet_dcas['DCA3'].__getitem__(index)),
                                   str(sheet_dcas['DCA4'].__getitem__(index)),
                                   str(sheet_dcas['DCA5'].__getitem__(index)),
                                   str(sheet_dcas['DCA6'].__getitem__(index)),
                                   str(sheet_dcas['DCA7'].__getitem__(index)),
                                   str(sheet_dcas['DCA8'].__getitem__(index)),
                                   str(sheet_dcas['DCA9'].__getitem__(index)),
                                   str(sheet_dcas['DCA10'].__getitem__(index)),
                                   str(sheet_dcas['DCA11'].__getitem__(index)),
                                   str(sheet_dcas['DCA12'].__getitem__(index)),
                                   str(sheet_dcas['DCA13'].__getitem__(index)),
                                   str(sheet_dcas['DCA14'].__getitem__(index)),
                                   str(sheet_dcas['DCA15'].__getitem__(index)),
                                   str(sheet_dcas['DCA16'].__getitem__(index)),
                                   str(sheet_dcas['DCA17'].__getitem__(index)),
                                   str(sheet_dcas['DCA18'].__getitem__(index)),
                                   str(sheet_dcas['DCA19'].__getitem__(index)),
                                   str(sheet_dcas['DCA20'].__getitem__(index)),
                                   str(sheet_dcas['DCA21'].__getitem__(index)),
                                   str(sheet_dcas['DCA22'].__getitem__(index)),
                                   str(sheet_dcas['DCA23'].__getitem__(index)),
                                   str(sheet_dcas['DCA24'].__getitem__(index)))

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
                               str(sheet_48V_and_pad['DX3 Pad'].__getitem__(index)))

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


def reset_progress_bar():
    pb['value'] = 0
    root.update()


def browse_files():
    reset_progress_bar()
    read_document(filedialog.askopenfilename(), get_checkbox_states())


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
Label(config_frame, text="       ").grid(row=0, column=0)
ip_frame.grid(row=1, column=0, sticky="W")
midi_channel_frame = Frame(config_frame)
midi_channel_frame.grid(row=2, column=0, sticky="W")
config_frame.pack(side=TOP)

columns = Checkbar(root, ['Name', 'Color', 'Mute', 'Fader Level', 'HPF On', 'HPF Value', '48V Phantom', 'Pad', 'DCA'])
ip_field = Frame(ip_frame)
ip_byte0 = Entry(ip_field, width=3)
ip_byte1 = Entry(ip_field, width=3)
ip_byte2 = Entry(ip_field, width=3)
ip_byte3 = Entry(ip_field, width=3)
mixrack_ip = ""
midi_channel = None
var_midi_channel = StringVar(root)


def get_checkbox_states():
    return list(columns.state())


if __name__ == '__main__':
    root.title('Channel List Manager for Allen & Heath dLive Systems - v' + version)
    root.geometry('700x300')
    root.resizable(False, False)
    Label(root, text=" ").pack(side=TOP)
    Label(root, text="Choose from the given Excel sheet which column you want to write.").pack(side=TOP)

    columns.pack(side=TOP, fill=X)
    columns.config(relief=GROOVE, bd=2)
    Label(ip_frame, text="Mixrack IP Address:", width=25).pack(side=LEFT)

    ip_byte0.grid(row=0, column=0)
    Label(ip_field, text=".").grid(row=0, column=1)
    ip_byte1.grid(row=0, column=2)
    Label(ip_field, text=".").grid(row=0, column=3)
    ip_byte2.grid(row=0, column=4)
    Label(ip_field, text=".").grid(row=0, column=5)
    ip_byte3.grid(row=0, column=6)
    ip_field.pack(side=RIGHT)

    var_midi_channel.set(dliveConstants.midi_channel_drop_down_string_12)  # default value

    Label(midi_channel_frame, text="   Mixrack Midi Channel:", width=25).pack(side=LEFT)

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

    ip_from_config_file = dliveConstants.ip.split(".")

    ip_byte0.insert(10, ip_from_config_file.__getitem__(0))
    ip_byte1.insert(11, ip_from_config_file.__getitem__(1))
    ip_byte2.insert(12, ip_from_config_file.__getitem__(2))
    ip_byte3.insert(13, ip_from_config_file.__getitem__(3))

    bottom_frame = Frame(root)

    Button(bottom_frame, text='Open Excel sheet and trigger writing process', command=browse_files).grid(row=0)
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
