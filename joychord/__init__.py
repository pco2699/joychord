"""JoyChord - Musical Chord Controller System

A cross-platform application that converts Bluetooth game controller inputs
into MIDI chord messages for DAWs.
"""

from __future__ import annotations

# Version
from joychord.constants import VERSION

# Enums
from joychord.enums import PlayMode, ChordQuality

# Models
from joychord.models import ChordButton, AppState

# Core Systems
from joychord.midi_system import MIDISystem
from joychord.musical_system import MusicalSystem
from joychord.joystick_mapper import JoystickQualityMapper
from joychord.controller_input import ControllerInput

# Configuration
from joychord.constants import (
    KEYS,
    MIN_OCTAVE,
    MAX_OCTAVE,
    MIN_BPM,
    MAX_BPM,
    DEFAULT_BPM,
    CHORD_INTERVALS,
    DEGREE_NAMES,
    BTN_TONIC,
    BTN_SUPERTONIC,
    BTN_MEDIANT,
    BTN_SUBDOMINANT,
    BTN_DOMINANT,
    BTN_SUBMEDIANT,
    BTN_LEADING,
    BTN_INVERSION,
    BTN_SELECT,
    BTN_START,
    MIN_MIDI_NOTE,
    MAX_MIDI_NOTE,
)
from joychord.chord_config import CHORD_BUTTONS

# Main Application
from joychord.joychord_app import JoyChord

# CLI
from joychord.cli import main

__version__ = VERSION

__all__ = [
    # Version
    "__version__",
    "VERSION",
    # Enums
    "PlayMode",
    "ChordQuality",
    # Models
    "ChordButton",
    "AppState",
    # Core Systems
    "MIDISystem",
    "MusicalSystem",
    "JoystickQualityMapper",
    "ControllerInput",
    # Configuration
    "KEYS",
    "MIN_OCTAVE",
    "MAX_OCTAVE",
    "MIN_BPM",
    "MAX_BPM",
    "DEFAULT_BPM",
    "CHORD_INTERVALS",
    "DEGREE_NAMES",
    "CHORD_BUTTONS",
    "BTN_TONIC",
    "BTN_SUPERTONIC",
    "BTN_MEDIANT",
    "BTN_SUBDOMINANT",
    "BTN_DOMINANT",
    "BTN_SUBMEDIANT",
    "BTN_LEADING",
    "BTN_INVERSION",
    "BTN_SELECT",
    "BTN_START",
    "MIN_MIDI_NOTE",
    "MAX_MIDI_NOTE",
    # Main Application
    "JoyChord",
    # CLI
    "main",
]
