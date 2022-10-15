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

sysexhdrstart = [0xF0, 0x00, 0x00, 0x1A, 0x50, 0x10, 0x01, 0x00]
sysexhdrend = [0xF7]

# mixrack ip and port for midi/tcp
ip = '192.168.1.70'
port = 51325
