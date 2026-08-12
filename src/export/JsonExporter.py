# coding=utf-8
####################################################
# JSON export for channel lists (Dante Config Editor
# channel labels format)
#
# Author: Tobias Grupe
####################################################

import json

import Toolinfo

SCHEMA_FORMAT = "dante-config-editor-channel-labels"
SCHEMA_VERSION = 1


def export_json(filepath, channel_data, device_name, direction="tx"):
    """Generate a Dante Config Editor compatible channel-labels JSON file.

    channel_data: list of dicts with keys:
        dliveChannel (int), name (str)
    """
    channels = []
    for d in channel_data:
        channel_number = d["dliveChannel"]
        channels.append({
            "channelNumber": channel_number,
            "label": str(d.get("name", "")),
            "danteId": channel_number,
        })

    data = {
        "format": SCHEMA_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "sourceApplication": Toolinfo.tool_name,
        "sourceVersion": Toolinfo.version,
        "sets": [
            {
                "deviceName": device_name,
                "direction": direction,
                "channels": channels,
            }
        ],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
