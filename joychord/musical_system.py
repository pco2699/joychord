"""Musical system for Nashville Number System and chord generation"""

from __future__ import annotations
from typing import TYPE_CHECKING

from joychord.constants import KEYS, CHORD_INTERVALS, MIN_MIDI_NOTE, MAX_MIDI_NOTE

if TYPE_CHECKING:
    from joychord.enums import ChordQuality


class MusicalSystem:
    """Nashville Number System and chord generation"""

    def __init__(self, key_index: int = 0, octave: int = 0) -> None:
        self.key_index = key_index
        self.octave = octave
        self.base_octave = 4  # Middle C octave

    def get_root_note(self, degree: int) -> int:
        """Get MIDI note number for a scale degree"""
        # Major scale intervals from tonic
        major_scale = [0, 2, 4, 5, 7, 9, 11]

        # Get interval for this degree
        interval = major_scale[degree - 1]

        # Calculate MIDI note
        base_note = 60  # Middle C
        key_offset = self.key_index
        octave_offset = self.octave * 12

        note = base_note + key_offset + interval + octave_offset
        return note

    def build_chord(self, degree: int, quality: ChordQuality, inversion: int = 0) -> list[int]:
        """Build a chord from degree, quality, and inversion"""
        root = self.get_root_note(degree)
        intervals = CHORD_INTERVALS.get(quality, [0, 4, 7])

        # Build base chord
        notes = [root + interval for interval in intervals]

        # Apply inversion
        notes = self.apply_inversion(notes, inversion)

        # Filter valid MIDI range
        notes = [n for n in notes if MIN_MIDI_NOTE <= n <= MAX_MIDI_NOTE]

        return notes

    def apply_inversion(self, notes: list[int], inversion: int) -> list[int]:
        """Apply chord inversion"""
        if inversion == 0 or len(notes) < 2:
            return notes

        result = notes.copy()
        for _ in range(inversion):
            # Move bottom note up an octave
            if result:
                bottom = result.pop(0)
                result.append(bottom + 12)

        return sorted(result)

    def get_bass_note(self, degree: int) -> int:
        """Get bass note for slash chord (one octave below)"""
        root = self.get_root_note(degree)
        bass = root - 12

        # Ensure it's in valid range
        if bass < MIN_MIDI_NOTE:
            bass += 12

        return bass

    def get_key_name(self) -> str:
        """Get current key name"""
        return KEYS[self.key_index]

    def change_key(self, delta: int) -> None:
        """Change key by delta (-1 or +1)"""
        self.key_index = (self.key_index + delta) % len(KEYS)

    def change_octave(self, delta: int) -> None:
        """Change octave by delta"""
        from joychord.constants import MIN_OCTAVE, MAX_OCTAVE
        new_octave = self.octave + delta
        self.octave = max(MIN_OCTAVE, min(MAX_OCTAVE, new_octave))
