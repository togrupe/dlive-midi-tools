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

## Workflow C – Console → DAW (dLive / Avantis)

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
| C1a | Connect to console via MIDI/TCP |
| C1b | Read channel name + color per channel via SysEx GET |
| C2a | Generate Reaper session from channel data |
| C2b | Generate Tracks Live template from channel data |

**Configurable:** Channel range (start / end channel) is set in the tool before reading.

**Prerequisites:** Console reachable at the configured IP address on port 51325.

---

## Workflow D – Spreadsheet → Mixing Station → Console

Apply channel names, colors, mute states, and fader levels to a console via the
**Mixing Station** app REST API. Currently supported console types: SQ and M32.

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
    MS["Mixing Station App\nAndroid / iOS / Desktop\nREST API · port 9000"]
    FOH["FOH Console\nSQ · M32"]

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
| Channel Color | `ch.{N}.cfg.color` | Integer 0–7 |
| Mute | `ch.{N}.mix.on` | `true` = unmuted |
| Fader Level | `ch.{N}.mix.lvl` | Float dB value |

### Color Mapping

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

**Prerequisites:** Mixing Station running with REST API enabled on port 9000.
Host IP and port are configured in the Connection Settings of the tool.

---

## Workflow E – Console → Mixing Station → DAW

Read channel names and colors from Mixing Station and generate DAW recording session files.

```mermaid
flowchart TD
    MS["Mixing Station App\nREST API · port 9000"]

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
| E1 | Connect to Mixing Station (host:port configured in tool) |
| E2 | Read channel name + color per channel via HTTP GET |
| E3 | Build channel models from REST responses |
| E4 | Generate Reaper session and / or Tracks Live template |

**Prerequisites:** Mixing Station running with REST API enabled on port 9000.

---

## Workflow Summary

| # | Workflow | Source | Target | Connection |
|---|----------|--------|--------|------------|
| A | Spreadsheet → Console / DAW | .xlsx / .ods | dLive / Avantis + DAW | MIDI over TCP |
| B | Spreadsheet → Director CSV | .xlsx / .ods | Director (offline) | CSV file |
| C | Console → DAW | dLive / Avantis | Reaper / Tracks Live | MIDI over TCP |
| D | Spreadsheet → Mixing Station | .xlsx / .ods | Console via Mixing Station | HTTP REST |
| E | Mixing Station → DAW | Mixing Station | Reaper / Tracks Live | HTTP REST |

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
