"""MIDI system for cross-platform MIDI output"""

from __future__ import annotations
from typing import Optional
import sys

import mido

from joychord.constants import MIDI_CHANNEL, DEFAULT_VELOCITY, MIN_MIDI_NOTE, MAX_MIDI_NOTE


class MIDISystem:
    """Cross-platform MIDI output system"""

    def __init__(self, port_name: Optional[str] = None) -> None:
        self.port: Optional[mido.ports.BaseOutput] = None
        self.active_notes: list[int] = []
        self.initialize_port(port_name)

    def initialize_port(self, port_name: Optional[str] = None) -> None:
        """Initialize MIDI output port (cross-platform)"""
        try:
            available_ports = mido.get_output_names()

            if not available_ports:
                # Try to create a virtual port (Linux/macOS)
                try:
                    self.port = mido.open_output('JoyChord Virtual', virtual=True)
                    print(f"✓ Created virtual MIDI port: JoyChord Virtual")
                    return
                except Exception:
                    print("✗ No MIDI ports available. On Windows, install loopMIDI.")
                    print("  On Linux, ensure ALSA/JACK is running.")
                    sys.exit(1)

            # Use specified port or first available
            if port_name and port_name in available_ports:
                self.port = mido.open_output(port_name)
                print(f"✓ Connected to MIDI port: {port_name}")
            else:
                self.port = mido.open_output(available_ports[0])
                print(f"✓ Connected to MIDI port: {available_ports[0]}")

        except Exception as e:
            print(f"✗ MIDI initialization error: {e}")
            sys.exit(1)

    def send_note_on(self, note: int, velocity: int = DEFAULT_VELOCITY) -> None:
        """Send MIDI note on message"""
        if self.port is None:
            return

        if MIN_MIDI_NOTE <= note <= MAX_MIDI_NOTE:
            msg = mido.Message('note_on', channel=MIDI_CHANNEL, note=note, velocity=velocity)
            self.port.send(msg)
            if note not in self.active_notes:
                self.active_notes.append(note)

    def send_note_off(self, note: int) -> None:
        """Send MIDI note off message"""
        if self.port is None:
            return

        if note in self.active_notes:
            msg = mido.Message('note_off', channel=MIDI_CHANNEL, note=note, velocity=0)
            self.port.send(msg)
            self.active_notes.remove(note)

    def all_notes_off(self) -> None:
        """Send note off for all active notes"""
        for note in list(self.active_notes):
            self.send_note_off(note)
        self.active_notes.clear()

    def close(self) -> None:
        """Close MIDI port"""
        self.all_notes_off()
        if self.port:
            self.port.close()

    @staticmethod
    def list_ports() -> None:
        """List available MIDI ports"""
        ports = mido.get_output_names()
        if ports:
            print("Available MIDI output ports:")
            for i, port in enumerate(ports):
                print(f"  {i+1}. {port}")
        else:
            print("No MIDI output ports found.")
