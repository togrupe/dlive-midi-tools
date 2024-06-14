# coding=utf-8
####################################################
# Director CSV Creator
#
# Author: Tobias Grupe
#
####################################################

import csv
import os

from directorcsv import CsvConstants
from spreadsheet import SpreadsheetConstants


def convert_to_csv_color(color):
    if color == SpreadsheetConstants.spreadsheet_color_blue:
        return CsvConstants.csv_color_blue
    elif color == SpreadsheetConstants.spreadsheet_color_red:
        return CsvConstants.csv_color_red
    elif color == SpreadsheetConstants.spreadsheet_color_yellow:
        return CsvConstants.csv_color_yellow
    elif color == SpreadsheetConstants.spreadsheet_color_red:
        return CsvConstants.csv_color_red
    elif color == SpreadsheetConstants.spreadsheet_color_green:
        return CsvConstants.csv_color_green
    elif color == SpreadsheetConstants.spreadsheet_color_light_blue:
        return CsvConstants.csv_color_cyan
    elif color == SpreadsheetConstants.spreadsheet_color_purple:
        return CsvConstants.csv_color_magenta
    elif color == SpreadsheetConstants.spreadsheet_color_white:
        return CsvConstants.csv_color_white
    elif color == SpreadsheetConstants.spreadsheet_color_black:
        return CsvConstants.csv_color_off
    else:
        return CsvConstants.csv_color_off


def convert_to_csv_pad(pad):
    if pad == "-" or pad == 'nan':
        return ''
    elif pad == "yes":
        return CsvConstants.csv_pad_on
    else:
        return CsvConstants.csv_pad_off


def convert_to_csv_phantom(phantom):
    if phantom == "-" or phantom == 'nan':
        return ''
    elif phantom == "yes":
        return CsvConstants.csv_phantom_on
    else:
        return CsvConstants.csv_phantom_off


def convert_to_csv_gain(gain):
    if gain == "-" or gain == 'nan':
        return ''
    return int(gain)


def create(sheet, reaper_output_dir, file_prefix):
    daten = []

    daten.append(
        ["[Version]", "V1.0", '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
         '', '', '', ''])
    daten.append(
        ["[Channels]", '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
         '', '', ''])

    for item in sheet.get_channel_model():
        # Input, 1, "1", Green, MixRack, 1,, 27, Off, Off, Unassigned,, , , , , Unassigned,, , , , , Unassigned,, , , ,
        daten.append(
            ['Input', item.get_channel(), item.get_name(), convert_to_csv_color(item.get_color()),
             item.get_source(), item.get_socket(), '', convert_to_csv_gain(item.get_gain()),
             convert_to_csv_pad(item.get_pad()), convert_to_csv_phantom(item.get_phantom()),
             'Unassigned', '', '', '', '', '', 'Unassigned', '', '', '', '', '', 'Unassigned', '', '', '', '', ])

    os.makedirs(reaper_output_dir, exist_ok=True)

    filepath = os.path.join(reaper_output_dir, file_prefix + '-director.csv')

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(daten)

    print("Director CSV-file successfully created.")
