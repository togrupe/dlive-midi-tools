# coding=utf-8
####################################################
# Represents an Action
#
# Author: Tobias Grupe
#
####################################################
class Action:
    def __init__(self, cb_text, sheet_tab, message, action, bus_type=None):
        self.cb_text = cb_text
        self.sheet_tab = sheet_tab
        self.message = message
        self.action = action
        self.bus_type = bus_type

    def get_cb_text(self):
        return self.cb_text

    def get_sheet_tab(self):
        return self.sheet_tab

    def get_message(self):
        return self.message

    def get_action(self):
        return self.action

    def get_bus_type(self):
        return self.bus_type
