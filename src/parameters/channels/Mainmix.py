import time

import mido

import dliveConstants
from spreadsheet import SpreadsheetConstants


def assign_mainmix(context, channel, mainmix_value):
    output = context.get_output()
    midi_channel = context.get_app_data().get_midi_channel()
    is_network_communication_allowed = context.get_network_connection_allowed()

    if is_network_communication_allowed:
        output.send(mido.Message('control_change', channel=midi_channel, control=0x63, value=channel))
        output.send(mido.Message('control_change', channel=midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_mainmix_assign))
        output.send(mido.Message('control_change', channel=midi_channel, control=0x6, value=mainmix_value))
        time.sleep(dliveConstants.DEFAULT_SLEEP_GROUPS_AFTER_MIDI_COMMAND)


def assign_mainmix_channel(context, item):
    logger = context.get_logger()

    channel = item.get_channel_console()
    mainmix_value = item.get_assign_mainmix()

    if mainmix_value == 'nan' or mainmix_value == SpreadsheetConstants.spreadsheet_bypass_sign or mainmix_value == SpreadsheetConstants.spreadsheet_bypass_string:
        logger.info("Don´t care flag found, skipping channel")
        return

    if mainmix_value.lower() == "yes":
        assign_mainmix(context, channel, dliveConstants.mainmix_on)
    else:
        assign_mainmix(context, channel, dliveConstants.mainmix_off)