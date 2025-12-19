# coding=utf-8
####################################################
# DCA Functions
#
# Author: Tobias Grupe
#
####################################################

import time
import mido
import dliveConstants
from spreadsheet import SpreadsheetConstants


def assign_group(context, channel, value, send_channel, bus_type):
    output = context.get_output()
    is_network_communication_allowed = context.get_network_connection_allowed()
    midi_channel = context.get_app_data().get_midi_channel()

    if is_network_communication_allowed:
        SndN = (midi_channel + dliveConstants.midi_channel_offset_groups)  # Groups MGrp & StGrp

        if bus_type == "mono":
            SndCh = send_channel
        elif bus_type == "stereo":
            SndCh = 0x40 + send_channel

        prefix = [midi_channel, dliveConstants.sysex_message_set_groups_on, channel, SndN, SndCh]

        message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + prefix + [value] + dliveConstants.sysexhdrend)

        output.send(message)
        time.sleep(dliveConstants.DEFAULT_SLEEP_AFTER_MIDI_COMMAND)



def assign_group_to_channel(context, item, bus_type):

    console = context.get_app_data().get_console()

    channel = item.get_channel_console()

    if bus_type == "mono" and console == "dLive":
        amount_of_groups = SpreadsheetConstants.dlive_mono_group_max
    elif bus_type == "stereo" and console == "dLive":
        amount_of_groups = SpreadsheetConstants.dlive_stereo_group_max
    elif bus_type == "mono" and console == "Avantis":
        amount_of_groups = SpreadsheetConstants.avantis_mono_group_max
    elif bus_type == "stereo" and console == "Avantis":
        amount_of_groups = SpreadsheetConstants.avantis_stereo_group_max

    if bus_type == "mono":
        group_array = item.get_mono_group_config().get_mono_group_array()
    elif bus_type == "stereo":
        group_array = item.get_stereo_group_config().get_stereo_group_array()

    for group_index in range(0, amount_of_groups):

        group_array_item_lower = group_array.__getitem__(group_index).lower()

        if group_array_item_lower == SpreadsheetConstants.spreadsheet_bypass_sign or group_array_item_lower == SpreadsheetConstants.spreadsheet_bypass_string:
            continue
        elif group_array.__getitem__(group_index).lower() == "x":
            assign_group(context, channel, dliveConstants.assign_on, group_index, bus_type)
        else:
            assign_group(context, channel, dliveConstants.assign_off, group_index, bus_type)

