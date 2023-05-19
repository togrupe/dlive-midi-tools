class MuteGroupListEntry:
    def __init__(self, channel, mg_config):
        self.channel = channel
        self.mg_config = mg_config

    def get_channel(self):
        return self.channel

    def get_channel_dlive(self):
        return self.get_channel() - 1

    def get_mg_config(self):
        return self.mg_config

