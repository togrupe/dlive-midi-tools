# coding=utf-8
import re
import time
from tkinter import filedialog, Button, Tk, Checkbutton, IntVar, W, Frame, LEFT, YES, TOP, X, GROOVE, RIGHT, Label

import mido
import pandas as pd
from mido.sockets import connect

import dliveConstants


version = "1.1.0"

is_network_communication_allowed = dliveConstants.allow_network_communication

def trigger_channel_renaming(message, output, names):
    print(message)

    index = 0

    for name in names:

        characters = re.findall('.?', name)

        payload = []

        for character in characters:
            if len(str(character)) != 0:
                payload.append(ord(character))

        prefix = [0x00, 0x03, index]
        message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + prefix + payload + dliveConstants.sysexhdrend)
        output.send(message)
        time.sleep(.1)
        index = index + 1

    print("Wait 1 seconds")
    time.sleep(1)


def color_channel(output, channel, color):
    colour = dliveConstants.lcd_color_black
    if color == "blue":
        colour = dliveConstants.lcd_color_blue
    elif color == "red":
        colour = dliveConstants.lcd_color_red
    elif color == "light blue":
        colour = dliveConstants.lcd_color_ltblue
    elif color == 'purple':
        colour = dliveConstants.lcd_color_purple
    elif color == 'green':
        colour = dliveConstants.lcd_color_green
    elif color == 'yellow':
        colour = dliveConstants.lcd_color_yellow
    elif color == 'black':
        colour = dliveConstants.lcd_color_black
    elif color == 'white':
        colour = dliveConstants.lcd_color_white

    payload_array = [0x00, 0x06, channel, colour]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    output.send(message)
    time.sleep(.1)


def trigger_coloring(message, output, colors):
    print(message)
    index = 0
    for color in colors:
        color_channel(output, index, color)
        index = index + 1

    print("Wait 1 seconds")
    time.sleep(1)


def phantom_channel(output, channel, phantom):
    if phantom == "yes":
        res = dliveConstants.phantom_power_on
    elif phantom == "no":
        res = dliveConstants.phantom_power_off
    else:
        res = dliveConstants.phantom_power_off

    payload_array = [0x00, 0x0C, channel, res]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    output.send(message)
    time.sleep(.1)


def trigger_phantom_power(message, output, phantoms):
    print(message)
    index = 0
    for phantom in phantoms:
        phantom_channel(output, index, phantom)
        index = index + 1

    time.sleep(1)


def read_document(filename, naming, coloring, phantoming):
    df = pd.read_excel(filename)

    names = []
    for name in df['Name']:
        names.append(name)

    colors = []
    for color in df['Color']:
        colors.append(color)

    phantoms = []
    for phantom in df['Phantom']:
        phantoms.append(phantom)

    time.sleep(2)
    if is_network_communication_allowed:
        print("Open connection to dlive...")
        output = connect(dliveConstants.ip, dliveConstants.port)
        print("Connection successful.")

    time.sleep(1)

    print("Start Processing...")
    if naming:
        print("1. Writing the following channel names...")
        print(names)
        if is_network_communication_allowed:
            trigger_channel_renaming("Naming the channels...", output, names)
    if coloring:
        print("2. Writing the following colors...")
        print(colors)
        if is_network_communication_allowed:
            trigger_coloring("Coloring the channels...", output, colors)
    if phantoming:
        print("3. Writing the following phantom power values...")
        print(phantoms)
        if is_network_communication_allowed:
            trigger_phantom_power("Set phantom power to the channels...", output, phantoms)
    print("Processing done")

    if is_network_communication_allowed:
        output.close()


def browse_files():
    file = filedialog.askopenfilename()

    states = allstates()

    if states.__getitem__(0):
        cb_naming = True
    else:
        cb_naming = False

    if states.__getitem__(1):
        cb_coloring = True
    else:
        cb_coloring = False

    if states.__getitem__(2):
        cb_phantom = True
    else:
        cb_phantom = False

    read_document(file, cb_naming, cb_coloring, cb_phantom)


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
lng = Checkbar(root, ['Names', 'Colors', '48V Phantom Power'])


def allstates():
    return list(lng.state())


if __name__ == '__main__':
    root.title('Allen & Heath dLive Channel List Manager, Version: ' + version)

    var = Label(root, text="Choose from the given Excel sheet which column you want to write.")
    var.pack(side=TOP)
    root.geometry('600x120')

    root.resizable(False, False)

    lng.pack(side=TOP, fill=X)
    lng.config(relief=GROOVE, bd=2)

    Button(root, text='Open Excel Sheet and Trigger Writing Process', command=browse_files).pack(side=LEFT)
    Button(root, text='Quit', command=root.quit).pack(side=RIGHT)
   
    root.mainloop()
