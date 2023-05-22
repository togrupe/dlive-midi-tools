####################################################
# dlive constants configuration file
#
# Author: Tobias Grupe
#
####################################################

# The dlive color mappings
lcd_color_black = 0x00
lcd_color_red = 0x01
lcd_color_green = 0x02
lcd_color_yellow = 0x03
lcd_color_blue = 0x04
lcd_color_purple = 0x05
lcd_color_ltblue = 0x06
lcd_color_white = 0x07

# The phantom power values
phantom_power_off = 0x00
phantom_power_on = 0x7F

# The HPF on values
hpf_off = 0x00
hpf_on = 0x7F

# The PAD  values
pad_off = 0x00
pad_on = 0x7F

# SysEx Header Major Version
sysex_header_major_version = 0x01
sysex_header_minor_version = 0x00

# SysEx messages
sysex_message_set_channel_name = 0x03
sysex_message_get_channel_name = 0x01
sysex_message_set_channel_colour = 0x06
sysex_message_get_channel_colour = 0x04
sysex_message_set_socket_preamp_48V = 0x0C
sysex_message_set_socket_preamp_pad = 0x09

# NRPN messages
nrpn_parameter_id_hpf_on = 0x31
nrpn_parameter_id_hpf_frequency = 0x30
nrpn_parameter_id_fader_level = 0x17
nrpn_parameter_id_dca_assign = 0x40
nrpn_parameter_id_mg_assign = 0x40

# Note
note_off = 0x00

# DCA
dca_on_base_address = 0x40
dca_off_base_address = 0x00

# Mute Groups
mg_on_base_address = 0x58
mg_off_base_address = 0x18

# Mute
mute_on = 0x7F
mute_off = 0x3F

# Fader levels
fader_level_plus10 = 0x7F
fader_level_plus5 = 0x74
fader_level_zero = 0x6B
fader_level_minus5 = 0x61
fader_level_minus10 = 0x57
fader_level_minus15 = 0x4D
fader_level_minus20 = 0x43
fader_level_minus25 = 0x39
fader_level_minus30 = 0x2F
fader_level_minus35 = 0x25
fader_level_minus40 = 0x1B
fader_level_minus45 = 0x11
fader_level_minus_inf = 0x00

# Gain levels
gain_level_plus60 = 0x7F
gain_level_plus55 = 0x73
gain_level_plus50 = 0x67
gain_level_plus45 = 0x5C
gain_level_plus40 = 0x50
gain_level_plus35 = 0x45
gain_level_plus30 = 0x3A
gain_level_plus25 = 0x2E
gain_level_plus20 = 0x22
gain_level_plus15 = 0x17
gain_level_plus10 = 0x0C
gain_level_plus5 = 0x0

# SysEx header definitions
sysexhdrstart = [0xF0, 0x00, 0x00, 0x1A, 0x50, 0x10, sysex_header_major_version, sysex_header_minor_version]
sysexhdrend = [0xF7]

# The max socket amount for each type
LOCAL_DLIVE_SOCKET_COUNT_MAX = 64
LOCAL_AVANTIS_SOCKET_COUNT_MAX = 12
DX1_SOCKET_COUNT_MAX = 32
DX3_SOCKET_COUNT_MAX = 32
SLINK_SOCKET_COUNT_MAX = 128

# Strings Midi Channel Selector
midi_channel_drop_down_string_1 = "1 to 5"
midi_channel_drop_down_string_2 = "2 to 6"
midi_channel_drop_down_string_3 = "3 to 7"
midi_channel_drop_down_string_4 = "4 to 8"
midi_channel_drop_down_string_5 = "5 to 9"
midi_channel_drop_down_string_6 = "6 to 10"
midi_channel_drop_down_string_7 = "7 to 11"
midi_channel_drop_down_string_8 = "8 to 12"
midi_channel_drop_down_string_9 = "9 to 13"
midi_channel_drop_down_string_10 = "10 to 14"
midi_channel_drop_down_string_11 = "11 to 15"
midi_channel_drop_down_string_12 = "12 to 16"

midi_channel_drop_down_string_default = midi_channel_drop_down_string_12

# Strings Console Selector
console_drop_down_avantis = "Avantis"
console_drop_down_dlive = "dLive"

console_drop_down_default = console_drop_down_dlive

# if no dlive system is available, you can simulate the outgoing midi calls, by setting the next parameter to False
allow_network_communication = True

# Trim after 6 or 8 Charactors
trim_after_x_charactors = 8

# dlive Mixrack ip and port for midi/tcp. Please use 127.0.0.1 for dLive Director.
ip = '192.168.1.70'
port = 51325
