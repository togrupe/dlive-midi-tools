class DcaListEntry:
    def __init__(self, channel, dca_config):
        self.channel = channel
        self.dca_config = dca_config

    def get_channel(self):
        return self.channel

    def get_channel_dlive(self):
        return self.get_channel() - 1

    def get_dca_config(self):
        return self.dca_config
