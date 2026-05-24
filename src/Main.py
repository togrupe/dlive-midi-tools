# coding=utf-8
####################################################
# Main Script
#
# Author: Tobias Grupe
#
####################################################

import logging

import Toolinfo
import dliveConstants
import GuiConstants
from AppData import AppData
from Context import Context
from gui.MainView import MainView
from gui.MainController import MainController

LOG_FILE = 'main.log'
CONFIG_FILE = 'config.json'

if __name__ == '__main__':
    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    context = Context(logger, None, None,
                      dliveConstants.allow_network_communication, CONFIG_FILE,
                      not GuiConstants.SHOW_CSV_PATCHING_HINT_ONCE_A_RUN)
    context.set_app_data(AppData(None, None, None))

    logger.info("dlive-midi-tool version: " + Toolinfo.version)

    view = MainView()
    MainController(view, context)

    view.root.mainloop()
