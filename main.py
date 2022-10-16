# coding=utf-8
import re
import time
from tkinter import filedialog, Button, Tk, Checkbutton, IntVar, W, Frame, LEFT, YES, TOP, X, GROOVE, RIGHT, Label, \
    Entry, BOTTOM

import mido
import pandas as pd
from mido.sockets import connect

import dliveConstants

version = "1.2.1"

is_network_communication_allowed = dliveConstants.allow_network_communication


def trigger_channel_renaming(message, output, names):
    print(message)

    index = 0

    for name in names:

        # Trim name if length of name > 6
        if len(str(name)) > 6:
            trimmed_name = name[0:6]
        else:
            trimmed_name = name

        characters = re.findall('.?', trimmed_name)

        payload = []

        for character in characters:
            if len(str(character)) != 0:
                payload.append(ord(character))

        prefix = [0x00, 0x03, index]
        message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + prefix + payload + dliveConstants.sysexhdrend)
        if is_network_communication_allowed:
            output.send(message)
        time.sleep(.1)
        index = index + 1

    print("Wait 1 seconds")
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

    payload_array = [0x00, 0x06, channel, colour]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
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
    lower_phantom = str(phantom).lower()
    if lower_phantom == "yes":
        res = dliveConstants.phantom_power_on
    elif lower_phantom == "no":
        res = dliveConstants.phantom_power_off
    else:
        res = dliveConstants.phantom_power_off

    payload_array = [0x00, 0x0C, channel, res]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
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
        mixrack_ip = ip_byte0.get() + "." + ip_byte1.get() + "." + ip_byte2.get() + "." + ip_byte3.get()
        print("Open connection to dlive on ip: " + mixrack_ip + ":" + str(dliveConstants.port) + " ...")
        output = connect(mixrack_ip, dliveConstants.port)
        print("Connection successful.")
    else:
        output = None

    time.sleep(1)

    print("Start Processing...")
    if naming:
        print("1. Writing the following channel names...")
        print("Input Array: " + str(names))
        trigger_channel_renaming("Naming the channels...", output, names)
    if coloring:
        print("2. Writing the following colors...")
        print("Input Array: " + str(colors))
        trigger_coloring("Coloring the channels...", output, colors)
    if phantoming:
        print("3. Writing the following phantom power values...")
        print("Input Array: " + str(phantoms))
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
ip_frame = Frame(root)
columns = Checkbar(root, ['Names', 'Colors', '48V Phantom Power'])
ip_byte0 = Entry(ip_frame, width=3)
ip_byte1 = Entry(ip_frame, width=3)
ip_byte2 = Entry(ip_frame, width=3)
ip_byte3 = Entry(ip_frame, width=3)
mixrack_ip = ""


def allstates():
    return list(columns.state())


if __name__ == '__main__':
    root.title('Channel List Manager for Allen & Heath dLive Systems - v' + version)
    root.geometry('600x200')
    root.resizable(False, False)
    Label(root, text="Choose from the given Excel sheet which column you want to write.").pack(side=TOP)

    columns.pack(side=TOP, fill=X)
    columns.config(relief=GROOVE, bd=2)
    Label(ip_frame, text="-->     ").grid(row=0, column=0)
    Label(ip_frame, text="Mixrack IP Address:").grid(row=0, column=1)
    ip_byte0.grid(row=0, column=2)
    Label(ip_frame, text=".").grid(row=0, column=3)
    ip_byte1.grid(row=0, column=4)
    Label(ip_frame, text=".").grid(row=0, column=5)
    ip_byte2.grid(row=0, column=6)
    Label(ip_frame, text=".").grid(row=0, column=7)
    ip_byte3.grid(row=0, column=8)

    ip = dliveConstants.ip.split(".")

    ip_byte0.insert(10, ip.__getitem__(0))
    ip_byte1.insert(11, ip.__getitem__(1))
    ip_byte2.insert(12, ip.__getitem__(2))
    ip_byte3.insert(13, ip.__getitem__(3))

    ip_frame.pack(side=RIGHT)

    Button(root, text='Open Excel sheet and trigger writing process', command=browse_files).pack(side=LEFT)
    Button(root, text='Quit', width=15, command=root.quit).pack(side=BOTTOM)

    root.mainloop()
