"""JoyChord constants and configuration"""

from __future__ import annotations
from typing import Dict

from joychord.enums import ChordQuality

# Version
VERSION = "0.1"

# MIDI Constants
MIDI_CHANNEL = 0  # Channel 1 (0-indexed)
DEFAULT_VELOCITY = 100
MIN_MIDI_NOTE = 24
MAX_MIDI_NOTE = 127

# Controller Button Mapping (pygame indices)
BTN_TONIC = 0       # Face Button 0 (×/A) - I (MAJOR)
BTN_LEADING = 1     # Face Button 1 (○/B) - VII (DIMINISHED)
BTN_MEDIANT = 2     # Face Button 2 (□/X) - III (MINOR)
BTN_DOMINANT = 3    # Face Button 3 (△/Y) - V (MAJOR)
BTN_SUBMEDIANT = 4  # L1 - VI (MINOR)
BTN_INVERSION = 5   # R1 - Inversion control
BTN_SUPERTONIC = 6  # L2 - II (MINOR)
BTN_SUBDOMINANT = 7 # R2 - IV (MAJOR)
BTN_SELECT = 8      # SELECT - Mode control
BTN_START = 9       # START - Help/Panic

# Joystick Settings
STICK_DEADZONE = 0.3
STICK_LEFT = 0  # LEFT stick index

# D-Pad Settings
DPAD_REPEAT_DELAY = 500  # ms
DPAD_REPEAT_RATE = 300   # ms

# Slash Chord Detection
SLASH_CHORD_WINDOW = 50  # ms

# BPM Settings
MIN_BPM = 40
MAX_BPM = 240
DEFAULT_BPM = 120

# Musical Constants
KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
MIN_OCTAVE = -2
MAX_OCTAVE = 2

# Degree Names
DEGREE_NAMES: Dict[int, str] = {
    1: "Tonic",
    2: "Supertonic",
    3: "Mediant",
    4: "Subdominant",
    5: "Dominant",
    6: "Submediant",
    7: "Leading Tone"
}

# Chord Quality Formulas
CHORD_INTERVALS: Dict[ChordQuality, list[int]] = {
    ChordQuality.MAJOR: [0, 4, 7],
    ChordQuality.MINOR: [0, 3, 7],
    ChordQuality.DOM7: [0, 4, 7, 10],
    ChordQuality.MAJ7: [0, 4, 7, 11],
    ChordQuality.MIN7: [0, 3, 7, 10],
    ChordQuality.MAJ9: [0, 4, 7, 11, 14],
    ChordQuality.MIN9: [0, 3, 7, 10, 14],
    ChordQuality.SUS2: [0, 2, 7],
    ChordQuality.SUS4: [0, 5, 7],
    ChordQuality.DIM: [0, 3, 6],
    ChordQuality.DIM7: [0, 3, 6, 9],
    ChordQuality.AUG: [0, 4, 8],
    ChordQuality.MAJ6: [0, 4, 7, 9],
}
