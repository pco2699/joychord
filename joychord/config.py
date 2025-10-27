"""Configuration models for JoyChord application."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


DEFAULT_KEY_ORDER: List[str] = [
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
]


@dataclass
class JoyChordConfig:
    """Runtime configuration values for the JoyChord application."""

    key: str = "C"
    octave: int = 0
    mode: str = "play"
    bpm: int = 120
    velocity: int = 100
    midi_channel: int = 0
    stick_deadzone: float = 0.3
    dpad_repeat_delay: float = 0.5
    dpad_repeat_rate: float = 0.3
    slash_window: float = 0.05
    keys: List[str] = field(default_factory=lambda: DEFAULT_KEY_ORDER.copy())

    def clamp_octave(self) -> None:
        """Clamp the octave within the supported -2..2 range."""
        if self.octave < -2:
            self.octave = -2
        elif self.octave > 2:
            self.octave = 2

    def clamp_bpm(self) -> None:
        """Clamp BPM to a sensible range (40-240)."""
        if self.bpm < 40:
            self.bpm = 40
        elif self.bpm > 240:
            self.bpm = 240


def key_index(key: str, keys: List[str] | None = None) -> int:
    """Return the index of ``key`` in ``keys`` raising ``ValueError`` if missing."""
    key_list = keys or DEFAULT_KEY_ORDER
    try:
        return key_list.index(key.upper())
    except ValueError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Unsupported key '{key}'. Supported keys: {', '.join(key_list)}") from exc
