# coding=utf-8
####################################################
# Faderlevel Functions
#
# Author: Tobias Grupe
#
####################################################

import time
import mido
import dliveConstants
from tkinter.messagebox import showerror
from spreadsheet import SpreadsheetConstants


def fader_level_channel(context, item):
    output = context.get_output()
    logger = context.get_logger()

    lower_fader_level = str(item.get_fader_level())

    if lower_fader_level == 'nan':
        return

    switcher = {
        "10": dliveConstants.fader_level_plus10,
        "5": dliveConstants.fader_level_plus5,
        "0": dliveConstants.fader_level_zero,
        "-5": dliveConstants.fader_level_minus5,
        "-10": dliveConstants.fader_level_minus10,
        "-15": dliveConstants.fader_level_minus15,
        "-20": dliveConstants.fader_level_minus20,
        "-25": dliveConstants.fader_level_minus25,
        "-30": dliveConstants.fader_level_minus30,
        "-35": dliveConstants.fader_level_minus35,
        "-40": dliveConstants.fader_level_minus40,
        "-45": dliveConstants.fader_level_minus45,
        "-99": dliveConstants.fader_level_minus_inf,
        SpreadsheetConstants.spreadsheet_bypass_sign: -1,
        SpreadsheetConstants.spreadsheet_bypass_string: -1
    }
    fader_level = switcher.get(lower_fader_level, -2)

    if fader_level == -1:
        logger.info("Don´t care flag found, skipping faderlevel level for channel: " + str(item.get_channel()))
        return

    if fader_level == -2:
        errormsg = "Invalid faderlevel level: " + lower_fader_level + " at channel: " + \
                   str(item.get_channel()) + ". Please use the dropdown values. Channel will be skipped"
        logger.info(errormsg)
        showerror(message=errormsg)
        return

    logger.info("Set Fader to: " + str(lower_fader_level) + " at Channel: " + str(item.get_channel()))

    if context.get_network_connection_allowed():
        midi_channel = context.get_app_data().get_midi_channel()
        output.send(
            mido.Message('control_change', channel=midi_channel, control=0x63, value=item.get_channel_console()))
        output.send(mido.Message('control_change', channel=midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_fader_level))
        output.send(mido.Message('control_change', channel=midi_channel, control=0x6, value=int(fader_level)))
        time.sleep(dliveConstants.DEFAULT_SLEEP_AFTER_MIDI_COMMAND)
