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


def assign_dca(context, channel, dca_value):
    output = context.get_output()
    is_network_communication_allowed = context.get_network_connection_allowed()
    midi_channel = context.get_app_data().get_midi_channel()

    if is_network_communication_allowed:
        output.send(mido.Message('control_change', channel=midi_channel, control=0x63, value=channel))
        output.send(mido.Message('control_change', channel=midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_dca_assign))
        output.send(mido.Message('control_change', channel=midi_channel, control=0x6, value=dca_value))
        time.sleep(dliveConstants.DEFAULT_SLEEP_GROUPS_AFTER_MIDI_COMMAND)


def dca_channel(context, item):
    console = context.get_app_data().get_console()

    channel = item.get_channel_console()

    for dca_index in range(0, 24):

        if console == dliveConstants.console_drop_down_avantis and dca_index > 15:
            return

        dca_config = item.get_dca_config()
        dca_array = dca_config.get_dca_array()

        dca_array_item_lower = dca_array.__getitem__(dca_index).lower()

        if dca_array_item_lower == SpreadsheetConstants.spreadsheet_bypass_sign or dca_array_item_lower == SpreadsheetConstants.spreadsheet_bypass_string:
            continue
        elif dca_array.__getitem__(dca_index).lower() == "x":
            assign_dca(context, channel, dliveConstants.dca_on_base_address + dca_index)
        else:
            assign_dca(context, channel, dliveConstants.dca_off_base_address + dca_index)
