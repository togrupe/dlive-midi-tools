# Release Notes

## v2.13.0

Feature Release

### New Features
- **Extended console support — SQ, DM7, Wing, M32/X32, QU** via Mixing Station REST API (HTTP port 8080):
  - Spreadsheet → Console: Name, Color, Mute, Fader Level
  - Console to DAW: reads channel names and colors (up to 99 channels)
  - Select the desired console type in the console dropdown; enter Mixing Station host IP and port in the connection bar
  - Each console type uses its own color mapping
  - Spreadsheet template [MixingStationChannelList.xlsx](../MixingStationChannelList.xlsx) added
- **Print / Export Channel List as PDF** — available in the **Utilities** tab:
  - `Export Channel List as PDF` — reads current channel list from the console or Mixing Station and saves a formatted PDF to a chosen location
  - `Print Channel List` — same read, opens the PDF in the system's default PDF viewer for direct printing
  - Channel color is rendered as a colored cell in the PDF
  - No spreadsheet required; uses the channel Start / End range selectors in the Console to DAW tab

### Improvements

### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, Group Assignments and Mute Groups for Avantis are currently not possible due to technical limitations on API.

### Issues Fixed

### Known Issues

---

## v2.12.0

Feature Release

### New Features
- UFX Name & Color Support for Avantis
- Spreadsheet Validator — validates channel and group names, colors, fader levels, HPF range, channel range, Source field (dLive & Avantis)
- Utilities Tab with the following actions (direct console communication, no spreadsheet required):
  - RESET all DCA Assignments
  - RESET all Mute Group Assignments (dLive only)
  - RESET all Main Mix Assignments
  - MUTE all Inputs / UNMUTE all Inputs
  - MUTE all Outputs / UNMUTE all Outputs
  - Set all Input Faders to 0 dB
  - Set all Input Faders to -inf
  - Phantom Power OFF (all Sockets)

### Improvements
- Redesigned UI — fits on 1440×900 screens without scrolling (also works on Full HD and larger)
- Dark / Light mode toggle added (via Settings menu), persisted across restarts
- Connection Settings consolidated into a single row (Console, MIDI Channel, IP and buttons in one line)
- Status bar redesigned with horizontal layout (label left, progress right)
- Allowed character validation for channel and group names
- Source field validation per console type (dLive / Avantis)

### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, Group Assignments and Mute Groups for Avantis are currently not possible due to technical limitations on API.

### Issues Fixed

### Known Issues

---

## v2.11.0

Feature Release

### New Features
- Channel to Group (Mono/Stereo) Assignments

### Improvements
- Enabled flag is now also effective for CSV Generation

### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, Group Assignments and Mute Groups for Avantis are currently not possible due to technical limitations on API.

### Issues Fixed

### Known Issues

---

## v2.10.0

Feature Release

### New Features
- "Enabled" Field introduced — to include or exclude lines from data processing

### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

### Issues Fixed

### Known Issues

---

## v2.9.0

Feature Release

### New Features
- UFX Name & Color Support

### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

### Issues Fixed

### Known Issues

---

## v2.8.3

Maintenance Release — Python 3.12 based binaries for all platforms

### Improvements
- Apple-Silicon (arm64) version officially added
- Binaries built on Python 3.12 (macOS Intel & Apple-Silicon, Windows) to be more future-proof
- 3rd party libraries updated
- Documentation improved

### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

### Issues Fixed
- On some systems, there was a strange mouse click behaviour
- Pad handling issue fixed
- Button size fixed

### Known Issues

---

## v2.8.2

Maintenance Release

### Improvements
- Hint for CSV Patch via Director only shown once per session.

### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

### Issues Fixed

### Known Issues

---

## v2.8.0

Feature & Maintenance Release

### New Features
- dLive Director CSV Support for V2.00

### Improvements
- Code refactoring

### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

### Issues Fixed

### Known Issues

---

## v2.7.0

Feature & Maintenance Release

### New Features
- Console to DAW Recording Session

### Improvements
- Switched to tab-based GUI
- Handling of invalid IP addresses
- Repository reorganized

### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

### Issues Fixed

### Known Issues

---

## v2.6.0

Feature & Maintenance Release

### New Features
- Tracks Live Support (Template Generation)
- Possibility to disable track coloring
- Channel to Main Mix Assignments
- Bypass feature for DCAs and Mute Groups added

### Improvements
- Support for spaces in track names for Reaper

### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

### Issues Fixed

### Known Issues

---

## v2.5.0

Feature & Maintenance Release

### New Features
- Bypass feature on channels, sockets, and groups sheet added
- Possibility to disable track numbering
- Possibility to add two additional master tracks
- Possibility to add a custom track prefix

### Improvements
- Gain value mapping improved — gain values are now more accurate.

### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

### Issues Fixed

### Known Issues

---

## v2.4.1

Maintenance Release

### Issues Fixed
- Spreadsheet template formula fixed at cell AT2

### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

---

## v2.4.0

Feature & Maintenance Release

### New Features
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

### Improvements
- HPF Value Formula improved
- Channels > 64 skipped for Avantis
- UI Error Handling improved
- Repository reorganized
- Spreadsheet improved (Mixer Config report, DCA names)

### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

### Issues Fixed

### Known Issues

---

## v2.3.0

Feature Release

### New Features
- Fader Level Support
- Gain Support
- DCA Support
- Mute Group Support (dLive only)
- HPF On Support (dLive only)
- HPF Value Support (dLive only)

### Improvements
- Progress Bar improved
- Infobox for missing Avantis features added
- Checkbox Groups introduced
- Checkbox Group "Select All" added
- IP-Address Label is now dynamic
- Processing accelerated

### Technical Limitations
- DX2 (Pad/Phantom/Gain) for Avantis via SLink is currently not possible due to technical limitations on API.
- HPF on, HPF value, and Mute Groups for Avantis are currently not possible due to technical limitations on API.

### Issues Fixed

### Known Issues

---

## v2.2.0

Feature Release

### New Features
- Avantis support
- Director button introduced
- Save button added, to persist data
- Default button added, to set back the IP to default
- Recordable & Record Arm feature added
- Reaper template is now generated next to the chosen spreadsheet with the same name as prefix

### Improvements
- Robustness improved

### Technical Limitations
- DX2 (Pad/Phantom) for Avantis via SLink is currently not possible due to technical limitations on API.

### Issues Fixed
- Temporary GUI freeze fixed

### Known Issues
