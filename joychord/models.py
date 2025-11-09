"""JoyChord data classes"""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from joychord.enums import ChordQuality, PlayMode


@dataclass
class ChordButton:
    """Represents a chord button configuration"""
    button_index: int
    degree: int
    name: str
    default_quality: ChordQuality
    symbol: str


@dataclass
class AppState:
    """Application state"""
    current_key: int = 0  # Index into KEYS list
    current_octave: int = 0
    play_mode: PlayMode | None = None
    bpm: int = 120
    inversion: int = 0  # 0=root, 1=1st, 2=2nd
    velocity: int = 100
    debug: bool = False
    show_help: bool = False
