# Troubleshooting

| Problem | Possible Solution |
|---------|-------------------|
| Console to DAW feature seems to hang | Make sure the MIDI Channel on the audio console matches the setting in the tool. You can find the MIDI settings under `Utils/Shows → Control → MIDI`. |
| Input to Group Routing for MGrp1 is weird | Writing beyond the buses defined in the mixer configuration can lead to internal errors, which can cause strange routings in MGrp1. To avoid this, use "-" by default for all routings and set "x" only where routing is actually required. |
| Test Connection fails | Check that the console is powered on and reachable on the network. Make sure your computer's IP is in the same subnet as the console (e.g. `192.168.1.x` for the default dLive address). Temporarily disable any firewall. For Mixing Station, ensure the REST API is enabled under Settings → Remote Control → HTTP API. |
| No parameters are written to the console | Verify the MIDI channel in the console matches the tool setting. Check that "Write to Audio Console or Director" is enabled. Use **Test Connection** to confirm the link first. |
| Mixing Station does not respond | Confirm the REST API is enabled in Mixing Station (Settings → Remote Control → HTTP API) and that the port (default: 8080) matches the tool. Verify the host IP is correct and the device running Mixing Station is on the same network. |
| Spreadsheet validation error on startup | Read the error summary shown by the tool. Common causes: special characters in channel names (`äöüéß` are not allowed), unsupported color value, fader level out of range, or channel number exceeding the console maximum (128 for dLive, 64 for Avantis, 99 for Mixing Station). |
| macOS: tool does not start after download | Go to System Preferences → Privacy and Security → Security → Open Anyway. See [Running the Tool](usage.md#running-the-tool) for screenshots. |
| Tool is slow to start on first launch (macOS) | Expected behavior on Apple Silicon with the x86_64 build running under Rosetta 2. Subsequent launches are faster. |
| PDF export is empty or channel names are missing | Confirm the console is reachable (use **Test Connection**). Check that the Start/End channel range in the Console to DAW tab matches the range of channels configured on the console. |
| Wrong colors appear after writing | Ensure the spreadsheet uses the exact color strings listed in [Channels](channels/README.md#color) (`blue`, `red`, `light blue`, `purple`, `green`, `yellow`, `black`, `white`). For Mixing Station, the correct console sub-type must be selected so the right color map is used. |

If you cannot find a solution here, open a thread in [GitHub Discussions](https://github.com/togrupe/dlive-midi-tools/discussions) or contact dmt@liveworks-vt.de.
