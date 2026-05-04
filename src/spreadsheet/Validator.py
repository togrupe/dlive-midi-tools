# coding=utf-8
import dliveConstants
from spreadsheet import SpreadsheetConstants

_VALID_COLORS = {
    SpreadsheetConstants.spreadsheet_color_black,
    SpreadsheetConstants.spreadsheet_color_blue,
    SpreadsheetConstants.spreadsheet_color_light_blue,
    SpreadsheetConstants.spreadsheet_color_red,
    SpreadsheetConstants.spreadsheet_color_yellow,
    SpreadsheetConstants.spreadsheet_color_green,
    SpreadsheetConstants.spreadsheet_color_purple,
    SpreadsheetConstants.spreadsheet_color_white,
}

_VALID_FADER_LEVELS = {'10', '5', '0', '-5', '-10', '-15', '-20', '-25', '-30', '-35', '-40', '-45', '-99'}

_VALID_GAIN_LEVELS = {'5', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55', '60'}

_VALID_YES_NO = {'yes', 'no'}

_VALID_SOURCE_DLIVE = {
    'Unassigned', 'MixRack', 'Surface', 'Surface DX 5/6',
    'IO 4', 'IO 5', 'USB',
    'MixRack DX 1/2', 'MixRack DX 3/4',
    'IO 1', 'IO 2', 'IO 3', 'SigGen',
}

_VALID_SOURCE_AVANTIS = {
    'Unassigned', 'Surface', 'SLink',
    'IO 1', 'IO 2', 'SigGen',
}

_VALID_TOGGLE = {'x'}

_BYPASS = {SpreadsheetConstants.spreadsheet_bypass_sign, SpreadsheetConstants.spreadsheet_bypass_string}

_NAN = 'nan'

_ALLOWED_CHARS = frozenset([
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    ' ', '!', '"', '#', '%', '&', "'", '(', ')', '*', '+', ',', '-',
    '.', '/', '<', '=', '>', '?', '@', '[', '\\', ']', '_', '{', '}', '~',
])


def _invalid_chars(text):
    """Return a set of characters in text that are not in _ALLOWED_CHARS."""
    return set(text) - _ALLOWED_CHARS


def _skip(value):
    return value in _BYPASS or value == _NAN


def _validate_channels(channel_entries, console, errors):
    max_ch = (dliveConstants.AVANTIS_MAX_CHANNELS
              if console == dliveConstants.console_drop_down_avantis
              else dliveConstants.DLIVE_MAX_CHANNELS)

    for entry in channel_entries:
        ch = entry.get_channel()
        p = f"Channels CH{ch}:"

        if ch < 1 or ch > max_ch:
            errors.append(f"{p} channel number {ch} out of range (1-{max_ch})")

        name = str(entry.get_name())
        if not _skip(name.lower()):
            bad = _invalid_chars(name)
            if bad:
                errors.append(f"{p} name '{name}' contains invalid character(s): {sorted(bad)}")

        source = str(entry.get_source())
        if not _skip(source.lower()):
            valid_sources = (_VALID_SOURCE_DLIVE
                             if console != dliveConstants.console_drop_down_avantis
                             else _VALID_SOURCE_AVANTIS)
            if source not in valid_sources:
                errors.append(f"{p} invalid Source '{source}'")

        color = entry.get_color().lower()
        if not _skip(color) and color not in _VALID_COLORS:
            errors.append(f"{p} invalid color '{entry.get_color()}'")

        mute = str(entry.get_mute()).lower()
        if not _skip(mute) and mute not in _VALID_YES_NO:
            errors.append(f"{p} invalid Mute value '{entry.get_mute()}' (expected yes/no)")

        hpf_on = str(entry.get_hpf_on()).lower()
        if not _skip(hpf_on) and hpf_on not in _VALID_YES_NO:
            errors.append(f"{p} invalid HPF On value '{entry.get_hpf_on()}' (expected yes/no)")

        hpf_val = str(entry.get_hpf_value())
        if not _skip(hpf_val.lower()):
            try:
                v = int(hpf_val)
                if not (dliveConstants.hpf_min_frequency <= v <= dliveConstants.hpf_max_frequency):
                    errors.append(
                        f"{p} HPF Value {v} out of range "
                        f"({dliveConstants.hpf_min_frequency}-{dliveConstants.hpf_max_frequency} Hz)"
                    )
            except ValueError:
                errors.append(f"{p} invalid HPF Value '{hpf_val}' (must be an integer)")

        fader = str(entry.get_fader_level())
        if not _skip(fader.lower()) and fader not in _VALID_FADER_LEVELS:
            errors.append(f"{p} invalid fader level '{fader}'")

        mainmix = str(entry.get_assign_mainmix()).lower()
        if not _skip(mainmix) and mainmix not in _VALID_YES_NO:
            errors.append(f"{p} invalid Main Mix value '{entry.get_assign_mainmix()}' (expected yes/no)")

        if entry.get_dca_config() is not None:
            for i, val in enumerate(entry.get_dca_config().get_dca_array()):
                v = val.lower()
                if not _skip(v) and v not in _VALID_TOGGLE:
                    errors.append(f"{p} invalid DCA{i + 1} value '{val}' (expected x)")

        if entry.get_mg_config() is not None:
            for i, val in enumerate(entry.get_mg_config().get_mg_array()):
                v = val.lower()
                if not _skip(v) and v not in _VALID_TOGGLE:
                    errors.append(f"{p} invalid Mute Group {i + 1} value '{val}' (expected x)")

        if entry.get_mono_group_config() is not None:
            for i, val in enumerate(entry.get_mono_group_config().get_mono_group_array()):
                v = val.lower()
                if not _skip(v) and v not in _VALID_TOGGLE:
                    errors.append(f"{p} invalid Mono Group {i + 1} value '{val}' (expected x)")

        if entry.get_stereo_group_config() is not None:
            for i, val in enumerate(entry.get_stereo_group_config().get_stereo_group_array()):
                v = val.lower()
                if not _skip(v) and v not in _VALID_TOGGLE:
                    errors.append(f"{p} invalid Stereo Group {i + 1} value '{val}' (expected x)")


def _validate_sockets(socket_entries, errors):
    for entry in socket_entries:
        sn = entry.get_socket_number()
        p = f"Sockets Socket{sn}:"

        for label, val in [
            ("Local Phantom", entry.get_local_phantom()),
            ("DX1 Phantom",   entry.get_dx1_phantom()),
            ("DX3 Phantom",   entry.get_dx3_phantom()),
            ("Slink Phantom", entry.get_slink_phantom()),
            ("Local Pad",     entry.get_local_pad()),
            ("DX1 Pad",       entry.get_dx1_pad()),
            ("DX3 Pad",       entry.get_dx3_pad()),
            ("Slink Pad",     entry.get_slink_pad()),
        ]:
            v = str(val).lower()
            if not _skip(v) and v not in _VALID_YES_NO:
                errors.append(f"{p} invalid {label} value '{val}' (expected yes/no)")

        for label, val in [
            ("Local Gain", entry.get_local_gain()),
            ("DX1 Gain",   entry.get_dx1_gain()),
            ("DX3 Gain",   entry.get_dx3_gain()),
            ("Slink Gain", entry.get_slink_gain()),
        ]:
            v = str(val).lower()
            if not _skip(v) and v not in _VALID_GAIN_LEVELS:
                errors.append(f"{p} invalid {label} value '{val}'")


def _validate_groups(groups_entry, errors):
    sections = [
        ("DCA",          groups_entry.get_dca_config()),
        ("Aux Mono",     groups_entry.get_auxes_mono_config()),
        ("Aux Stereo",   groups_entry.get_auxes_stereo_config()),
        ("Group Mono",   groups_entry.get_group_mono_config()),
        ("Group Stereo", groups_entry.get_group_stereo_config()),
        ("Matrix Mono",  groups_entry.get_matrix_mono_config()),
        ("Matrix Stereo",groups_entry.get_matrix_stereo_config()),
        ("FX Send Mono", groups_entry.get_fx_send_mono_config()),
        ("FX Send Stereo",groups_entry.get_fx_send_stereo_config()),
        ("FX Return",    groups_entry.get_fx_return_config()),
        ("UFX Send",     groups_entry.get_ufx_send_config()),
        ("UFX Return",   groups_entry.get_ufx_return_config()),
    ]

    for section_name, entries in sections:
        for entry in entries:
            p = f"Groups {section_name} #{entry.get_channel()}:"

            name = str(entry.get_name())
            if not _skip(name.lower()):
                bad = _invalid_chars(name)
                if bad:
                    errors.append(f"{p} name '{name}' contains invalid character(s): {sorted(bad)}")

            color = str(entry.get_color()).lower()
            if not _skip(color) and color not in _VALID_COLORS:
                errors.append(f"{p} invalid color '{entry.get_color()}'")


def validate(sheet, console):
    """Return a list of human-readable error strings; empty list means the sheet is valid."""
    errors = []
    _validate_channels(sheet.get_channel_model(), console, errors)
    _validate_sockets(sheet.get_socket_model(), errors)
    _validate_groups(sheet.get_group_model(), errors)
    return errors
