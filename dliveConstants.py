# The color mappings
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

# SysEx Header Major Version
sysex_header_major_version = 0x01
sysex_header_minor_version = 0x00

# SysEx messages
sysex_message_set_channel_name = 0x03
sysex_message_set_channel_colour = 0x06
sysex_message_set_socket_preamp_48V = 0x0C

# SysEx header definitions
sysexhdrstart = [0xF0, 0x00, 0x00, 0x1A, 0x50, 0x10, sysex_header_major_version, sysex_header_minor_version]
sysexhdrend = [0xF7]

# if no dlive system is available, you can simulate the outgoing midi calls, by setting the next parameter to False
allow_network_communication = True

# dlive Mixrack ip and port for midi/tcp
ip = '192.168.1.70'
port = 51325

# MIDI channel number - MIDI channel 1 to 12 = 0 to B
midi_channel_number = 0x00
