# coding=utf-8
####################################################
# Mixing Station channel parameter handlers
#
# Author: Tobias Grupe
####################################################

import logging

from spreadsheet import SpreadsheetConstants
from mixingstation import MixingStationConstants


def get_channel_data(ms_client, start_channel, end_channel, console=""):
    _, reverse_map = MixingStationConstants.get_color_maps(console)
    data = []
    for channel in range(start_channel, end_channel):
        color_id = int(ms_client.get(MixingStationConstants.PATH_CHANNEL_COLOR.format(channel))["value"])
        color = reverse_map.get(color_id, SpreadsheetConstants.spreadsheet_color_black)

        name = ms_client.get(MixingStationConstants.PATH_CHANNEL_NAME.format(channel))["value"]

        logging.info(f"Mixing Station ch {channel + 1}: name={name}, color={color}")
        data.append({
            "dliveChannel": channel + 1,
            "technicalChannel": channel,
            "color": color,
            "name": name,
        })
    return data


def handle_ms_channels(log, ms_client, channel_list_entries, action, console=""):
    for item in channel_list_entries:
        lower_enabled = str(item.get_enabled()).lower()
        if lower_enabled in ('nan', 'no'):
            log.info(f"Skipping MS {action} for channel {item.get_channel()}")
            continue
        log.info(f"Processing MS {action} for channel {item.get_channel_console() + 1}")
        if action == "name":
            _write_name(ms_client, log, item)
        elif action == "color":
            _write_color(ms_client, log, item, console)
        elif action == "fader_level":
            _write_fader_level(ms_client, log, item)
        elif action == "mute":
            _write_mute(ms_client, log, item)
        else:
            log.warning(f"MS: action '{action}' is not supported, skipping")


def _write_name(ms_client, log, item):
    name = str(item.get_name())
    if name in (SpreadsheetConstants.spreadsheet_bypass_sign,
                SpreadsheetConstants.spreadsheet_bypass_string, 'nan'):
        log.info(f"Skipping MS name for channel {item.get_channel()}")
        return
    trimmed = name[:6]
    path = MixingStationConstants.PATH_CHANNEL_NAME.format(item.get_channel_console())
    ms_client.set(path, trimmed)


def _write_color(ms_client, log, item, console=""):
    color = item.get_color().lower()
    if color in (SpreadsheetConstants.spreadsheet_bypass_sign,
                 SpreadsheetConstants.spreadsheet_bypass_string, 'nan'):
        log.info(f"Skipping MS color for channel {item.get_channel()}")
        return
    color_map, _ = MixingStationConstants.get_color_maps(console)
    ms_color = color_map.get(color, 0)
    path = MixingStationConstants.PATH_CHANNEL_COLOR.format(item.get_channel_console())
    ms_client.set(path, ms_color, fmt="val")


def _write_fader_level(ms_client, log, item):
    level_str = str(item.get_fader_level())
    if level_str in (SpreadsheetConstants.spreadsheet_bypass_sign,
                     SpreadsheetConstants.spreadsheet_bypass_string, 'nan'):
        log.info(f"Skipping MS fader for channel {item.get_channel()}")
        return
    db_value = MixingStationConstants.FADER_DB_MAP.get(level_str)
    if db_value is None:
        log.warning(f"MS: unknown fader level '{level_str}' for channel {item.get_channel()}")
        return
    path = MixingStationConstants.PATH_CHANNEL_FADER.format(item.get_channel_console())
    ms_client.set(path, db_value)


def _write_mute(ms_client, log, item):
    mute_str = item.get_mute().lower()
    if mute_str in (SpreadsheetConstants.spreadsheet_bypass_sign,
                    SpreadsheetConstants.spreadsheet_bypass_string, 'nan'):
        log.info(f"Skipping MS mute for channel {item.get_channel()}")
        return
    if mute_str == "yes":
        is_on = False   # MS mix.on=true means unmuted → muted=False
    elif mute_str == "no":
        is_on = True
    else:
        log.warning(f"MS: unexpected mute value '{mute_str}' for channel {item.get_channel()}")
        return
    path = MixingStationConstants.PATH_CHANNEL_MUTE.format(item.get_channel_console())
    ms_client.set(path, is_on)
