# cabana-for-ag setup

A practical guide for sniffing ag-CAN, discovering signals, and producing DBC contributions for this repository.

This doc walks the **generic** end-to-end workflow first (applies to any ag-CAN bus), then lists the **fleet-specific** pinouts and tap points the maintainer is still working through. Fleet-specific sections are explicitly flagged `<TODO>` until first-hand capture has been done — they are intentionally not guessed.

---

## 0. Scope check before you start

This project documents **publicly-summarized** ag-CAN content. Before you capture or contribute:

- Capture **only on equipment you own** or have written permission to capture on.
- Document only PGNs in the **standard ranges** (anything outside `0xEF00` and `0xFF00..0xFFFF`).
- If you suspect a frame is proprietary OEM content, **do not document it here.** Either keep your notes private or contribute it to a project whose scope welcomes that content. See `CONTRIBUTING.md` and `docs/code-of-conduct.md` §8.

---

## 1. Pick your tooling

Two stacks are commonly used; pick whichever fits your workflow.

### 1a. SavvyCAN (recommended for first-time ag users)

Qt desktop app. Live capture, log replay, custom dissectors, DBC import/export. Cross-platform.

| OS | Install |
|---|---|
| Linux (apt-based) | Build from source: `git clone https://github.com/collin80/SavvyCAN && cd SavvyCAN && qmake && make` (needs Qt5 or Qt6, libqt5serialbus or libqt6serialbus) |
| Linux (Fedora) | Same source build; install `qt5-qtbase-devel qt5-qtserialbus-devel` first |
| macOS | `brew install qt && git clone https://github.com/collin80/SavvyCAN && cd SavvyCAN && qmake && make` |
| Windows | Pre-built binaries on [SavvyCAN Releases](https://github.com/collin80/SavvyCAN/releases) |

### 1b. cabana (web-based, comma.ai)

Lives inside the `openpilot/tools` repo. Browser-based viewer, optimized for replay rather than live capture. Good for sharing a session with a remote collaborator over a hosted log.

```sh
git clone https://github.com/commaai/openpilot
cd openpilot/tools/cabana
# follow the README — uses bazel/cmake; depends on capnproto
```

### 1c. command-line baseline (always works)

`can-utils` from the linux-can project. Works on any SocketCAN interface.

```sh
# Debian / Ubuntu / Fedora
sudo apt install can-utils      # or: sudo dnf install can-utils

# Bring up the interface (rates: 250000 for ISOBUS, 500000 for many chassis CAN)
sudo ip link set can0 type can bitrate 250000
sudo ip link set up can0

# Watch live traffic
candump can0

# Log to a file for later replay in SavvyCAN
candump -L can0 > capture.log
```

---

## 2. Pick your dongle

| Dongle | Bitrate | CAN-FD | Bus power | Notes |
|---|---|---|---|---|
| **PCAN-USB FD (PEAK)** | up to 5 Mbps FD | ✅ | external | Industry standard, well-supported by both Linux SocketCAN and Windows |
| **Kvaser USBcan Pro 2xHS v2** | up to 5 Mbps FD | ✅ | external | Two channels — handy when you need tractor-side + implement-side simultaneously |
| **Comma Panda (white/grey/red)** | up to 1 Mbps classic | classic only on older units | OBD-II native | Cheap, openpilot ecosystem; you'll typically adapt OBD-II → Deutsch DT-09 |
| **CANable Pro / CandleLight** | up to 1 Mbps classic | varies by firmware | external | Inexpensive, open hardware; check firmware for CAN-FD support |
| **Macchina M2 / SuperB** | up to 1 Mbps classic | classic only | external | Arduino-friendly if you also want to inject |
| **CAN-FD required for** | — | newer Hagie, some JD 9R variants, parts of CNH Magnum 5G upgrade | — | Confirm bus type before buying — wrong rate = no frames |

Rule of thumb: **buy CAN-FD-capable.** Classic CAN dongles cannot read CAN-FD buses (they will see error frames or silence). CAN-FD dongles can read classic CAN.

---

## 3. Generic ISOBUS connector reference (public spec)

The standard implement-bus connector is a 9-pin Deutsch (DT04-9P on the tractor side, DT06-9S on the implement side). The pinout is published in many public sources — the project does not transcribe ISO 11783-2 directly.

| Pin | Function | Typical wire color |
|---|---|---|
| 1 | CAN_H (high) | yellow |
| 2 | CAN_L (low) | green |
| 3 | TBC_RTN — terminator bias return (signal ground reference) | brown |
| 4 | TBC_PWR — terminator bias circuit power | white |
| 5 | TBC_SHIELD — shield ground for the twisted pair | bare |
| 6 | ECU_GND — power ground | black |
| 7 | ECU_PWR — battery-positive, unswitched | red |
| 8 | ECU_PWR — battery-positive, key-switched | red |
| 9 | ECU_GND — power ground | black |

Confirm against your machine's service literature before connecting power pins. **Probe with a multimeter first**; wire color is convention, not guarantee.

Source citations:
- AgIsoStack++ documentation and source comments (`Open-Agriculture/AgIsoStack-plus-plus`)
- Wikipedia: [ISOBUS](https://en.wikipedia.org/wiki/ISO_11783) connector summary
- VDMA public PGN reference at [isobus.net](https://www.isobus.net/)

If you have access to the paid ISO 11783-2 PDF, **do not paste its text into this repository**. Cite the standard's section number and use only summary-level information.

---

## 4. Sniff the bus

### 4a. Wire it up

1. **Identify the bus first.** Most modern ag tractors have *several*: a chassis/J1939 bus (500 kbps), the ISOBUS implement bus (250 kbps), one or more body / comfort buses, and increasingly CAN-FD on newer hydraulic / steering systems. The wrong bus + wrong bitrate looks like silence.
2. **Terminate correctly.** ISOBUS is 120 Ω termination at each physical end. **Do not** add a third terminator with your dongle if the bus already has two — you will load the bus and cause arbitration errors. Most dongles let you disable internal termination via DIP switch or config.
3. **Use the diagnostic / implement bus connector when you can.** It's a passive tap. Splicing into harness wiring should be your last resort.

### 4b. Capture

```sh
# SocketCAN live, 250 kbps ISOBUS, log everything
sudo ip link set can0 type can bitrate 250000
sudo ip link set up can0
candump -L can0 > isobus_$(date +%Y%m%d_%H%M%S).log
```

Or in SavvyCAN: `Connection → Add New Connection → SocketCAN (can0)`, set bitrate, hit `Start`.

### 4c. What to capture

Run-of-the-day captures are more useful than synthetic test loops. Plan a captures around a known stimulus:

| Goal | Stimulus | Expected signal class |
|---|---|---|
| Speed | drive at known speeds (5 / 10 / 15 km/h) | Wheel-based vehicle speed (PGN 0xFE48), ground-based vehicle speed |
| Engine | idle → mid → max RPM | EEC1 PGN 0xF004 |
| Hydraulics | lift / lower three-point | Aux valve commands, hitch position |
| PTO | engage / disengage | PTO output engagement, PTO speed |
| Steering | left lock → straight → right lock | Curvature command, machine info |
| Implement | hook up a known ISOBUS implement, run its standard sequence | Address claim (PGN 0xEE00), TIM, working set master |

Save each capture with a descriptive filename: `combine_threshing_jd9870_2026-04-12.log`.

---

## 5. Discover signals

### 5a. Bit-flip discovery

For each candidate message ID, take a stretch of log where the stimulus is **off**, then a stretch where it's **on**. Diff the payload bytes. Bits that flip between the two stretches are candidate signal locations.

In SavvyCAN: `Tools → Signal Editor → Bit Editor` will color cells by bit-flip frequency.

### 5b. Periodic / cadence inference

Most ag-CAN frames repeat at a fixed cadence (10 ms, 100 ms, 1 s). Frames with no fixed cadence are usually request-response or session-establishment, not signal-carrying.

### 5c. Scale + offset inference

Once you've isolated the bytes carrying a numeric signal:

1. Find the **minimum** and **maximum** observed raw values across a capture that covers the signal's full physical range.
2. Compare to the matching gauge reading or test instrument value.
3. Fit a linear `physical = raw * scale + offset`.
4. Sanity check: if your scale isn't a "clean" number (1, 0.1, 0.5, 0.025, etc.), you probably haven't isolated the right byte span — most ag/J1939 signals use clean scales documented in public summaries.

### 5d. Value tables (enums)

Discrete-state signals (switches, gear positions, mode indicators) show up as a small set of stable raw values. Capture each known state for at least one second, and you'll have your value table directly. J1939 conventionally uses `0 = off/disabled`, `1 = on/enabled`, `2 = error`, `3 = not available` for 2-bit enums.

### 5e. Cross-check against existing DBC

Always run your candidate signal through:

```sh
python -c "import cantools; cantools.database.load_file('opendbc_ag/dbc/iso11783_from_agisostack.dbc').get_message_by_frame_id(<id>)"
```

If the PGN already exists in one of the three DBCs in this repo, you're enriching (good), not duplicating. If you're tempted to add it to a **second** DBC, stop — that creates the cross-DBC duplicate that the consistency CI workflow rejects.

---

## 6. Export and contribute

### 6a. Build a candidate DBC entry

Use `canmatrix` to convert your handwritten signal definitions or to build entries programmatically.

```python
from canmatrix import canmatrix
from canmatrix.formats import dumpp

matrix = canmatrix.CanMatrix()
frame = canmatrix.Frame(
    "MyDescriptiveFrameName",
    arbitration_id=canmatrix.ArbitrationId(id=0x18FEF100, extended=True),
    size=8,
    cycle_time=100,
)
frame.add_signal(canmatrix.Signal(
    name="EngineCoolantTemp",
    start_bit=0,
    size=8,
    factor=1,
    offset=-40,
    unit="°C",
    min=-40,
    max=215,
    comment="Source: <URL>",
))
matrix.add_frame(frame)
with open("candidate.dbc", "wb") as f:
    dumpp({"": matrix}, f)
```

### 6b. Validate before opening a PR

```sh
# Syntax + structure
canmatrix convert candidate.dbc /tmp/roundtrip.dbc

# Repo's own validation suite
pytest opendbc_ag/tests/
```

### 6c. Anonymize any included log

If your PR also adds a sample log to `corpus/`, run it through the anonymizer first to strip GPS, machine IDs, and timestamps. See `opendbc_ag/tools/anonymize.py` (Phase 9 deliverable).

### 6d. Open the PR

Follow `.github/PULL_REQUEST_TEMPLATE.md`. Cite your public source for every signal in a `CM_ SG_` comment. See `docs/signal-naming-guide.md` for naming conventions.

---

## 7. Fleet-specific pinouts and tap points

Each section below is filled in only after first-hand capture. Until then, the section names the machine class and lists what's known to be public from service documentation — the actual harness photo, pinout, and tap procedure go in once the maintainer has verified them.

### 7a. John Deere 9R-series tractor (cab CAN tap)

`<TODO: fill after first capture — cab connector identification, ISOBUS implement-bus connector location at the rear, diagnostic CAN port location, bitrate confirmation, photo of harness with annotations>`

Known public starting points:
- 9R-series has a standard ISO 11783 implement-bus connector at the rear (Deutsch DT-09).
- A separate in-cab diagnostic port exists; layout varies by model year.
- Newer 9R units (post-2022) include CAN-FD on parts of the bus tree.

### 7b. Kinze 3700 planter (ISOBUS connector location)

`<TODO: fill after first capture — implement-bus connector physical location, mating connector part number, terminator location on the planter side, working-set master behavior on power-up>`

Known public starting points:
- Kinze 3700 supports ISOBUS via dealer-installed harness; standard 9-pin Deutsch DT-09 implement connector.
- Working-set master should issue address claim within seconds of power-up.

### 7c. Hagie STS-series sprayer (Raven controller CAN-FD bus access)

`<TODO: fill after first capture — Raven Viper controller CAN-FD physical access point, bitrate confirmation, isolation from main ISOBUS bus, boom-section control PGNs observed>`

Known public starting points:
- Newer Hagie STS units use CAN-FD on the Raven control bus; **classic CAN dongles will not work** on that segment.
- Boom-section ON/OFF and rate control commands ride on this bus.

### 7d. Brent V-Series TRAX auger wagon harness

`<TODO: fill after first capture — TRAX system CAN bus access point, bitrate, weight-sensor PGN identification, hydraulic command PGNs>`

Known public starting points:
- TRAX (load-monitoring) system speaks ISOBUS-style CAN.
- Standard 9-pin Deutsch DT-09 if connected to a tractor via ISOBUS pass-through.

### 7e. John Deere S-series / X-series combine (ISOBUS port)

`<TODO: fill after first capture — implement-bus connector location, header-bus tap, header-class PGNs (reel speed, header height, threshing speed), separator drive PGNs>`

Known public starting points:
- S-series / X-series combines have a rear ISOBUS connector (header / cart hookup).
- Header bus may be electrically separate from chassis bus; verify with multimeter before bridging.

---

## 8. Safety notes

- **Power the dongle from its own source** when possible. Some dongles back-feed onto the bus's TBC_PWR pin in failure modes.
- **Probe with a multimeter** before connecting power. Wire colors are convention, not guarantee. Find ECU_PWR and ECU_GND before assuming pin 7/9 assignments.
- **Do not inject** (send frames) during initial discovery. Read-only captures are safe; sending arbitrary frames onto a live ag bus during operation can engage actuators (hydraulics, PTO, three-point hitch) and hurt people or damage equipment.
- **Park, set brake, chock wheels, and disengage hydraulics** before any tap-and-capture session, even read-only.
- Safety-relevant signal interpretations (brake, steering, hydraulic, PTO) follow the disclosure rule in `docs/code-of-conduct.md` §7.

---

## 9. Where to ask questions

- **Repo issues:** open one with the `new-pgn` or `bug` template.
- **Discussions:** for open-ended "is this signal what I think it is?" questions, open a draft PR; reviewers can comment on bit positions inline.
- **Adjacent communities** (Open-Agriculture, AgOpenGPS, Tractor Hacking) host broader discussions but follow each one's posting norms.

---

## Changes

| Date | Change |
|---|---|
| 2026-05-13 | Initial draft (v0.1.0-private). Generic sections complete; fleet-specific pinouts flagged `<TODO>` for post-Stub-R capture work. |
