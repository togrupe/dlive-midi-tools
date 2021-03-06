# coding=utf-8
import re
import time
from tkinter import filedialog, Button, Tk

import mido
import pandas as pd
from mido.sockets import connect

import dliveConstants


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
    elif color == 'magenta':
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


def read_document(filename):
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

    print("Open connection to dlive...")
    output = connect(dliveConstants.ip, dliveConstants.port)
    print("Connection successful.")
    
    time.sleep(1)

    print("Start Processing...")
    trigger_channel_renaming("Naming the channels...", output, names)
    trigger_coloring("Coloring the channels...", output, colors)
    trigger_phantom_power("Set phantom power to the channels...", output, phantoms)
    print("Processing done")

    output.close()


if __name__ == '__main__':
    root = Tk()

    root.title('Allen & Heath dLive Channel List Manager')

    root.geometry('480x60')

    root.config(bg='grey')


    def browse_files():
        file = filedialog.askopenfilename()

        read_document(file)


    button_1 = Button(root, text='Open Excel Sheet and Trigger Writing Process', command=browse_files)

    button_1.place(x=100, y=0)

    root.resizable(False, False)

    root.mainloop()
