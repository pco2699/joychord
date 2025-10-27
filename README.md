# JoyChord

JoyChord is a Linux-oriented application that turns a standard Bluetooth game controller
into a Nashville number chord controller with MIDI output. The project follows the
v0.1 specification supplied in the repository task description and focuses on the
core performer workflow:

- Seven chord buttons mapped to the controller face buttons, triggers, and left
  shoulder using the Nashville Number System
- Real-time chord quality morphing using the left analog stick
- Slash chord detection with a 50 ms window
- Key and octave navigation through the D-pad with repeat behaviour
- Inversion cycling via the R1 shoulder button
- Mode switching with playback engines for Play, Arpeggiator, Repeat, Drum, and
  AutoDrum behaviours
- MIDI output via `mido`/`python-rtmidi`

## Getting Started

### Requirements

- Python 3.8+
- [`pygame`](https://www.pygame.org/news) 2.0 or newer
- [`mido`](https://mido.readthedocs.io/en/latest/) with a `python-rtmidi` backend

Install dependencies with:

```bash
python -m pip install pygame mido python-rtmidi
```

### Running JoyChord

Plug in or pair a supported Bluetooth controller, then run:

```bash
python -m joychord
```

Key command-line options:

- `--key` – starting key (default `C`)
- `--octave` – octave shift from -2 to +2 (default `0`)
- `--bpm` – starting tempo (default `120`)
- `--mode` – starting mode (`play`, `arp`, `repeat`, `drum`, `autodrum`)
- `--velocity` – MIDI velocity (default `100`)
- `--midi-port` – explicit MIDI output port name
- `--test-buttons` – print controller mapping without starting the runtime
- `--test-controller` – interactive pygame event tester (hardware required)
- `--list-midi` – enumerate MIDI output ports

### Controller Reference

| Button | Degree | Quality | Notes |
| ------ | ------ | ------- | ----- |
| × / A (0) | Tonic (I) | Major | Base chord button |
| ○ / B (1) | Leading tone (VII) | Diminished | |
| □ / X (2) | Mediant (III) | Minor | |
| △ / Y (3) | Dominant (V) | Major | |
| L1 / LB (4) | Submediant (VI) | Minor | |
| R1 / RB (5) | — | Inversion cycle | Hold a chord and tap to cycle root → 1st → 2nd |
| L2 / LT (6) | Supertonic (II) | Minor | |
| R2 / RT (7) | Subdominant (IV) | Major | |
| SELECT (8) | Mode | Cycle playback modes / edit BPM & rhythm while held |
| START (9) | Help / Panic | Single tap shows help (console log), double tap sends all notes off |

### Left Stick Qualities

The left stick provides eight-way chord quality morphing relative to a degree’s
base quality.

| Direction | Major Degrees | Minor Degrees | VII (diminished) |
| --------- | ------------- | ------------- | ---------------- |
| Center / Up | Major | Minor | Diminished |
| Up-Right | Dominant 7 | Minor 7 | Diminished 7 |
| Right | Major 7 | Minor 7 | Diminished 7 |
| Down-Right | Major 9 | Minor 9 | Diminished 7 |
| Down | Sus4 | Sus4 | Sus4 |
| Down-Left | Major 6 | Sus2 | Sus2 |
| Left | Diminished | Diminished | Diminished |
| Up-Left | Augmented | Augmented | Augmented |

### Slash Chords

Hold a primary chord button and press another chord button to assign its degree
as the bass within a 50 ms window. The console displays slash chord feedback,
e.g. `🎸 Slash: I/III (Tonic/Mediant) -> [52, 60, 64, 67]`.

### SELECT + D-Pad Shortcuts

- SELECT + Up/Down: adjust BPM in ±10 increments (clamped to 40–240)
- SELECT + Left/Right: cycle rhythm rates (1/4, 1/8, 1/16, 1/32, 1/16T) for ARP,
  Repeat, and AutoDrum modes

## Development Notes

The runtime uses pygame for controller events and mido for MIDI transport. The
`joychord.controller.ControllerApp` class orchestrates input interpretation,
while the playback engines live in `joychord.modes`. MIDI routing lives in
`joychord.midi.MidiOutput` with automatic virtual port creation when no ports are
available.

Unit tests are not provided because the primary features require hardware
interaction. The console logging acts as a textual UI reflecting the spec’s
feedback examples.
