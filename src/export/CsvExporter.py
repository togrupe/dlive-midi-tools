# coding=utf-8
####################################################
# CSV export for channel lists (Dante Config Editor
# channel labels format)
#
# Author: Tobias Grupe
####################################################

import csv

import Toolinfo

SCHEMA_VERSION = 1

FIELDNAMES = [
    "format_version",
    "source_app",
    "source_version",
    "device",
    "direction",
    "channel",
    "dante_id",
    "label",
]


def export_csv(filepath, channel_data, device_name, direction="tx"):
    """Generate a Dante Config Editor compatible channel-labels CSV file.

    channel_data: list of dicts with keys:
        dliveChannel (int), name (str)
    """
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for d in channel_data:
            channel_number = d["dliveChannel"]
            writer.writerow({
                "format_version": SCHEMA_VERSION,
                "source_app": Toolinfo.tool_name,
                "source_version": Toolinfo.version,
                "device": device_name,
                "direction": direction,
                "channel": channel_number,
                "dante_id": channel_number,
                "label": str(d.get("name", "")),
            })
