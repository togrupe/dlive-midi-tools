# coding=utf-8
####################################################
# Mixing Station REST API constants
#
# Author: Tobias Grupe
####################################################

import dliveConstants

MS_DEFAULT_PORT = 9000

# REST parameter path templates (channel index is 0-based)
PATH_CHANNEL_NAME = "ch.{}.cfg.name"
PATH_CHANNEL_COLOR = "ch.{}.cfg.color"
PATH_CHANNEL_FADER = "ch.{}.mix.lvl"
PATH_CHANNEL_MUTE = "ch.{}.mix.on"

# --------------------------------------------------------------------------
# Per-console color maps
# Forward maps:  spreadsheet color string  →  Mixing Station integer
# Reverse maps:  Mixing Station integer    →  spreadsheet color string
# --------------------------------------------------------------------------

# SQ:  0:Black 1:Red 2:Green 3:Blue 4:Cyan 5:Yellow 6:Magenta 7:White
_CM_SQ = {
    "black": 0, "red": 1, "green": 2, "blue": 3,
    "light blue": 4, "yellow": 5, "purple": 6, "white": 7,
}
_RM_SQ = {
    0: "black", 1: "red", 2: "green", 3: "blue",
    4: "light blue", 5: "yellow", 6: "purple", 7: "white",
}

# DM7: 0:Purple 1:Magenta 2:Red 3:Orange 4:Yellow 5:Blue 6:Cyan 7:Green 9:LightGreen 10:White 11:Black
_CM_DM7 = {
    "black": 11, "red": 2, "green": 7, "blue": 5,
    "light blue": 6, "yellow": 4, "purple": 0, "white": 10,
}
_RM_DM7 = {
    0: "purple", 1: "purple", 2: "red", 3: "yellow",
    4: "yellow", 5: "blue", 6: "light blue", 7: "green",
    9: "green", 10: "white", 11: "black",
}

# Wing: 0-2:Blue 3:Cyan 4:Green 5-6:Yellow 7:Brown 8-9:Red 10:Pink
#       11:Purple 12:Orange 13:Blue 14:Orange 15:Teal 16:Gray 17:White
_CM_WING = {
    "black": 16, "red": 8, "green": 4, "blue": 0,
    "light blue": 3, "yellow": 5, "purple": 11, "white": 17,
}
_RM_WING = {
    0: "blue",   1: "blue",   2: "blue",       3: "light blue",
    4: "green",  5: "yellow", 6: "yellow",      7: "yellow",
    8: "red",    9: "red",   10: "red",         11: "purple",
    12: "yellow", 13: "blue", 14: "yellow",     15: "light blue",
    16: "black", 17: "white",
}

# M32: 0:Black 1:Red 2:Green 3:Yellow 4:Blue 5:Magenta 6:Cyan 7:White
#      8-15: inverted variants of 0-7
_CM_M32 = {
    "black": 0, "red": 1, "green": 2, "blue": 4,
    "light blue": 6, "yellow": 3, "purple": 5, "white": 7,
}
_RM_M32 = {
    0: "black",  1: "red",    2: "green",       3: "yellow",
    4: "blue",   5: "purple", 6: "light blue",  7: "white",
    8: "black",  9: "red",   10: "green",      11: "yellow",
    12: "blue", 13: "purple", 14: "light blue", 15: "white",
}

# QU16: 0:Black 1:Red 2:Green 3:Yellow 4:Blue 5:Magenta 6:Cyan 7:White
#       8-15: inverted variants  16:Gray  17:Orange  18:Purple
_CM_QU16 = {
    "black": 0, "red": 1, "green": 2, "blue": 4,
    "light blue": 6, "yellow": 3, "purple": 18, "white": 7,
}
_RM_QU16 = {
    0: "black",  1: "red",    2: "green",       3: "yellow",
    4: "blue",   5: "purple", 6: "light blue",  7: "white",
    8: "black",  9: "red",   10: "green",      11: "yellow",
    12: "blue", 13: "purple", 14: "light blue", 15: "white",
    16: "black", 17: "yellow", 18: "purple",
}

CONSOLE_COLOR_MAPS = {
    dliveConstants.console_drop_down_sq_mixing_station:   (_CM_SQ,   _RM_SQ),
    dliveConstants.console_drop_down_dm7_mixing_station:  (_CM_DM7,  _RM_DM7),
    dliveConstants.console_drop_down_wing_mixing_station: (_CM_WING, _RM_WING),
    dliveConstants.console_drop_down_m32_mixing_station:  (_CM_M32,  _RM_M32),
    dliveConstants.console_drop_down_qu16_mixing_station: (_CM_QU16, _RM_QU16),
}


def get_color_maps(console):
    """Return (forward_map, reverse_map) for the given console; defaults to SQ."""
    return CONSOLE_COLOR_MAPS.get(console, (_CM_SQ, _RM_SQ))


# Spreadsheet fader dB string → float dB value for MS REST API
FADER_DB_MAP = {
    "10":  10.0,
    "5":    5.0,
    "0":    0.0,
    "-5":  -5.0,
    "-10": -10.0,
    "-15": -15.0,
    "-20": -20.0,
    "-25": -25.0,
    "-30": -30.0,
    "-35": -35.0,
    "-40": -40.0,
    "-45": -45.0,
    "-99": -90.0,
}
