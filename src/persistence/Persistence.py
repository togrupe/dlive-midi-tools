# coding=utf-8
####################################################
# Methods for persistence handling
#
# Author: Tobias Grupe
#
####################################################

import json
import os

import dliveConstants


def read_persisted_midi_port(context):
    logging = context.get_logger()
    filename = context.get_config_file()
    if os.path.exists(filename):
        logging.info("Try to read persisted midi-port from " + str(filename) + " file.")
        with open(filename, 'r') as file:
            data = json.load(file)
            try:
                midi_port_ret = data['midi-port']
                logging.info("Using midi-port: " + str(midi_port_ret) + " from config file: " + str(filename))
            except KeyError:
                logging.info("Use default midi-port: " +
                             dliveConstants.midi_channel_drop_down_string_default +
                             " from dliveConstants instead.")

                midi_port_ret = dliveConstants.midi_channel_drop_down_string_default
    else:
        logging.info("No config file found, using default midi-port: " +
                     dliveConstants.midi_channel_drop_down_string_default +
                     " from dliveConstants instead.")

        midi_port_ret = dliveConstants.midi_channel_drop_down_string_default

    return midi_port_ret


def read_persisted_console(context):
    log = context.get_logger()
    filename = context.get_config_file()
    if os.path.exists(filename):
        log.info("Try to read persisted console from " + str(filename) + " file.")
        with open(filename, 'r') as file:
            data = json.load(file)
            try:
                console_ret = data['console']
                log.info("Using console: " + str(console_ret) + " from config file: " + str(filename))
            except KeyError:
                log.error("No key: console found, Using default console: " +
                          dliveConstants.console_drop_down_default +
                          " from dliveConstants instead.")

                console_ret = dliveConstants.console_drop_down_default
    else:
        log.info("No config file found, using default console: " +
                 dliveConstants.console_drop_down_default +
                 " from dliveConstants instead.")

        console_ret = dliveConstants.console_drop_down_default

    return console_ret


def read_persisted_ip(context):
    log = context.get_logger()
    filename = context.get_config_file()
    if os.path.exists(filename):
        log.info("Try to read persisted ip from " + str(filename) + " file.")
        with open(filename, 'r') as file:
            data = json.load(file)
            try:
                ip_ret = data['ip']
                log.info("Using ip: " + str(ip_ret) + " from config file: " + str(filename))
            except KeyError:
                log.error("No key: ip found, using default ip: " +
                          dliveConstants.ip +
                          " from dliveConstants instead.")
                ip_ret = dliveConstants.ip
    else:
        log.info("No config file found, using default ip: "
                 + dliveConstants.ip +
                 " from dliveConstants instead")
        ip_ret = dliveConstants.ip

    return ip_ret


def migrate_config_if_needed(context):
    """Migrates config from v1 to v2 by adding appearance-mode default."""
    log = context.get_logger()
    filename = context.get_config_file()
    if not os.path.exists(filename):
        return
    with open(filename, 'r') as file:
        data = json.load(file)
    if data.get('version', 1) < 2:
        data['version'] = 2
        data.setdefault('appearance-mode', 'dark')
        with open(filename, 'w') as file:
            json.dump(data, file)
        log.info("Config migrated from v1 to v2.")


def read_persisted_appearance_mode(context):
    log = context.get_logger()
    filename = context.get_config_file()
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            try:
                return data['appearance-mode']
            except KeyError:
                pass
    log.info("No appearance-mode found in config, using default: dark")
    return "dark"


def persist_current_ui_settings(context):
    log = context.get_logger()
    filename = context.get_config_file()
    console = context.get_app_data().get_console()
    midi_channel = context.get_app_data().get_midi_channel()
    current_ip = context.get_app_data().get_current_ip()
    appearance_mode = context.get_app_data().get_appearance_mode()

    data = {
        'version': 2,
        'ip': str(current_ip),
        'console': console,
        'midi-port': midi_channel,
        'appearance-mode': appearance_mode
    }

    json_str = json.dumps(data)

    data = json.loads(json_str)
    with open(filename, 'w') as file:
        json.dump(data, file)
        log.info("Following data has be persisted: " + str(json_str) + " into file: " + str(file) + ".")
