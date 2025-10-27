"""Command line entry point for JoyChord."""
from __future__ import annotations

import argparse
import logging
import sys
from typing import Iterable, Optional

from .config import JoyChordConfig, key_index
from .constants import BUTTON_DEFINITIONS, MODE_ORDER
from .controller import ControllerApp, initialize_pygame
from .midi import MidiOutput

try:  # pragma: no cover - optional dependency
    import pygame
except ModuleNotFoundError:  # pragma: no cover - fallback in docs
    pygame = None  # type: ignore

LOGGER = logging.getLogger(__name__)


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="JoyChord - Bluetooth gamepad to MIDI chord controller")
    parser.add_argument("--key", default="C", help="Starting key (default: C)")
    parser.add_argument("--octave", type=int, default=0, help="Starting octave shift (-2 to +2)")
    parser.add_argument("--bpm", type=int, default=120, help="Starting tempo (40-240)")
    parser.add_argument("--mode", default="play", choices=MODE_ORDER, help="Starting playback mode")
    parser.add_argument("--velocity", type=int, default=100, help="Default MIDI velocity (0-127)")
    parser.add_argument("--midi-port", dest="midi_port", help="Explicit MIDI output port name")
    parser.add_argument("--list-midi", action="store_true", help="List available MIDI ports and exit")
    parser.add_argument("--test-buttons", action="store_true", help="Print controller button mapping and exit")
    parser.add_argument("--test-controller", action="store_true", help="Poll controller inputs for diagnostics")
    parser.add_argument("--debug", action="store_true", help="Enable verbose logging")
    return parser.parse_args(argv)


def setup_logging(debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def print_button_mapping() -> None:
    print("JoyChord controller mapping:")
    for index, definition in sorted(BUTTON_DEFINITIONS.items()):
        print(f"  Button {index}: {definition.name} ({definition.short_name}) - {definition.default_quality.upper()}")
    print("  Button 5: Inversion (R1)")
    print("  Button 8: SELECT (mode)")
    print("  Button 9: START (help/panic)")


def list_midi_ports() -> None:
    ports = MidiOutput.available_ports()
    if not ports:
        print("No MIDI ports available. JoyChord will create a virtual port when running.")
        return
    print("Available MIDI ports:")
    for port in ports:
        print(f"  {port}")


def controller_test_loop() -> None:  # pragma: no cover - requires hardware
    if pygame is None:
        raise RuntimeError("pygame is required for controller testing")
    initialize_pygame()
    print("Press controller buttons to see their pygame events. Press CTRL+C to exit.")
    clock = pygame.time.Clock()
    try:
        while True:
            for event in pygame.event.get():
                print(event)
            clock.tick(60)
    except KeyboardInterrupt:
        print("Exiting controller test.")
    finally:
        pygame.quit()


def build_config(args: argparse.Namespace) -> JoyChordConfig:
    config = JoyChordConfig(
        key=args.key.upper(),
        octave=args.octave,
        mode=args.mode,
        bpm=args.bpm,
        velocity=args.velocity,
    )
    config.clamp_octave()
    config.clamp_bpm()
    key_index(config.key, config.keys)  # Validate key
    return config


def run_app(args: argparse.Namespace) -> int:  # pragma: no cover - hardware loop
    if pygame is None:
        raise RuntimeError("pygame is required to run JoyChord")

    config = build_config(args)

    midi = MidiOutput(port_name=args.midi_port)
    midi.open()

    initialize_pygame()
    app = ControllerApp(config, midi)

    clock = pygame.time.Clock()
    try:
        while app.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    app.running = False
                    break
                app.process_event(event)
            app.tick()
            clock.tick(120)
    except KeyboardInterrupt:
        LOGGER.info("Interrupted by user")
    finally:
        app.panic()
        midi.close()
        pygame.quit()
    return 0


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)
    setup_logging(args.debug)

    if args.list_midi:
        list_midi_ports()
        return 0

    if args.test_buttons:
        print_button_mapping()
        return 0

    if args.test_controller:
        controller_test_loop()
        return 0

    try:
        return run_app(args)
    except Exception as exc:  # pragma: no cover - user feedback
        LOGGER.error("JoyChord terminated: %s", exc)
        return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
