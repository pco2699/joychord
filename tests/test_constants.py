"""Unit tests for JoyChord constants and configuration"""

import pytest
from joychord.constants import (
    KEYS,
    MIN_OCTAVE,
    MAX_OCTAVE,
    MIN_BPM,
    MAX_BPM,
    DEFAULT_BPM,
    BTN_TONIC,
    BTN_SUPERTONIC,
    BTN_MEDIANT,
    BTN_SUBDOMINANT,
    BTN_DOMINANT,
    BTN_SUBMEDIANT,
    BTN_LEADING,
    DEGREE_NAMES,
)
from joychord.chord_config import CHORD_BUTTONS
from joychord.enums import ChordQuality, PlayMode


class TestConstants:
    """Test JoyChord constants"""

    def test_keys_list(self):
        """Test that KEYS contains all 12 chromatic notes"""
        assert len(KEYS) == 12
        assert KEYS[0] == 'C'
        assert KEYS[6] == 'F#'
        assert KEYS[11] == 'B'

    def test_octave_range(self):
        """Test octave range constants"""
        assert MIN_OCTAVE == -2
        assert MAX_OCTAVE == 2
        assert MIN_OCTAVE < MAX_OCTAVE

    def test_bpm_range(self):
        """Test BPM range constants"""
        assert MIN_BPM == 40
        assert MAX_BPM == 240
        assert DEFAULT_BPM == 120
        assert MIN_BPM < DEFAULT_BPM < MAX_BPM

    def test_degree_names(self):
        """Test degree name constants"""
        assert len(DEGREE_NAMES) == 7
        assert DEGREE_NAMES[1] == "Tonic"
        assert DEGREE_NAMES[2] == "Supertonic"
        assert DEGREE_NAMES[3] == "Mediant"
        assert DEGREE_NAMES[4] == "Subdominant"
        assert DEGREE_NAMES[5] == "Dominant"
        assert DEGREE_NAMES[6] == "Submediant"
        assert DEGREE_NAMES[7] == "Leading Tone"


class TestChordButtons:
    """Test chord button configuration"""

    def test_chord_buttons_count(self):
        """Test that there are 7 chord buttons"""
        assert len(CHORD_BUTTONS) == 7

    def test_chord_button_indices(self):
        """Test chord button index mapping"""
        assert BTN_TONIC in CHORD_BUTTONS
        assert BTN_SUPERTONIC in CHORD_BUTTONS
        assert BTN_MEDIANT in CHORD_BUTTONS
        assert BTN_SUBDOMINANT in CHORD_BUTTONS
        assert BTN_DOMINANT in CHORD_BUTTONS
        assert BTN_SUBMEDIANT in CHORD_BUTTONS
        assert BTN_LEADING in CHORD_BUTTONS

    def test_tonic_button_config(self):
        """Test Tonic button configuration"""
        btn = CHORD_BUTTONS[BTN_TONIC]
        assert btn.degree == 1
        assert btn.name == "Tonic (I)"
        assert btn.default_quality == ChordQuality.MAJOR
        assert btn.symbol == "I"

    def test_supertonic_button_config(self):
        """Test Supertonic button configuration"""
        btn = CHORD_BUTTONS[BTN_SUPERTONIC]
        assert btn.degree == 2
        assert btn.name == "Supertonic (II)"
        assert btn.default_quality == ChordQuality.MINOR
        assert btn.symbol == "ii"

    def test_mediant_button_config(self):
        """Test Mediant button configuration"""
        btn = CHORD_BUTTONS[BTN_MEDIANT]
        assert btn.degree == 3
        assert btn.name == "Mediant (III)"
        assert btn.default_quality == ChordQuality.MINOR
        assert btn.symbol == "iii"

    def test_subdominant_button_config(self):
        """Test Subdominant button configuration"""
        btn = CHORD_BUTTONS[BTN_SUBDOMINANT]
        assert btn.degree == 4
        assert btn.name == "Subdominant (IV)"
        assert btn.default_quality == ChordQuality.MAJOR
        assert btn.symbol == "IV"

    def test_dominant_button_config(self):
        """Test Dominant button configuration"""
        btn = CHORD_BUTTONS[BTN_DOMINANT]
        assert btn.degree == 5
        assert btn.name == "Dominant (V)"
        assert btn.default_quality == ChordQuality.MAJOR
        assert btn.symbol == "V"

    def test_submediant_button_config(self):
        """Test Submediant button configuration"""
        btn = CHORD_BUTTONS[BTN_SUBMEDIANT]
        assert btn.degree == 6
        assert btn.name == "Submediant (VI)"
        assert btn.default_quality == ChordQuality.MINOR
        assert btn.symbol == "vi"

    def test_leading_tone_button_config(self):
        """Test Leading Tone button configuration"""
        btn = CHORD_BUTTONS[BTN_LEADING]
        assert btn.degree == 7
        assert btn.name == "Leading Tone (VII)"
        assert btn.default_quality == ChordQuality.DIM
        assert btn.symbol == "vii°"

    def test_all_degrees_unique(self):
        """Test that all chord buttons have unique degrees"""
        degrees = [btn.degree for btn in CHORD_BUTTONS.values()]
        assert len(degrees) == len(set(degrees))
        assert set(degrees) == {1, 2, 3, 4, 5, 6, 7}


class TestPlayMode:
    """Test PlayMode enum"""

    def test_play_mode_values(self):
        """Test PlayMode enum values"""
        assert PlayMode.PLAY.value == "PLAY"
        assert PlayMode.ARP.value == "ARP"
        assert PlayMode.REPEAT.value == "REPEAT"
        assert PlayMode.DRUM.value == "DRUM"
        assert PlayMode.AUTODRUM.value == "AUTODRUM"

    def test_play_mode_count(self):
        """Test that there are 5 play modes"""
        assert len(list(PlayMode)) == 5
