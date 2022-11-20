import logging

from reathon.nodes import Project, Track

import dliveConstants


def convert_sheet_color_to_reaper_color(color):
    lower_color = color.lower()
    if lower_color == "blue":
        colour = dliveConstants.reaper_color_blue
    elif lower_color == "red":
        colour = dliveConstants.reaper_color_red
    elif lower_color == "light blue":
        colour = dliveConstants.reaper_color_ltblue
    elif lower_color == 'purple':
        colour = dliveConstants.reaper_color_purple
    elif lower_color == 'green':
        colour = dliveConstants.reaper_color_green
    elif lower_color == 'yellow':
        colour = dliveConstants.reaper_color_yellow
    elif lower_color == 'black':
        colour = dliveConstants.reaper_color_black
    elif lower_color == 'white':
        colour = dliveConstants.reaper_color_white
    else:
        logging.warning("Given color: " + lower_color + " is not supported, setting default color: black")
        colour = dliveConstants.reaper_color_black
    return colour


def create_reaper_session(sheet):
    project = Project()

    for item in sheet.get_channel_model():
        track = Track()
        track_name = "{:0>3d}_{}".format(item.get_channel(), item.get_name())
        track.props = [
            ["NAME", track_name],
            ["PEAKCOL", convert_sheet_color_to_reaper_color(item.get_color())],
            ["REC", "1 0 1 0 0 0 0 0"],
            ["TRACKHEIGHT", "40 0 0 0 0 0"]
        ]
        project.add(track)

    project.write("recording-template.rpp")


if __name__ == '__main__':
    create_reaper_session()
