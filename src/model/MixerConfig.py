# coding=utf-8
####################################################
# Represents the mixer config (buses configured on the console).
# Holds the amount of mono/stereo buses per bus type.
# A value of None means "not limited" (console
# maximum applies).
#
# Author: Tobias Grupe
#
####################################################
import dliveConstants

# Bus types of a mixer config, each with a mono and a stereo amount.
MIXER_CONFIG_ROWS = ["Group", "FX", "Aux", "Matrix"]

# Highest (mono, stereo) amount which can be entered per console.
# dLive: the MIDI protocol (V1.9) addresses Aux/Group/Matrix up to 62 mono / 31 stereo
# and FX Sends up to 16 / 16, so the pool without LR & PAFL (60 mono / 30 stereo)
# is the practical limit.
# Avantis: freely configurable pool of 42 buses and 12 FX racks; the MIDI protocol
# addresses Aux/Group/Matrix up to 54 mono / 27 stereo and FX Sends up to 12 / 12,
# so the pool without LR & PAFL (38 mono / 19 stereo) is the practical limit.
MIXER_CONFIG_MAXIMA = {
    dliveConstants.console_drop_down_dlive: {
        "Group": (60, 30), "FX": (16, 16), "Aux": (60, 30), "Matrix": (60, 30)},
    dliveConstants.console_drop_down_avantis: {
        "Group": (38, 19), "FX": (12, 12), "Aux": (38, 19), "Matrix": (38, 19)},
}


# Total amount of buses which can be configured per console (a stereo bus counts twice).
# dLive: 64 configurable buses. Avantis: pool of 42 buses.
MIXER_CONFIG_BUS_POOL = {
    dliveConstants.console_drop_down_dlive: 64,
    dliveConstants.console_drop_down_avantis: 42,
}

# Buses of the pool always in use: Main LR (2) and PAFL (2).
MIXER_CONFIG_RESERVED_BUSES = 4


def available_buses(console_type):
    """Amount of buses left for Group/FX/Aux/Matrix, or None if the console is unknown."""
    pool = MIXER_CONFIG_BUS_POOL.get(console_type)
    return None if pool is None else pool - MIXER_CONFIG_RESERVED_BUSES


def count_buses(rows):
    """Amount of buses used by the given rows {"Group": (mono, stereo), ...}.
    A stereo bus counts twice, None (not set) counts as 0."""
    return sum((mono or 0) + 2 * (stereo or 0) for mono, stereo in rows.values())


class MixerConfig:
    def __init__(self, group_mono=None, group_stereo=None, fx_mono=None, fx_stereo=None,
                 aux_mono=None, aux_stereo=None, matrix_mono=None, matrix_stereo=None):
        self.group_mono = group_mono
        self.group_stereo = group_stereo
        self.fx_mono = fx_mono
        self.fx_stereo = fx_stereo
        self.aux_mono = aux_mono
        self.aux_stereo = aux_stereo
        self.matrix_mono = matrix_mono
        self.matrix_stereo = matrix_stereo

    def get_bus_limit(self, bus_type_key):
        """Configured amount for a GroupsCommon.BUS_TYPES key (e.g. "group_mono"),
        or None if the mixer config does not cover / specify it."""
        return {
            "group_mono": self.group_mono,
            "group_stereo": self.group_stereo,
            "fx_send_mono": self.fx_mono,
            "fx_send_stereo": self.fx_stereo,
            "aux_mono": self.aux_mono,
            "aux_stereo": self.aux_stereo,
            "matrix_mono": self.matrix_mono,
            "matrix_stereo": self.matrix_stereo,
        }.get(bus_type_key)

    def apply(self, bus_type_key, count):
        """The configured amount of the given bus type, or `count` if not configured."""
        configured = self.get_bus_limit(bus_type_key)
        return count if configured is None else configured

    def limit(self, bus_type_key, count):
        """`count` reduced to the configured amount of the given bus type, if any."""
        configured = self.get_bus_limit(bus_type_key)
        return count if configured is None else min(count, configured)

    def get_group_mono(self):
        return self.group_mono

    def get_group_stereo(self):
        return self.group_stereo

    def get_fx_mono(self):
        return self.fx_mono

    def get_fx_stereo(self):
        return self.fx_stereo

    def get_aux_mono(self):
        return self.aux_mono

    def get_aux_stereo(self):
        return self.aux_stereo

    def get_matrix_mono(self):
        return self.matrix_mono

    def get_matrix_stereo(self):
        return self.matrix_stereo
