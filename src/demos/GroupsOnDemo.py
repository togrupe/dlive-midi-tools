import mido
from mido.sockets import connect

import dliveConstants

if __name__ == '__main__':
    #Mono Groups 1 to 62: N = N + 1, CH = 00 to 3D
    #Stereo Groups 1 to 31: N = N + 1, CH = 40 to 5E

    #Sysex Header, 0N, 0E, CH, SndN, SndCH, V, F7

    # Where SndN and SndCH are the MIDI channel and note number for the channel to be sent to.

    #V On value = 40 to 7F

    midi_channel = 11 # Midi Channel 12 to 16
    dsp_channel = 0  # Channel 1

    SndN = (midi_channel + dliveConstants.midi_channel_offset_groups)  # Groups MGrp & StGrp

    SndCh = 0x00  #MGrp1
    #SndCh = 0x03  #MGrp4
    #SndCh = 0x3D# MGrp62

    #SndCh = 0x40# StGrp1
    #SndCh = 0x47  # StGrp7
    #SndCh = 0x5E# StGrp31

    value = 0x7F  # on
    #value = 0x0 # off

    prefix = [midi_channel, dliveConstants.sysex_message_set_groups_on, dsp_channel, SndN, SndCh]

    message = mido.Message.from_bytes(dliveConstants.sysexhdrstart + prefix + [value] + dliveConstants.sysexhdrend)

    output = connect("127.0.0.1", dliveConstants.port)

    output.send(message)
