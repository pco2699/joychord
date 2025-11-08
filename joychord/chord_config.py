"""Chord button configuration"""

from __future__ import annotations
from typing import Dict

from joychord.enums import ChordQuality
from joychord.models import ChordButton
from joychord.constants import (
    BTN_TONIC, BTN_SUPERTONIC, BTN_MEDIANT, BTN_SUBDOMINANT,
    BTN_DOMINANT, BTN_SUBMEDIANT, BTN_LEADING
)


CHORD_BUTTONS: Dict[int, ChordButton] = {
    BTN_TONIC: ChordButton(BTN_TONIC, 1, "Tonic (I)", ChordQuality.MAJOR, "I"),
    BTN_SUPERTONIC: ChordButton(BTN_SUPERTONIC, 2, "Supertonic (II)", ChordQuality.MINOR, "ii"),
    BTN_MEDIANT: ChordButton(BTN_MEDIANT, 3, "Mediant (III)", ChordQuality.MINOR, "iii"),
    BTN_SUBDOMINANT: ChordButton(BTN_SUBDOMINANT, 4, "Subdominant (IV)", ChordQuality.MAJOR, "IV"),
    BTN_DOMINANT: ChordButton(BTN_DOMINANT, 5, "Dominant (V)", ChordQuality.MAJOR, "V"),
    BTN_SUBMEDIANT: ChordButton(BTN_SUBMEDIANT, 6, "Submediant (VI)", ChordQuality.MINOR, "vi"),
    BTN_LEADING: ChordButton(BTN_LEADING, 7, "Leading Tone (VII)", ChordQuality.DIM, "vii°"),
}
