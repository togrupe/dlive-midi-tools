# coding=utf-8
####################################################
# Common functions for sockets
#
# Author: Tobias Grupe
#
####################################################

import dliveConstants
from parameters.sockets.Gain import gain_socket
from parameters.sockets.Pad import pad_socket
from parameters.sockets.Phantom import phantom_socket


def handle_sockets_parameter(message, context, socket_list_entries, action):
    log = context.get_logger()
    console = context.get_app_data().get_console()

    log.info(message)

    for item in socket_list_entries:
        log.info("Processing " + action + " for socket: " + str(item.get_socket_number()))
        if action == "phantom":
            if console == dliveConstants.console_drop_down_dlive:
                phantom_socket(context, item, "local")
                phantom_socket(context, item, "DX1")
                phantom_socket(context, item, "DX3")
            elif console == dliveConstants.console_drop_down_avantis:
                phantom_socket(context, item, "local")
                phantom_socket(context, item, "Slink")
        elif action == "pad":
            if console == dliveConstants.console_drop_down_dlive:
                pad_socket(context, item, "local")
                pad_socket(context, item, "DX1")
                pad_socket(context, item, "DX3")
            elif console == dliveConstants.console_drop_down_avantis:
                pad_socket(context, item, "local")
                pad_socket(context, item, "Slink")
        elif action == "gain":
            if console == dliveConstants.console_drop_down_dlive:
                gain_socket(context, item, "local")
                gain_socket(context, item, "DX1")
                gain_socket(context, item, "DX3")
            elif console == dliveConstants.console_drop_down_avantis:
                gain_socket(context, item, "local")
                gain_socket(context, item, "Slink")