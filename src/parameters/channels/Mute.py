# coding=utf-8
####################################################
# Mute Functions
#
# Author: Tobias Grupe
#
####################################################

import time
import mido
import dliveConstants
from spreadsheet import SpreadsheetConstants


def mute_on_channel(context, item):
    midi_channel_tmp = context.get_app_data().get_midi_channel()
    logger = context.get_logger()
    output = context.get_output()
    is_network_communication_allowed = context.get_network_connection_allowed()

    lower_mute_on = item.get_mute().lower()
    channel = item.get_channel_console()

    if lower_mute_on == SpreadsheetConstants.spreadsheet_bypass_sign or lower_mute_on == SpreadsheetConstants.spreadsheet_bypass_string:
        logger.info("Don´t care flag found, skipping channel")
        return
    elif lower_mute_on == "yes":
        message_on = mido.Message('note_on', channel=midi_channel_tmp, note=channel, velocity=dliveConstants.mute_on)
        message_off = mido.Message('note_on', channel=midi_channel_tmp, note=channel, velocity=dliveConstants.note_off)
    elif lower_mute_on == "no":
        message_on = mido.Message('note_on', channel=midi_channel_tmp, note=channel, velocity=dliveConstants.mute_off)
        message_off = mido.Message('note_on', channel=midi_channel_tmp, note=channel, velocity=dliveConstants.note_off)
    elif lower_mute_on == 'nan':
        logger.info("Empty cell found, treating as don´t care, skipping channel")
        return
    else:
        logger.warning("Unexpected input value found")
        return

    if is_network_communication_allowed:
        output.send(message_on)
        output.send(message_off)
        time.sleep(dliveConstants.DEFAULT_SLEEP_AFTER_MIDI_COMMAND)
