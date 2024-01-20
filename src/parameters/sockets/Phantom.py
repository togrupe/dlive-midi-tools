import time
import mido
import dliveConstants
from spreadsheet import SpreadsheetConstants


def phantom_socket(context, item, socket_type):
    output = context.get_output()
    console = context.get_app_data().get_console()
    midi_channel = context.get_app_data().get_midi_channel()
    is_network_communication_allowed = context.get_network_connection_allowed()
    logger = context.get_logger()

    socket_tmp = item.get_socket_number()
    socket_dlive_tmp = item.get_socket_number_dlive()

    if socket_type == "local":
        if socket_tmp <= dliveConstants.LOCAL_DLIVE_SOCKET_COUNT_MAX and console == dliveConstants.console_drop_down_dlive:
            lower_phantom = str(item.get_local_phantom()).lower()
            socket = socket_dlive_tmp
        elif socket_tmp <= dliveConstants.LOCAL_AVANTIS_SOCKET_COUNT_MAX and console == dliveConstants.console_drop_down_avantis:
            lower_phantom = str(item.get_local_phantom()).lower()
            socket = socket_dlive_tmp
        else:
            return

    elif socket_type == "DX1":
        if socket_tmp <= dliveConstants.DX1_SOCKET_COUNT_MAX:
            lower_phantom = str(item.get_dx1_phantom()).lower()
            socket = socket_dlive_tmp + 64
        else:
            return

    elif socket_type == "DX3":
        if socket_tmp <= dliveConstants.DX3_SOCKET_COUNT_MAX:
            lower_phantom = str(item.get_dx3_phantom()).lower()
            socket = socket_dlive_tmp + 96
        else:
            return

    elif socket_type == "Slink":
        if socket_tmp <= dliveConstants.SLINK_SOCKET_COUNT_MAX:
            lower_phantom = str(item.get_slink_phantom()).lower()
            socket = socket_dlive_tmp + 64
        else:
            return

    if lower_phantom == SpreadsheetConstants.spreadsheet_bypass_sign or lower_phantom == SpreadsheetConstants.spreadsheet_bypass_string:
        logger.info("Don´t care flag found, skipping socket: " + str(socket))
        return
    elif lower_phantom == "yes":
        res = dliveConstants.phantom_power_on
    elif lower_phantom == "no":
        res = dliveConstants.phantom_power_off
    else:
        logger.info("empty cell found, treating as don´t care, skipping socket: " + str(socket))
        return

    # TODO Currently required because value of socket cannot be higher than 127
    if socket > 127:
        return

    payload_array = [midi_channel, dliveConstants.sysex_message_set_socket_preamp_48V, socket,
                     res]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload_array + dliveConstants.sysexhdrend)
    if is_network_communication_allowed:
        output.send(message)
        time.sleep(dliveConstants.DEFAULT_SLEEP_AFTER_MIDI_COMMAND)
