class Context:
    def __init__(self, logger, output, app_data, network_connection_allowed, config_file, csv_patching_hint_already_seen):
        self.logger = logger
        self.output = output
        self.app_data = app_data
        self.network_connection_allowed = network_connection_allowed
        self.config_file = config_file
        self.csv_patching_hint_already_seen = csv_patching_hint_already_seen

    def get_logger(self):
        return self.logger

    def get_output(self):
        return self.output

    def set_output(self, output):
        self.output = output

    def get_app_data(self):
        return self.app_data

    def set_app_data(self, app_data):
        self.app_data = app_data

    def get_network_connection_allowed(self):
        return self.network_connection_allowed

    def get_config_file(self):
        return self.config_file

    def get_csv_patching_hint_already_seen(self):
        return self.csv_patching_hint_already_seen

    def set_csv_patching_hint_already_seen(self, value):
        self.csv_patching_hint_already_seen = value
