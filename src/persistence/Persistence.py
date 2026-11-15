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
from model.MixerConfig import MIXER_CONFIG_ROWS

# v1: initial, v2: appearance-mode, v3: mixer-config
CONFIG_VERSION = 3


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


def _sanitize_mixer_config_rows(rows):
    """Returns the mixer config rows in the format {"Group": [mono, stereo], ...} with
    every amount being an int >= 0 or None (not limited), or None if rows is unusable."""
    if not isinstance(rows, dict):
        return None

    def to_count(value):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            return None
        return int(value)

    sanitized = {}
    for label in MIXER_CONFIG_ROWS:
        values = rows.get(label)
        if not isinstance(values, (list, tuple)) or len(values) != 2:
            values = [None, None]
        sanitized[label] = [to_count(values[0]), to_count(values[1])]
    return sanitized


def migrate_config_if_needed(context):
    """Migrates config step by step to CONFIG_VERSION.
    v1 -> v2: adds appearance-mode default.
    v2 -> v3: adds the (per console) mixer-config section. Entries already present
    (e.g. written by a development build) are sanitized, unusable ones are dropped.
    Older tool versions ignore the additional key."""
    log = context.get_logger()
    filename = context.get_config_file()
    if not os.path.exists(filename):
        return
    with open(filename, 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            log.warning("Config file " + str(filename) + " is not valid JSON, skipping migration.")
            return
    version = data.get('version', 1)
    if version >= CONFIG_VERSION:
        return

    if version < 2:
        data.setdefault('appearance-mode', 'dark')
        log.info("Config migrated from v1 to v2.")

    if version < 3:
        mixer_configs = data.get('mixer-config')
        if not isinstance(mixer_configs, dict):
            mixer_configs = {}
        migrated = {}
        for console, rows in mixer_configs.items():
            sanitized = _sanitize_mixer_config_rows(rows)
            if sanitized is None:
                log.warning("Dropping invalid mixer config for console " + str(console) + ": " + str(rows))
                continue
            migrated[console] = sanitized
        data['mixer-config'] = migrated
        log.info("Config migrated from v2 to v3.")

    data['version'] = CONFIG_VERSION
    with open(filename, 'w') as file:
        json.dump(data, file)


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


def read_persisted_ms_port(context):
    log = context.get_logger()
    filename = context.get_config_file()
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            try:
                port = data['ms-port']
                log.info("Using ms-port: " + str(port) + " from config file.")
                return str(port)
            except KeyError:
                pass
    log.info("No ms-port in config, using default: " + str(dliveConstants.mixing_station_default_port))
    return str(dliveConstants.mixing_station_default_port)


def _read_config(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                pass
    return {}


def read_persisted_mixer_config(context, console):
    """Returns the saved mixer config rows for the given console as
    {"Group": [mono, stereo], "FX": [...], ...} or None if nothing was saved."""
    log = context.get_logger()
    mixer_configs = _read_config(context.get_config_file()).get('mixer-config')
    rows = _sanitize_mixer_config_rows(mixer_configs.get(console)) if isinstance(mixer_configs, dict) else None
    if rows is None:
        log.info("No saved mixer config found for console: " + str(console))
    else:
        log.info("Recalled mixer config for console " + str(console) + ": " + str(rows))
    return rows


def persist_mixer_config(context, console, rows):
    log = context.get_logger()
    filename = context.get_config_file()
    data = _read_config(filename)
    if not isinstance(data.get('mixer-config'), dict):
        data['mixer-config'] = {}
    data['mixer-config'][console] = rows
    data['version'] = CONFIG_VERSION
    with open(filename, 'w') as file:
        json.dump(data, file)
    log.info("Mixer config for console " + str(console) + " has been persisted: " + str(rows))


def _write_mixer_config_presets(context, console, presets):
    filename = context.get_config_file()
    data = _read_config(filename)
    if not isinstance(data.get('mixer-config-presets'), dict):
        data['mixer-config-presets'] = {}
    data['mixer-config-presets'][console] = presets
    data['version'] = CONFIG_VERSION
    with open(filename, 'w') as file:
        json.dump(data, file)


def read_mixer_config_presets(context, console):
    """Returns the named mixer config presets of the given console as
    {name: {"Group": [mono, stereo], ...}, ...}. Unusable entries are skipped."""
    all_presets = _read_config(context.get_config_file()).get('mixer-config-presets')
    presets = all_presets.get(console) if isinstance(all_presets, dict) else None
    if not isinstance(presets, dict):
        return {}
    sanitized = {}
    for name, rows in presets.items():
        rows = _sanitize_mixer_config_rows(rows)
        if isinstance(name, str) and name.strip() != "" and rows is not None:
            sanitized[name] = rows
    return sanitized


def persist_mixer_config_preset(context, console, name, rows):
    presets = read_mixer_config_presets(context, console)
    presets[name] = rows
    _write_mixer_config_presets(context, console, presets)
    context.get_logger().info("Mixer config preset \"" + name + "\" for console " + str(console) +
                              " has been persisted: " + str(rows))


def delete_mixer_config_preset(context, console, name):
    presets = read_mixer_config_presets(context, console)
    if presets.pop(name, None) is not None:
        _write_mixer_config_presets(context, console, presets)
        context.get_logger().info("Mixer config preset \"" + name + "\" for console " + str(console) +
                                  " has been deleted.")


def persist_current_ui_settings(context):
    log = context.get_logger()
    filename = context.get_config_file()
    console = context.get_app_data().get_console()
    midi_channel = context.get_app_data().get_midi_channel()
    current_ip = context.get_app_data().get_current_ip()
    appearance_mode = context.get_app_data().get_appearance_mode()
    ms_port = context.get_app_data().get_mixing_station_port()

    # Keep keys not managed here (e.g. the saved mixer configs).
    data = _read_config(filename)
    data.update({
        'version': CONFIG_VERSION,
        'ip': str(current_ip),
        'console': console,
        'midi-port': midi_channel,
        'appearance-mode': appearance_mode,
        'ms-port': ms_port,
    })

    json_str = json.dumps(data)

    data = json.loads(json_str)
    with open(filename, 'w') as file:
        json.dump(data, file)
        log.info("Following data has be persisted: " + str(json_str) + " into file: " + str(file) + ".")
