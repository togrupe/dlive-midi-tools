# dlive-midi-tools
Python, midi and tcpip based tool to prepare channel lists for Allen &amp; Heath dlive systems.

Input file: Excel sheet, Please edit the columns: Name, Color and Phantom

An example excel file named: dLiveChannelList.xls can be found in the root folder. 

The following colors are allowed:
blue, red, light blue, magenta, green, yellow, black, white

The Midi Channel setting on dlive under Utils/Shows -> Control -> Midi has to be: 1 to 5

The default mixrack ip address is: 192.168.1.70. This ip is preconfigured as well the the scripts. If you want to change it, you can edit the field "ip" in the file: dliveConstants.py.   
