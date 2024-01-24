# coding=utf-8
####################################################
# Color Functions
#
# Author: Tobias Grupe
#
####################################################

import time
import mido
import dliveConstants
from spreadsheet import SpreadsheetConstants


def color_channel(context, item, midi_channel_offset, channel_offset):
    log = context.get_logger()
    output = context.get_output()
    is_network_communication_allowed = context.get_network_connection_allowed()
    midi_channel = context.get_app_data().get_midi_channel()

    lower_color = item.get_color().lower()

    if lower_color == SpreadsheetConstants.spreadsheet_bypass_sign or lower_color == SpreadsheetConstants.spreadsheet_bypass_string:
        log.info("Don´t care flag found, skipping channel color: " + str(item.get_channel()))
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
        log.info("Empty cell found, treating as don´t care, skipping channel")
        return
    else:
        log.warning("Given color: " + lower_color + " is not supported, setting default color: black")
        colour = dliveConstants.lcd_color_black

    payload_array = [midi_channel + midi_channel_offset, dliveConstants.sysex_message_set_channel_colour,
                     channel_offset + item.get_channel_console(),
                     colour]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
        time.sleep(dliveConstants.DEFAULT_SLEEP_AFTER_MIDI_COMMAND)


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


def get_color_channel(context, start_channel, end_channel):
    output = context.get_output()
    is_network_communication_allowed = context.get_network_connection_allowed()
    midi_channel = context.get_app_data().get_midi_channel()

    color = []

    for channel in range(start_channel, end_channel):
        prefix = [midi_channel, dliveConstants.sysex_message_get_channel_colour, channel]

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

            time.sleep(dliveConstants.DEFAULT_SLEEP_AFTER_MIDI_COMMAND)


    return color
