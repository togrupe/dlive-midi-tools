# coding=utf-8
####################################################
# High Pass Filter Functions
#
# Author: Tobias Grupe
#
####################################################

import time
import mido
import numpy
import dliveConstants
from tkinter.messagebox import showerror
from spreadsheet import SpreadsheetConstants


def hpf_on_channel(context, item):
    log = context.get_logger()
    output = context.get_output()
    midi_channel = context.get_app_data().get_midi_channel()
    is_network_communication_allowed = context.get_network_connection_allowed()

    lower_hpf_on = str(item.get_hpf_on()).lower()

    if lower_hpf_on == SpreadsheetConstants.spreadsheet_bypass_sign or lower_hpf_on == SpreadsheetConstants.spreadsheet_bypass_string:
        log.info("Don´t care flag found, skipping channel")
        return
    elif lower_hpf_on == "yes":
        res = dliveConstants.hpf_on
    elif lower_hpf_on == "no":
        res = dliveConstants.hpf_off
    elif lower_hpf_on == 'nan':
        log.info("Empty cell found, treating as don´t care, skipping channel")
        return
    else:
        log.warning("Unexpected input value found")
        return

    if is_network_communication_allowed:
        output.send(
            mido.Message('control_change', channel=midi_channel, control=0x63, value=item.get_channel_console()))
        output.send(mido.Message('control_change', channel=midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_hpf_on))
        output.send(mido.Message('control_change', channel=midi_channel, control=0x6, value=res))
        time.sleep(dliveConstants.DEFAULT_SLEEP_AFTER_MIDI_COMMAND)


def calculate_vv(hpf_value):
    return int(27.58 * numpy.log(float(hpf_value)) - 82.622)


def clamp(value, lower_limit, upper_limit):
    return max(lower_limit, min(value, upper_limit))


def hpf_value_channel(context, item):
    logger = context.get_logger()
    output = context.get_output()
    midi_channel = context.get_app_data().get_midi_channel()
    is_network_communication_allowed = context.get_network_connection_allowed()

    hpf_value = item.get_hpf_value()
    if hpf_value == 'nan' or hpf_value == SpreadsheetConstants.spreadsheet_bypass_sign or hpf_value == SpreadsheetConstants.spreadsheet_bypass_string:
        logger.info("Don´t care flag found, skipping channel")
        return
    if int(hpf_value) < dliveConstants.hpf_min_frequency or int(hpf_value) > dliveConstants.hpf_max_frequency:
        showerror(message="Highpass filter value of CH: " + str(item.get_channel()) +
                          " only allows values between " + str(dliveConstants.hpf_min_frequency) + " and "
                          + str(dliveConstants.hpf_max_frequency) + " Hz. Given value: " + hpf_value +
                          " has been clipped to the lower or upper limit.")

    value_freq = calculate_vv(clamp(int(hpf_value), 20, 2000))

    if is_network_communication_allowed:
        output.send(
            mido.Message('control_change', channel=midi_channel, control=0x63, value=item.get_channel_console()))
        output.send(mido.Message('control_change', channel=midi_channel, control=0x62,
                                 value=dliveConstants.nrpn_parameter_id_hpf_frequency))
        output.send(mido.Message('control_change', channel=midi_channel, control=0x6, value=value_freq))
        time.sleep(dliveConstants.DEFAULT_SLEEP_AFTER_MIDI_COMMAND)
