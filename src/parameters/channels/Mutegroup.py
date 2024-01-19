# coding=utf-8
####################################################
# Mutegroups Functions
#
# Author: Tobias Grupe
#
####################################################

import time
import mido
import dliveConstants
from spreadsheet import SpreadsheetConstants


def assign_mg(context, channel, mg_value):
    output = context.get_output()
    midi_channel = context.get_app_data().get_midi_channel()
    is_network_communication_allowed = context.get_network_connection_allowed()

    if is_network_communication_allowed:
        output.send(mido.Message('control_change', channel=midi_channel, control=0x63, value=channel))
        output.send(mido.Message('control_change', channel=midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_mg_assign))
        output.send(mido.Message('control_change', channel=midi_channel, control=0x6, value=mg_value))
        time.sleep(dliveConstants.DEFAULT_SLEEP_GROUPS_AFTER_MIDI_COMMAND)


def mg_channel(context, item):

    channel = item.get_channel_console()

    for mg_index in range(0, 8):

        mg_config = item.get_mg_config()
        mg_array = mg_config.get_mg_array()

        mg_array_item_lower = mg_array.__getitem__(mg_index).lower()
        if mg_array_item_lower == SpreadsheetConstants.spreadsheet_bypass_sign or mg_array_item_lower == SpreadsheetConstants.spreadsheet_bypass_string:
            continue
        elif mg_array_item_lower == "x":
            assign_mg(context, channel, dliveConstants.mg_on_base_address + mg_index)
        else:
            assign_mg(context, channel, dliveConstants.mg_off_base_address + mg_index)