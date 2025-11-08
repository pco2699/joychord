# JoyChord - Musical Chord Controller System

Convert your Bluetooth game controller into a powerful MIDI chord controller for DAWs like Ableton Live.

## Features

- **Cross-Platform Support**: Windows, Linux, and macOS
- **7 Chord Buttons**: Nashville Number System (I, II, III, IV, V, VI, VII)
- **Real-Time Chord Quality**: LEFT stick modifies chord quality in 8 directions
- **Slash Chords**: Simultaneous button press for bass notes
- **Inversions**: R1 shoulder button cycles through inversions
- **Key Transposition**: All 12 keys via D-Pad
- **Octave Shifting**: -2 to +2 octaves
- **5 Playback Modes**: Play, Arp, Repeat, Drum, AutoDrum
- **BPM Control**: 40-240 BPM

## Quick Start

### Prerequisites

**All Platforms:**
- Python 3.8 or higher
- Bluetooth game controller (PlayStation, Xbox, Nintendo Switch, or generic)

**Windows:**
- loopMIDI or similar virtual MIDI driver

**Linux:**
- ALSA or JACK audio system

**macOS:**
- Core MIDI (built-in)

### Installation

**Using uv (Recommended - Fast & Modern):**

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install JoyChord and dependencies
uv sync

# Run JoyChord
uv run joychord.py

# Or use the command directly
uv run joychord
```

**Using pip (Traditional):**

```bash
# Install dependencies
pip install -r requirements.txt

# Run JoyChord
python3 joychord.py  # Linux/macOS
python joychord.py   # Windows
```

## Controller Layout

### Chord Buttons

```
    L2[II]   L1[VI]          R1[Inversion]  R2[IV]
   (MINOR)  (MINOR)                        (MAJOR)

            △[V]
          (MAJOR)
        □[III]  ○[VII]
       (MINOR)  (DIM)
            ×[I]
          (MAJOR)
```

### LEFT Stick - Chord Quality (8 Directions)

```
              UP
         (maj/min)
              |
    UL        |        UR
   (aug)      |       (7)
      \       |       /
LEFT ----+----+---- RIGHT
(dim)         |    (maj/min7)
         /    |    \
       DL     |     DR
  (sus2/maj6) |   (maj9)
              |
            DOWN
           (sus4)
```

### D-Pad Navigation

- **LEFT/RIGHT**: Change key (C → C# → D ... → B)
- **UP/DOWN**: Change octave (-2 to +2)

### Slash Chords

Hold one button, then press another:
- Hold × (I) + Press □ (III) = I/III (C/E)

## Command-Line Options

```bash
# Test button layout
uv run joychord --test-buttons

# Start in D major
uv run joychord --key D

# Set BPM
uv run joychord --bpm 140

# Debug mode
uv run joychord --debug

# Or with python directly
python3 joychord.py --test-buttons
```

## Platform-Specific Setup

### Windows

1. Install [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)
2. Create at least one virtual MIDI port
3. Pair your Bluetooth controller
4. Run JoyChord

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get install python3-pygame libasound2-dev

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install JoyChord
uv sync
```

### macOS

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew
brew install uv

# Install JoyChord
uv sync
```

## Controls Reference

**CHORD BUTTONS:**
- × /A (Button 0) = Tonic (I) MAJOR
- L2 (Button 6) = Supertonic (II) MINOR
- □/X (Button 2) = Mediant (III) MINOR
- R2 (Button 7) = Subdominant (IV) MAJOR
- △/Y (Button 3) = Dominant (V) MAJOR
- L1 (Button 4) = Submediant (VI) MINOR
- ○/B (Button 1) = Leading Tone (VII) DIMINISHED

**MODIFIERS:**
- R1 = Cycle inversions (Root → 1st → 2nd)
- LEFT Stick = Change chord quality
- D-Pad = Key/Octave navigation

**SYSTEM:**
- SELECT = Mode switching, BPM control
- START = Help overlay / Panic (double-tap)

## License

MIT License - See LICENSE file for details

## Version

v0.1 - Initial MVP Release
