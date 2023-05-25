# coding=utf-8
####################################################
# Represents the complete input sheet.
#
# Author: Tobias Grupe
#
####################################################
class Sheet:
    def __init__(self):
        self.channel_model = None
        self.socket_model = None
        self.group_model = None
        self.misc_model = None

    def get_channel_model(self):
        return self.channel_model

    def get_socket_model(self):
        return self.socket_model

    def get_group_model(self):
        return self.group_model

    def get_misc_model(self):
        return self.misc_model

    def set_channel_model(self, channel_model):
        self.channel_model = channel_model

    def set_socket_model(self, socket_model):
        self.socket_model = socket_model

    def set_group_model(self, group_model):
        self.group_model = group_model

    def set_misc_model(self, misc_model):
        self.misc_model = misc_model


