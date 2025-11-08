"""Unit tests for JoyChord MIDI System"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from joychord import MIDISystem, MIN_MIDI_NOTE, MAX_MIDI_NOTE


class TestMIDISystem:
    """Test the MIDISystem class"""

    @patch('joychord.mido')
    def test_initialization_with_existing_port(self, mock_mido):
        """Test MIDI system initialization with existing port"""
        mock_mido.get_output_names.return_value = ['Test Port']
        mock_port = Mock()
        mock_mido.open_output.return_value = mock_port

        system = MIDISystem(port_name='Test Port')

        assert system.port == mock_port
        assert system.active_notes == []
        mock_mido.open_output.assert_called_once_with('Test Port')

    @patch('joychord.mido')
    def test_initialization_with_first_available_port(self, mock_mido):
        """Test initialization uses first available port when none specified"""
        mock_mido.get_output_names.return_value = ['Port1', 'Port2']
        mock_port = Mock()
        mock_mido.open_output.return_value = mock_port

        system = MIDISystem()

        assert system.port == mock_port
        mock_mido.open_output.assert_called_once_with('Port1')

    @patch('sys.exit', side_effect=SystemExit)
    @patch('joychord.mido')
    def test_initialization_no_ports(self, mock_mido, mock_exit):
        """Test initialization fails gracefully with no ports"""
        mock_mido.get_output_names.return_value = []
        mock_mido.open_output.side_effect = Exception("No virtual port support")

        with pytest.raises(SystemExit):
            MIDISystem()

    @patch('joychord.mido')
    def test_send_note_on(self, mock_mido):
        """Test sending MIDI note on message"""
        mock_mido.get_output_names.return_value = ['Test Port']
        mock_port = Mock()
        mock_mido.open_output.return_value = mock_port
        mock_message = Mock()
        mock_mido.Message.return_value = mock_message

        system = MIDISystem()
        system.send_note_on(60, 100)

        mock_mido.Message.assert_called_once_with(
            'note_on', channel=0, note=60, velocity=100
        )
        mock_port.send.assert_called_once_with(mock_message)
        assert 60 in system.active_notes

    @patch('joychord.mido')
    def test_send_note_on_out_of_range_low(self, mock_mido):
        """Test that notes below MIN_MIDI_NOTE are not sent"""
        mock_mido.get_output_names.return_value = ['Test Port']
        mock_port = Mock()
        mock_mido.open_output.return_value = mock_port

        system = MIDISystem()
        system.send_note_on(MIN_MIDI_NOTE - 1)

        mock_port.send.assert_not_called()
        assert len(system.active_notes) == 0

    @patch('joychord.mido')
    def test_send_note_on_out_of_range_high(self, mock_mido):
        """Test that notes above MAX_MIDI_NOTE are not sent"""
        mock_mido.get_output_names.return_value = ['Test Port']
        mock_port = Mock()
        mock_mido.open_output.return_value = mock_port

        system = MIDISystem()
        system.send_note_on(MAX_MIDI_NOTE + 1)

        mock_port.send.assert_not_called()
        assert len(system.active_notes) == 0

    @patch('joychord.mido')
    def test_send_note_off(self, mock_mido):
        """Test sending MIDI note off message"""
        mock_mido.get_output_names.return_value = ['Test Port']
        mock_port = Mock()
        mock_mido.open_output.return_value = mock_port
        mock_message = Mock()
        mock_mido.Message.return_value = mock_message

        system = MIDISystem()
        system.active_notes = [60]
        system.send_note_off(60)

        mock_mido.Message.assert_called_once_with(
            'note_off', channel=0, note=60, velocity=0
        )
        mock_port.send.assert_called_once_with(mock_message)
        assert 60 not in system.active_notes

    @patch('joychord.mido')
    def test_send_note_off_not_active(self, mock_mido):
        """Test that note off is not sent for inactive notes"""
        mock_mido.get_output_names.return_value = ['Test Port']
        mock_port = Mock()
        mock_mido.open_output.return_value = mock_port

        system = MIDISystem()
        system.send_note_off(60)

        mock_port.send.assert_not_called()

    @patch('joychord.mido')
    def test_all_notes_off(self, mock_mido):
        """Test all notes off functionality"""
        mock_mido.get_output_names.return_value = ['Test Port']
        mock_port = Mock()
        mock_mido.open_output.return_value = mock_port
        mock_mido.Message.return_value = Mock()

        system = MIDISystem()
        system.active_notes = [60, 64, 67]
        system.all_notes_off()

        assert len(system.active_notes) == 0
        assert mock_port.send.call_count == 3

    @patch('joychord.mido')
    def test_close(self, mock_mido):
        """Test MIDI system cleanup"""
        mock_mido.get_output_names.return_value = ['Test Port']
        mock_port = Mock()
        mock_mido.open_output.return_value = mock_port
        mock_mido.Message.return_value = Mock()

        system = MIDISystem()
        system.active_notes = [60, 64]
        system.close()

        assert len(system.active_notes) == 0
        mock_port.close.assert_called_once()

    @patch('joychord.mido')
    def test_list_ports(self, mock_mido, capsys):
        """Test listing available MIDI ports"""
        mock_mido.get_output_names.return_value = ['Port1', 'Port2', 'Port3']

        MIDISystem.list_ports()

        captured = capsys.readouterr()
        assert 'Port1' in captured.out
        assert 'Port2' in captured.out
        assert 'Port3' in captured.out

    @patch('joychord.mido')
    def test_list_ports_empty(self, mock_mido, capsys):
        """Test listing ports when none are available"""
        mock_mido.get_output_names.return_value = []

        MIDISystem.list_ports()

        captured = capsys.readouterr()
        assert 'No MIDI output ports found' in captured.out

    @patch('joychord.mido')
    def test_duplicate_note_on_not_duplicated(self, mock_mido):
        """Test that sending the same note on twice doesn't duplicate"""
        mock_mido.get_output_names.return_value = ['Test Port']
        mock_port = Mock()
        mock_mido.open_output.return_value = mock_port
        mock_mido.Message.return_value = Mock()

        system = MIDISystem()
        system.send_note_on(60)
        system.send_note_on(60)

        assert system.active_notes.count(60) == 1

    @patch('joychord.mido')
    def test_multiple_notes_active(self, mock_mido):
        """Test tracking multiple active notes"""
        mock_mido.get_output_names.return_value = ['Test Port']
        mock_port = Mock()
        mock_mido.open_output.return_value = mock_port
        mock_mido.Message.return_value = Mock()

        system = MIDISystem()
        system.send_note_on(60)
        system.send_note_on(64)
        system.send_note_on(67)

        assert len(system.active_notes) == 3
        assert 60 in system.active_notes
        assert 64 in system.active_notes
        assert 67 in system.active_notes
