import time

import mido

import dliveConstants
from spreadsheet import SpreadsheetConstants


def gain_socket(context, item, socket_type):
    logger = context.get_logger()
    output = context.get_output()
    console = context.get_app_data().get_console()
    midi_channel = context.get_app_data().get_midi_channel()

    is_network_communication_allowed = context.get_network_connection_allowed()

    socket_tmp = item.get_socket_number()
    socket_dlive_tmp = item.get_socket_number_dlive()

    if socket_type == "local":
        if socket_tmp <= dliveConstants.LOCAL_DLIVE_SOCKET_COUNT_MAX and console == dliveConstants.console_drop_down_dlive:
            gain_sheet_lower = str(item.get_local_gain())
            socket = socket_dlive_tmp
        elif socket_tmp <= dliveConstants.LOCAL_AVANTIS_SOCKET_COUNT_MAX and console == dliveConstants.console_drop_down_avantis:
            gain_sheet_lower = str(item.get_local_gain())
            socket = socket_dlive_tmp
        else:
            return

    elif socket_type == "DX1":
        if socket_tmp <= dliveConstants.DX1_SOCKET_COUNT_MAX:
            gain_sheet_lower = str(item.get_dx1_gain())
            socket = socket_dlive_tmp + 64
        else:
            return

    elif socket_type == "DX3":
        if socket_tmp <= dliveConstants.DX3_SOCKET_COUNT_MAX:
            gain_sheet_lower = str(item.get_dx3_gain())
            socket = socket_dlive_tmp + 96
        else:
            return

    elif socket_type == "Slink":
        if socket_tmp <= dliveConstants.SLINK_SOCKET_COUNT_MAX:
            gain_sheet_lower = str(item.get_slink_gain())
            socket = socket_dlive_tmp + 64
        else:
            return

    # TODO Currently required because value of socket cannot be higher than 127
    if socket > 127:
        return

    if gain_sheet_lower == 'nan' or gain_sheet_lower == 'byp':
        logger.info("empty cell found, treating as don´t care, skipping socket: " + str(socket))
        return

    switcher = {
        "60": dliveConstants.gain_level_plus60,
        "55": dliveConstants.gain_level_plus55,
        "50": dliveConstants.gain_level_plus50,
        "45": dliveConstants.gain_level_plus45,
        "40": dliveConstants.gain_level_plus40,
        "35": dliveConstants.gain_level_plus35,
        "30": dliveConstants.gain_level_plus30,
        "25": dliveConstants.gain_level_plus25,
        "20": dliveConstants.gain_level_plus20,
        "15": dliveConstants.gain_level_plus15,
        "10": dliveConstants.gain_level_plus10,
        "5": dliveConstants.gain_level_plus5,
        SpreadsheetConstants.spreadsheet_bypass_sign: -1
    }
    gain_level = switcher.get(gain_sheet_lower, "Invalid gain level")

    if gain_level == -1:
        logger.info("Don´t care flag found, skipping socket: " + str(socket))
        return

    if is_network_communication_allowed:
        logger.info("Set Gain Level " + str(gain_sheet_lower) + "dB/" + str(hex(gain_level)) + " to socket: " + str(
            socket_type) + ":" + str(socket))

        byte_1 = gain_level << 8
        byte_2 = socket << 1
        byte_all = byte_1 | byte_2
        byte_out = byte_all >> 1
        byte_out = byte_out - 8192

        output.send(mido.Message('pitchwheel', channel=midi_channel, pitch=byte_out))
        time.sleep(dliveConstants.DEFAULT_SLEEP_AFTER_MIDI_COMMAND)