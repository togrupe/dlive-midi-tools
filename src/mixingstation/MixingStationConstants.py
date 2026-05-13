# coding=utf-8
####################################################
# Mixing Station REST API constants
#
# Author: Tobias Grupe
####################################################

MS_DEFAULT_PORT = 9000

# REST parameter path templates (channel index is 0-based)
PATH_CHANNEL_NAME = "ch.{}.cfg.name"
PATH_CHANNEL_COLOR = "ch.{}.cfg.color"
PATH_CHANNEL_FADER = "ch.{}.mix.lvl"
PATH_CHANNEL_MUTE = "ch.{}.mix.on"

# Spreadsheet color string → Mixing Station integer (matches dLive 1:1)
COLOR_MAP = {
    "black":   0,
    "red":     1,
    "green":   2,
    "blue":    3,
    "cyan":    4,
    "yellow":  5,
    "magenta": 6,
    "white":   7,
}

# Mixing Station color integer → spreadsheet color string (inverse of COLOR_MAP)
MS_COLOR_TO_SPREADSHEET = {
    0: "black",
    1: "red",
    2: "green",
    3: "blue",
    4: "light blue",  # Cyan
    5: "yellow",
    6: "purple",      # Magenta
    7: "white",
}

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
    "-99": -90.0,   # spreadsheet -inf → practical silence
}
