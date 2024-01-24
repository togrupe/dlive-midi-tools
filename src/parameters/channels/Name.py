# coding=utf-8
####################################################
# Name Functions
#
# Author: Tobias Grupe
#
####################################################

import re
import time
import mido
import dliveConstants
from spreadsheet import SpreadsheetConstants
from tkinter.messagebox import showerror


def name_channel(context, item, midi_channel_offset, channel_offset, bus_type):
    log = context.get_logger()
    output = context.get_output()
    midi_channel = context.get_app_data().get_midi_channel()
    is_network_communication_allowed = context.get_network_connection_allowed()

    # Trim name if length of name > dliveConstants.trim_after_x_charactors
    if len(str(item.get_name())) > dliveConstants.trim_after_x_charactors:
        trimmed_name = str(item.get_name())[0:dliveConstants.trim_after_x_charactors]
        log.info(
            "Channel name will be trimmed to 6 characters, before: " + str(item.get_name()) + " after: " + str(
                trimmed_name))
    else:
        trimmed_name = str(item.get_name())

    if trimmed_name == SpreadsheetConstants.spreadsheet_bypass_sign or trimmed_name == SpreadsheetConstants.spreadsheet_bypass_string:
        log.info("Don´t care flag found, skipping name for channel: " + str(item.get_channel()))
        return

    if trimmed_name == 'nan':
        characters = [' ', ' ', ' ', ' ', ' ', ' ', '']
    else:
        characters = re.findall('.?', trimmed_name)

    payload = []

    for character in characters:
        if len(str(character)) != 0:
            value = ord(character)
            if value > 127:
                error_msg = "One of the characters in " + str(bus_type) + ": channel " + str(
                    item.get_channel_console() + 1) + " is not supported. Characters like ä, ö, ü, é are not supported."
                log.error(error_msg)
                showerror(message=error_msg)
                output.close()
                return 1
            else:
                payload.append(value)

    prefix = [midi_channel + midi_channel_offset, dliveConstants.sysex_message_set_channel_name,
              channel_offset + item.get_channel_console()]
    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + prefix + payload + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
        time.sleep(dliveConstants.DEFAULT_SLEEP_AFTER_MIDI_COMMAND)
        return 0


def extract_name(original_array):
    name = original_array.data[10:]

    ascii_string = ''.join(chr(num) for num in name if num != 0)

    return ascii_string.rstrip()


def get_name_channel(context, data_color, start_channel, end_channel):
    output = context.get_output()
    is_network_communication_allowed = context.get_network_connection_allowed()
    midi_channel = context.get_app_data().get_midi_channel()

    for channel in range(start_channel, end_channel):
        prefix = [midi_channel, dliveConstants.sysex_message_get_channel_name,
                  channel]

        message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + prefix + dliveConstants.sysexhdrend)
        if is_network_communication_allowed:
            output.send(message)

            channel_name = extract_name(output.receive())

            for item in data_color:
                if item['technicalChannel'] == channel:
                    item['name'] = channel_name
                    break

            time.sleep(dliveConstants.DEFAULT_SLEEP_AFTER_MIDI_COMMAND)
    return data_color
