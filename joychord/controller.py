"""Game controller handling for JoyChord."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

try:  # pragma: no cover - optional dependency
    import pygame
except ModuleNotFoundError:  # pragma: no cover - fallback in docs
    pygame = None  # type: ignore

from .config import JoyChordConfig, key_index
from .constants import (
    BUTTON_DEFINITIONS,
    DRUM_NOTES,
    INVERSION_BUTTON,
    LEFT_STICK_AXES,
    MODE_ORDER,
    SELECT_BUTTON,
    SLASH_BUTTONS,
    START_BUTTON,
)
from .chords import (
    ChordRequest,
    build_chord,
    degree_definition,
    describe_chord,
    direction_from_axis,
    resolve_quality,
)
from .midi import MidiOutput
from .modes import MODE_CLASSES, BaseMode, ModeContext

LOGGER = logging.getLogger(__name__)


@dataclass
class ButtonState:
    pressed: bool = False
    timestamp: float = 0.0


@dataclass
class ControllerState:
    buttons: Dict[int, ButtonState] = field(default_factory=dict)
    inversion: int = 0
    axis_x: float = 0.0
    axis_y: float = 0.0
    current_button: Optional[int] = None
    slash_candidate: Optional[float] = None
    active_slash_button: Optional[int] = None
    last_dpad_time: Dict[str, float] = field(default_factory=dict)
    start_press_times: list[float] = field(default_factory=list)


class ControllerApp:
    def __init__(self, config: JoyChordConfig, midi: MidiOutput) -> None:
        self.config = config
        self.midi = midi
        self.state = ControllerState()
        self.running = True
        self.mode_context = ModeContext(midi=midi, config=config)
        self.mode: BaseMode = self._create_mode(config.mode)
        self._rhythm_options = [4, 8, 16, 32, "16T"]
        self._rhythm_index = 1  # corresponds to eighth notes
        self.mode.enter()
        self._apply_rhythm_setting()

    def _create_mode(self, name: str) -> BaseMode:
        name = name.lower()
        cls = MODE_CLASSES.get(name, MODE_CLASSES["play"])
        LOGGER.info("Switching mode to %s", name)
        return cls(self.mode_context)

    def _cycle_mode(self) -> None:
        idx = MODE_ORDER.index(self.mode.name)
        new_mode_name = MODE_ORDER[(idx + 1) % len(MODE_ORDER)]
        self.mode.exit()
        self.mode = self._create_mode(new_mode_name)
        self.mode.enter()
        self._apply_rhythm_setting()
        LOGGER.info("🎵 Mode: %s", new_mode_name.upper())

    def _handle_button_down(self, button: int, timestamp: float) -> None:
        self.state.buttons.setdefault(button, ButtonState()).pressed = True
        self.state.buttons[button].timestamp = timestamp

        if button == SELECT_BUTTON:
            self._cycle_mode()
            return
        if button == START_BUTTON:
            self._handle_start_button(timestamp)
            return
        if button == INVERSION_BUTTON:
            self._advance_inversion()
            return

        if button in BUTTON_DEFINITIONS:
            self._trigger_chord(button, timestamp)
        elif self.mode.name == "drum" and button in DRUM_NOTES:
            self.mode.play_chord([DRUM_NOTES[button]])

    def _handle_button_up(self, button: int) -> None:
        self.state.buttons.setdefault(button, ButtonState()).pressed = False
        if button in (START_BUTTON, INVERSION_BUTTON, SELECT_BUTTON):
            return
        if button == self.state.active_slash_button:
            self.state.active_slash_button = None
            if self.state.current_button is not None:
                request = ChordRequest(button=self.state.current_button, inversion=self.state.inversion)
                direction = direction_from_axis(
                    self.state.axis_x, self.state.axis_y, self.config.stick_deadzone
                )
                definition = degree_definition(self.state.current_button)
                base_quality = definition.default_quality if definition else "major"
                quality = resolve_quality(base_quality, direction)
                notes = build_chord(self.config, request, direction)
                self.mode.play_chord(notes)
                if definition:
                    LOGGER.info(
                        "♪ Slash released: %s -> %s",
                        describe_chord(definition, quality, self.state.inversion),
                        notes,
                    )
            return
        if button == self.state.current_button:
            self.mode.release()
            self.state.current_button = None
            self.state.slash_candidate = None
            self.state.active_slash_button = None

    def _advance_inversion(self) -> None:
        self.state.inversion = (self.state.inversion + 1) % 3
        if self.state.current_button is not None:
            request = ChordRequest(button=self.state.current_button, inversion=self.state.inversion)
            direction = direction_from_axis(self.state.axis_x, self.state.axis_y, self.config.stick_deadzone)
            definition = degree_definition(self.state.current_button)
            base_quality = definition.default_quality if definition else "major"
            quality = resolve_quality(base_quality, direction)
            notes = build_chord(self.config, request, direction)
            self.mode.play_chord(notes)
            if definition:
                LOGGER.info("♪ R1 pressed: %s", describe_chord(definition, quality, self.state.inversion))

    def _trigger_chord(self, button: int, timestamp: float) -> None:
        primary_button = button
        slash_button = None
        existing = self.state.current_button

        if existing is None:
            new_primary = True
        else:
            new_primary = False
            if button == existing:
                primary_button = existing
            elif button in SLASH_BUTTONS:
                primary_button = existing
                slash_button = button
            else:
                primary_button = button
                new_primary = True

        if (
            slash_button is None
            and self.state.slash_candidate is not None
            and timestamp - self.state.slash_candidate < self.config.slash_window
            and existing is not None
            and button != existing
        ):
            primary_button = existing
            slash_button = button

        request = ChordRequest(
            button=primary_button,
            inversion=self.state.inversion,
            slash_bass_button=slash_button,
        )
        direction = direction_from_axis(self.state.axis_x, self.state.axis_y, self.config.stick_deadzone)
        definition = degree_definition(primary_button)
        base_quality = definition.default_quality if definition else "major"
        quality = resolve_quality(base_quality, direction)
        notes = build_chord(self.config, request, direction)
        self.mode.play_chord(notes)

        if new_primary or existing is None:
            self.state.current_button = primary_button
            self.state.slash_candidate = timestamp
            self.state.active_slash_button = slash_button
        elif slash_button is not None:
            self.state.active_slash_button = slash_button
        else:
            self.state.active_slash_button = None

        if slash_button is not None:
            chord_def = degree_definition(primary_button)
            bass_def = degree_definition(slash_button)
            if chord_def and bass_def:
                LOGGER.info(
                    "🎸 Slash: %s/%s (%s/%s) -> %s",
                    chord_def.short_name,
                    bass_def.short_name,
                    chord_def.name,
                    bass_def.name,
                    notes,
                )
            else:
                LOGGER.info("🎸 Slash chord -> %s", notes)
        elif definition:
            LOGGER.info(
                "♪ Button %s (%s %s): %s -> %s",
                primary_button,
                definition.name,
                definition.short_name,
                quality,
                notes,
            )

    def _handle_start_button(self, timestamp: float) -> None:
        self.state.start_press_times.append(timestamp)
        self.state.start_press_times = [t for t in self.state.start_press_times if timestamp - t < 1.0]
        if len(self.state.start_press_times) >= 2:
            LOGGER.info("START double tap: Panic")
            self.midi.panic()
            self.state.start_press_times.clear()
        else:
            LOGGER.info("START pressed: Showing help overlay")

    def _handle_dpad(self, value: tuple[int, int], timestamp: float) -> None:
        x, y = value
        select_pressed = self.state.buttons.get(SELECT_BUTTON, ButtonState()).pressed
        if select_pressed:
            if x == 1:
                self._change_rhythm(1)
            elif x == -1:
                self._change_rhythm(-1)
            if y == 1:
                self._change_bpm(10)
            elif y == -1:
                self._change_bpm(-10)
            return

        if x == 1:
            self._change_key(1, timestamp)
        elif x == -1:
            self._change_key(-1, timestamp)
        if y == 1:
            self._change_octave(1)
        elif y == -1:
            self._change_octave(-1)

    def _change_bpm(self, delta: int) -> None:
        self.config.bpm += delta
        self.config.clamp_bpm()
        LOGGER.info("⏱️ SELECT + D-Pad %s: BPM -> %s", "Up" if delta > 0 else "Down", self.config.bpm)

    def _change_key(self, delta: int, timestamp: float) -> None:
        last = self.state.last_dpad_time.get("key", 0.0)
        if timestamp - last < self.config.dpad_repeat_rate:
            return
        self.state.last_dpad_time["key"] = timestamp
        idx = key_index(self.config.key, self.config.keys)
        idx = (idx + delta) % len(self.config.keys)
        self.config.key = self.config.keys[idx]
        LOGGER.info("🎹 D-Pad %s: Key -> %s", "Right" if delta > 0 else "Left", self.config.key)

    def _change_octave(self, delta: int) -> None:
        self.config.octave += delta
        self.config.clamp_octave()
        LOGGER.info("📈 D-Pad %s: Octave -> %s", "Up" if delta > 0 else "Down", self.config.octave)

    def _change_rhythm(self, delta: int) -> None:
        self._rhythm_index = (self._rhythm_index + delta) % len(self._rhythm_options)
        self._apply_rhythm_setting()
        LOGGER.info(
            "🥁 SELECT + D-Pad %s: Rhythm -> %s",
            "Right" if delta > 0 else "Left",
            self._rhythm_options[self._rhythm_index],
        )

    def _apply_rhythm_setting(self) -> None:
        value = self._rhythm_options[self._rhythm_index]
        if hasattr(self.mode, "rhythm_rate"):
            setattr(self.mode, "rhythm_rate", value)

    def _update_axes(self) -> None:
        if pygame is None:
            return
        joystick = pygame.joystick.Joystick(0)
        self.state.axis_x = joystick.get_axis(LEFT_STICK_AXES[0])
        self.state.axis_y = joystick.get_axis(LEFT_STICK_AXES[1])

    def process_event(self, event: "pygame.event.Event") -> None:  # type: ignore[name-defined]
        timestamp = time.monotonic()
        if event.type == pygame.JOYBUTTONDOWN:
            self._handle_button_down(event.button, timestamp)
        elif event.type == pygame.JOYBUTTONUP:
            self._handle_button_up(event.button)
        elif event.type == pygame.JOYHATMOTION:
            self._handle_dpad(event.value, timestamp)
        elif event.type == pygame.JOYAXISMOTION and event.axis in LEFT_STICK_AXES:
            self._update_axes()
            if self.state.current_button is not None:
                request = ChordRequest(button=self.state.current_button, inversion=self.state.inversion)
                direction = direction_from_axis(
                    self.state.axis_x, self.state.axis_y, self.config.stick_deadzone
                )
                notes = build_chord(self.config, request, direction)
                self.mode.play_chord(notes)

    def tick(self) -> None:
        self.mode.update()

    def panic(self) -> None:
        self.midi.panic()


def initialize_pygame() -> None:  # pragma: no cover - requires pygame
    if pygame is None:
        raise RuntimeError("pygame is required to run JoyChord")
    if not pygame.get_init():
        pygame.init()
    if not pygame.joystick.get_init():
        pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        raise RuntimeError("No joystick detected. Please connect a controller.")
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    LOGGER.info("Using controller: %s", joystick.get_name())
