"""Joystick quality mapper for LEFT stick input"""

from __future__ import annotations
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from joychord.enums import ChordQuality


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
    def get_quality(x: float, y: float, default_quality: ChordQuality, deadzone: float = 0.3) -> ChordQuality:
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
        from joychord.enums import ChordQuality

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
