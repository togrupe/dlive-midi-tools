class ChannelListEntry:
    def __init__(self, channel, name, color, phantom):
        self.channel = channel
        self.name = name
        self.color = color
        self.phantom = phantom

    def get_channel(self):
        return self.channel

    def get_name(self):
        return self.name

    def get_color(self):
        return self.color

    def get_phantom(self):
        return self.phantom
