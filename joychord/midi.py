"""MIDI output helpers for JoyChord."""
from __future__ import annotations

import contextlib
import logging
from typing import Iterable, List, Optional

try:  # pragma: no cover - optional dependency
    import mido
except ModuleNotFoundError:  # pragma: no cover - fallback in docs
    mido = None  # type: ignore

LOGGER = logging.getLogger(__name__)


class MidiOutput:
    """Thin wrapper around ``mido`` output ports with graceful fallbacks."""

    def __init__(self, port_name: Optional[str] = None) -> None:
        self._port = None
        self._port_name = port_name
        self._last_notes: List[int] = []

    @staticmethod
    def available_ports() -> List[str]:  # pragma: no cover - passthrough
        if mido is None:
            return []
        return list(mido.get_output_names())

    def open(self) -> None:
        if mido is None:
            LOGGER.warning("mido is not available; MIDI output disabled")
            return
        if self._port is not None:
            return

        port_name = self._port_name
        create_virtual = False
        available = self.available_ports()
        if port_name is None:
            if available:
                port_name = available[0]
            else:
                port_name = "JoyChord Virtual"
                create_virtual = True
        else:
            create_virtual = port_name not in available
        LOGGER.info("Opening MIDI output '%s'%s", port_name, " (virtual)" if create_virtual else "")
        self._port = mido.open_output(port_name, virtual=create_virtual)

    def close(self) -> None:
        if self._port is None:
            return
        LOGGER.info("Closing MIDI output")
        self.all_notes_off()
        self._port.close()
        self._port = None

    def send_note_on(self, note: int, velocity: int, channel: int = 0) -> None:
        if self._port is None:
            LOGGER.debug("Skipping note on for note %s; no port", note)
            return
        msg = mido.Message("note_on", note=note, velocity=velocity, channel=channel)
        self._port.send(msg)

    def send_note_off(self, note: int, channel: int = 0) -> None:
        if self._port is None:
            LOGGER.debug("Skipping note off for note %s; no port", note)
            return
        msg = mido.Message("note_off", note=note, velocity=0, channel=channel)
        self._port.send(msg)

    def play_notes(self, notes: Iterable[int], velocity: int, channel: int = 0) -> None:
        self.stop_last_notes(channel)
        self._last_notes = list(notes)
        for note in self._last_notes:
            self.send_note_on(note, velocity, channel)

    def stop_last_notes(self, channel: int = 0) -> None:
        if not self._last_notes:
            return
        for note in self._last_notes:
            self.send_note_off(note, channel)
        self._last_notes.clear()

    def all_notes_off(self, channel: int = 0) -> None:
        if mido is None or self._port is None:
            return
        for note in range(128):
            self.send_note_off(note, channel)
        self._last_notes.clear()

    def panic(self) -> None:
        self.all_notes_off()

    def __enter__(self) -> "MidiOutput":  # pragma: no cover - passthrough
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - passthrough
        with contextlib.suppress(Exception):
            self.close()
