# coding=utf-8
####################################################
# Common functions for channels
#
# Author: Tobias Grupe
#
####################################################

import dliveConstants
from parameters.channels.Color import color_channel
from parameters.channels.Dca import dca_channel
from parameters.channels.Faderlevel import fader_level_channel
from parameters.channels.Hpf import hpf_on_channel, hpf_value_channel
from parameters.channels.Mainmix import assign_mainmix_channel
from parameters.channels.Mute import mute_on_channel
from parameters.channels.Mutegroup import mg_channel
from parameters.channels.Name import name_channel


def handle_channels_parameter(message, context, channel_list_entries, action):
    logging = context.get_logger()

    logging.info(message)

    if context.get_app_data().get_console() == dliveConstants.console_drop_down_avantis:
        max_count_dsp_channels = dliveConstants.AVANTIS_MAX_CHANNELS
    else:
        max_count_dsp_channels = dliveConstants.DLIVE_MAX_CHANNELS

    for item in channel_list_entries:
        lower_enabled = str(item.get_enabled()).lower()
        if lower_enabled == 'nan' or lower_enabled == "no":
            logging.info("No " + action + " processing wanted for channel: " + str(item.get_channel()))
            continue
        if item.get_channel_console() > max_count_dsp_channels - 1:
            logging.warning("Skipping Channel...current channel number: " + str(item.get_channel()) +
                            " is bigger than the console supports.")
            continue
        logging.info("Processing " + action + " for channel: " + str(item.get_channel_console() + 1))
        if action == "name":
            if name_channel(context, item, dliveConstants.midi_channel_offset_channels,
                            dliveConstants.channel_offset_channels, "Input Channels") == 1:
                return 1
        elif action == "color":
            color_channel(context, item, dliveConstants.midi_channel_offset_channels,
                          dliveConstants.channel_offset_channels)
        elif action == "mute":
            mute_on_channel(context, item)
        elif action == "fader_level":
            fader_level_channel(context, item)
        elif action == "hpf_on":
            hpf_on_channel(context, item)
        elif action == "hpf_value":
            hpf_value_channel(context, item)
        elif action == "dca":
            dca_channel(context, item)
        elif action == "mute_group":
            mg_channel(context, item)
        elif action == "assign_main_mix":
            assign_mainmix_channel(context, item)
