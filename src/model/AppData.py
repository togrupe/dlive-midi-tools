class AppData:
    def __init__(self, midi_channel, console):
        self.midi_channel = midi_channel
        self.console = console

    def get_midi_channel(self):
        return self.midi_channel

    def set_midi_channel(self, midi_channel):
        self.midi_channel = midi_channel

    def get_console(self):
        return self.console

    def set_console(self, console):
        self.console = console




