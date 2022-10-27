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
from numpy import byte

import dliveConstants
from model.ChannelListEntry import ChannelListEntry
from model.DcaConfig import DcaConfig
from model.DcaListEntry import DcaListEntry

logging.basicConfig(filename='main.log', level=logging.INFO)

version = "2.0.0"

is_network_communication_allowed = dliveConstants.allow_network_communication


def trigger_channel_renaming(message, output, names):
    logging.info(message)

    for item in names:

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

    logging.info("Wait 1 seconds")
    time.sleep(1)


def color_channel(output, channel, color):
    colour = dliveConstants.lcd_color_black

    lower_color = str(color).lower()
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

    payload_array = [root.midi_channel, dliveConstants.sysex_message_set_channel_colour, channel,
                     colour]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
        time.sleep(.1)


def trigger_coloring(message, output, colors):
    logging.info(message)
    for item in colors:
        color_channel(output, item.get_channel_dlive(), item.get_color())

    logging.info("Wait 1 seconds")
    time.sleep(1)


def phantom_channel(output, channel, phantom):
    lower_phantom = str(phantom).lower()
    if lower_phantom == "yes":
        res = dliveConstants.phantom_power_on
    elif lower_phantom == "no":
        res = dliveConstants.phantom_power_off
    else:
        res = dliveConstants.phantom_power_off

    payload_array = [root.midi_channel, dliveConstants.sysex_message_set_socket_preamp_48V, channel,
                     res]

    if is_network_communication_allowed:
        message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
        output.send(message)
        time.sleep(.1)


def hpf_on_channel(output, channel, hpf_on):
    # TODO: NRPN is currently not supported from mido
    lower_hpf_on = str(hpf_on).lower()
    if lower_hpf_on == "yes":
        res = dliveConstants.hpf_on
    else:
        res = dliveConstants.hpf_off

    midi_channel_tmp = 0xB << 4
    midi_channel_tmp = midi_channel_tmp + root.midi_channel

    select_channel = [midi_channel_tmp, 0x63, channel]
    parameter = [midi_channel_tmp, 0x62, dliveConstants.nrpn_message_hpf_on]
    set_value = [midi_channel_tmp, 0x06, res]

    if is_network_communication_allowed:
        message = mido.Message.from_bytes(select_channel + parameter + set_value)
        output.send(message)
        time.sleep(.1)


def mute_on_channel(output, channel, mute_on):
    midi_channel_tmp = root.midi_channel

    lower_mute_on = str(mute_on).lower()

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


def fader_level_channel(output, channel, fader_level):
    # TODO: NRPN is currently not supported by mido
    lower_fader_level = str(fader_level).lower()

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

    select_channel = [byte(midi_channel_tmp), byte(0x63), byte(channel)]
    parameter = [byte(midi_channel_tmp), byte(0x62), byte(dliveConstants.nrpn_message_fader_level)]
    set_value = [byte(midi_channel_tmp), byte(0x06), byte(fader_level)]

    message = mido.Message.from_bytes(select_channel + parameter + set_value)

    if is_network_communication_allowed:
        output.send(message)
        time.sleep(.1)


def calculate_vv(hpf_value):
    return int(127 * ((4608 * numpy.log10(hpf_value / 4) / numpy.log10(2)) - 10699) / 41314)


def hpf_value_channel(output, channel, hpf_value):
    # TODO: NRPN is currenty not supported from mido
    midi_channel = 0xB << 4
    midi_channel = midi_channel + root.midi_channel

    select_channel = [midi_channel, 0x63, channel]
    parameter = [midi_channel, 0x62, dliveConstants.nrpn_message_hpf_frequency]
    set_value = [midi_channel, 0x06, calculate_vv(hpf_value)]

    if is_network_communication_allowed:
        message = mido.Message.from_bytes(select_channel + parameter + set_value)
        output.send(message)
        time.sleep(.1)


def trigger_phantom_power(message, output, phantoms):
    logging.info(message)
    for item in phantoms:
        phantom_channel(output, item.get_channel_dlive(), item.get_phantom())

    time.sleep(1)


def pad_channel(output, channel, pad):
    lower_pad = str(pad).lower()
    if lower_pad == "yes":
        res = dliveConstants.pad_on
    else:
        res = dliveConstants.pad_off

    payload_array = [root.midi_channel, dliveConstants.sysex_message_set_socket_preamp_pad, channel, res]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
    time.sleep(.1)


def handle_channels_parameter(message, output, channel_list_entries, action):
    logging.info(message)
    for item in channel_list_entries:

        if action == "fader_level":
            fader_level_channel(output, item.get_channel_dlive(), item.get_fader_level())
        elif action == "mute":
            mute_on_channel(output, item.get_channel_dlive(), item.get_mute())
        elif action == "hpf_on":
            hpf_on_channel(output, item.get_channel_dlive(), item.get_hpf_on())
        elif action == "hpf_value":
            hpf_value_channel(output, item.get_channel_dlive(), item.get_hpf_value())


def read_document_sheet_channels(filename, check_box_states):
    logging.info('The following file will be read : ' + str(filename))

    # read_document_sheet_dcas(filename, check_box_states) # TODO:Continue here
    # sheet_misc = pd.read_excel(filename, sheet_name="Misc") # TODO:Continue here
    # sheet_48V_and_pad = pd.read_excel(filename, sheet_name="48V") # TODO:Continue here

    sheet_channels = pd.read_excel(filename, sheet_name="Channels")

    channels = []
    for channel in sheet_channels['Channel']:
        channels.append(channel)

    names = []
    for name in sheet_channels['Name']:
        names.append(str(name))

    colors = []
    for color in sheet_channels['Color']:
        colors.append(color)

    mute_list = []
    for mute in sheet_channels['Mute']:
        mute_list.append(mute)

    fader_level_list = []
    for fader_level in sheet_channels['Fader Level']:
        fader_level_list.append(fader_level)

    hpf_on_list = []
    for hpf in sheet_channels['HPF On']:
        hpf_on_list.append(hpf)

    hpf_value_list = []
    for hpf_value in sheet_channels['HPF Value']:
        hpf_value_list.append(hpf_value)

    channel_list_entries = []
    index = 0
    for channel in channels:
        cle = ChannelListEntry(channel, names.__getitem__(index), colors.__getitem__(index),
                               hpf_on_list.__getitem__(index), hpf_value_list.__getitem__(index),
                               fader_level_list.__getitem__(index), mute_list.__getitem__(index))
        channel_list_entries.append(cle)
        index = index + 1

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

    # if check_box_states.__getitem__(3):  # Fader Level
    #     actions = actions + 1
    #     cb_fader_level = True
    # else:
    #     cb_fader_level = False
    #
    # if check_box_states.__getitem__(4):  # HPF On
    #     actions = actions + 1
    #     cb_hpf_on = True
    # else:
    #     cb_hpf_on = False
    #
    # if check_box_states.__getitem__(5):  # HPF value
    #     actions = actions + 1
    #     cb_hpf_value = True
    # else:
    #     cb_hpf_value = False

    logging.info("Start Processing...")

    if cb_names:
        logging.debug("Writing the following channel names...")
        logging.debug("Input Array: " + str(names))
        trigger_channel_renaming("Naming the channels...", output, channel_list_entries)
        progress(actions)
        root.update()

    if cb_color:
        logging.debug("Writing the following colors...")
        logging.debug("Input Array: " + str(colors))
        trigger_coloring("Coloring the channels...", output, channel_list_entries)
        progress(actions)
        root.update()

    if cb_mute:
        logging.debug("Writing the following mutes states...")
        logging.debug("Input Array: " + str(mute_list))
        handle_channels_parameter("Set Mute on to the channels...", output, channel_list_entries, action="mute")
        progress(actions)
        root.update()

    # if cb_fader_level:
    #     logging.debug("Writing the following fader levels...")
    #     logging.debug("Input Array: " + str(fader_level_list))
    #     handle_channels_parameter("Set Fader Level on to the channels...", output, channel_list_entries,
    #                               action="fader_level")
    #     progress(actions)
    #     root.update()
    #
    # if cb_hpf_on:
    #     logging.debug("Writing the following HPF on states...")
    #     logging.debug("Input Array: " + str(hpf_on_list))
    #     handle_channels_parameter("Set HPF On to the channels...", output, channel_list_entries, action="hpf_on")
    #     progress(actions)
    #     root.update()
    #
    # if cb_hpf_value:
    #     logging.debug("Writing the following HPF values ...")
    #     logging.debug("Input Array: " + str(hpf_value_list))
    #     handle_channels_parameter("Set HPF Value to the channels...", output, channel_list_entries, action="hpf_value")
    #     progress(actions)
    #     root.update()

    if actions == 0:
        progress(actions)
        root.update()

    logging.info("Processing done")

    if is_network_communication_allowed:
        output.close()
    progress_open_or_close_connection()
    progress_open_or_close_connection()
    root.update()


def read_document_sheet_dcas(filename, check_box_states):
    logging.info('The following file will be read : ' + str(filename))

    dca_setup = []

    sheet_dcas = pd.read_excel(filename, sheet_name="DCAs", usecols="A2,C2:Z2")
    for label, content in sheet_dcas.items():
        dca_config_temp = DcaConfig(content.__getitem__(0), None, None, None, None, None, None, None)
        dle = DcaListEntry(label, dca_config_temp)
        dca_setup.append(dle)

    time.sleep(2)

    if is_network_communication_allowed:
        mixrack_ip = ip_byte0.get() + "." + ip_byte1.get() + "." + ip_byte2.get() + "." + ip_byte3.get()
        logging.info("Open connection to dlive on ip: " + mixrack_ip + ":" + str(dliveConstants.port) + " ...")
        output = connect(mixrack_ip, dliveConstants.port)
        logging.info("Connection successful.")
    else:
        output = None
    progress_open_or_close_connection()
    root.update()

    root.midi_channel = determine_technical_midi_port(var_midi_channel.get())

    time.sleep(1)

    actions = 0

    logging.info("Start Processing...")

    if actions == 0:
        progress(actions)
        root.update()

    logging.info("Processing done")

    if is_network_communication_allowed:
        output.close()
    progress_open_or_close_connection()
    progress_open_or_close_connection()
    root.update()


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
    read_document_sheet_channels(filedialog.askopenfilename(), get_checkbox_states())


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

# columns = Checkbar(root, ['Names', 'Colors', 'Mute', 'Fader Level', 'HPF On', 'HPF Value'])
columns = Checkbar(root, ['Names', 'Colors', 'Mute'])
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

    Label(midi_channel_frame, text="   Mixrack Midi Port:", width=25).pack(side=LEFT)

    dropdown_midi_port = OptionMenu(midi_channel_frame, var_midi_channel, "1 to 5", "2 to 6", "3 to 7", "4 to 8", "5 to 9",
                                    "6 to 10", "7 to 11",
                                    "8 to 12", "9 to 13", "10 to 14", "11 to 15", "12 to 16")
    dropdown_midi_port.pack(side=RIGHT)

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
