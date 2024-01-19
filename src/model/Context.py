class Context:
    def __init__(self, logger, output, app_data, network_connection_allowed):
        self.logger = logger
        self.output = output
        self.app_data = app_data
        self.network_connection_allowed = network_connection_allowed

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

