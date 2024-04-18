class AppData:
    def __init__(self, midi_channel, console, current_ip):
        self.midi_channel = midi_channel
        self.console = console
        self.current_ip = current_ip

    def get_midi_channel(self):
        return self.midi_channel

    def set_midi_channel(self, midi_channel):
        self.midi_channel = midi_channel

    def get_console(self):
        return self.console

    def set_console(self, console):
        self.console = console

    def get_current_ip(self):
        return self.current_ip

    def set_current_ip(self, current_ip):
        self.current_ip = current_ip





