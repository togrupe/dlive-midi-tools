# dlive-midi-tools
## Description
Python and midi/tcp based tool to prepare channel lists for Allen &amp; Heath dlive systems. Based on a spread sheet the following parameters can be preconfigured and in one or more steps be written into real dlive systems or into dLive Director via midi/tcp. Additionally from the same spread sheet a DAW recording session for Reaper can be generated. 
- Channel Name
- Channel Color
- Channel Mute
- 48V Phantom Power & PAD (Local, DX1 & DX3)

more information about future releases can be found in the [wiki](https://github.com/togrupe/dlive-midi-tools/wiki)

## Use Cases
* Single source (spread sheet) for channel lists in single or multi console situations
* Better overview on all channels during preparation phase
* Sync channel names and colors between consoles and DAW for virtual soundchecks
* Supports dLive Director (use the external ip or 127.0.0.1 of your own machine as "Mixrack IP Address")

## Used Python Libraries
* mido - Midi Library
* pandas - excel reader/writer
* reathon - Reaper Session Creator
* pyinstaller - Binary creator

## Overview
![Overview](overview.drawio.png)

## Download
| Version | OS      | Download                                                                                               |
|---------|---------|--------------------------------------------------------------------------------------------------------|
| v2.1.0  | MacOS   |                                                                                                        |
|         | Windows |                                                                                                        |
| v2.0.1  | MacOS   | [Link](http://wp1054826.server-he.de/downloads/dlive-midi-tools/v2_0_1/macos/dmt-v2_0_1-macos.zip)     |
|         | Windows | [Link](http://wp1054826.server-he.de/downloads/dlive-midi-tools/v2_0_1/windows/dmt-v2_0_1-windows.zip) |

## Input file
Excel sheet, please have a look at the following tabs

# Channel Overview
![Channels](doc/excel_channels.png)
# 48V Phantom Power and PAD Overview
![Phantom](doc/excel_phantom.png)


An example Excel file named: **dLiveChannelList.xlsx** can be found in the root folder. 
By default, the channels 1-128 are available in the sheet. If you need less, 
just delete the channels you don't want to process. Empty lines in between are not supported.

Microsoft Excel and LibreOffice Calc Spreadsheet can be used to write / save the sheets.
Please make sure that you save your changes in the (*.xlsx or .ods) format. 

The following colors are allowed:
* blue
* red 
* light blue 
* purple 
* green 
* yellow 
* black
* white

If the given color does not match, the default color black is used instead.

## Settings on the dlive console
The Midi Channel setting on dlive under `Utils/Shows -> Control -> Midi` should be be set to : `12 to 16`, which is default.

If you want to change the preconfigured Midi port, you can change it in the Graphical User Interface according to your dlive settings. 

## Default ip and port
The default dlive mixrack ip address is: 192.168.1.70. This IP-Address is preconfigured in the scripts. If you want to 
change it, you can edit the field `ip` in the file: dliveConstants.py or during runtime within the Graphical User Interface.  

Please make sure that your ethernet or Wi-Fi interface has an ip address in the same subnet. e.g. 192.168.1.10
 

## Usage
Prerequisites: 
* Python >= 3.8
* dlive Firmware: >= 1.90

1. Recommendation: Please backup your current show file, just to be on the safe side if something goes wrong.

2. Before you run the script, please run the following command to download the required python modules using `pip`. Please make sure `pip` is installed.

`pip install -r dependencies.txt`

3. Run the script with the following command: 

`python3 main.py`

4. (Optional) If you want to make a binary out of it, please do the following: 

    4.1 Installation of pyinstaller

    `pip install pyinstaller`

    4.2 Create a onefile binary (works for Windows and MacOS)

    `pyinstaller.exe --onefile -w main.py`


Afterwards the following window appears. 

![Gui](doc/gui.png)


1. Check the Mixrack IP and Midi Port.

2. Select the columns you want to write, and select "Write to dLive"

3. If you also want to create a Reaper Template session, set the corresponding tick. The Reaper session file `recording-template.rpp` will be generated into the directory from where the tool was executed. You can also use the tool to create only the Reaper session file.

4. Click the button "Open spread sheet and trigger writing process" to select your custom Excel sheet. Afterwards the selected action(s) start automatically.

5. If something goes wrong, please check the python console.

If you find any issues, please let me know.

Have fun!
