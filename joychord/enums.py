"""JoyChord enumerations"""

from __future__ import annotations
from enum import Enum


class PlayMode(Enum):
    """Playback modes"""
    PLAY = "PLAY"
    ARP = "ARP"
    REPEAT = "REPEAT"
    DRUM = "DRUM"
    AUTODRUM = "AUTODRUM"


class ChordQuality(Enum):
    """Chord quality types"""
    MAJOR = "major"
    MINOR = "minor"
    DOM7 = "7"
    MAJ7 = "maj7"
    MIN7 = "min7"
    MAJ9 = "maj9"
    MIN9 = "min9"
    SUS2 = "sus2"
    SUS4 = "sus4"
    DIM = "dim"
    DIM7 = "dim7"
    AUG = "aug"
    MAJ6 = "maj6"
