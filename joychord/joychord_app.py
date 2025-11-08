"""Main JoyChord application"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import pygame

from joychord.midi_system import MIDISystem
from joychord.controller_input import ControllerInput
from joychord.musical_system import MusicalSystem
from joychord.joystick_mapper import JoystickQualityMapper
from joychord.models import AppState
from joychord.chord_config import CHORD_BUTTONS
from joychord.help_text import HELP_TEXT
from joychord.constants import (
    VERSION, BTN_INVERSION, BTN_SELECT, BTN_START, DEFAULT_BPM, KEYS
)
from joychord.enums import PlayMode, ChordQuality

if TYPE_CHECKING:
    from joychord.models import ChordButton


class JoyChord:
    """Main JoyChord application"""

    def __init__(self, args: object) -> None:
        print(f"\n🎹 JoyChord v{VERSION} - Musical Chord Controller")
        print("=" * 60)

        # Initialize systems
        midi_port = getattr(args, 'midi_port', None)
        self.midi = MIDISystem(midi_port)
        self.controller = ControllerInput()

        key = getattr(args, 'key', 'C')
        octave = getattr(args, 'octave', 0)
        self.musical = MusicalSystem(
            key_index=KEYS.index(key) if key in KEYS else 0,
            octave=octave
        )

        # Application state
        bpm = getattr(args, 'bpm', DEFAULT_BPM)
        debug = getattr(args, 'debug', False)

        self.state = AppState(
            current_key=KEYS.index(key) if key in KEYS else 0,
            current_octave=octave,
            bpm=bpm,
            debug=debug,
            play_mode=PlayMode.PLAY
        )

        # Chord state tracking
        self.active_chord_button: Optional[int] = None
        self.active_bass_button: Optional[int] = None
        self.active_notes: list[int] = []
        self.current_quality: Optional[ChordQuality] = None

        # Timing
        self.running = True
        self.clock = pygame.time.Clock()
        self.last_start_press: int = 0

        print(f"\n✓ JoyChord initialized")
        print(f"  Key: {self.musical.get_key_name()}")
        print(f"  Octave: {self.state.current_octave:+d}")
        print(f"  Mode: {self.state.play_mode.value}")
        print(f"  BPM: {self.state.bpm}")
        print(f"\n💡 Press START for help")
        print("=" * 60)

    def handle_chord_button_press(self, button: int) -> None:
        """Handle chord button press"""
        if button not in CHORD_BUTTONS:
            return

        chord_info = CHORD_BUTTONS[button]

        # Check if this is a slash chord (another button already held)
        if self.active_chord_button is not None and self.active_chord_button != button:
            # This is a slash chord - use this as bass
            self.active_bass_button = button
            self.play_slash_chord()
            return

        # Regular chord
        self.active_chord_button = button
        self.active_bass_button = None
        self.play_current_chord()

    def handle_chord_button_release(self, button: int) -> None:
        """Handle chord button release"""
        if button == self.active_chord_button:
            self.stop_current_chord()
            self.active_chord_button = None
        elif button == self.active_bass_button:
            self.stop_current_chord()
            self.active_bass_button = None

    def play_current_chord(self) -> None:
        """Play the current chord based on active button and stick position"""
        if self.active_chord_button is None:
            return

        chord_info = CHORD_BUTTONS[self.active_chord_button]

        # Get LEFT stick position for quality
        stick_x = self.controller.get_axis(0)  # X axis
        stick_y = self.controller.get_axis(1)  # Y axis

        quality = JoystickQualityMapper.get_quality(
            stick_x, stick_y, chord_info.default_quality
        )

        # Build chord
        notes = self.musical.build_chord(
            chord_info.degree,
            quality,
            self.state.inversion
        )

        # Stop previous notes
        self.stop_current_chord()

        # Play new notes
        for note in notes:
            self.midi.send_note_on(note, self.state.velocity)

        self.active_notes = notes
        self.current_quality = quality

        # Display feedback
        quality_str = quality.value
        inversion_str = ["Root", "1st", "2nd"][self.state.inversion]
        print(f"♪ {chord_info.name}: {self.musical.get_key_name()}{quality_str} → {notes} ({inversion_str})")

    def play_slash_chord(self) -> None:
        """Play slash chord (chord with different bass note)"""
        if self.active_chord_button is None or self.active_bass_button is None:
            return

        chord_info = CHORD_BUTTONS[self.active_chord_button]
        bass_info = CHORD_BUTTONS[self.active_bass_button]

        # Get chord quality from stick
        stick_x = self.controller.get_axis(0)
        stick_y = self.controller.get_axis(1)
        quality = JoystickQualityMapper.get_quality(
            stick_x, stick_y, chord_info.default_quality
        )

        # Build chord (no inversion for slash chords)
        chord_notes = self.musical.build_chord(chord_info.degree, quality, 0)

        # Get bass note
        bass_note = self.musical.get_bass_note(bass_info.degree)

        # Combine bass + chord
        notes = [bass_note] + chord_notes

        # Stop previous
        self.stop_current_chord()

        # Play new
        for note in notes:
            self.midi.send_note_on(note, self.state.velocity)

        self.active_notes = notes

        # Display feedback
        chord_symbol = f"{chord_info.symbol}/{bass_info.symbol}"
        key_name = self.musical.get_key_name()
        print(f"🎸 Slash: {chord_symbol} ({key_name}{quality.value}) → {notes}")

    def stop_current_chord(self) -> None:
        """Stop all currently playing notes"""
        for note in self.active_notes:
            self.midi.send_note_off(note)
        self.active_notes.clear()

    def handle_inversion_button(self) -> None:
        """Handle R1 inversion button"""
        if self.active_chord_button is not None and self.active_bass_button is None:
            # Cycle inversion
            self.state.inversion = (self.state.inversion + 1) % 3

            # Re-play chord with new inversion
            self.play_current_chord()

    def handle_dpad(self) -> None:
        """Handle D-Pad input for key/octave changes"""
        hat_x, hat_y = self.controller.get_hat(0)

        # Key change (LEFT/RIGHT)
        if hat_x != 0:
            self.musical.change_key(hat_x)
            self.state.current_key = self.musical.key_index
            print(f"🎹 Key: {self.musical.get_key_name()}")

            # Update chord if playing
            if self.active_chord_button is not None:
                if self.active_bass_button is not None:
                    self.play_slash_chord()
                else:
                    self.play_current_chord()

        # Octave change (UP/DOWN)
        if hat_y != 0:
            self.musical.change_octave(hat_y)
            self.state.current_octave = self.musical.octave
            print(f"📈 Octave: {self.state.current_octave:+d}")

            # Update chord if playing
            if self.active_chord_button is not None:
                if self.active_bass_button is not None:
                    self.play_slash_chord()
                else:
                    self.play_current_chord()

    def handle_select_button(self) -> None:
        """Handle SELECT button - mode cycling"""
        modes = list(PlayMode)
        current_index = modes.index(self.state.play_mode) if self.state.play_mode else 0
        next_index = (current_index + 1) % len(modes)
        self.state.play_mode = modes[next_index]
        print(f"🎵 Mode: {self.state.play_mode.value}")

    def handle_start_button(self) -> None:
        """Handle START button - help/panic"""
        current_time = pygame.time.get_ticks()

        # Check for double-tap (panic)
        if current_time - self.last_start_press < 300:
            # Double tap - PANIC
            self.midi.all_notes_off()
            self.active_notes.clear()
            self.active_chord_button = None
            self.active_bass_button = None
            print("🚨 PANIC: All notes off")
        else:
            # Single tap - toggle help
            self.state.show_help = not self.state.show_help
            if self.state.show_help:
                print(HELP_TEXT)
            else:
                print("Help closed")

        self.last_start_press = current_time

    def update_joystick_quality(self) -> None:
        """Update chord quality in real-time based on joystick position"""
        if self.active_chord_button is not None and self.active_bass_button is None:
            # Get current quality from stick
            stick_x = self.controller.get_axis(0)
            stick_y = self.controller.get_axis(1)

            chord_info = CHORD_BUTTONS[self.active_chord_button]
            quality = JoystickQualityMapper.get_quality(
                stick_x, stick_y, chord_info.default_quality
            )

            # If quality changed, replay chord
            if quality != self.current_quality:
                self.play_current_chord()

    def process_events(self) -> None:
        """Process pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.JOYBUTTONDOWN:
                button = event.button

                # Chord buttons
                if button in CHORD_BUTTONS:
                    self.handle_chord_button_press(button)

                # Inversion button
                elif button == BTN_INVERSION:
                    self.handle_inversion_button()

                # SELECT button
                elif button == BTN_SELECT:
                    self.handle_select_button()

                # START button
                elif button == BTN_START:
                    self.handle_start_button()

            elif event.type == pygame.JOYBUTTONUP:
                button = event.button

                if button in CHORD_BUTTONS:
                    self.handle_chord_button_release(button)

            elif event.type == pygame.JOYHATMOTION:
                self.handle_dpad()

    def run(self) -> None:
        """Main application loop"""
        try:
            while self.running:
                # Process input events
                self.process_events()

                # Update joystick quality in real-time
                self.update_joystick_quality()

                # Update controller state
                self.controller.update_button_states()

                # Cap at 60 FPS
                self.clock.tick(60)

        except KeyboardInterrupt:
            print("\n\n⚠ Interrupted by user")

        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Cleanup resources"""
        print("\n🔌 Shutting down JoyChord...")
        self.midi.close()
        pygame.quit()
        print("✓ Goodbye!\n")
