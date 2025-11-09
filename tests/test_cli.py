"""Unit tests for Click CLI"""

import pytest
from click.testing import CliRunner
from joychord.cli import main
from joychord.constants import VERSION


class TestCLI:
    """Test Click command-line interface"""

    def test_help_option(self):
        """Test --help option"""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])

        assert result.exit_code == 0
        assert 'JoyChord' in result.output
        assert '--key' in result.output
        assert '--octave' in result.output
        assert '--bpm' in result.output

    def test_version_option(self):
        """Test --version option"""
        runner = CliRunner()
        result = runner.invoke(main, ['--version'])

        assert result.exit_code == 0
        assert VERSION in result.output

    def test_list_midi_option(self):
        """Test --list-midi option"""
        runner = CliRunner()
        result = runner.invoke(main, ['--list-midi'])

        # Should not crash, even if no MIDI available
        assert result.exit_code in [0, 1]

    def test_invalid_key(self):
        """Test invalid key argument"""
        runner = CliRunner()
        result = runner.invoke(main, ['--key', 'Z'])

        assert result.exit_code != 0
        assert 'Invalid value' in result.output

    def test_invalid_octave_high(self):
        """Test octave above range"""
        runner = CliRunner()
        result = runner.invoke(main, ['--octave', '5'])

        assert result.exit_code != 0
        assert 'Invalid value' in result.output or 'not in the range' in result.output

    def test_invalid_octave_low(self):
        """Test octave below range"""
        runner = CliRunner()
        result = runner.invoke(main, ['--octave', '-5'])

        assert result.exit_code != 0
        assert 'Invalid value' in result.output or 'not in the range' in result.output

    def test_invalid_bpm_high(self):
        """Test BPM above range"""
        runner = CliRunner()
        result = runner.invoke(main, ['--bpm', '300'])

        assert result.exit_code != 0
        assert 'Invalid value' in result.output or 'not in the range' in result.output

    def test_invalid_bpm_low(self):
        """Test BPM below range"""
        runner = CliRunner()
        result = runner.invoke(main, ['--bpm', '10'])

        assert result.exit_code != 0
        assert 'Invalid value' in result.output or 'not in the range' in result.output

    def test_invalid_mode(self):
        """Test invalid mode argument"""
        runner = CliRunner()
        result = runner.invoke(main, ['--mode', 'invalid'])

        assert result.exit_code != 0
        assert 'Invalid value' in result.output

    def test_valid_key_case_insensitive(self):
        """Test that key option is case-insensitive"""
        runner = CliRunner()

        # Test lowercase
        result = runner.invoke(main, ['--key', 'd', '--test-buttons'])
        # Should fail due to no controller, not bad argument
        assert 'Invalid value' not in result.output

        # Test uppercase
        result = runner.invoke(main, ['--key', 'D', '--test-buttons'])
        assert 'Invalid value' not in result.output

    def test_valid_mode_case_insensitive(self):
        """Test that mode option is case-insensitive"""
        runner = CliRunner()

        result = runner.invoke(main, ['--mode', 'arp', '--test-buttons'])
        assert 'Invalid value' not in result.output

        result = runner.invoke(main, ['--mode', 'ARP', '--test-buttons'])
        assert 'Invalid value' not in result.output

    def test_debug_flag(self):
        """Test --debug flag"""
        runner = CliRunner()
        result = runner.invoke(main, ['--debug', '--list-midi'])

        # Should accept the flag without error
        assert 'Invalid' not in result.output or result.exit_code in [0, 1]

    def test_midi_port_option(self):
        """Test --midi-port option"""
        runner = CliRunner()
        result = runner.invoke(main, ['--midi-port', 'TestPort', '--list-midi'])

        # Should accept the option without error
        assert 'Invalid' not in result.output or result.exit_code in [0, 1]

    def test_multiple_options(self):
        """Test multiple options together"""
        runner = CliRunner()
        result = runner.invoke(main, [
            '--key', 'D',
            '--octave', '1',
            '--bpm', '140',
            '--mode', 'arp',
            '--list-midi'
        ])

        # Should not have argument parsing errors
        assert 'Invalid value' not in result.output
