class ChannelListEntry:
    def __init__(self, channel, name, color, hpf_on, hpf_value, fader_level, mute, recording, record_arm):
        self.channel = channel
        self.name = name
        self.color = color
        self.hpf_on = hpf_on
        self.hpf_value = hpf_value
        self.fader_level = fader_level
        self.mute = mute
        self.recording = recording
        self.record_arm = record_arm

    def get_channel(self):
        return self.channel

    def get_channel_dlive(self):
        return self.get_channel() - 1

    def get_name(self):
        return self.name

    def get_color(self):
        return self.color

    def get_hpf_on(self):
        return self.hpf_on

    def get_hpf_value(self):
        return self.hpf_value

    def get_fader_level(self):
        return self.fader_level

    def get_mute(self):
        return self.mute

    def get_recording(self):
        return self.recording

    def get_record_arm(self):
        return self.record_arm
