"""Chord utilities for JoyChord."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

from .config import JoyChordConfig, key_index
from .constants import BUTTON_DEFINITIONS, DegreeDefinition


ChordNotes = List[int]


@dataclass
class ChordRequest:
    """Represents the musical intent derived from controller state."""

    button: int
    inversion: int = 0
    quality_override: str | None = None
    slash_bass_button: int | None = None


BASE_NOTE = 60  # C4
SEMITONES_PER_OCTAVE = 12

CHORD_FORMULAS: Dict[str, Sequence[int]] = {
    "major": (0, 4, 7),
    "minor": (0, 3, 7),
    "diminished": (0, 3, 6),
    "augmented": (0, 4, 8),
    "dominant7": (0, 4, 7, 10),
    "maj7": (0, 4, 7, 11),
    "min7": (0, 3, 7, 10),
    "maj9": (0, 4, 7, 11, 14),
    "min9": (0, 3, 7, 10, 14),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
    "maj6": (0, 4, 7, 9),
    "dim7": (0, 3, 6, 9),
}

QUALITY_ALIAS = {
    "maj": "major",
    "min": "minor",
    "dim": "diminished",
    "aug": "augmented",
    "7": "dominant7",
    "maj7": "maj7",
    "min7": "min7",
    "maj9": "maj9",
    "min9": "min9",
    "sus2": "sus2",
    "sus4": "sus4",
    "maj6": "maj6",
    "dim7": "dim7",
}

QUALITY_BY_BASE = {
    "major": {
        "center": "major",
        "up": "major",
        "up_right": "dominant7",
        "right": "maj7",
        "down_right": "maj9",
        "down": "sus4",
        "down_left": "maj6",
        "left": "diminished",
        "up_left": "augmented",
    },
    "minor": {
        "center": "minor",
        "up": "minor",
        "up_right": "min7",
        "right": "min7",
        "down_right": "min9",
        "down": "sus4",
        "down_left": "sus2",
        "left": "diminished",
        "up_left": "augmented",
    },
    "diminished": {
        "center": "diminished",
        "up": "diminished",
        "up_right": "dim7",
        "right": "dim7",
        "down_right": "dim7",
        "down": "sus4",
        "down_left": "sus2",
        "left": "diminished",
        "up_left": "augmented",
    },
}


DIRECTION_VECTORS: Dict[str, Tuple[float, float]] = {
    "up": (0.0, -1.0),
    "up_right": (math.sqrt(2) / 2, -math.sqrt(2) / 2),
    "right": (1.0, 0.0),
    "down_right": (math.sqrt(2) / 2, math.sqrt(2) / 2),
    "down": (0.0, 1.0),
    "down_left": (-math.sqrt(2) / 2, math.sqrt(2) / 2),
    "left": (-1.0, 0.0),
    "up_left": (-math.sqrt(2) / 2, -math.sqrt(2) / 2),
}


def direction_from_axis(x: float, y: float, deadzone: float) -> str:
    """Return the chord quality direction keyword from an axis vector."""
    magnitude = math.sqrt(x * x + y * y)
    if magnitude < deadzone:
        return "center"

    norm_x, norm_y = x / magnitude, y / magnitude
    best_direction = "center"
    best_dot = -float("inf")
    for direction, (dx, dy) in DIRECTION_VECTORS.items():
        dot = norm_x * dx + norm_y * dy
        if dot > best_dot:
            best_dot = dot
            best_direction = direction
    return best_direction


def resolve_quality(base_quality: str, direction: str) -> str:
    """Resolve the effective chord quality name based on base and direction."""
    mapping = QUALITY_BY_BASE.get(base_quality, QUALITY_BY_BASE["major"])
    quality = mapping.get(direction, mapping["center"])
    return QUALITY_ALIAS.get(quality, quality)


def base_note_for_key(config: JoyChordConfig) -> int:
    idx = key_index(config.key, config.keys)
    return BASE_NOTE + idx


def degree_definition(button: int) -> DegreeDefinition | None:
    return BUTTON_DEFINITIONS.get(button)


def chord_root_midi(config: JoyChordConfig, definition: DegreeDefinition) -> int:
    base = base_note_for_key(config)
    octave_offset = config.octave * SEMITONES_PER_OCTAVE
    return base + definition.semitone_offset + octave_offset


def apply_inversion(notes: Iterable[int], inversion: int) -> ChordNotes:
    notes = list(notes)
    if not notes or inversion <= 0:
        return notes

    inversion = inversion % len(notes)
    result = notes[:]
    for _ in range(inversion):
        bottom = result.pop(0)
        result.append(bottom + SEMITONES_PER_OCTAVE)
    return result


def slash_bass_note(config: JoyChordConfig, button: int) -> int:
    definition = degree_definition(button)
    if definition is None:
        raise ValueError(f"Button {button} cannot be used as a slash bass note")
    base = base_note_for_key(config)
    octave_offset = (config.octave - 1) * SEMITONES_PER_OCTAVE
    note = base + definition.semitone_offset + octave_offset
    while note < 24:
        note += SEMITONES_PER_OCTAVE
    return note


def build_chord(config: JoyChordConfig, request: ChordRequest, direction: str) -> ChordNotes:
    definition = degree_definition(request.button)
    if definition is None:
        raise ValueError(f"Button {request.button} is not mapped to a chord degree")

    quality_name = request.quality_override or resolve_quality(
        definition.default_quality, direction
    )
    intervals = CHORD_FORMULAS.get(quality_name)
    if not intervals:
        raise ValueError(f"Unsupported chord quality '{quality_name}'")

    root = chord_root_midi(config, definition)
    chord_notes = [root + interval for interval in intervals]
    chord_notes = apply_inversion(chord_notes, request.inversion)

    if request.slash_bass_button is not None:
        bass = slash_bass_note(config, request.slash_bass_button)
        if bass not in chord_notes:
            chord_notes = [bass] + chord_notes
        else:
            chord_notes = chord_notes[:]
            chord_notes[0] = bass
    return chord_notes


def describe_chord(definition: DegreeDefinition, quality: str, inversion: int) -> str:
    """Return a user friendly description string."""
    inversion_names = {0: "Root", 1: "1st", 2: "2nd"}
    inversion_label = inversion_names.get(inversion % 3, f"{inversion}th")
    quality_name = quality.replace("dominant", "dom")
    return f"{definition.name} ({definition.short_name}) {quality_name} [{inversion_label}]"
