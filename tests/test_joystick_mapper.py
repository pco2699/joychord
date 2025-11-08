"""Unit tests for JoyChord Joystick Quality Mapper"""

import pytest
import math
from joychord import JoystickQualityMapper, ChordQuality


class TestJoystickQualityMapper:
    """Test the JoystickQualityMapper class"""

    def test_get_angle_right(self):
        """Test angle calculation for right direction"""
        angle = JoystickQualityMapper.get_angle(1.0, 0.0)
        assert abs(angle - 0.0) < 0.1

    def test_get_angle_up(self):
        """Test angle calculation for up direction"""
        angle = JoystickQualityMapper.get_angle(0.0, -1.0)
        assert abs(angle - 90.0) < 0.1

    def test_get_angle_left(self):
        """Test angle calculation for left direction"""
        angle = JoystickQualityMapper.get_angle(-1.0, 0.0)
        assert abs(angle - 180.0) < 0.1

    def test_get_angle_down(self):
        """Test angle calculation for down direction"""
        angle = JoystickQualityMapper.get_angle(0.0, 1.0)
        assert abs(angle - 270.0) < 0.1

    def test_get_angle_diagonal(self):
        """Test angle calculation for diagonal directions"""
        # Up-right (45°)
        angle = JoystickQualityMapper.get_angle(1.0, -1.0)
        assert abs(angle - 45.0) < 0.1

        # Up-left (135°)
        angle = JoystickQualityMapper.get_angle(-1.0, -1.0)
        assert abs(angle - 135.0) < 0.1

    def test_get_quality_center_major(self):
        """Test quality at center position with major default"""
        quality = JoystickQualityMapper.get_quality(
            0.0, 0.0, ChordQuality.MAJOR, deadzone=0.3
        )
        assert quality == ChordQuality.MAJOR

    def test_get_quality_center_minor(self):
        """Test quality at center position with minor default"""
        quality = JoystickQualityMapper.get_quality(
            0.0, 0.0, ChordQuality.MINOR, deadzone=0.3
        )
        assert quality == ChordQuality.MINOR

    def test_get_quality_within_deadzone(self):
        """Test that small movements stay in deadzone"""
        quality = JoystickQualityMapper.get_quality(
            0.2, 0.1, ChordQuality.MAJOR, deadzone=0.3
        )
        assert quality == ChordQuality.MAJOR

    def test_get_quality_up(self):
        """Test quality when stick is up (default quality)"""
        quality = JoystickQualityMapper.get_quality(
            0.0, -1.0, ChordQuality.MAJOR, deadzone=0.3
        )
        assert quality == ChordQuality.MAJOR

        quality = JoystickQualityMapper.get_quality(
            0.0, -1.0, ChordQuality.MINOR, deadzone=0.3
        )
        assert quality == ChordQuality.MINOR

    def test_get_quality_right_major(self):
        """Test quality when stick is right with major default"""
        quality = JoystickQualityMapper.get_quality(
            1.0, 0.0, ChordQuality.MAJOR, deadzone=0.3
        )
        assert quality == ChordQuality.MAJ7

    def test_get_quality_right_minor(self):
        """Test quality when stick is right with minor default"""
        quality = JoystickQualityMapper.get_quality(
            1.0, 0.0, ChordQuality.MINOR, deadzone=0.3
        )
        assert quality == ChordQuality.MIN7

    def test_get_quality_down(self):
        """Test quality when stick is down (sus4)"""
        quality = JoystickQualityMapper.get_quality(
            0.0, 1.0, ChordQuality.MAJOR, deadzone=0.3
        )
        assert quality == ChordQuality.SUS4

    def test_get_quality_left_major(self):
        """Test quality when stick is left (diminished)"""
        quality = JoystickQualityMapper.get_quality(
            -1.0, 0.0, ChordQuality.MAJOR, deadzone=0.3
        )
        assert quality == ChordQuality.DIM

    def test_get_quality_left_dim_default(self):
        """Test quality when stick is left with diminished default"""
        quality = JoystickQualityMapper.get_quality(
            -1.0, 0.0, ChordQuality.DIM, deadzone=0.3
        )
        assert quality == ChordQuality.DIM7

    def test_get_quality_up_right(self):
        """Test quality when stick is up-right (dominant 7th)"""
        quality = JoystickQualityMapper.get_quality(
            0.7, -0.7, ChordQuality.MAJOR, deadzone=0.3
        )
        assert quality == ChordQuality.DOM7

    def test_get_quality_up_left(self):
        """Test quality when stick is up-left (augmented)"""
        quality = JoystickQualityMapper.get_quality(
            -0.7, -0.7, ChordQuality.MAJOR, deadzone=0.3
        )
        assert quality == ChordQuality.AUG

    def test_get_quality_down_right(self):
        """Test quality when stick is down-right (maj9)"""
        quality = JoystickQualityMapper.get_quality(
            0.7, 0.7, ChordQuality.MAJOR, deadzone=0.3
        )
        assert quality == ChordQuality.MAJ9

    def test_get_quality_down_left_major(self):
        """Test quality when stick is down-left with major (maj6)"""
        quality = JoystickQualityMapper.get_quality(
            -0.7, 0.7, ChordQuality.MAJOR, deadzone=0.3
        )
        assert quality == ChordQuality.MAJ6

    def test_get_quality_down_left_minor(self):
        """Test quality when stick is down-left with minor (sus2)"""
        quality = JoystickQualityMapper.get_quality(
            -0.7, 0.7, ChordQuality.MINOR, deadzone=0.3
        )
        assert quality == ChordQuality.SUS2

    def test_get_quality_all_8_directions(self):
        """Test all 8 directional mappings"""
        # Define 8 directions with expected qualities for major default
        directions = [
            (1.0, 0.0, ChordQuality.MAJ7),      # Right
            (0.7, -0.7, ChordQuality.DOM7),     # Up-Right
            (0.0, -1.0, ChordQuality.MAJOR),    # Up
            (-0.7, -0.7, ChordQuality.AUG),     # Up-Left
            (-1.0, 0.0, ChordQuality.DIM),      # Left
            (-0.7, 0.7, ChordQuality.MAJ6),     # Down-Left
            (0.0, 1.0, ChordQuality.SUS4),      # Down
            (0.7, 0.7, ChordQuality.MAJ9),      # Down-Right
        ]

        for x, y, expected_quality in directions:
            quality = JoystickQualityMapper.get_quality(
                x, y, ChordQuality.MAJOR, deadzone=0.3
            )
            assert quality == expected_quality, \
                f"Failed at ({x}, {y}): expected {expected_quality}, got {quality}"

    def test_deadzone_boundary(self):
        """Test behavior at deadzone boundary"""
        # Just inside deadzone
        quality = JoystickQualityMapper.get_quality(
            0.29, 0.0, ChordQuality.MAJOR, deadzone=0.3
        )
        assert quality == ChordQuality.MAJOR

        # Just outside deadzone
        quality = JoystickQualityMapper.get_quality(
            0.31, 0.0, ChordQuality.MAJOR, deadzone=0.3
        )
        assert quality == ChordQuality.MAJ7

    def test_custom_deadzone(self):
        """Test with custom deadzone value"""
        # Large deadzone
        quality = JoystickQualityMapper.get_quality(
            0.4, 0.0, ChordQuality.MAJOR, deadzone=0.5
        )
        assert quality == ChordQuality.MAJOR  # Still in deadzone

        # Small deadzone
        quality = JoystickQualityMapper.get_quality(
            0.15, 0.0, ChordQuality.MAJOR, deadzone=0.1
        )
        assert quality == ChordQuality.MAJ7  # Outside deadzone
