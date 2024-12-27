# dlive-midi-tools
## Description
Python and MIDI/TCP-based tool to prepare channel lists for Allen &amp; Heath dLive & Avantis consoles. 
Based on a spreadsheet the following parameters can be preconfigured and in very few steps be written to real 
dLive/Avantis systems or to dLive/Avantis Director via MIDI/TCP or CSV import. Additionally, from the same spreadsheet 
or the current console settings a DAW (Digital Audio Workstation) recording session for Reaper or Tracks Live can be generated. 
- Name & Color for: 
  - Channel
  - DCA
  - Aux
  - Group
  - Matrices
  - FX Sends
  - FX Returns
- Channel Mute
- Fader Level
- Main Mix Assignments
- DCA Assignments
- 48V Phantom Power (Local, DX1 & DX3, SLink) 
- PAD (Local, DX1 & DX3, SLink)
- Gain (Local, DX1 & DX3, SLink)
- Mute Group Assignments (dLive only)
- HPF On (dLive only)
- HPF Value (dLive only)
- Source & Socket Patching (via dLive Director CSV Import)

More information about future releases can be found in the [wiki](https://github.com/togrupe/dlive-midi-tools/wiki)

## Use Cases

* Single source (spreadsheet) for channel lists in single or multi-console situations
* Better overview of all channels during preparation phase
* Sync channel names and colors between consoles and DAW for virtual soundchecks
* Supports dLive & dLive Director (offline and online)
* Supports Avantis & Avantis Director (offline and online)
* Generate DAW session(s) from current console settings
* Generate CSV File incl. channel patching for Director CSV Import

## Software Liability Warning

This software is provided "as is," without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

Furthermore, this software may be subject to known or unknown bugs, errors, and vulnerabilities, which may result in unexpected behavior or security breaches. The authors or copyright holders shall not be liable for any damages or losses resulting from such bugs, errors, or vulnerabilities.

By using this software, you acknowledge and agree that you do so at your own risk and that you will be solely responsible for any damages or losses that may arise from such use.


## Used Python Libraries
* mido - Midi Library
* pandas - spreadsheet reader/writer
* reathon - Reaper Session Creator
* xlrd - supports xls format
* odfpy - supports odf format
* openpyxl - supports xlsx format
* numpy - array computing
* pyinstaller - Binary creator

see [3rd Party Licenses](ThirdParty-Licenses.txt)

## Overview
![Overview](doc/overview.drawio.png)

## Download
| Version | Date       | OS                                    | Download                                                                                 | Release Notes | MD5 Checksum                     |
|---------|------------|---------------------------------------|------------------------------------------------------------------------------------------|---------------|----------------------------------|
| v2.8.3  | 27.12.2024 | macOS (x86_64 - Intel)                | [Link](https://liveworks-vt.de/downloads/dlive-midi-tools/v2_8_3/dmt-v2_8_3-macos-x86_64.zip) | [Link](#v283) | 7f925278baf8c797091295dc38d70fcc |
|         |            | macOS (arm64 - Apple-Silicon*)        | [Link](https://liveworks-vt.de/downloads/dlive-midi-tools/v2_8_3/dmt-v2_8_3-macos-arm64.zip) |               | b7e5d3777defcade38d37b3775401b5d |
|         |            | Windows (x86_64)                      | [Link](https://liveworks-vt.de/downloads/dlive-midi-tools/v2_8_3/dmt-v2_8_3-windows.zip) |               | 3bfcff4d0ed6aa2c3be4fda9651b6593 |
| v2.8.2  | 15.11.2024 | macOS (x86_64 - Intel)                | [Link](https://liveworks-vt.de/downloads/dlive-midi-tools/v2_8_2/dmt-v2_8_2-macos-x86_64.zip) | [Link](#v282) | 41ebc6df4db9ca7ba56d63204cef0ff9 |
|         |            | macOS (arm64 - Apple-Silicon*)        | [Link](https://liveworks-vt.de/downloads/dlive-midi-tools/v2_8_2/dmt-v2_8_2-macos-arm64.zip) |               | 32da0fcfcc13e40fb12c6d2fcfd9c25a |
|         |            | Windows (x86_64)                      | [Link](https://liveworks-vt.de/downloads/dlive-midi-tools/v2_8_2/dmt-v2_8_2-windows.zip) |               | 8886149376e24f3614ae588c5258515b |
| v2.8.0  | 16.07.2024 | macOS (x86_64 - Intel/Apple-Silicon*) | [Link](https://liveworks-vt.de/downloads/dlive-midi-tools/v2_8_0/dmt-v2_8_0-macos-x86_64.zip) | [Link](#v280) | c5b3bc6c563a125e973e75e879002331 |
|         |            | Windows (x86_64)                      | [Link](https://liveworks-vt.de/downloads/dlive-midi-tools/v2_8_0/dmt-v2_8_0-windows.zip) |               | c13c95a79d8ea9fcadbba1a988441c10 |
| v2.7.0  | 24.01.2024 | macOS (x86_64 - Intel/Apple-Silicon*) | [Link](https://liveworks-vt.de/downloads/dlive-midi-tools/v2_7_0/dmt-v2_7_0-macos-x86_64.zip) | [Link](#v270) | 0067242c999b6b44570076fbaed86aa7 |
|         |            | Windows (x86_64)                      | [Link](https://liveworks-vt.de/downloads/dlive-midi-tools/v2_7_0/dmt-v2_7_0-windows.zip) |               | ba57e67e20ee83c249a773cd762ead98 |
| v2.6.0  | 15.12.2023 | macOS (x86_64 - Intel/Apple-Silicon*) | [Link](https://liveworks-vt.de/downloads/dlive-midi-tools/v2_6_0/dmt-v2_6_0-macos-intel.zip) | [Link](#v260) | 420ae04d475091c15cf5094f2c9c5d3a |
|         |            | Windows (x86_64)                      | [Link](https://liveworks-vt.de/downloads/dlive-midi-tools/v2_6_0/dmt-v2_6_0-windows.zip) |               | 6e3d3adf822604d49708a434274c438f |

Older versions see [archive](doc/download-archive.md)

(*) Hints for Apple-Silicon: In combination with Rosetta 2 also compatible for Intel. Newer versions of macOS should have it installed by default. 
    Keep in mind that the first start can take a while.<br><br>
    If you see the following message: <br><br> ![Message](doc/message.png) <br><br>
    Please go to System Preferences -> Privacy and Security -> Security -> Open Anyway <br><br>![Preferences](doc/preferences_privacy.png)
    More infos below in [Usage](#usage)




## Input file / The Spreadsheet Template
Example spreadsheet files for dLive: **dLiveChannelList.xlsx** and Avantis: **AvantisChannelList.xlsx** can be found in the root folder. 
By default, channels 1-128 (dLive) and 1-64 (Avantis) are available in the sheets. If you need less, 
just delete the channels you don't want to process. <br>

You can also write in blocks. e.g. 
* CH1-16
* CH25-32
* CH97-128

in this case, the channels not mentioned are not affected, this works as well for the  `Groups`.

Empty lines in between are **not** supported. <br>

Microsoft Excel and LibreOffice Calc Spreadsheet can be used to write/save the sheets.
Please make sure that you save your changes in the (*.xlsx or *.ods) format.

> **_NOTE:_**  You can add additional columns, like 'Mic Stand', 'Mic/DI', 'Sub-core Patching' etc., but please make sure that the first line keeps the existing fields including their names, otherwise the data can´t be parsed properly. If you want, you can also reorder the columns to your needs.

### Channel Overview
![Channels](doc/channels/excel_channels.png)

More details about the `Channels` columns can be found [here](doc/channels/README.md)

### Sockets Overview
![Sockets](doc/sockets/excel_sockets.png)

More details about the `Sockets` columns can be found [here](doc/sockets/README.md)

### Groups Overview
![Groups](doc/groups/excel_groups.png)

More details about the `Groups` columns can be found [here](doc/groups/README.md)

### Mixer Config
This is a report of used busses. It does not change the "Mixer Config". <br> Please have a look at the yellow box. <br>
It can help you to set the "Mixer Config" properly.

![mixerconfig](doc/mixerconfig/excel_mixerconfig.png)

# Example Generated Reaper Recording Session
If you select the "Generate Reaper Recording Session" checkbox, 
the columns `Name`, `Color`, `Recording`, and `Record Arm` are considered for the template generation process. 

![Reaper](doc/reaper/reaper_demo.png)

# Example Generated Tracks Live Template
If you select the "Generate Tracks Live Template" checkbox, 
the columns `Name`, `Color`, `Recording`, and `Record Arm` are considered for the template generation process.

![Trackslive](doc/trackslive/trackslive_demo.png)

The tool generates a Tracks Live template (*.template), which can be used to create a recording session in Tracks Live

![TracksliveOpenTemplate](doc/trackslive/trackslive_open_template.png)

Click on `Open Template` and select the generated file.


## Settings on the console
The `Midi Channel` setting on dLive under `Utils/Shows -> Control -> Midi` should be set to: `12 to 16`, which is default.

If you want to change the preconfigured Midi port, you can change it in the Graphical User Interface according to your dLive settings. 

## Default IP-Address
The default dLive Mixrack IP-Address is: 192.168.1.70. This IP-Address is preconfigured in the scripts. If you want to 
change it, you can edit the field `ip` in the file: dliveConstants.py or during runtime within the Graphical User Interface.  

Please make sure that your Ethernet or Wi-Fi interface has an IP-Address in the same subnet. e.g. IP: 192.168.1.10 / Subnet: 255.255.255.0
 

## Usage
Prerequisites: 
* Windows >= 10 / macOS >= Monterey
* dLive Firmware: 1.9x / 2.x
* dLive Director: 1.9x / 2.x (Optional)
* Avantis Firmware: 1.30
* Microsoft Excel or LibreOffice Calc Spreadsheet
* Reaper (Optional)
* Tracks Live v1.3 (Optional)
* Python 3.12 (Optional, if you want to build the software yourself)

To run the tool, you have two options:<br><br>
A: Use an available download (see above), unzip it, start the dmt tool and continue with Step 4 <br> If the tool does not start automatically: Try it with "Open with -> Terminal" or run it from terminal.<br><br>
    
   If you see the following message: ![Overview](doc/message.png) <br><br>
   Please go to System Preferences -> Privacy and Security -> Security -> Open Anyway ![Overview](doc/preferences_privacy.png)<br><br>
   Enter your Password and click ![Overview](doc/open-anyway.png)
   Continue with Step 4.
    
B: Build it your own from scratch, using the following steps.<br>

B1. Before you run the script, please run the following command to download the required Python modules using `pip`. Please make sure `pip` is installed.

`pip install -r dependencies.txt`

B2. Run the script with the following command: 

`cd src` <br>
`python3 Main.py`

B3. (Optional) If you want to make a binary out of it, please do the following: 

    B3.1 Installation of pyinstaller

    `pip install pyinstaller`

    B3.2 Create a onefile binary (works for Windows and macOS)

    `pyinstaller -y --onefile -w ./src/Main.py`


4. Afterwards, the following window appears. This can take a couple of seconds.

![Gui](doc/gui.png)

__Recommendation__: Please back up your current show file, just to be on the safe side if something goes wrong.


1. Select the console: `dLive` or `Avantis`

2. Check the (Mixrack-) IP and Midi Port. 

3. `Save` Persists the current settings (console, IP, midi-port) for the next start of the tool.

4. `Director`, sets the IP to 127.0.0.1, to use Director locally on the same machine. Director has to be started before. You can also write to a Director instance running on a different machine, in this case, please use the external IP-Address of this machine where Director is already started and running. (In case of connection issues, please check the firewall rules or disable it temporarily)

5. `Default` Sets the IP back to default: 192.168.1.70.

6. `Test Connection` Tries to establish a test connection to the console. In both cases (successful/failed) you will be informed by a pop-up.

The tool has currently the following modes:
* Spreadsheet to Console / DAW (Continue with next Step) - Reads from a spreadsheet into console or to a DAW Session.
* Console to DAW (Continue with Step 10) - Reads from the console and writes a DAW session.

Choose which mode you want to use:

<img alt="tabs" src="doc/tabs.png" width="300"/>

7. Select the spreadsheet columns you want to write and then select `Write to Audio Console or Director`.
   
   `Select All` selects all checkboxes.
   `Clear` removes all ticks.

8. If you also want to create a DAW Session template (Reaper or Tracks Live), set the corresponding tick. The session files `<input-spreadsheet-file>-reaper-recording-template.rpp` / `<input-spreadsheet-file>-trackslive-recording.template` 
   will be generated into the directory from where the spreadsheet has been chosen. In the `Channels` tab, you can configure which channel shall be recorded and "record armed". The patching is 1:1 (derived from the channel number) <br><br>
   
   The following DAW-based options are available: <br>
   * Disable Track Numbering <br>
   * Disable Track Coloring <br>
   * An additional custom track prefix can also be added.<br>
   * Add two additional mono busses to record your mixing sum.

<br><br>
> **_NOTE:_**  You can also use the tool to create only the DAW session file (Reaper or Tracks Live), in case you use a different audio console. In this case, disable the checkbox "Write to Audio Console or Director", choose your DAW and continue with Step 10.<br><br>


9. `Generate Director CSV (Columns: Name, Color, Source, Socket, Gain, Pad, Phantom)` Generates a CSV file for Director incl. Name, Color, Patching, Gain, Pad, Phantom, using the Director CSV Import function, you can use this as a baseline for the MIDI based parameters. 

<img alt="director-main-system" src="doc/directorcsv/director-main-system.png" width="150"/>

<img alt="director-import-export" src="doc/directorcsv/director-import-export.png" width="300"/>

> **_NOTE:_** This feature uses the columns Name, Color, Source, Socket, Gain, Pad, Phantom from the `Channels` Tab. 



10. Click the button `Open spreadsheet and start writing process` to select the spreadsheet. Afterwards, the selected action(s) start automatically.
   
   **Recommendation:** Please test it first with the delivered spreadsheet to make sure everything works properly.

11. Console to DAW - Generates a DAW session from the current console settings. This can be triggered even later, when an existing show is available on the console. This process doesn´t need a spreadsheet. 

<img alt="consoletodaw" src="doc/console-to-daw.png" width="600"/>

Options:
   * Choose `Start` and `End` channel to be used for DAW generation.
   * Disable Track Numbering <br>
   * Disable Track Coloring <br>
   * An additional custom track prefix can also be added.<br>
   * Add two additional mono busses to record your mixing sum.

Click `Generate DAW session(s) from current console settings`

12. If something goes wrong, please check the Python console or the `main.log`

If you find any issues, please let me know. New ideas are welcome. 

Have fun!

## Feedback
If you want to give feedback, report an issue or contribute (new ideas, coding, testing, documentation) please use the following mail address: <br>
dmt@liveworks-vt.de or the following [Link](https://github.com/togrupe/dlive-midi-tools/discussions)

## Troubleshooting

| Problem                              | Possible Solution                                                                               | 
|--------------------------------------|-------------------------------------------------------------------------------------------------|
| Console to DAW Feature seems to hang | Please make sure, the MIDI Channel on the Audio console fits to the settings in the tool. <br> You can find the MIDI Settings under "Utils/Shows -> Control -> Midi" |


## Release Notes

### v2.8.3

Maintenance Release

#### New Features

#### Improvements
- Button size fixed
- Apple-Silicon (arm64) version officially added
- Build on python12 (macOS Intel, macOS Apple-Silicon, Windows)
- Documentation improved

#### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

#### Issues fixed

#### Known issues

### v2.8.2

Maintenance Release

#### New Features

#### Improvements
- Hint for CSV Patch via Director only shown once per session.

#### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

#### Issues fixed

#### Known issues

### v2.8.0

Feature & Maintenance Release

#### New Features
- dLive Director CSV Support for V2.00

#### Improvements
- Code refactoring


#### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

#### Issues fixed

#### Known issues


### v2.7.0

Feature & Maintenance Release

#### New Features
- Console to DAW Recording Session


#### Improvements
- Switched to tab based GUI
- Handling of invalid IP-Addresses
- Repository reorganized


#### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

#### Issues fixed

#### Known issues

### v2.6.0

Feature & Maintenance Release

#### New Features
- Tracks Live Support (Template Generation)
- Possibility to disable track coloring
- Channel to Main Mix Assignments
- Bypass feature for DCAs and Mute Groups added


#### Improvements
- Support for spaces in track names for Reaper


#### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

#### Issues fixed

#### Known issues

### v2.5.0

Feature & Maintenance Release

#### New Features
- Bypass feature on channels, sockets, and groups sheet added
- Possibility to disable track numbering
- Possibility to add two additional master tracks
- Possibility to add a custom track prefix

#### Improvements
- Gain value mapping improved - gain values are now more accurate.

#### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently due to technical limitation not possible.
- HPF on, HPF value and Mute Groups for Avantis due to technical limitation currently not possible.

#### Issues fixed

#### Known issues


### v2.4.1

Maintenance Release

#### Issues fixed
- spreadsheet template formula fixed at cell AT2

#### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently due to technical limitation not possible.
- HPF on, HPF value and Mute Groups for Avantis due to technical limitation currently not possible.

### v2.4.0

Feature & Maintenance Release

#### New Features
- DCA Name & Color
- Aux Name & Color
- Group Name & Color
- Matrices Name & Color
- FX Sends Name & Color
- FX Returns Name & Color
- Current Processing Action now shown in UI
- Test Connection Button added
- Select All Button added
- Clear Button added

#### Improvements
- HPF Value Formula improved
- Channels > 64 skipped for Avantis
- UI Error Handling improved
- Repository reorganized
- Spreadsheet improved (Mixer Config report, DCA names) 

#### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently due to technical limitation not possible.
- HPF on, HPF value and Mute Groups for Avantis due to technical limitation currently not possible.

#### Issues fixed

#### Known issues



### v2.3.0

Feature Release

#### New Features
- Fader Level Support
- Gain Support
- DCA Support
- Mute Group Support (dLive only)
- HPF On Support (dLive only)
- HPF Value Support (dLive only)

#### Improvements
- Progress Bar improved
- Infobox for missing Avantis features added
- Checkbox Groups introduced
- Checkbox Group "Select All" added
- IP-Address Label is now dynamic
- Processing accelerated


#### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently due to technical limitation not possible.
- HPF on, HPF value and Mute Groups for Avantis due to technical limitation currently not possible.

#### Issues fixed

#### Known issues


### v2.2.0

Feature Release

#### New Features
- Avantis support
- Director button introduced
- Save button added, to persist data
- Default button added, to set back the ip to default
- Recordable & Record Arm feature added
- Reaper template is now generated right next to the chosen spreadsheet with the same name as prefix

#### Technical Limitations
- DX2 (Pad/Phantom) for Avantis via SLink is currently due to technical limitation not possible.

#### Issues fixed
- Temporary GUI freeze fixed

#### Improvements
- Robustness improved

#### Known issues
