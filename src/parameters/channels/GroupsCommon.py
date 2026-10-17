# coding=utf-8
####################################################
# Common functions for groups
#
# Author: Tobias Grupe
#
####################################################

import dliveConstants
from parameters.channels.Color import color_channel
from parameters.channels.Name import name_channel


def _within_boundary(context, items, bus_type, mixer_config):
    """Yields only the buses within the amount configured in the mixer config."""
    boundary = None if mixer_config is None else mixer_config.get_bus_limit(bus_type)
    for item in items:
        if boundary is not None and item.get_channel() > boundary:
            context.get_logger().warning("Skipping " + bus_type + " " + str(item.get_channel()) +
                                         ", only " + str(boundary) + " configured (Mixer Config).")
            continue
        yield item


def handle_groups_parameter(message, context, groups_model, action, bus_type, mixer_config=None):
    logging = context.get_logger()

    logging.info(message)

    if bus_type == "dca":
        for item in groups_model.get_dca_config():
            if action == "name":
                if name_channel(context, item, dliveConstants.midi_channel_offset_dca,
                                dliveConstants.channel_offset_dca, bus_type) == 1:
                    return 1

            elif action == "color":
                color_channel(context, item, dliveConstants.midi_channel_offset_dca, dliveConstants.channel_offset_dca)

    if bus_type == "aux_mono":
        for item in _within_boundary(context, groups_model.get_auxes_mono_config(), "aux_mono", mixer_config):
            if action == "name":
                if name_channel(context, item, dliveConstants.midi_channel_offset_auxes,
                                dliveConstants.channel_offset_auxes_mono, bus_type) == 1:
                    return 1
            elif action == "color":
                color_channel(context, item, dliveConstants.midi_channel_offset_auxes,
                              dliveConstants.channel_offset_auxes_mono)

    if bus_type == "aux_stereo":
        for item in _within_boundary(context, groups_model.get_auxes_stereo_config(), "aux_stereo", mixer_config):
            if action == "name":
                if name_channel(context, item, dliveConstants.midi_channel_offset_auxes,
                                dliveConstants.channel_offset_auxes_stereo, bus_type) == 1:
                    return 1
            elif action == "color":
                color_channel(context, item, dliveConstants.midi_channel_offset_auxes,
                              dliveConstants.channel_offset_auxes_stereo)

    if bus_type == "group_mono":
        for item in _within_boundary(context, groups_model.get_group_mono_config(), "group_mono", mixer_config):
            if action == "name":
                if name_channel(context, item, dliveConstants.midi_channel_offset_groups,
                                dliveConstants.channel_offset_groups_mono, bus_type) == 1:
                    return 1
            elif action == "color":
                color_channel(context, item, dliveConstants.midi_channel_offset_groups,
                              dliveConstants.channel_offset_groups_mono)

    if bus_type == "group_stereo":
        for item in _within_boundary(context, groups_model.get_group_stereo_config(), "group_stereo", mixer_config):
            if action == "name":
                if name_channel(context, item, dliveConstants.midi_channel_offset_groups,
                                dliveConstants.channel_offset_groups_stereo, bus_type) == 1:
                    return 1
            elif action == "color":
                color_channel(context, item, dliveConstants.midi_channel_offset_groups,
                              dliveConstants.channel_offset_groups_stereo)

    if bus_type == "matrix_mono":
        for item in _within_boundary(context, groups_model.get_matrix_mono_config(), "matrix_mono", mixer_config):
            if action == "name":
                if name_channel(context, item, dliveConstants.midi_channel_offset_matrices,
                                dliveConstants.channel_offset_matrices_mono, bus_type) == 1:
                    return 1
            elif action == "color":
                color_channel(context, item, dliveConstants.midi_channel_offset_matrices,
                              dliveConstants.channel_offset_matrices_mono)

    if bus_type == "matrix_stereo":
        for item in _within_boundary(context, groups_model.get_matrix_stereo_config(), "matrix_stereo", mixer_config):
            if action == "name":
                if name_channel(context, item, dliveConstants.midi_channel_offset_matrices,
                                dliveConstants.channel_offset_matrices_stereo, bus_type) == 1:
                    return 1
            elif action == "color":
                color_channel(context, item, dliveConstants.midi_channel_offset_matrices,
                              dliveConstants.channel_offset_matrices_stereo)

    if bus_type == "fx_send_mono":
        for item in _within_boundary(context, groups_model.get_fx_send_mono_config(), "fx_send_mono", mixer_config):
            if action == "name":
                if name_channel(context, item, dliveConstants.midi_channel_offset_fx_send_mono,
                                dliveConstants.channel_offset_fx_send_mono, bus_type) == 1:
                    return 1
            elif action == "color":
                color_channel(context, item, dliveConstants.midi_channel_offset_fx_send_mono,
                              dliveConstants.channel_offset_fx_send_mono)

    if bus_type == "fx_send_stereo":
        for item in _within_boundary(context, groups_model.get_fx_send_stereo_config(), "fx_send_stereo", mixer_config):
            if action == "name":
                if name_channel(context, item, dliveConstants.midi_channel_offset_fx_send_stereo,
                                dliveConstants.channel_offset_fx_send_stereo, bus_type) == 1:
                    return 1
            elif action == "color":
                color_channel(context, item, dliveConstants.midi_channel_offset_fx_send_stereo,
                              dliveConstants.channel_offset_fx_send_stereo)

    if bus_type == "fx_return":
        for item in groups_model.get_fx_return_config():
            if action == "name":
                if name_channel(context, item, dliveConstants.midi_channel_offset_fx_return,
                                dliveConstants.channel_offset_fx_return, bus_type) == 1:
                    return 1
            elif action == "color":
                color_channel(context, item, dliveConstants.midi_channel_offset_fx_return,
                              dliveConstants.channel_offset_fx_return)

    if bus_type == "ufx_send":
        for item in groups_model.get_ufx_send_config():
            if action == "name":
                if name_channel(context, item, dliveConstants.midi_channel_offset_ufx_send,
                                dliveConstants.channel_offset_ufx_send, bus_type) == 1:
                    return 1
            elif action == "color":
                color_channel(context, item, dliveConstants.midi_channel_offset_ufx_send,
                              dliveConstants.channel_offset_ufx_send)

    if bus_type == "ufx_return":
        for item in groups_model.get_ufx_return_config():
            if action == "name":
                if name_channel(context, item, dliveConstants.midi_channel_offset_ufx_return,
                                dliveConstants.channel_offset_ufx_return, bus_type) == 1:
                    return 1
            elif action == "color":
                color_channel(context, item, dliveConstants.midi_channel_offset_ufx_return,
                              dliveConstants.channel_offset_ufx_return)