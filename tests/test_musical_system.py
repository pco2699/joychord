"""Unit tests for JoyChord Musical System"""

import pytest
from joychord.musical_system import MusicalSystem
from joychord.enums import ChordQuality
from joychord.constants import KEYS, MIN_OCTAVE, MAX_OCTAVE, CHORD_INTERVALS


class TestMusicalSystem:
    """Test the MusicalSystem class"""

    def test_initialization(self):
        """Test MusicalSystem initialization"""
        system = MusicalSystem(key_index=0, octave=0)
        assert system.key_index == 0
        assert system.octave == 0
        assert system.base_octave == 4

    def test_get_key_name(self):
        """Test getting current key name"""
        system = MusicalSystem(key_index=0, octave=0)
        assert system.get_key_name() == "C"

        system = MusicalSystem(key_index=2, octave=0)
        assert system.get_key_name() == "D"

    def test_get_root_note_c_major(self):
        """Test getting root notes in C major"""
        system = MusicalSystem(key_index=0, octave=0)

        # Test all scale degrees
        assert system.get_root_note(1) == 60  # C4 (Tonic)
        assert system.get_root_note(2) == 62  # D4 (Supertonic)
        assert system.get_root_note(3) == 64  # E4 (Mediant)
        assert system.get_root_note(4) == 65  # F4 (Subdominant)
        assert system.get_root_note(5) == 67  # G4 (Dominant)
        assert system.get_root_note(6) == 69  # A4 (Submediant)
        assert system.get_root_note(7) == 71  # B4 (Leading Tone)

    def test_get_root_note_with_octave_shift(self):
        """Test root notes with octave shifting"""
        system = MusicalSystem(key_index=0, octave=1)
        assert system.get_root_note(1) == 72  # C5 (one octave up)

        system = MusicalSystem(key_index=0, octave=-1)
        assert system.get_root_note(1) == 48  # C3 (one octave down)

    def test_get_root_note_different_keys(self):
        """Test root notes in different keys"""
        # D major (key_index=2)
        system = MusicalSystem(key_index=2, octave=0)
        assert system.get_root_note(1) == 62  # D4

        # F# major (key_index=6)
        system = MusicalSystem(key_index=6, octave=0)
        assert system.get_root_note(1) == 66  # F#4

    def test_build_chord_major(self):
        """Test building major chords"""
        system = MusicalSystem(key_index=0, octave=0)
        chord = system.build_chord(1, ChordQuality.MAJOR, 0)

        # C major: C, E, G
        assert chord == [60, 64, 67]

    def test_build_chord_minor(self):
        """Test building minor chords"""
        system = MusicalSystem(key_index=0, octave=0)
        chord = system.build_chord(2, ChordQuality.MINOR, 0)

        # D minor: D, F, A
        assert chord == [62, 65, 69]

    def test_build_chord_dominant_7(self):
        """Test building dominant 7th chords"""
        system = MusicalSystem(key_index=0, octave=0)
        chord = system.build_chord(5, ChordQuality.DOM7, 0)

        # G7: G, B, D, F
        assert chord == [67, 71, 74, 77]

    def test_build_chord_maj7(self):
        """Test building major 7th chords"""
        system = MusicalSystem(key_index=0, octave=0)
        chord = system.build_chord(1, ChordQuality.MAJ7, 0)

        # Cmaj7: C, E, G, B
        assert chord == [60, 64, 67, 71]

    def test_build_chord_sus4(self):
        """Test building sus4 chords"""
        system = MusicalSystem(key_index=0, octave=0)
        chord = system.build_chord(1, ChordQuality.SUS4, 0)

        # Csus4: C, F, G
        assert chord == [60, 65, 67]

    def test_build_chord_diminished(self):
        """Test building diminished chords"""
        system = MusicalSystem(key_index=0, octave=0)
        chord = system.build_chord(7, ChordQuality.DIM, 0)

        # Bdim: B, D, F
        assert chord == [71, 74, 77]

    def test_apply_inversion_root(self):
        """Test root position (no inversion)"""
        system = MusicalSystem(key_index=0, octave=0)
        notes = [60, 64, 67]  # C, E, G
        inverted = system.apply_inversion(notes, 0)
        assert inverted == [60, 64, 67]

    def test_apply_inversion_first(self):
        """Test first inversion"""
        system = MusicalSystem(key_index=0, octave=0)
        notes = [60, 64, 67]  # C, E, G
        inverted = system.apply_inversion(notes, 1)
        # First inversion: E, G, C (E, G, C+octave)
        assert inverted == [64, 67, 72]

    def test_apply_inversion_second(self):
        """Test second inversion"""
        system = MusicalSystem(key_index=0, octave=0)
        notes = [60, 64, 67]  # C, E, G
        inverted = system.apply_inversion(notes, 2)
        # Second inversion: G, C, E (G, C+octave, E+octave)
        assert inverted == [67, 72, 76]

    def test_get_bass_note(self):
        """Test getting bass note for slash chords"""
        system = MusicalSystem(key_index=0, octave=0)

        # Bass note should be one octave below root
        bass = system.get_bass_note(1)  # C
        assert bass == 48  # C3

        bass = system.get_bass_note(5)  # G
        assert bass == 55  # G3

    def test_change_key(self):
        """Test changing key"""
        system = MusicalSystem(key_index=0, octave=0)
        assert system.get_key_name() == "C"

        system.change_key(1)
        assert system.key_index == 1
        assert system.get_key_name() == "C#"

        system.change_key(-1)
        assert system.key_index == 0
        assert system.get_key_name() == "C"

        # Test wrap-around
        system.change_key(-1)
        assert system.key_index == 11
        assert system.get_key_name() == "B"

    def test_change_octave(self):
        """Test changing octave"""
        system = MusicalSystem(key_index=0, octave=0)
        assert system.octave == 0

        system.change_octave(1)
        assert system.octave == 1

        system.change_octave(1)
        assert system.octave == 2

        # Test max boundary
        system.change_octave(1)
        assert system.octave == 2  # Should stay at max

        # Test min boundary
        system.octave = -2
        system.change_octave(-1)
        assert system.octave == -2  # Should stay at min

    def test_chord_intervals_coverage(self):
        """Test that all chord qualities have interval definitions"""
        required_qualities = [
            ChordQuality.MAJOR,
            ChordQuality.MINOR,
            ChordQuality.DOM7,
            ChordQuality.MAJ7,
            ChordQuality.MIN7,
            ChordQuality.MAJ9,
            ChordQuality.MIN9,
            ChordQuality.SUS2,
            ChordQuality.SUS4,
            ChordQuality.DIM,
            ChordQuality.DIM7,
            ChordQuality.AUG,
            ChordQuality.MAJ6,
        ]

        for quality in required_qualities:
            assert quality in CHORD_INTERVALS, f"Missing intervals for {quality}"
            intervals = CHORD_INTERVALS[quality]
            assert isinstance(intervals, list)
            assert len(intervals) >= 2
            assert 0 in intervals  # Root should always be present

    def test_build_all_chord_qualities(self):
        """Test building all chord quality types"""
        system = MusicalSystem(key_index=0, octave=0)

        for quality in ChordQuality:
            if quality in CHORD_INTERVALS:
                chord = system.build_chord(1, quality, 0)
                assert isinstance(chord, list)
                assert len(chord) >= 2
                assert chord[0] == 60  # Should start with C


class TestChordQuality:
    """Test ChordQuality enum"""

    def test_chord_quality_values(self):
        """Test that chord qualities have correct string values"""
        assert ChordQuality.MAJOR.value == "major"
        assert ChordQuality.MINOR.value == "minor"
        assert ChordQuality.DOM7.value == "7"
        assert ChordQuality.MAJ7.value == "maj7"
        assert ChordQuality.MIN7.value == "min7"
        assert ChordQuality.SUS4.value == "sus4"
        assert ChordQuality.DIM.value == "dim"
        assert ChordQuality.AUG.value == "aug"
