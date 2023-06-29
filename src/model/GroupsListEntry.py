# coding=utf-8
####################################################
# Represents groups with its attributes.
#
# Author: Tobias Grupe
#
####################################################
class GroupsListEntry:
    def __init__(self, dca_config, auxes_mono_config, auxes_stereo_config, group_mono_config, group_stereo_config,
                 matrix_mono_config, matrix_stereo_config, fx_send_mono_config, fx_send_stereo_config, fx_return_config):
        self.dca_config = dca_config
        self.auxes_mono_config = auxes_mono_config
        self.auxes_stereo_config = auxes_stereo_config
        self.group_mono_config = group_mono_config
        self.group_stereo_config = group_stereo_config
        self.matrix_mono_config = matrix_mono_config
        self.matrix_stereo_config = matrix_stereo_config
        self.fx_send_mono_config = fx_send_mono_config
        self.fx_send_stereo_config = fx_send_stereo_config
        self.fx_return_config = fx_return_config

    def get_dca_config(self):
        return self.dca_config

    def get_auxes_mono_config(self):
        return self.auxes_mono_config

    def get_auxes_stereo_config(self):
        return self.auxes_stereo_config

    def get_group_mono_config(self):
        return self.group_mono_config

    def get_group_stereo_config(self):
        return self.group_stereo_config

    def get_matrix_mono_config(self):
        return self.matrix_mono_config

    def get_matrix_stereo_config(self):
        return self.matrix_stereo_config

    def get_fx_send_mono_config(self):
        return self.fx_send_mono_config

    def get_fx_send_stereo_config(self):
        return self.fx_send_stereo_config

    def get_fx_return_config(self):
        return self.fx_return_config
