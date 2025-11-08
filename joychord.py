#!/usr/bin/env python3
"""
JoyChord - Musical Chord Controller System
Converts Bluetooth game controller inputs into MIDI chord messages
Version: 0.1
"""

import pygame
import mido
import time
import sys
import click
import math
from enum import Enum
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


# ============================================================================
# CONSTANTS
# ============================================================================

VERSION = "0.1"

# MIDI Constants
MIDI_CHANNEL = 0  # Channel 1 (0-indexed)
DEFAULT_VELOCITY = 100
MIN_MIDI_NOTE = 24
MAX_MIDI_NOTE = 127

# Controller Button Mapping (pygame indices)
BTN_TONIC = 0       # Face Button 0 (×/A) - I (MAJOR)
BTN_LEADING = 1     # Face Button 1 (○/B) - VII (DIMINISHED)
BTN_MEDIANT = 2     # Face Button 2 (□/X) - III (MINOR)
BTN_DOMINANT = 3    # Face Button 3 (△/Y) - V (MAJOR)
BTN_SUBMEDIANT = 4  # L1 - VI (MINOR)
BTN_INVERSION = 5   # R1 - Inversion control
BTN_SUPERTONIC = 6  # L2 - II (MINOR)
BTN_SUBDOMINANT = 7 # R2 - IV (MAJOR)
BTN_SELECT = 8      # SELECT - Mode control
BTN_START = 9       # START - Help/Panic

# Joystick Settings
STICK_DEADZONE = 0.3
STICK_LEFT = 0  # LEFT stick index

# D-Pad Settings
DPAD_REPEAT_DELAY = 500  # ms
DPAD_REPEAT_RATE = 300   # ms

# Slash Chord Detection
SLASH_CHORD_WINDOW = 50  # ms

# BPM Settings
MIN_BPM = 40
MAX_BPM = 240
DEFAULT_BPM = 120

# Musical Constants
KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
MIN_OCTAVE = -2
MAX_OCTAVE = 2

# Degree Names
DEGREE_NAMES = {
    1: "Tonic",
    2: "Supertonic",
    3: "Mediant",
    4: "Subdominant",
    5: "Dominant",
    6: "Submediant",
    7: "Leading Tone"
}


# ============================================================================
# ENUMS
# ============================================================================

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


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ChordButton:
    """Represents a chord button configuration"""
    button_index: int
    degree: int
    name: str
    default_quality: ChordQuality
    symbol: str


@dataclass
class AppState:
    """Application state"""
    current_key: int = 0  # Index into KEYS list
    current_octave: int = 0
    play_mode: PlayMode = PlayMode.PLAY
    bpm: int = DEFAULT_BPM
    inversion: int = 0  # 0=root, 1=1st, 2=2nd
    velocity: int = DEFAULT_VELOCITY
    debug: bool = False
    show_help: bool = False


# ============================================================================
# CHORD CONFIGURATION
# ============================================================================

CHORD_BUTTONS = {
    BTN_TONIC: ChordButton(BTN_TONIC, 1, "Tonic (I)", ChordQuality.MAJOR, "I"),
    BTN_SUPERTONIC: ChordButton(BTN_SUPERTONIC, 2, "Supertonic (II)", ChordQuality.MINOR, "ii"),
    BTN_MEDIANT: ChordButton(BTN_MEDIANT, 3, "Mediant (III)", ChordQuality.MINOR, "iii"),
    BTN_SUBDOMINANT: ChordButton(BTN_SUBDOMINANT, 4, "Subdominant (IV)", ChordQuality.MAJOR, "IV"),
    BTN_DOMINANT: ChordButton(BTN_DOMINANT, 5, "Dominant (V)", ChordQuality.MAJOR, "V"),
    BTN_SUBMEDIANT: ChordButton(BTN_SUBMEDIANT, 6, "Submediant (VI)", ChordQuality.MINOR, "vi"),
    BTN_LEADING: ChordButton(BTN_LEADING, 7, "Leading Tone (VII)", ChordQuality.DIM, "vii°"),
}


# ============================================================================
# CHORD QUALITY FORMULAS
# ============================================================================

CHORD_INTERVALS = {
    ChordQuality.MAJOR: [0, 4, 7],
    ChordQuality.MINOR: [0, 3, 7],
    ChordQuality.DOM7: [0, 4, 7, 10],
    ChordQuality.MAJ7: [0, 4, 7, 11],
    ChordQuality.MIN7: [0, 3, 7, 10],
    ChordQuality.MAJ9: [0, 4, 7, 11, 14],
    ChordQuality.MIN9: [0, 3, 7, 10, 14],
    ChordQuality.SUS2: [0, 2, 7],
    ChordQuality.SUS4: [0, 5, 7],
    ChordQuality.DIM: [0, 3, 6],
    ChordQuality.DIM7: [0, 3, 6, 9],
    ChordQuality.AUG: [0, 4, 8],
    ChordQuality.MAJ6: [0, 4, 7, 9],
}


# ============================================================================
# MIDI SYSTEM
# ============================================================================

class MIDISystem:
    """Cross-platform MIDI output system"""

    def __init__(self, port_name: Optional[str] = None):
        self.port = None
        self.active_notes: List[int] = []
        self.initialize_port(port_name)

    def initialize_port(self, port_name: Optional[str] = None):
        """Initialize MIDI output port (cross-platform)"""
        try:
            available_ports = mido.get_output_names()

            if not available_ports:
                # Try to create a virtual port (Linux/macOS)
                try:
                    self.port = mido.open_output('JoyChord Virtual', virtual=True)
                    print(f"✓ Created virtual MIDI port: JoyChord Virtual")
                    return
                except:
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

    def send_note_on(self, note: int, velocity: int = DEFAULT_VELOCITY):
        """Send MIDI note on message"""
        if MIN_MIDI_NOTE <= note <= MAX_MIDI_NOTE:
            msg = mido.Message('note_on', channel=MIDI_CHANNEL, note=note, velocity=velocity)
            self.port.send(msg)
            if note not in self.active_notes:
                self.active_notes.append(note)

    def send_note_off(self, note: int):
        """Send MIDI note off message"""
        if note in self.active_notes:
            msg = mido.Message('note_off', channel=MIDI_CHANNEL, note=note, velocity=0)
            self.port.send(msg)
            self.active_notes.remove(note)

    def all_notes_off(self):
        """Send note off for all active notes"""
        for note in list(self.active_notes):
            self.send_note_off(note)
        self.active_notes.clear()

    def close(self):
        """Close MIDI port"""
        self.all_notes_off()
        if self.port:
            self.port.close()

    @staticmethod
    def list_ports():
        """List available MIDI ports"""
        ports = mido.get_output_names()
        if ports:
            print("Available MIDI output ports:")
            for i, port in enumerate(ports):
                print(f"  {i+1}. {port}")
        else:
            print("No MIDI output ports found.")


# ============================================================================
# MUSICAL SYSTEM
# ============================================================================

class MusicalSystem:
    """Nashville Number System and chord generation"""

    def __init__(self, key_index: int = 0, octave: int = 0):
        self.key_index = key_index
        self.octave = octave
        self.base_octave = 4  # Middle C octave

    def get_root_note(self, degree: int) -> int:
        """Get MIDI note number for a scale degree"""
        # Major scale intervals from tonic
        major_scale = [0, 2, 4, 5, 7, 9, 11]

        # Get interval for this degree
        interval = major_scale[degree - 1]

        # Calculate MIDI note
        base_note = 60  # Middle C
        key_offset = self.key_index
        octave_offset = self.octave * 12

        note = base_note + key_offset + interval + octave_offset
        return note

    def build_chord(self, degree: int, quality: ChordQuality, inversion: int = 0) -> List[int]:
        """Build a chord from degree, quality, and inversion"""
        root = self.get_root_note(degree)
        intervals = CHORD_INTERVALS.get(quality, [0, 4, 7])

        # Build base chord
        notes = [root + interval for interval in intervals]

        # Apply inversion
        notes = self.apply_inversion(notes, inversion)

        # Filter valid MIDI range
        notes = [n for n in notes if MIN_MIDI_NOTE <= n <= MAX_MIDI_NOTE]

        return notes

    def apply_inversion(self, notes: List[int], inversion: int) -> List[int]:
        """Apply chord inversion"""
        if inversion == 0 or len(notes) < 2:
            return notes

        result = notes.copy()
        for _ in range(inversion):
            # Move bottom note up an octave
            if result:
                bottom = result.pop(0)
                result.append(bottom + 12)

        return sorted(result)

    def get_bass_note(self, degree: int) -> int:
        """Get bass note for slash chord (one octave below)"""
        root = self.get_root_note(degree)
        bass = root - 12

        # Ensure it's in valid range
        if bass < MIN_MIDI_NOTE:
            bass += 12

        return bass

    def get_key_name(self) -> str:
        """Get current key name"""
        return KEYS[self.key_index]

    def change_key(self, delta: int):
        """Change key by delta (-1 or +1)"""
        self.key_index = (self.key_index + delta) % len(KEYS)

    def change_octave(self, delta: int):
        """Change octave by delta"""
        new_octave = self.octave + delta
        self.octave = max(MIN_OCTAVE, min(MAX_OCTAVE, new_octave))


# ============================================================================
# JOYSTICK QUALITY MAPPER
# ============================================================================

class JoystickQualityMapper:
    """Map LEFT joystick position to chord quality"""

    @staticmethod
    def get_angle(x: float, y: float) -> float:
        """Calculate angle in degrees (0=right, 90=up, 180=left, 270=down)"""
        # pygame joystick: x right is positive, y down is positive
        # We want: up=90°, so we negate y
        angle = math.degrees(math.atan2(-y, x))
        # Normalize to 0-360
        if angle < 0:
            angle += 360
        return angle

    @staticmethod
    def get_quality(x: float, y: float, default_quality: ChordQuality, deadzone: float = STICK_DEADZONE) -> ChordQuality:
        """
        Map joystick position to chord quality

        8-direction layout:
        - UP (90°): maj/min (default)
        - UP-RIGHT (45°): 7
        - RIGHT (0°): maj7/min7
        - DOWN-RIGHT (315°): maj9
        - DOWN (270°): sus4
        - DOWN-LEFT (225°): sus2/maj6
        - LEFT (180°): dim
        - UP-LEFT (135°): aug
        """
        magnitude = math.sqrt(x**2 + y**2)

        # Within deadzone - use default
        if magnitude < deadzone:
            return default_quality

        angle = JoystickQualityMapper.get_angle(x, y)

        # Determine quality by angle (45° sectors)
        # RIGHT: 337.5° to 22.5°
        if angle >= 337.5 or angle < 22.5:
            if default_quality == ChordQuality.MINOR:
                return ChordQuality.MIN7
            else:
                return ChordQuality.MAJ7

        # UP-RIGHT: 22.5° to 67.5°
        elif 22.5 <= angle < 67.5:
            return ChordQuality.DOM7

        # UP: 67.5° to 112.5°
        elif 67.5 <= angle < 112.5:
            return default_quality

        # UP-LEFT: 112.5° to 157.5°
        elif 112.5 <= angle < 157.5:
            return ChordQuality.AUG

        # LEFT: 157.5° to 202.5°
        elif 157.5 <= angle < 202.5:
            if default_quality == ChordQuality.DIM:
                return ChordQuality.DIM7
            else:
                return ChordQuality.DIM

        # DOWN-LEFT: 202.5° to 247.5°
        elif 202.5 <= angle < 247.5:
            # sus2 for minor, maj6 for major
            if default_quality == ChordQuality.MINOR:
                return ChordQuality.SUS2
            else:
                return ChordQuality.MAJ6

        # DOWN: 247.5° to 292.5°
        elif 247.5 <= angle < 292.5:
            return ChordQuality.SUS4

        # DOWN-RIGHT: 292.5° to 337.5°
        elif 292.5 <= angle < 337.5:
            return ChordQuality.MAJ9

        return default_quality


# ============================================================================
# CONTROLLER INPUT
# ============================================================================

class ControllerInput:
    """Handle pygame joystick input"""

    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.joystick = None
        self.button_states = {}
        self.button_press_times = {}
        self.dpad_last_press = {}
        self.dpad_repeat_active = {}
        self.last_start_press = 0

        self.initialize_controller()

    def initialize_controller(self):
        """Initialize game controller"""
        joystick_count = pygame.joystick.get_count()

        if joystick_count == 0:
            print("✗ No game controller detected.")
            print("  Please connect a Bluetooth controller and try again.")
            sys.exit(1)

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        print(f"✓ Controller connected: {self.joystick.get_name()}")
        print(f"  Buttons: {self.joystick.get_numbuttons()}")
        print(f"  Axes: {self.joystick.get_numaxes()}")
        print(f"  Hats: {self.joystick.get_numhats()}")

    def get_button_state(self, button: int) -> bool:
        """Get button state"""
        if self.joystick and button < self.joystick.get_numbuttons():
            return self.joystick.get_button(button)
        return False

    def get_axis(self, axis: int) -> float:
        """Get axis value"""
        if self.joystick and axis < self.joystick.get_numaxes():
            return self.joystick.get_axis(axis)
        return 0.0

    def get_hat(self, hat: int = 0) -> Tuple[int, int]:
        """Get D-pad hat value"""
        if self.joystick and hat < self.joystick.get_numhats():
            return self.joystick.get_hat(hat)
        return (0, 0)

    def is_button_just_pressed(self, button: int) -> bool:
        """Check if button was just pressed this frame"""
        current = self.get_button_state(button)
        previous = self.button_states.get(button, False)
        return current and not previous

    def is_button_just_released(self, button: int) -> bool:
        """Check if button was just released this frame"""
        current = self.get_button_state(button)
        previous = self.button_states.get(button, False)
        return not current and previous

    def update_button_states(self):
        """Update button state tracking"""
        for i in range(self.joystick.get_numbuttons()):
            self.button_states[i] = self.get_button_state(i)

    def get_pressed_chord_buttons(self) -> List[int]:
        """Get list of currently pressed chord buttons"""
        pressed = []
        for btn in CHORD_BUTTONS.keys():
            if self.get_button_state(btn):
                pressed.append(btn)
        return pressed


# ============================================================================
# HELP DISPLAY
# ============================================================================

HELP_TEXT = """
╔════════════════════════════════════════════════════════════════╗
║                  JoyChord Control Reference                     ║
╠════════════════════════════════════════════════════════════════╣
║                                                                  ║
║ CHORD BUTTONS:                                                  ║
║   ×/A    = Tonic (I) (MAJOR)              [Face Button 0]      ║
║   L2     = Supertonic (II) (MINOR)        [Button 6]           ║
║   □/X    = Mediant (III) (MINOR)          [Face Button 2]      ║
║   R2     = Subdominant (IV) (MAJOR)       [Button 7]           ║
║   △/Y    = Dominant (V) (MAJOR)           [Face Button 3]      ║
║   L1     = Submediant (VI) (MINOR)        [Button 4]           ║
║   ○/B    = Leading Tone (VII) (DIM)       [Face Button 1]      ║
║                                                                  ║
║ SLASH CHORDS:                                                   ║
║   Hold chord button + Press bass button                        ║
║   Example: Hold ×(I) then press □(III) = I/III (C/E)          ║
║                                                                  ║
║ LEFT STICK: Change chord quality (8 directions)                ║
║   Center/Up     = maj/min (default)                            ║
║   Up-Right      = 7 (dominant 7th)                             ║
║   Right         = maj7/min7                                    ║
║   Down-Right    = maj9                                          ║
║   Down          = sus4                                          ║
║   Down-Left     = sus2/maj6                                    ║
║   Left          = dim/dim7                                     ║
║   Up-Left       = aug                                           ║
║                                                                  ║
║ D-PAD:                                                          ║
║   Left/Right = Change key (-1/+1)                              ║
║   Up/Down    = Change octave (+1/-1)                           ║
║                                                                  ║
║ R1 (Button 5): Cycle inversions                               ║
║   Hold chord + press R1 → Root → 1st → 2nd → Root             ║
║                                                                  ║
║ SELECT (Button 8):                                             ║
║   Tap            = Cycle mode (PLAY→ARP→REPEAT→DRUM→AUTODRUM)║
║   Hold + D-Pad   = Adjust BPM/rhythm (future)                 ║
║                                                                  ║
║ START (Button 9):                                              ║
║   Single tap     = Toggle this help                            ║
║   Double tap     = Panic (all notes off)                       ║
║                                                                  ║
║ Press START again to close                                      ║
╚════════════════════════════════════════════════════════════════╝
"""


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class JoyChord:
    """Main JoyChord application"""

    def __init__(self, args):
        print(f"\n🎹 JoyChord v{VERSION} - Musical Chord Controller")
        print("=" * 60)

        # Initialize systems
        self.midi = MIDISystem(args.midi_port)
        self.controller = ControllerInput()
        self.musical = MusicalSystem(
            key_index=KEYS.index(args.key) if args.key in KEYS else 0,
            octave=args.octave
        )

        # Application state
        self.state = AppState(
            current_key=KEYS.index(args.key) if args.key in KEYS else 0,
            current_octave=args.octave,
            bpm=args.bpm,
            debug=args.debug
        )

        # Chord state tracking
        self.active_chord_button = None
        self.active_bass_button = None
        self.active_notes = []
        self.current_quality = None

        # Timing
        self.running = True
        self.clock = pygame.time.Clock()

        print(f"\n✓ JoyChord initialized")
        print(f"  Key: {self.musical.get_key_name()}")
        print(f"  Octave: {self.state.current_octave:+d}")
        print(f"  Mode: {self.state.play_mode.value}")
        print(f"  BPM: {self.state.bpm}")
        print(f"\n💡 Press START for help")
        print("=" * 60)

    def handle_chord_button_press(self, button: int):
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

    def handle_chord_button_release(self, button: int):
        """Handle chord button release"""
        if button == self.active_chord_button:
            self.stop_current_chord()
            self.active_chord_button = None
        elif button == self.active_bass_button:
            self.stop_current_chord()
            self.active_bass_button = None

    def play_current_chord(self):
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

    def play_slash_chord(self):
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

    def stop_current_chord(self):
        """Stop all currently playing notes"""
        for note in self.active_notes:
            self.midi.send_note_off(note)
        self.active_notes.clear()

    def handle_inversion_button(self):
        """Handle R1 inversion button"""
        if self.active_chord_button is not None and self.active_bass_button is None:
            # Cycle inversion
            self.state.inversion = (self.state.inversion + 1) % 3

            # Re-play chord with new inversion
            self.play_current_chord()

    def handle_dpad(self):
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

    def handle_select_button(self):
        """Handle SELECT button - mode cycling"""
        modes = list(PlayMode)
        current_index = modes.index(self.state.play_mode)
        next_index = (current_index + 1) % len(modes)
        self.state.play_mode = modes[next_index]
        print(f"🎵 Mode: {self.state.play_mode.value}")

    def handle_start_button(self):
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

    def update_joystick_quality(self):
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

    def process_events(self):
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

    def run(self):
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

    def cleanup(self):
        """Cleanup resources"""
        print("\n🔌 Shutting down JoyChord...")
        self.midi.close()
        pygame.quit()
        print("✓ Goodbye!\n")


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_controller_buttons():
    """Test mode: Display button presses"""
    print("\n🎮 Controller Button Test Mode")
    print("=" * 60)
    print("Press buttons to see their indices and mappings.")
    print("Press Ctrl+C to exit.\n")

    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("✗ No controller detected.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"Controller: {joystick.get_name()}")
    print(f"Buttons: {joystick.get_numbuttons()}\n")

    clock = pygame.time.Clock()
    running = True

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.JOYBUTTONDOWN:
                    button = event.button

                    if button in CHORD_BUTTONS:
                        chord = CHORD_BUTTONS[button]
                        print(f"Button {button}: {chord.name} ({chord.default_quality.value})")
                    elif button == BTN_INVERSION:
                        print(f"Button {button}: Inversion (R1)")
                    elif button == BTN_SELECT:
                        print(f"Button {button}: SELECT - Mode")
                    elif button == BTN_START:
                        print(f"Button {button}: START - Help/Panic")
                    else:
                        print(f"Button {button}: Unmapped")

                elif event.type == pygame.JOYHATMOTION:
                    hat_x, hat_y = event.value
                    if hat_x != 0 or hat_y != 0:
                        direction = []
                        if hat_y == 1: direction.append("UP")
                        if hat_y == -1: direction.append("DOWN")
                        if hat_x == -1: direction.append("LEFT")
                        if hat_x == 1: direction.append("RIGHT")
                        print(f"D-Pad: {' '.join(direction)}")

                elif event.type == pygame.JOYAXISMOTION:
                    if event.axis == 0 or event.axis == 1:  # LEFT stick
                        x = joystick.get_axis(0)
                        y = joystick.get_axis(1)
                        if abs(x) > 0.5 or abs(y) > 0.5:
                            angle = math.degrees(math.atan2(-y, x))
                            print(f"LEFT Stick: x={x:.2f}, y={y:.2f}, angle={angle:.1f}°")

            clock.tick(60)

    except KeyboardInterrupt:
        print("\n✓ Test complete")

    finally:
        pygame.quit()


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

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
def main(key, octave, bpm, mode, midi_port, list_midi, test_buttons, debug):
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
    app = JoyChord(args)
    app.run()


if __name__ == '__main__':
    main()
