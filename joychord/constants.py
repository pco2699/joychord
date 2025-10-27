"""Static mappings and enumerations for the JoyChord controller layout."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class DegreeDefinition:
    """Represents a Nashville number degree and its default quality."""

    name: str
    short_name: str
    default_quality: str
    semitone_offset: int


MAJOR_SCALE_OFFSETS = [0, 2, 4, 5, 7, 9, 11]

# Mapping from controller button index to Nashville number degree
BUTTON_DEFINITIONS: Dict[int, DegreeDefinition] = {
    0: DegreeDefinition("Tonic", "I", "major", MAJOR_SCALE_OFFSETS[0]),
    6: DegreeDefinition("Supertonic", "II", "minor", MAJOR_SCALE_OFFSETS[1]),
    2: DegreeDefinition("Mediant", "III", "minor", MAJOR_SCALE_OFFSETS[2]),
    7: DegreeDefinition("Subdominant", "IV", "major", MAJOR_SCALE_OFFSETS[3]),
    3: DegreeDefinition("Dominant", "V", "major", MAJOR_SCALE_OFFSETS[4]),
    4: DegreeDefinition("Submediant", "VI", "minor", MAJOR_SCALE_OFFSETS[5]),
    1: DegreeDefinition("Leading Tone", "VII", "diminished", MAJOR_SCALE_OFFSETS[6]),
}

# Button indexes that can be used as slash chord bass notes (same as chord buttons)
SLASH_BUTTONS = set(BUTTON_DEFINITIONS.keys())

# Buttons reserved for special functions
INVERSION_BUTTON = 5  # R1 / RB / R
SELECT_BUTTON = 8
START_BUTTON = 9

# Hats and axes
LEFT_STICK_AXES: Tuple[int, int] = (0, 1)


MODE_ORDER = ["play", "arp", "repeat", "drum", "autodrum"]


# Drum mode MIDI note mapping (Generic GM percussion layout)
DRUM_NOTES: Dict[int, int] = {
    0: 36,  # Kick
    2: 38,  # Snare
    3: 42,  # Closed hat
    1: 46,  # Open hat
    6: 41,  # Low tom
    7: 45,  # Mid tom
    4: 49,  # Crash
}
