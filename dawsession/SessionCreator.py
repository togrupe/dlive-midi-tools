####################################################
# Session Creator
#
# Author: Tobias Grupe
#
####################################################

import logging

from reathon.nodes import Project, Track

from dawsession import ReaperConstants


def convert_sheet_color_to_reaper_color(color):
    lower_color = color.lower()
    if lower_color == "blue":
        colour = ReaperConstants.reaper_color_blue
    elif lower_color == "red":
        colour = ReaperConstants.reaper_color_red
    elif lower_color == "light blue":
        colour = ReaperConstants.reaper_color_ltblue
    elif lower_color == 'purple':
        colour = ReaperConstants.reaper_color_purple
    elif lower_color == 'green':
        colour = ReaperConstants.reaper_color_green
    elif lower_color == 'yellow':
        colour = ReaperConstants.reaper_color_yellow
    elif lower_color == 'black':
        colour = ReaperConstants.reaper_color_black
    elif lower_color == 'white':
        colour = ReaperConstants.reaper_color_white
    else:
        logging.warning("Given color: " + lower_color + " is not supported, setting default color: black")
        colour = ReaperConstants.reaper_color_black
    return colour


def generate_rec_item(channel):
    ret = "1 " + str(channel) + " 1 0 0 0 0 0"

    return ret


def generate_hwout_item(channel):
    channel_temp = 1024 + channel
    ret = "" + str(channel_temp) + " 0 1 0 0 0 0 -1:U -1"
    return ret


def create_reaper_session(sheet, reaper_output_dir, prefix):
    project = Project()

    project.props = [
        ["MASTERHWOUT", ""]
    ]

    for item in sheet.get_channel_model():
        track = Track()
        name = item.get_name()

        if name == 'nan':
            track_name_raw = ""
        else:
            track_name_raw = name

        track_name_combined = "{:0>3d}_{}".format(item.get_channel(), track_name_raw)
        track.props = [
            ["NAME", track_name_combined],
            ["PEAKCOL", convert_sheet_color_to_reaper_color(item.get_color())],
            ["REC", generate_rec_item(item.get_channel_dlive())],
            ["TRACKHEIGHT", "40 0 0 0 0 0"],
            ["HWOUT", generate_hwout_item(item.get_channel_dlive())]
        ]
        project.add(track)

    reaper_outputfile = reaper_output_dir + "/" + prefix + "-" + "recording-template.rpp"
    logging.info("Reaper template will be generated into folder:" + reaper_outputfile)

    project.write(reaper_outputfile)


if __name__ == '__main__':
    create_reaper_session()
