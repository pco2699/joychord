"""Playback modes for JoyChord."""
from __future__ import annotations

import itertools
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence

from .config import JoyChordConfig
from .midi import MidiOutput


@dataclass
class ModeContext:
    midi: MidiOutput
    config: JoyChordConfig


class BaseMode:
    name: str = "base"

    def __init__(self, context: ModeContext) -> None:
        self.context = context

    def enter(self) -> None:
        self.context.midi.stop_last_notes()

    def exit(self) -> None:
        self.context.midi.stop_last_notes()

    def play_chord(self, notes: Iterable[int]) -> None:
        raise NotImplementedError

    def release(self) -> None:
        self.context.midi.stop_last_notes()

    def update(self) -> None:
        """Hook for time-based behaviour."""

    def tick_duration(self) -> float:
        bpm = self.context.config.bpm
        beats_per_second = bpm / 60.0
        rate = getattr(self, "rhythm_rate", 4)
        if isinstance(rate, str) and rate.lower().endswith("t"):
            base = int(rate[:-1])
            beat_fraction = (4 / base) * (2 / 3)
        else:
            beat_fraction = 4 / float(rate)
        return beat_fraction / beats_per_second if beats_per_second else 0.0


class PlayMode(BaseMode):
    name = "play"

    def play_chord(self, notes: Iterable[int]) -> None:
        self.context.midi.play_notes(notes, self.context.config.velocity, self.context.config.midi_channel)


class RepeatMode(BaseMode):
    name = "repeat"

    def __init__(self, context: ModeContext) -> None:
        super().__init__(context)
        self._last_notes: List[int] = []
        self._next_trigger: float = 0.0
        self.rhythm_rate = 8

    def enter(self) -> None:
        super().enter()
        self._last_notes = []
        self._next_trigger = 0.0

    def play_chord(self, notes: Iterable[int]) -> None:
        self._last_notes = list(notes)
        self._next_trigger = time.monotonic()

    def update(self) -> None:
        if not self._last_notes:
            return
        now = time.monotonic()
        if now >= self._next_trigger:
            self.context.midi.play_notes(self._last_notes, self.context.config.velocity, self.context.config.midi_channel)
            self._next_trigger = now + self.tick_duration()

    def release(self) -> None:
        self._last_notes = []
        super().release()


class ArpMode(BaseMode):
    name = "arp"

    def __init__(self, context: ModeContext) -> None:
        super().__init__(context)
        self._pattern: List[int] = []
        self._iterator: Optional[Iterable[int]] = None
        self._next_trigger: float = 0.0
        self.rhythm_rate = 8

    def play_chord(self, notes: Iterable[int]) -> None:
        self._pattern = list(notes)
        if not self._pattern:
            return
        arp_notes = self._pattern + [self._pattern[0] + 12]
        self._iterator = itertools.cycle(arp_notes)
        self._next_trigger = time.monotonic()

    def update(self) -> None:
        if self._iterator is None:
            return
        now = time.monotonic()
        if now >= self._next_trigger:
            note = next(self._iterator)
            self.context.midi.stop_last_notes(self.context.config.midi_channel)
            self.context.midi.play_notes([note], self.context.config.velocity, self.context.config.midi_channel)
            self._next_trigger = now + self.tick_duration()

    def release(self) -> None:
        self._iterator = None
        self._pattern = []
        super().release()


class DrumMode(BaseMode):
    name = "drum"

    def play_chord(self, notes: Iterable[int]) -> None:
        for note in notes:
            self.context.midi.send_note_on(note, self.context.config.velocity, self.context.config.midi_channel)
            self.context.midi.send_note_off(note, self.context.config.midi_channel)


class AutoDrumMode(BaseMode):
    name = "autodrum"

    def __init__(self, context: ModeContext) -> None:
        super().__init__(context)
        self._pattern: Sequence[List[int]] = (
            [36, 42],
            [36, 38, 46],
            [36, 42],
            [36, 49],
        )
        self._index = 0
        self._next_trigger = 0.0

    def enter(self) -> None:
        super().enter()
        self._index = 0
        self._next_trigger = time.monotonic()

    def play_chord(self, notes: Iterable[int]) -> None:
        # Buttons select pattern index.
        if isinstance(notes, list) and notes:
            self._index = notes[0] % len(self._pattern)
        self._next_trigger = time.monotonic()

    def update(self) -> None:
        now = time.monotonic()
        if now >= self._next_trigger:
            pattern_notes = self._pattern[self._index]
            self.context.midi.play_notes(pattern_notes, self.context.config.velocity, self.context.config.midi_channel)
            self._next_trigger = now + self.tick_duration()


MODE_CLASSES = {
    PlayMode.name: PlayMode,
    ArpMode.name: ArpMode,
    RepeatMode.name: RepeatMode,
    DrumMode.name: DrumMode,
    AutoDrumMode.name: AutoDrumMode,
}
