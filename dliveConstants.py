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
sysex_message_set_channel_colour = 0x06
sysex_message_set_socket_preamp_48V = 0x0C
sysex_message_set_socket_preamp_pad = 0x09

# NRPN messages
nrpn_parameter_id_hpf_on = 0x31
nrpn_parameter_id_hpf_frequency = 0x30
nrpn_parameter_id_fader_level = 0x17
nrpn_parameter_id_dca_assign = 0x40

# Note
note_off = 0x00

# DCA
dca_on_base_address = 0x40
dca_off_base_address = 0x00

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

# SysEx header definitions
sysexhdrstart = [0xF0, 0x00, 0x00, 0x1A, 0x50, 0x10, sysex_header_major_version, sysex_header_minor_version]
sysexhdrend = [0xF7]

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

# The Reaper color mappings
reaper_color_black = 16777216
reaper_color_red = 17236731
reaper_color_green = 23527270
reaper_color_yellow = 23527423
reaper_color_blue = 33521679
reaper_color_purple = 30371836
reaper_color_ltblue = 33541222
reaper_color_white = 33554431

# if no dlive system is available, you can simulate the outgoing midi calls, by setting the next parameter to False
allow_network_communication = True

# dlive Mixrack ip and port for midi/tcp
ip = '192.168.1.70'
port = 51325
