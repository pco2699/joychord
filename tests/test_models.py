"""Unit tests for JoyChord models and data classes"""

from __future__ import annotations
import pytest

from joychord.models import ChordButton, AppState
from joychord.enums import ChordQuality, PlayMode


class TestChordButton:
    """Test ChordButton dataclass"""

    def test_chord_button_creation(self):
        """Test creating a ChordButton"""
        button = ChordButton(
            button_index=0,
            degree=1,
            name="Tonic (I)",
            default_quality=ChordQuality.MAJOR,
            symbol="I"
        )

        assert button.button_index == 0
        assert button.degree == 1
        assert button.name == "Tonic (I)"
        assert button.default_quality == ChordQuality.MAJOR
        assert button.symbol == "I"

    def test_chord_button_equality(self):
        """Test ChordButton equality comparison"""
        button1 = ChordButton(0, 1, "Test", ChordQuality.MAJOR, "I")
        button2 = ChordButton(0, 1, "Test", ChordQuality.MAJOR, "I")

        assert button1 == button2


class TestAppState:
    """Test AppState dataclass"""

    def test_app_state_defaults(self):
        """Test AppState default values"""
        state = AppState()

        assert state.current_key == 0
        assert state.current_octave == 0
        assert state.play_mode is None
        assert state.bpm == 120
        assert state.inversion == 0
        assert state.velocity == 100
        assert state.debug is False
        assert state.show_help is False

    def test_app_state_with_values(self):
        """Test AppState with custom values"""
        state = AppState(
            current_key=5,
            current_octave=2,
            play_mode=PlayMode.ARP,
            bpm=140,
            inversion=1,
            velocity=110,
            debug=True,
            show_help=True
        )

        assert state.current_key == 5
        assert state.current_octave == 2
        assert state.play_mode == PlayMode.ARP
        assert state.bpm == 140
        assert state.inversion == 1
        assert state.velocity == 110
        assert state.debug is True
        assert state.show_help is True
