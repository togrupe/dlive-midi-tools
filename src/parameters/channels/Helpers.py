# coding=utf-8
import time
import mido

import dliveConstants
from parameters.channels.Dca import assign_dca
from parameters.channels.Mutegroup import assign_mg
from parameters.channels.Mainmix import assign_mainmix

_DLIVE_DCA_COUNT   = 24
_AVANTIS_DCA_COUNT = 16
_MG_COUNT          = 8   # dLive only

# Conservative output-bus counts per console type.
# The console silently ignores messages for non-existent buses.
_DLIVE_AUX_MONO_MAX        = 48
_DLIVE_AUX_STEREO_MAX      = 24
_DLIVE_GROUP_MONO_MAX      = 24
_DLIVE_GROUP_STEREO_MAX    = 12
_DLIVE_MATRIX_MONO_MAX     = 12
_DLIVE_MATRIX_STEREO_MAX   = 8
_DLIVE_FX_SEND_MONO_MAX    = 8
_DLIVE_FX_SEND_STEREO_MAX  = 4
_DLIVE_FX_RETURN_MAX       = 8
_DLIVE_UFX_SEND_MAX        = 8
_DLIVE_UFX_RETURN_MAX      = 8

_AVANTIS_AUX_MONO_MAX      = 24
_AVANTIS_AUX_STEREO_MAX    = 12
_AVANTIS_GROUP_MONO_MAX    = 12
_AVANTIS_GROUP_STEREO_MAX  = 8
_AVANTIS_MATRIX_MONO_MAX   = 4
_AVANTIS_MATRIX_STEREO_MAX = 4
_AVANTIS_FX_SEND_MONO_MAX  = 4
_AVANTIS_FX_SEND_STEREO_MAX = 2
_AVANTIS_FX_RETURN_MAX     = 4
_AVANTIS_UFX_SEND_MAX      = 8
_AVANTIS_UFX_RETURN_MAX    = 8


def _is_avantis(context):
    return context.get_app_data().get_console() == dliveConstants.console_drop_down_avantis


def _send_mute(output, midi_channel, note, velocity):
    output.send(mido.Message('note_on', channel=midi_channel, note=note, velocity=velocity))
    output.send(mido.Message('note_on', channel=midi_channel, note=note, velocity=dliveConstants.note_off))
    time.sleep(dliveConstants.DEFAULT_SLEEP_AFTER_MIDI_COMMAND)


def reset_all_dca(context):
    avantis = _is_avantis(context)
    max_ch    = dliveConstants.AVANTIS_MAX_CHANNELS if avantis else dliveConstants.DLIVE_MAX_CHANNELS
    dca_count = _AVANTIS_DCA_COUNT if avantis else _DLIVE_DCA_COUNT
    for ch in range(max_ch):
        for i in range(dca_count):
            assign_dca(context, ch, dliveConstants.dca_off_base_address + i)


def reset_all_mute_groups(context):
    # dLive only – caller must ensure this is not invoked for Avantis
    for ch in range(dliveConstants.DLIVE_MAX_CHANNELS):
        for i in range(_MG_COUNT):
            assign_mg(context, ch, dliveConstants.mg_off_base_address + i)


def reset_all_main_mix(context):
    avantis = _is_avantis(context)
    max_ch = dliveConstants.AVANTIS_MAX_CHANNELS if avantis else dliveConstants.DLIVE_MAX_CHANNELS
    for ch in range(max_ch):
        assign_mainmix(context, ch, dliveConstants.assign_off)



def mute_all_inputs(context):
    if not context.get_network_connection_allowed():
        return
    avantis  = _is_avantis(context)
    max_ch   = dliveConstants.AVANTIS_MAX_CHANNELS if avantis else dliveConstants.DLIVE_MAX_CHANNELS
    output   = context.get_output()
    midi_ch  = context.get_app_data().get_midi_channel()
    for ch in range(max_ch):
        _send_mute(output,
                   midi_ch + dliveConstants.midi_channel_offset_channels,
                   dliveConstants.channel_offset_channels + ch,
                   dliveConstants.mute_on)


def unmute_all_inputs(context):
    if not context.get_network_connection_allowed():
        return
    avantis = _is_avantis(context)
    max_ch  = dliveConstants.AVANTIS_MAX_CHANNELS if avantis else dliveConstants.DLIVE_MAX_CHANNELS
    output  = context.get_output()
    midi_ch = context.get_app_data().get_midi_channel()
    for ch in range(max_ch):
        _send_mute(output,
                   midi_ch + dliveConstants.midi_channel_offset_channels,
                   dliveConstants.channel_offset_channels + ch,
                   dliveConstants.mute_off)


def unmute_all_outputs(context):
    if not context.get_network_connection_allowed():
        return
    avantis = _is_avantis(context)
    output  = context.get_output()
    midi_ch = context.get_app_data().get_midi_channel()

    ch_groups   = midi_ch + dliveConstants.midi_channel_offset_groups
    ch_auxes    = midi_ch + dliveConstants.midi_channel_offset_auxes
    ch_matrices = midi_ch + dliveConstants.midi_channel_offset_matrices
    ch_fx       = midi_ch + dliveConstants.midi_channel_offset_fx_send_mono

    if avantis:
        specs = [
            (ch_auxes,    dliveConstants.channel_offset_auxes_mono,      _AVANTIS_AUX_MONO_MAX),
            (ch_auxes,    dliveConstants.channel_offset_auxes_stereo,    _AVANTIS_AUX_STEREO_MAX),
            (ch_groups,   dliveConstants.channel_offset_groups_mono,     _AVANTIS_GROUP_MONO_MAX),
            (ch_groups,   dliveConstants.channel_offset_groups_stereo,   _AVANTIS_GROUP_STEREO_MAX),
            (ch_matrices, dliveConstants.channel_offset_matrices_mono,   _AVANTIS_MATRIX_MONO_MAX),
            (ch_matrices, dliveConstants.channel_offset_matrices_stereo, _AVANTIS_MATRIX_STEREO_MAX),
            (ch_fx,       dliveConstants.channel_offset_fx_send_mono,    _AVANTIS_FX_SEND_MONO_MAX),
            (ch_fx,       dliveConstants.channel_offset_fx_send_stereo,  _AVANTIS_FX_SEND_STEREO_MAX),
            (ch_fx,       dliveConstants.channel_offset_fx_return,       _AVANTIS_FX_RETURN_MAX),
            (ch_fx,       dliveConstants.channel_offset_ufx_send,        _AVANTIS_UFX_SEND_MAX),
            (ch_fx,       dliveConstants.channel_offset_ufx_return,      _AVANTIS_UFX_RETURN_MAX),
        ]
    else:
        specs = [
            (ch_auxes,    dliveConstants.channel_offset_auxes_mono,      _DLIVE_AUX_MONO_MAX),
            (ch_auxes,    dliveConstants.channel_offset_auxes_stereo,    _DLIVE_AUX_STEREO_MAX),
            (ch_groups,   dliveConstants.channel_offset_groups_mono,     _DLIVE_GROUP_MONO_MAX),
            (ch_groups,   dliveConstants.channel_offset_groups_stereo,   _DLIVE_GROUP_STEREO_MAX),
            (ch_matrices, dliveConstants.channel_offset_matrices_mono,   _DLIVE_MATRIX_MONO_MAX),
            (ch_matrices, dliveConstants.channel_offset_matrices_stereo, _DLIVE_MATRIX_STEREO_MAX),
            (ch_fx,       dliveConstants.channel_offset_fx_send_mono,    _DLIVE_FX_SEND_MONO_MAX),
            (ch_fx,       dliveConstants.channel_offset_fx_send_stereo,  _DLIVE_FX_SEND_STEREO_MAX),
            (ch_fx,       dliveConstants.channel_offset_fx_return,       _DLIVE_FX_RETURN_MAX),
            (ch_fx,       dliveConstants.channel_offset_ufx_send,        _DLIVE_UFX_SEND_MAX),
            (ch_fx,       dliveConstants.channel_offset_ufx_return,      _DLIVE_UFX_RETURN_MAX),
        ]

    for midi_channel, offset, count in specs:
        for i in range(count):
            _send_mute(output, midi_channel, offset + i, dliveConstants.mute_off)


def mute_all_outputs(context):
    if not context.get_network_connection_allowed():
        return
    avantis = _is_avantis(context)
    output  = context.get_output()
    midi_ch = context.get_app_data().get_midi_channel()

    ch_groups   = midi_ch + dliveConstants.midi_channel_offset_groups
    ch_auxes    = midi_ch + dliveConstants.midi_channel_offset_auxes
    ch_matrices = midi_ch + dliveConstants.midi_channel_offset_matrices
    ch_fx       = midi_ch + dliveConstants.midi_channel_offset_fx_send_mono

    if avantis:
        specs = [
            (ch_auxes,    dliveConstants.channel_offset_auxes_mono,      _AVANTIS_AUX_MONO_MAX),
            (ch_auxes,    dliveConstants.channel_offset_auxes_stereo,    _AVANTIS_AUX_STEREO_MAX),
            (ch_groups,   dliveConstants.channel_offset_groups_mono,     _AVANTIS_GROUP_MONO_MAX),
            (ch_groups,   dliveConstants.channel_offset_groups_stereo,   _AVANTIS_GROUP_STEREO_MAX),
            (ch_matrices, dliveConstants.channel_offset_matrices_mono,   _AVANTIS_MATRIX_MONO_MAX),
            (ch_matrices, dliveConstants.channel_offset_matrices_stereo, _AVANTIS_MATRIX_STEREO_MAX),
            (ch_fx,       dliveConstants.channel_offset_fx_send_mono,    _AVANTIS_FX_SEND_MONO_MAX),
            (ch_fx,       dliveConstants.channel_offset_fx_send_stereo,  _AVANTIS_FX_SEND_STEREO_MAX),
            (ch_fx,       dliveConstants.channel_offset_fx_return,       _AVANTIS_FX_RETURN_MAX),
            (ch_fx,       dliveConstants.channel_offset_ufx_send,        _AVANTIS_UFX_SEND_MAX),
            (ch_fx,       dliveConstants.channel_offset_ufx_return,      _AVANTIS_UFX_RETURN_MAX),
        ]
    else:
        specs = [
            (ch_auxes,    dliveConstants.channel_offset_auxes_mono,      _DLIVE_AUX_MONO_MAX),
            (ch_auxes,    dliveConstants.channel_offset_auxes_stereo,    _DLIVE_AUX_STEREO_MAX),
            (ch_groups,   dliveConstants.channel_offset_groups_mono,     _DLIVE_GROUP_MONO_MAX),
            (ch_groups,   dliveConstants.channel_offset_groups_stereo,   _DLIVE_GROUP_STEREO_MAX),
            (ch_matrices, dliveConstants.channel_offset_matrices_mono,   _DLIVE_MATRIX_MONO_MAX),
            (ch_matrices, dliveConstants.channel_offset_matrices_stereo, _DLIVE_MATRIX_STEREO_MAX),
            (ch_fx,       dliveConstants.channel_offset_fx_send_mono,    _DLIVE_FX_SEND_MONO_MAX),
            (ch_fx,       dliveConstants.channel_offset_fx_send_stereo,  _DLIVE_FX_SEND_STEREO_MAX),
            (ch_fx,       dliveConstants.channel_offset_fx_return,       _DLIVE_FX_RETURN_MAX),
            (ch_fx,       dliveConstants.channel_offset_ufx_send,        _DLIVE_UFX_SEND_MAX),
            (ch_fx,       dliveConstants.channel_offset_ufx_return,      _DLIVE_UFX_RETURN_MAX),
        ]

    for midi_channel, offset, count in specs:
        for i in range(count):
            _send_mute(output, midi_channel, offset + i, dliveConstants.mute_on)


def _send_fader(output, midi_channel, channel, fader_value):
    output.send(mido.Message('control_change', channel=midi_channel, control=0x63, value=channel))
    output.send(mido.Message('control_change', channel=midi_channel, control=0x62,
                             value=dliveConstants.nrpn_parameter_id_fader_level))
    output.send(mido.Message('control_change', channel=midi_channel, control=0x06, value=fader_value))
    time.sleep(dliveConstants.DEFAULT_SLEEP_AFTER_MIDI_COMMAND)


def set_all_input_faders_to_zero(context):
    if not context.get_network_connection_allowed():
        return
    avantis = _is_avantis(context)
    max_ch  = dliveConstants.AVANTIS_MAX_CHANNELS if avantis else dliveConstants.DLIVE_MAX_CHANNELS
    output  = context.get_output()
    midi_ch = context.get_app_data().get_midi_channel()
    for ch in range(max_ch):
        _send_fader(output, midi_ch + dliveConstants.midi_channel_offset_channels,
                    ch, dliveConstants.fader_level_zero)


def set_all_input_faders_to_minus_inf(context):
    if not context.get_network_connection_allowed():
        return
    avantis = _is_avantis(context)
    max_ch  = dliveConstants.AVANTIS_MAX_CHANNELS if avantis else dliveConstants.DLIVE_MAX_CHANNELS
    output  = context.get_output()
    midi_ch = context.get_app_data().get_midi_channel()
    for ch in range(max_ch):
        _send_fader(output, midi_ch + dliveConstants.midi_channel_offset_channels,
                    ch, dliveConstants.fader_level_minus_inf)


def phantom_power_off_all_sockets(context):
    if not context.get_network_connection_allowed():
        return
    avantis = _is_avantis(context)
    output  = context.get_output()
    midi_ch = context.get_app_data().get_midi_channel()

    def _send_phantom_off(socket):
        if socket > 127:
            return
        payload = [midi_ch, dliveConstants.sysex_message_set_socket_preamp_48V,
                   socket, dliveConstants.phantom_power_off]
        msg = mido.Message.from_bytes(dliveConstants.sysexhdrstart + payload + dliveConstants.sysexhdrend)
        output.send(msg)
        time.sleep(dliveConstants.DEFAULT_SLEEP_AFTER_MIDI_COMMAND)

    if avantis:
        for s in range(dliveConstants.LOCAL_AVANTIS_SOCKET_COUNT_MAX):
            _send_phantom_off(s)
        for s in range(64):  # Slink offset 64; cap at 63 to stay <= 127
            _send_phantom_off(s + 64)
    else:
        for s in range(dliveConstants.LOCAL_DLIVE_SOCKET_COUNT_MAX):
            _send_phantom_off(s)
        for s in range(dliveConstants.DX1_SOCKET_COUNT_MAX):
            _send_phantom_off(s + 64)
        for s in range(dliveConstants.DX3_SOCKET_COUNT_MAX):
            _send_phantom_off(s + 96)
