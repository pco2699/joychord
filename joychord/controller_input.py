"""Controller input handling with pygame"""

from __future__ import annotations
import sys
from typing import Optional

import pygame


class ControllerInput:
    """Handle pygame joystick input"""

    def __init__(self) -> None:
        pygame.init()
        pygame.joystick.init()

        self.joystick: Optional[pygame.joystick.JoystickType] = None
        self.button_states: dict[int, bool] = {}
        self.button_press_times: dict[int, int] = {}
        self.dpad_last_press: dict[tuple[int, int], int] = {}
        self.dpad_repeat_active: dict[tuple[int, int], bool] = {}
        self.last_start_press: int = 0

        self.initialize_controller()

    def initialize_controller(self) -> None:
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
            return bool(self.joystick.get_button(button))
        return False

    def get_axis(self, axis: int) -> float:
        """Get axis value"""
        if self.joystick and axis < self.joystick.get_numaxes():
            return float(self.joystick.get_axis(axis))
        return 0.0

    def get_hat(self, hat: int = 0) -> tuple[int, int]:
        """Get D-pad hat value"""
        if self.joystick and hat < self.joystick.get_numhats():
            return tuple(self.joystick.get_hat(hat))  # type: ignore
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

    def update_button_states(self) -> None:
        """Update button state tracking"""
        if not self.joystick:
            return

        for i in range(self.joystick.get_numbuttons()):
            self.button_states[i] = self.get_button_state(i)

    def get_pressed_chord_buttons(self) -> list[int]:
        """Get list of currently pressed chord buttons"""
        from joychord.constants import (
            BTN_TONIC, BTN_SUPERTONIC, BTN_MEDIANT, BTN_SUBDOMINANT,
            BTN_DOMINANT, BTN_SUBMEDIANT, BTN_LEADING
        )

        chord_button_indices = [
            BTN_TONIC, BTN_SUPERTONIC, BTN_MEDIANT, BTN_SUBDOMINANT,
            BTN_DOMINANT, BTN_SUBMEDIANT, BTN_LEADING
        ]

        pressed = []
        for btn in chord_button_indices:
            if self.get_button_state(btn):
                pressed.append(btn)
        return pressed
