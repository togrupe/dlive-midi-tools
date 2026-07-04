# How-To: Mixing Station Integration

This guide explains how to use dmt with a console connected via **Mixing Station Desktop** running on the same PC/Mac as dmt (e.g. an A&H SQ).

> **Note:** The workflow labels used here (C, E) refer to the same workflows defined in the [Workflows & Overview](workflows.md) document.

Supported console types: **SQ, DM7, Wing, M32/X32, QU**

---

## Prerequisites

- [Mixing Station Desktop](https://mixingstation.app) installed and running on the same machine as dmt
- HTTP REST API enabled in Mixing Station: **Global Settings → API: HTTP REST** (without Pro license the API stops after 15 minutes)
- The console reachable from that machine over the local network

---

## Workflow C — Spreadsheet → Mixing Station → Console

**1. Prepare the spreadsheet**

Use [MixingStationChannelList.xlsx](../MixingStationChannelList.xlsx) as the template. Fill in the columns you want to write — only these are supported via Mixing Station:

| Column | Notes |
|--------|-------|
| Name | Max 6 characters (SQ) |
| Color | `black`, `red`, `green`, `blue`, `light blue`, `yellow`, `purple`, `white` |
| Mute | `yes` = muted, `no` = unmuted |
| Fader Level | dB value, e.g. `0`, `-10`, `-99` for −inf |

**2. Configure dmt**

- Console dropdown → **Mixing Station**
- Type dropdown → your console type (e.g. **SQ**)
- IP → `127.0.0.1` (Mixing Station runs locally), port → `8080` (default)
- Click **Test Connection**

**3. Write to console**

Select the parameters to write (Name / Color / Mute / Fader Level), click **Open Spreadsheet and Start Writing Process**, and select your file. dmt validates, then sends each parameter to Mixing Station, which applies it to the console in real time.

---

## Workflow E — Console → DAW (read from Mixing Station)

Switch to the **Console to DAW** tab, set Start/End channel, and click **Generate DAW Session(s) from Current Console Settings**. dmt reads name and color from Mixing Station and writes a Reaper or Tracks Live session file (max 99 channels).

---

## PDF Export

In the **Utilities** tab, click **Export Channel List as PDF** or **Print Channel List**. Channel range from the Console to DAW tab applies.

---

## Troubleshooting

| Problem | Check |
|---------|-------|
| Test Connection fails | REST API enabled? Is `127.0.0.1:8080` correct? |
| No changes on console | Is Mixing Station connected to the console? |
| Name truncated | SQ limit is 6 characters — shorten the name in the spreadsheet |
| Wrong colors | Correct console sub-type selected in the Type dropdown? |

---

← [back](../README.md)
