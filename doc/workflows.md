# Workflows & Overview

This document describes the five main workflows supported by **dLive MIDI Tools (dmt)**.
All workflows share the central **Channel List Manager** tool and connect to one or more
external targets (console, Director, Mixing Station, DAW).

The original full overview diagram is available as `doc/overview.drawio.svg` /
`doc/overview.drawio.png`.

---

## Workflow A – Spreadsheet → Console / DAW (dLive / Avantis)

Apply channel list data directly to a connected dLive or Avantis console via MIDI over TCP.
Optionally generate DAW recording session files in the same run.

```mermaid
flowchart TD
    TMPL["Channel List Template\n(.xlsx / .ods)"]

    subgraph dmt["Channel List Manager"]
        PARSE["Parse Spreadsheet\npandas / openpyxl / odfpy"]
        VALIDATE{"Validate\nnames · colors · fader\nHPF range · channel range"}
    end

    ERR["Errors shown to user\nProcessing stops"]

    subgraph console_out["Console Output (optional)"]
        MIDI["Write Parameters\nMIDI over TCP · port 51325"]
    end

    subgraph daw_out["DAW Session Output (optional)"]
        REAPER["Reaper Session (.rpp)"]
        TL["Tracks Live Template (.template)"]
    end

    subgraph csv_out["Director CSV Output (optional)"]
        CSVGEN["Generate Director CSV (.csv)"]
    end

    FOH["FOH Console\ndLive / Avantis"]
    ADD["Additional Console\nMonitor / Broadcast"]
    DIRECTOR["dLive / Avantis Director\nOffline Software"]
    DAW["Recording Tools\nReaper / Tracks Live"]
    VCHECK["Virtual Soundcheck\nDante / Waves Soundgrid"]

    TMPL --> PARSE
    PARSE --> VALIDATE
    VALIDATE -->|"invalid"| ERR
    VALIDATE -->|"valid"| MIDI
    VALIDATE -->|"valid"| REAPER
    VALIDATE -->|"valid"| TL
    VALIDATE -->|"valid"| CSVGEN
    MIDI -->|"MIDI/TCP"| FOH
    MIDI -->|"MIDI/TCP"| ADD
    REAPER --> DAW
    TL --> DAW
    CSVGEN --> DIRECTOR
    FOH -.->|"audio routing"| VCHECK
    ADD -.->|"audio routing"| VCHECK
    VCHECK -.->|"virtual soundcheck"| DAW
```

### Step Sequence

| Step | Action |
|------|--------|
| A1 | Open Channel List Template (.xlsx / .ods) on PC / Mac |
| A2 | *(Optional)* Pre-configure names in dLive / Avantis Director offline first |
| A3 | Channel List Manager parses the spreadsheet |
| A4 | Validator checks names, colors, fader levels, HPF values, channel range |
| A5a | Write channel parameters to FOH console via MIDI/TCP |
| A5b | *(Optional)* Write to additional console (Monitor / Broadcast) |
| A6a | *(Optional)* Generate Reaper recording session (.rpp) |
| A6b | *(Optional)* Generate Tracks Live template (.template) |

### Output Options (configurable in tool)

| Checkbox | Output |
|----------|--------|
| Write to Audio Console or Director | Sends MIDI over TCP to console |
| Generate Director CSV | Creates `.csv` for Director import |
| Generate Reaper Session | Creates `.rpp` session file |
| Generate Tracks Live Template | Creates `.template` file |

**Prerequisites:** Console reachable at the configured IP address on port 51325.

---

## Workflow B – Spreadsheet → Director CSV

Generate a Director-compatible CSV file from the spreadsheet for offline import into
dLive or Avantis Director — no live console connection required.

```mermaid
flowchart TD
    TMPL["Channel List Template\n(.xlsx / .ods)"]

    subgraph dmt["Channel List Manager"]
        PARSE["Parse Spreadsheet"]
        VALIDATE{"Validate Data"}
        CSVGEN["Generate Director CSV (.csv)"]
    end

    ERR["Errors shown to user\nProcessing stops"]
    CSV["CSV File"]
    DIRECTOR["dLive / Avantis Director\nOffline Software"]
    FOH["FOH Console\ndLive / Avantis"]

    TMPL --> PARSE
    PARSE --> VALIDATE
    VALIDATE -->|"invalid"| ERR
    VALIDATE -->|"valid"| CSVGEN
    CSVGEN --> CSV
    CSV -->|"Import into Director"| DIRECTOR
    DIRECTOR -->|"Apply to console"| FOH
```

### Step Sequence

| Step | Action |
|------|--------|
| B1 | Open Channel List Template (.xlsx / .ods) |
| B3 | Channel List Manager parses the spreadsheet |
| B4 | Validator checks data |
| B5 | Generate Director CSV file |
| B6 | Import CSV into dLive / Avantis Director (manual step) |

**Prerequisites:** None for CSV generation (fully offline). dLive Director 1.9x / 2.x or
Avantis Director 1.3x required for the import step.

> **Recommended workflow:** Use Director CSV first to establish a solid channel naming baseline,
> then apply further parameters (routing, mute groups, fader levels) via MIDI in Workflow A.

---

## Workflow C – Spreadsheet → Mixing Station → Console

### Idea & Background

**Mixing Station** is a third-party app (Android / iOS / macOS / Windows) that runs on a
tablet or laptop and connects to a physical console over the local WiFi or wired network.
It exposes an HTTP REST API that allows external tools — like dmt — to read and write mixer
parameters without a direct MIDI/TCP connection to the console.

This workflow is the Mixing Station equivalent of Workflow A. Instead of sending MIDI
messages to a dLive or Avantis console via MIDI/TCP, dmt sends HTTP POST requests to the
Mixing Station app, which immediately forwards each change to the connected console.

**Typical scenario:** Pre-show or rehearsal preparation. You have built your channel list in
the spreadsheet (names, colors, mute states, fader levels) and want to load it into the
console in one click. Your console (SQ, DM7, Wing, M32/X32, or QU) is reachable through
Mixing Station running on a tablet or laptop on the same network. dmt connects to Mixing
Station and applies all selected parameters channel by channel — no manual console
surface work required.

### Prerequisites & Setup

1. Install and start **Mixing Station** on a device that is on the same network as your console.
2. In Mixing Station, connect to your console and enable the **REST API** (Settings → Remote Control → HTTP API). Note the host IP and port (default: 8080).
3. In dmt Connection Settings, select **Mixing Station** as the console, choose the console sub-type (SQ / DM7 / Wing / M32/X32 / QU) from the Type dropdown, and enter the Mixing Station host IP and port.
4. Use **Test Connection** to verify that dmt can reach the Mixing Station REST API before starting the write process.

### Step Sequence

| Step | Action |
|------|--------|
| C1 | Prepare the channel list spreadsheet (names, colors, mute, fader levels) — use [MixingStationChannelList.xlsx](../MixingStationChannelList.xlsx) as the starting template |
| C2 | Start Mixing Station, connect to your console, enable HTTP REST API |
| C3 | In dmt: select Mixing Station, choose console sub-type, enter host IP and port |
| C4 | Click **Test Connection** to confirm the link |
| C5 | Select the checkboxes for the parameters to write (Name, Color, Mute, Fader Level) |
| C6 | Click **Open Spreadsheet and Start Writing Process** — dmt validates and writes |
| C7 | Mixing Station applies each parameter to the connected console in real time |

> **Note:** Only the four parameters listed above are available for Mixing Station. All other
> checkboxes (Phantom Power, Gain, Pad, DCA, Routing etc.) are automatically disabled when
> Mixing Station is selected.

Apply channel names, colors, mute states, and fader levels to a console via the
**Mixing Station** app REST API. Supported console types: **SQ, DM7, Wing, M32/X32, QU**.

```mermaid
flowchart TD
    TMPL["Channel List Template\n(.xlsx / .ods)"]

    subgraph dmt["Channel List Manager"]
        PARSE["Parse Spreadsheet"]
        VALIDATE{"Validate Data\nname · color · mute · fader"}
        MSHANDLER["Mixing Station Handler"]
        MSCLIENT["HTTP REST Client\nHTTP POST"]
    end

    ERR["Errors shown to user\nProcessing stops"]
    MS["Mixing Station App\nAndroid / iOS / Desktop\nREST API · port 8080"]
    FOH["FOH Console\nSQ · DM7 · Wing · M32/X32 · QU"]

    TMPL --> PARSE
    PARSE --> VALIDATE
    VALIDATE -->|"invalid"| ERR
    VALIDATE -->|"valid"| MSHANDLER
    MSHANDLER --> MSCLIENT
    MSCLIENT -->|"HTTP POST\n/console/data/set/ch.N.…"| MS
    MS -->|"applies parameters"| FOH
```

### Supported Parameters

| Parameter | REST Path | Notes |
|-----------|-----------|-------|
| Channel Name | `ch.{N}.cfg.name` | Max 6 characters |
| Channel Color | `ch.{N}.cfg.color` | Console-specific integer (see color maps below) |
| Mute | `ch.{N}.mix.on` | `true` = unmuted |
| Fader Level | `ch.{N}.mix.lvl` | Float dB value |

### Color Mapping

Color IDs differ per console type. The spreadsheet color values are mapped to console-specific integers automatically when a console type is selected in the tool.

#### SQ

| ID | Mixing Station | Spreadsheet Value |
|----|---------------|-------------------|
| 0 | Black | `black` |
| 1 | Red | `red` |
| 2 | Green | `green` |
| 3 | Blue | `blue` |
| 4 | Cyan | `light blue` |
| 5 | Yellow | `yellow` |
| 6 | Magenta | `purple` |
| 7 | White | `white` |

#### DM7

| ID | Mixing Station | Spreadsheet Value |
|----|---------------|-------------------|
| 0 | Purple | `purple` |
| 2 | Red | `red` |
| 4 | Yellow | `yellow` |
| 5 | Blue | `blue` |
| 6 | Cyan | `light blue` |
| 7 | Green | `green` |
| 10 | White | `white` |
| 11 | Black | `black` |

#### Wing

| ID | Mixing Station | Spreadsheet Value |
|----|---------------|-------------------|
| 0 | Blue | `blue` |
| 1 | Light Blue | `light blue` |
| 4 | Green | `green` |
| 6 | Yellow | `yellow` |
| 7 | Brown / Black | `black` |
| 8 | Red | `red` |
| 10 | Purple | `purple` |

#### M32 / X32

| ID | Mixing Station | Spreadsheet Value |
|----|---------------|-------------------|
| 0 | Black | `black` |
| 1 | Red | `red` |
| 2 | Green | `green` |
| 3 | Yellow | `yellow` |
| 4 | Blue | `blue` |
| 5 | Magenta | `purple` |
| 6 | Cyan | `light blue` |
| 7 | White | `white` |

IDs 8–15 are inverted variants of 0–7 and map back to the same spreadsheet colors on read.

#### QU

| ID | Mixing Station | Spreadsheet Value |
|----|---------------|-------------------|
| 1 | Yellow | `yellow` |
| 2 | Red | `red` |
| 3 | Green | `green` |
| 4 | Blue | `blue` |
| 6 | Purple | `purple` |
| 8 | White | `white` |

**Prerequisites:** Mixing Station running with REST API enabled on port 8080.
Host IP and port are configured in the Connection Settings of the tool.
Select the matching console sub-type (SQ / DM7 / Wing / M32/X32 / QU) in the Type dropdown.

---

## Workflow D – Console → DAW (dLive / Avantis)

Read current channel names and colors directly from a live console and generate DAW
recording session files — no spreadsheet required.

```mermaid
flowchart TD
    FOH["FOH Console\ndLive / Avantis"]

    subgraph dmt["Channel List Manager"]
        READ["Read Channel Names & Colors\nSysEx GET · MIDI/TCP · port 51325"]
        MODELS["Build Channel Models"]
        REAPER["Generate Reaper Session (.rpp)"]
        TL["Generate Tracks Live Template (.template)"]
    end

    DAW["Recording Tools\nReaper / Tracks Live"]

    FOH -->|"MIDI/TCP"| READ
    READ --> MODELS
    MODELS --> REAPER
    MODELS --> TL
    REAPER --> DAW
    TL --> DAW
```

### Step Sequence

| Step | Action |
|------|--------|
| D1a | Connect to console via MIDI/TCP |
| D1b | Read channel name + color per channel via SysEx GET |
| D2a | Generate Reaper session from channel data |
| D2b | Generate Tracks Live template from channel data |

**Configurable:** Channel range (start / end channel) is set in the tool before reading.

**Prerequisites:** Console reachable at the configured IP address on port 51325.

---

## Workflow E – Console → Mixing Station → DAW

### Idea & Background

This workflow is the Mixing Station equivalent of Workflow D. Instead of reading channel
names and colors from a dLive or Avantis console via MIDI, dmt reads them from the Mixing
Station REST API and generates a matching DAW recording session.

**Typical scenario:** A show is already loaded on the console and you want a DAW session
(Reaper or Tracks Live) that mirrors the current channel names and colors — without
re-entering any data in a spreadsheet. dmt reads each channel from Mixing Station and
builds the session file automatically.

This is particularly useful for last-minute setups where the console state diverged from the
original spreadsheet (last-minute channel swaps, renamed inputs on site) and you need the
DAW to reflect what is actually on the desk.

### Prerequisites & Setup

1. Mixing Station must be running and connected to the console, with the REST API enabled.
2. In dmt, select **Mixing Station**, choose the console sub-type, and enter host IP and port.
3. Switch to the **Console to DAW** tab, set the channel range, and click **Generate DAW Session(s) from Current Console Settings**.

Read channel names and colors from Mixing Station and generate DAW recording session files.

```mermaid
flowchart TD
    MS["Mixing Station App\nREST API · port 8080"]

    subgraph dmt["Channel List Manager"]
        MSCLIENT["HTTP REST Client\nHTTP GET per channel"]
        MSHANDLER["Mixing Station Handler\nget_channel_data()"]
        MODELS["Build Channel Models\nname · color"]
        REAPER["Generate Reaper Session (.rpp)"]
        TL["Generate Tracks Live Template (.template)"]
    end

    DAW["Recording Tools\nReaper / Tracks Live"]

    MS -->|"HTTP GET\n/console/data/get/ch.N.cfg.name\n/console/data/get/ch.N.cfg.color"| MSCLIENT
    MSCLIENT --> MSHANDLER
    MSHANDLER --> MODELS
    MODELS --> REAPER
    MODELS --> TL
    REAPER --> DAW
    TL --> DAW
```

### Step Sequence

| Step | Action |
|------|--------|
| E1 | Start Mixing Station, connect to console, confirm REST API is enabled |
| E2 | In dmt: select Mixing Station, choose console sub-type, enter host IP and port |
| E3a | Switch to the **Console to DAW** tab, set Start and End channel |
| E3b | Click **Generate DAW Session(s) from Current Console Settings** |
| E3c | dmt reads channel name + color per channel via HTTP GET (channels 1–99 max) |
| E4 | dmt builds channel models and writes the Reaper (.rpp) or Tracks Live (.template) file |
| E5 | Open the generated file in Reaper or Tracks Live |

**Prerequisites:** Mixing Station running with REST API enabled on port 8080.

---

## Channel List Print & Export

Print or export the current channel list as a PDF file directly from the console or Mixing
Station — no spreadsheet required.

### Idea & Background

After a show is set up on the console, it is often useful to have a printed or archived copy
of the channel list — for documentation, for the monitor engineer, or as a reference during
setup. This feature reads the live channel list directly from the console (the same read path
as Workflows D and E) and produces a formatted, printable PDF.

Two variants are available:

| Button | Behaviour |
|--------|-----------|
| **Export Channel List as PDF** | Asks for a save location and writes the PDF to disk |
| **Print Channel List** | Saves the PDF to a temporary file and opens it in the system's default PDF viewer for direct printing |

Both buttons are found in the **Utilities** tab. The channel Start / End range selectors
in the Console to DAW tab control which channels are included.

### PDF Content

The PDF contains a table with one row per channel. Columns depend on the console type:

| Column | dLive / Avantis | Mixing Station |
|--------|-----------------|----------------|
| Ch | Yes | Yes |
| Name | Yes | Yes |
| Color | Yes — colored cell background | Yes — colored cell background |

Both console paths read name and color only — the same data available via the read-back
path (MIDI SysEx for dLive / Avantis; REST GET for Mixing Station).

### Step Sequence

| Step | Action |
|------|--------|
| 1 | Ensure the console or Mixing Station is reachable (use **Test Connection** if unsure) |
| 2 | Switch to the **Utilities** tab |
| 3a | Click **Export Channel List as PDF** → choose a save location → PDF is written |
| 3b | *or* Click **Print Channel List** → PDF opens in the system PDF viewer → print from there |

**Prerequisites:** Same as Workflow D (dLive / Avantis) or Workflow E (Mixing Station).

---

## Workflow Summary

| # | Workflow | Source | Target | Connection |
|---|----------|--------|--------|------------|
| A | Spreadsheet → Console / DAW | .xlsx / .ods | dLive / Avantis + DAW | MIDI over TCP |
| B | Spreadsheet → Director CSV | .xlsx / .ods | Director (offline) | CSV file |
| C | Spreadsheet → Mixing Station → Console | .xlsx / .ods | Console via Mixing Station | HTTP REST |
| D | Console → DAW | dLive / Avantis | Reaper / Tracks Live | MIDI over TCP |
| E | Console → Mixing Station → DAW | Mixing Station | Reaper / Tracks Live | HTTP REST |
| — | Console → PDF (Print / Export) | dLive / Avantis or Mixing Station | PDF file / printer | MIDI over TCP or HTTP REST |

---

## Shared Components

All workflows pass through one or more of these shared components:

```mermaid
flowchart LR
    subgraph sources["Sources"]
        TMPL["Channel List Template\n.xlsx / .ods"]
        CON_R["Console\nread via MIDI/TCP"]
        MS_R["Mixing Station\nread via HTTP"]
    end

    subgraph dmt["Channel List Manager (dmt)"]
        PARSER["Spreadsheet Parser\npandas / openpyxl / odfpy"]
        VALIDATOR["Validator"]
        MIDI_H["MIDI Parameter Handlers\nSysEx · NRPN · CC"]
        MS_H["Mixing Station Handler\nHTTP REST"]
        REAPER_G["Reaper Session Creator"]
        TL_G["Tracks Live Creator"]
        CSV_G["Director CSV Creator"]
        PERSIST["Persistence\nconfig.json"]
    end

    subgraph targets["Targets"]
        CON_W["Console\nwrite via MIDI/TCP"]
        DIR["Director\nCSV import"]
        MS_W["Mixing Station\nwrite via HTTP"]
        DAW["Recording Tools\nReaper / Tracks Live"]
    end

    TMPL --> PARSER --> VALIDATOR
    VALIDATOR --> MIDI_H --> CON_W
    VALIDATOR --> CSV_G --> DIR
    VALIDATOR --> MS_H --> MS_W
    VALIDATOR --> REAPER_G --> DAW
    VALIDATOR --> TL_G --> DAW
    CON_R --> MIDI_H
    MS_R --> MS_H
    PERSIST -.->|"load / save settings"| dmt
```

See `doc/architecture.md` for full module descriptions, MIDI protocol details,
and the complete console support matrix.
