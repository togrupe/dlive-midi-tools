# coding=utf-8
####################################################
# Represents the misc tab from the sheet.
#
# Author: Tobias Grupe
#
####################################################
class Misc:
    def __init__(self):
        self.version = None

    def get_version(self):
        return self.version

    def set_version(self, version):
        self.version = version
