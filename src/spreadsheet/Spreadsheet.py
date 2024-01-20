# coding=utf-8
####################################################
# Methods for spreadsheet handling
#
# Author: Tobias Grupe
#
####################################################

from model.ChannelListEntry import ChannelListEntry
from model.DcaConfig import DcaConfig
from model.GroupSetup import GroupSetup
from model.GroupsListEntry import GroupsListEntry
from model.Misc import Misc
from model.MuteGroupConfig import MuteGroupConfig
from model.SocketListEntry import SocketListEntry


def extract_data(list_entries, sheet_groups, type_name, name, color):
    index = 0
    for item in sheet_groups[type_name]:
        if str(item) != 'nan':
            gse = GroupSetup(int(item),
                             str(sheet_groups[name].__getitem__(index)),
                             str(sheet_groups[color].__getitem__(index))
                             )

            list_entries.append(gse)
            index = index + 1


def create_channel_list_content(sheet_channels):
    channel_list_entries = []
    index = 0

    for channel in sheet_channels['Channel']:

        dca_array = []
        for dca_number in range(1, 25):
            dca_array.append(str(sheet_channels["DCA" + str(dca_number)].__getitem__(index)))

        dca_config_tmp = DcaConfig(dca_array)

        mg_array = []
        for mg_number in range(1, 9):
            mg_array.append(str(sheet_channels["Mute" + str(mg_number)].__getitem__(index)))

        mg_config_tmp = MuteGroupConfig(mg_array)

        cle = ChannelListEntry(int(channel),
                               str(sheet_channels['Name'].__getitem__(index)),
                               str(sheet_channels['Color'].__getitem__(index)),
                               str(sheet_channels['HPF On'].__getitem__(index)),
                               str(sheet_channels['HPF Value'].__getitem__(index)),
                               str(sheet_channels['Fader Level'].__getitem__(index)),
                               str(sheet_channels['Mute'].__getitem__(index)),
                               str(sheet_channels['Recording'].__getitem__(index)),
                               str(sheet_channels['Record Arm'].__getitem__(index)),
                               dca_config_tmp,
                               mg_config_tmp,
                               str(sheet_channels['Main Mix'].__getitem__(index))
                               )
        channel_list_entries.append(cle)
        index = index + 1
    return channel_list_entries


def create_misc_content(sheet_misc):
    misc = Misc()
    sheet_version = None
    index = 0
    for property_item in sheet_misc['Property']:
        if str(property_item).strip() == "Version":
            sheet_version = str(sheet_misc['Value'].__getitem__(index)).strip()

    misc.set_version(sheet_version)
    return misc


def create_socket_list_content(sheet_sockets):
    socket_list_entries = []
    index = 0

    for socket in sheet_sockets['Socket Number']:
        ple = SocketListEntry(int(socket),
                              str(sheet_sockets['Local Phantom'].__getitem__(index)),
                              str(sheet_sockets['DX1 Phantom'].__getitem__(index)),
                              str(sheet_sockets['DX3 Phantom'].__getitem__(index)),
                              str(sheet_sockets['Local Pad'].__getitem__(index)),
                              str(sheet_sockets['DX1 Pad'].__getitem__(index)),
                              str(sheet_sockets['DX3 Pad'].__getitem__(index)),
                              str(sheet_sockets['Slink Phantom'].__getitem__(index)),
                              str(sheet_sockets['Slink Pad'].__getitem__(index)),
                              str(sheet_sockets['Local Gain'].__getitem__(index)),
                              str(sheet_sockets['DX1 Gain'].__getitem__(index)),
                              str(sheet_sockets['DX3 Gain'].__getitem__(index)),
                              str(sheet_sockets['Slink Gain'].__getitem__(index)),
                              )

        socket_list_entries.append(ple)
        index = index + 1
    return socket_list_entries


def create_groups_list_content(sheet_groups):
    dca_list_entries = []
    extract_data(dca_list_entries, sheet_groups, 'DCA', 'DCA Name', 'DCA Color')

    aux_mono_list_entries = []
    extract_data(aux_mono_list_entries, sheet_groups, 'Mono Auxes', 'Aux Name', 'Aux Color')

    aux_stereo_list_entries = []
    extract_data(aux_stereo_list_entries, sheet_groups, 'Stereo Auxes', 'StAux Name', 'StAux Color')

    grp_mono_list_entries = []
    extract_data(grp_mono_list_entries, sheet_groups, 'Mono Group', 'Group Name', 'Group Color')

    grp_stereo_list_entries = []
    extract_data(grp_stereo_list_entries, sheet_groups, 'Stereo Group', 'StGroup Name', 'StGroup Color')

    mtx_mono_list_entries = []
    extract_data(mtx_mono_list_entries, sheet_groups, 'Mono Matrix', 'Matrix Name', 'Matrix Color')

    mtx_stereo_list_entries = []
    extract_data(mtx_stereo_list_entries, sheet_groups, 'Stereo Matrix', 'StMatrix Name', 'StMatrix Color')

    fx_send_mono_list_entries = []
    extract_data(fx_send_mono_list_entries, sheet_groups, 'Mono FX Send', 'FX Name', 'FX Color')

    fx_send_stereo_list_entries = []
    extract_data(fx_send_stereo_list_entries, sheet_groups, 'Stereo FX Send', 'StFX Name', 'StFX Color')

    fx_return_list_entries = []
    extract_data(fx_return_list_entries, sheet_groups, 'FX Return', 'FX Return Name', 'FX Return Color')

    return GroupsListEntry(dca_list_entries,
                           aux_mono_list_entries,
                           aux_stereo_list_entries,
                           grp_mono_list_entries,
                           grp_stereo_list_entries,
                           mtx_mono_list_entries,
                           mtx_stereo_list_entries,
                           fx_send_mono_list_entries,
                           fx_send_stereo_list_entries,
                           fx_return_list_entries)


def create_channel_list_content_from_console(data_fin):
    channel_list_entries = []
    index = 0

    for item in data_fin:
        cle = ChannelListEntry(item['dliveChannel'],
                               item['name'],
                               item['color'],
                               None,
                               None,
                               None,
                               None,
                               'yes',
                               'yes',
                               None,
                               None,
                               None)

        channel_list_entries.append(cle)
        index = index + 1

    return channel_list_entries