# coding=utf-8
####################################################
# Represents groups with its attributes.
#
# Author: Tobias Grupe
#
####################################################

class GroupSetup:

    def __init__(self, channel, name, color):
        self.channel = channel
        self.name = name
        self.color = color

    def get_channel(self):
        return self.channel

    def get_channel_console(self):
        return self.channel-1

    def get_name(self):
        return self.name

    def get_color(self):
        return self.color
