class Sheet:
    def __init__(self):
        self.channel_model = None
        self.dca_model = None
        self.phantom_pad_model = None
        self.misc_model = None

    def get_channel_model(self):
        return self.channel_model

    def get_dca_model(self):
        return self.dca_model

    def get_phantom_pad_model(self):
        return self.phantom_pad_model

    def get_misc_model(self):
        return self.misc_model

    def set_channel_model(self, channel_model):
        self.channel_model = channel_model

    def set_dca_model(self, dca_model):
        self.dca_model = dca_model

    def set_phantom_pad_model(self, phantom_pad_model):
        self.phantom_pad_model = phantom_pad_model

    def set_misc_model(self, misc_model):
        self.misc_model = misc_model


