"""Click CLI for JoyChord"""

from __future__ import annotations
import click

from joychord.constants import KEYS, MIN_OCTAVE, MAX_OCTAVE, MIN_BPM, MAX_BPM, DEFAULT_BPM, VERSION
from joychord.midi_system import MIDISystem
from joychord.testing import test_controller_buttons


@click.command()
@click.option('--key', type=click.Choice(KEYS, case_sensitive=False), default='C',
              help='Starting key (default: C)')
@click.option('--octave', type=click.IntRange(MIN_OCTAVE, MAX_OCTAVE), default=0,
              help=f'Starting octave offset from {MIN_OCTAVE} to {MAX_OCTAVE} (default: 0)')
@click.option('--bpm', type=click.IntRange(MIN_BPM, MAX_BPM), default=DEFAULT_BPM,
              help=f'Starting BPM from {MIN_BPM} to {MAX_BPM} (default: {DEFAULT_BPM})')
@click.option('--mode', type=click.Choice(['play', 'arp', 'repeat', 'drum', 'autodrum'], case_sensitive=False),
              default='play', help='Starting playback mode (default: play)')
@click.option('--midi-port', type=str, default=None,
              help='MIDI output port name')
@click.option('--list-midi', is_flag=True,
              help='List available MIDI ports and exit')
@click.option('--test-buttons', is_flag=True,
              help='Test controller button mapping')
@click.option('--debug', is_flag=True,
              help='Enable debug output')
@click.version_option(version=VERSION, prog_name='joychord')
def main(
    key: str,
    octave: int,
    bpm: int,
    mode: str,
    midi_port: str | None,
    list_midi: bool,
    test_buttons: bool,
    debug: bool
) -> None:
    """JoyChord - Musical Chord Controller System

    Convert your Bluetooth game controller into a powerful MIDI chord controller.

    Examples:

      \b
      joychord                          # Start with defaults
      joychord --key D --octave 1       # Start in D major, octave +1
      joychord --bpm 140                # Set BPM to 140
      joychord --test-buttons           # Test controller button mapping
      joychord --list-midi              # List available MIDI ports
    """
    # Handle special modes
    if list_midi:
        MIDISystem.list_ports()
        return

    if test_buttons:
        test_controller_buttons()
        return

    # Create a simple args object for compatibility
    class Args:
        pass

    args = Args()
    args.key = key
    args.octave = octave
    args.bpm = bpm
    args.mode = mode
    args.midi_port = midi_port
    args.debug = debug

    # Run main application
    from joychord.joychord_app import JoyChord
    app = JoyChord(args)
    app.run()


if __name__ == '__main__':
    main()
