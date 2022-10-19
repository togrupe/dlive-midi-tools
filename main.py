# coding=utf-8
import logging
import re
import time
from tkinter import filedialog, Button, Tk, Checkbutton, IntVar, W, Frame, LEFT, YES, TOP, X, GROOVE, RIGHT, Label, \
    Entry, BOTTOM, StringVar, OptionMenu, ttk
from tkinter.messagebox import showinfo

import mido
import pandas as pd
from mido.sockets import connect

import dliveConstants
from ChannelListEntry import ChannelListEntry

logging.basicConfig(filename='main.log', level=logging.DEBUG)

version = "1.5.0"

is_network_communication_allowed = dliveConstants.allow_network_communication


def trigger_channel_renaming(message, output, names):
    logging.info(message)

    for item in names:

        # Trim name if length of name > 6
        if len(str(item.get_name())) > 6:
            trimmed_name = str(item.get_name())[0:6]
            logging.info("Channel name will be trimmed to 6 characters, before: " + str(item.get_name()) + " after: " + str(
                trimmed_name))
        else:
            trimmed_name = str(item.get_name())

        characters = re.findall('.?', trimmed_name)

        payload = []

        for character in characters:
            if len(str(character)) != 0:
                payload.append(ord(character))

        prefix = [root.midi_port, dliveConstants.sysex_message_set_channel_name,
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

    payload_array = [root.midi_port, dliveConstants.sysex_message_set_channel_colour, channel,
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

    payload_array = [root.midi_port, dliveConstants.sysex_message_set_socket_preamp_48V, channel,
                     res]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
    time.sleep(.1)


def trigger_phantom_power(message, output, phantoms):
    logging.info(message)
    for item in phantoms:
        phantom_channel(output, item.get_channel_dlive(), item.get_phantom())

    time.sleep(1)


def read_document(filename, check_box_states):
    logging.info('The following file will be read : ' + str(filename))

    df = pd.read_excel(filename)

    channels = []
    for channel in df['Channel']:
        channels.append(channel)

    names = []
    for name in df['Name']:
        names.append(str(name))

    colors = []
    for color in df['Color']:
        colors.append(color)

    phantoms = []
    for phantom in df['Phantom']:
        phantoms.append(phantom)

    channel_list_entries = []
    index = 0
    for channel in channels:
        cle = ChannelListEntry(channel, names.__getitem__(index), colors.__getitem__(index),
                               phantoms.__getitem__(index))
        channel_list_entries.append(cle)
        index = index + 1

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

    root.midi_port = determine_technical_midi_port(var_midi_port.get())

    time.sleep(1)

    actions = 0

    if check_box_states.__getitem__(0):  # Names
        actions = actions + 1
        naming = True
    else:
        naming = False

    if check_box_states.__getitem__(1):  # Colors
        actions = actions + 1
        coloring = True
    else:
        coloring = False

    if check_box_states.__getitem__(2):  # Phantom power
        actions = actions + 1
        phantoming = True
    else:
        phantoming = False

    logging.info("Start Processing...")

    if naming:
        logging.debug("Writing the following channel names...")
        logging.debug("Input Array: " + str(names))
        trigger_channel_renaming("Naming the channels...", output, channel_list_entries)
        progress(actions)
        root.update()

    if coloring:
        logging.debug("Writing the following colors...")
        logging.debug("Input Array: " + str(colors))
        trigger_coloring("Coloring the channels...", output, channel_list_entries)
        progress(actions)
        root.update()

    if phantoming:
        logging.debug("Writing the following phantom power values...")
        logging.debug("Input Array: " + str(phantoms))
        trigger_phantom_power("Set phantom power to the channels...", output, channel_list_entries)
        progress(actions)
        root.update()

    if actions == 0:
        progress(actions)
        root.update()

    logging.info("Processing done")

    if is_network_communication_allowed:
        output.close()
    progress_open_or_close_connection()
    root.update()


def determine_technical_midi_port(selected_midi_port_as_string):
    switcher = {
        "1 to 5": 0,
        "2 to 6": 1,
        "3 to 7": 2,
        "4 to 8": 3,
        "5 to 9": 4,
        "6 to 10": 5,
        "7 to 11": 6,
        "8 to 12": 7,
        "9 to 13": 8,
        "10 to 14": 9,
        "11 to 15": 10,
        "12 to 16": 11
    }
    return switcher.get(selected_midi_port_as_string, "Invalid port")


def browse_files():
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
midi_port_frame = Frame(config_frame)
midi_port_frame.grid(row=2, column=0, sticky="W")
config_frame.pack(side=TOP)

columns = Checkbar(root, ['Names', 'Colors', '48V Phantom Power'])
ip_field = Frame(ip_frame)
ip_byte0 = Entry(ip_field, width=3)
ip_byte1 = Entry(ip_field, width=3)
ip_byte2 = Entry(ip_field, width=3)
ip_byte3 = Entry(ip_field, width=3)
mixrack_ip = ""
midi_port = None
var_midi_port = StringVar(root)


def get_checkbox_states():
    return list(columns.state())


if __name__ == '__main__':
    root.title('Channel List Manager for Allen & Heath dLive Systems - v' + version)
    root.geometry('600x300')
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

    var_midi_port.set("12 to 16")  # default value

    Label(midi_port_frame, text="   Mixrack Midi Port:", width=25).pack(side=LEFT)

    dropdown_midi_port = OptionMenu(midi_port_frame, var_midi_port, "1 to 5", "2 to 6", "3 to 7", "4 to 8", "5 to 9",
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
                showinfo(message='The progress completed!')


    def progress_open_or_close_connection():
        if pb['value'] < 100:
            pb['value'] += 5
            value_label['text'] = update_progress_label()
        else:
            showinfo(message='The progress completed!')


    # label to show current value in percent
    value_label = ttk.Label(bottom_frame, text=update_progress_label())
    value_label.grid(row=3)

    Button(bottom_frame, text='Quit', command=root.quit).grid(row=4)
    bottom_frame.pack(side=BOTTOM)

    root.mainloop()
