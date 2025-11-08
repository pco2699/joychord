"""Testing functions for JoyChord"""

from __future__ import annotations
import pygame
import math

from joychord.chord_config import CHORD_BUTTONS
from joychord.constants import BTN_INVERSION, BTN_SELECT, BTN_START


def test_controller_buttons() -> None:
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
                        if hat_y == 1:
                            direction.append("UP")
                        if hat_y == -1:
                            direction.append("DOWN")
                        if hat_x == -1:
                            direction.append("LEFT")
                        if hat_x == 1:
                            direction.append("RIGHT")
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
