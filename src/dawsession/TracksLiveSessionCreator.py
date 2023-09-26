# coding=utf-8
####################################################
# Session Creator
#
# Author: Tobias Grupe
#
####################################################
import copy
import logging
import xml.etree.ElementTree as ET
from dawsession import TracksLiveConstants


def convert_sheet_color_to_trackslive_color(color, disable_track_coloring=False):
    if disable_track_coloring:
        colour = TracksLiveConstants.trackslive_color_default
    else:
        lower_color = color.lower()
        if lower_color == "blue":
            colour = TracksLiveConstants.trackslive_color_blue
        elif lower_color == "red":
            colour = TracksLiveConstants.trackslive_color_red
        elif lower_color == "light blue":
            colour = TracksLiveConstants.trackslive_color_ltblue
        elif lower_color == 'purple':
            colour = TracksLiveConstants.trackslive_color_purple
        elif lower_color == 'green':
            colour = TracksLiveConstants.trackslive_color_green
        elif lower_color == 'yellow':
            colour = TracksLiveConstants.trackslive_color_yellow
        elif lower_color == 'black':
            colour = TracksLiveConstants.trackslive_color_black
        elif lower_color == 'white':
            colour = TracksLiveConstants.trackslive_color_white
        elif lower_color == 'orange':
            colour = TracksLiveConstants.trackslive_color_orange
        else:
            logging.warning("Given color: " + lower_color + " is not supported, setting default color: black")
            colour = TracksLiveConstants.trackslive_color_black
    return colour


def calulate_track_id(get_channel_console):
    return str(1000 + int(get_channel_console))


def extract_first_channel(master_recording_patch_string):
    return int(master_recording_patch_string.split("-")[0]) - 1


def create_session(sheet, output_dir, file_prefix, disable_default_track_numbering, has_additional_prefix,
                   additional_prefix, has_master_recording_tracks, master_recording_patch_string,
                   disable_track_coloring):
    tree = ET.parse('tracks-live-template.xml')
    root = tree.getroot()

    routes = root.find('Routes')
    playlists = root.find('Playlists')
    GUIObjectStates = root.find('Extra/UI/GUIObjectState')

    template_route_org = root.find('Routes/Route[@id="102"]')
    template_playlist_org = root.find('Playlists/Playlist[@id="623"]')
    template_GUIObjectState_route_org = root.find('Extra/UI/GUIObjectState/Object[@id="route 29"]')
    template_GUIObjectState_rtav_org = root.find('Extra/UI/GUIObjectState/Object[@id="rtav 29"]')

    print("stop")

    for item in sheet.get_channel_model():
        lower_recording = str(item.get_recording()).lower()
        if lower_recording == 'nan':
            continue
        if lower_recording == 'yes':
            name_local = item.get_name()
            trackid_local = calulate_track_id(item.get_channel())

            if name_local == 'nan':
                track_name_raw = ""
            else:
                track_name_raw = name_local

            if disable_default_track_numbering:
                if has_additional_prefix:
                    track_name_combined = additional_prefix + "_" + track_name_raw
                else:
                    track_name_combined = track_name_raw
            else:
                if has_additional_prefix:
                    track_name_combined = "{}_{:0>3d}_{}".format(additional_prefix, item.get_channel(), track_name_raw)
                else:
                    track_name_combined = "{:0>3d}_{}".format(item.get_channel(), track_name_raw)

            # Handling of Route
            template_route_to_update = copy.deepcopy(template_route_org)
            template_route_to_update.set("id", trackid_local)
            template_route_to_update.set("name", track_name_combined)

            input = template_route_to_update.find('IO[@id="119"]')
            input.set("name", track_name_combined)

            input_port = template_route_to_update.find('IO[@id="119"]/Port')
            input_port.set("name", track_name_combined + "/audio_in " + str(item.get_channel()))

            output = template_route_to_update.find('IO[@id="120"]')
            output.set("name", track_name_combined)

            output_port1 = template_route_to_update.find('IO[@id="120"]/Port')
            output_port1.set("name", track_name_combined + "/audio_out 1")

            output_port2 = template_route_to_update.findall('IO[@id="120"]/Port')[1]
            output_port2.set("name", track_name_combined + "/audio_out 2")

            processor = template_route_to_update.find('Processor[@id="128"]')
            processor.set("name", track_name_combined)
            processor.set("output", track_name_combined)

            diskstream = template_route_to_update.find('Diskstream[@id="132"]')
            diskstream.set("name", track_name_combined)
            diskstream.set("playlist", track_name_combined)

            routes.append(template_route_to_update)

            # Handling of playlist
            template_playlist_to_update = copy.deepcopy(template_playlist_org)
            template_playlist_to_update.set("id", str(int(trackid_local) + 1000))
            template_playlist_to_update.set("name", track_name_combined)
            template_playlist_to_update.set("orig-track-id", trackid_local)
            playlists.append(template_playlist_to_update)

            # Handling of UI
            template_GUIObjectState_route_to_update = copy.deepcopy(template_GUIObjectState_route_org)
            template_GUIObjectState_route_to_update.set("id", "route " + trackid_local)
            template_GUIObjectState_route_to_update.set("color",
                                                        convert_sheet_color_to_trackslive_color(item.get_color(),
                                                                                                disable_track_coloring))

            template_GUIObjectState_rtav_to_update = copy.deepcopy(template_GUIObjectState_rtav_org)
            template_GUIObjectState_rtav_to_update.set("id", "rtav " + trackid_local)
            template_GUIObjectState_rtav_to_update.set("visible", "1")

            GUIObjectStates.append(template_GUIObjectState_route_to_update)
            GUIObjectStates.append(template_GUIObjectState_rtav_to_update)

    # if has_master_recording_tracks:
    #     master_recording_patch = extract_first_channel(master_recording_patch_string)
    #
    #     logging.info("Processing MasterL channel")
    #
    #     logging.info("Processing MasterR channel")

    routes.remove(template_route_org)
    playlists.remove(template_playlist_org)

    tree.write(output_dir + "/" + file_prefix + '-tracklive.template')

    print("Stop")
