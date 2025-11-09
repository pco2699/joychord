"""Pytest configuration and fixtures"""

import pytest


@pytest.fixture
def mock_controller():
    """Mock controller for testing without hardware"""
    from unittest.mock import Mock
    controller = Mock()
    controller.get_button_state.return_value = False
    controller.get_axis.return_value = 0.0
    controller.get_hat.return_value = (0, 0)
    return controller


@pytest.fixture
def mock_midi_system():
    """Mock MIDI system for testing without MIDI hardware"""
    from unittest.mock import Mock
    midi = Mock()
    midi.active_notes = []
    midi.send_note_on = Mock()
    midi.send_note_off = Mock()
    midi.all_notes_off = Mock()
    return midi
