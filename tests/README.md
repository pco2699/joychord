# JoyChord Test Suite

## Overview

Comprehensive unit test suite for JoyChord with 86 tests achieving 50% code coverage.

## Running Tests

### Run all tests
```bash
uv run pytest tests/
```

### Run with coverage
```bash
uv run pytest tests/ --cov=. --cov-report=html
```

### Run specific test file
```bash
uv run pytest tests/test_musical_system.py -v
```

### Run specific test
```bash
uv run pytest tests/test_musical_system.py::TestMusicalSystem::test_build_chord_major -v
```

## Type Checking

```bash
uv run mypy joychord.py
```

## Test Structure

### `test_musical_system.py` (26 tests)
Tests for the Nashville Number System and chord generation:
- Scale degree calculation
- Chord building (all qualities)
- Chord inversions
- Key transposition
- Octave shifting
- Bass note generation

### `test_joystick_mapper.py` (22 tests)
Tests for the LEFT stick quality mapper:
- Angle calculation (8 directions)
- Quality mapping by angle
- Deadzone behavior
- Context-aware quality selection

### `test_midi_system.py` (14 tests)
Tests for MIDI input/output:
- Port initialization
- Note on/off messages
- Active note tracking
- Note range validation
- All notes off (panic)
- Port listing

### `test_constants.py` (16 tests)
Tests for configuration and constants:
- Key list validation
- BPM and octave ranges
- Chord button configuration
- Degree names
- Play modes

### `test_cli.py` (14 tests)
Tests for Click CLI:
- Help and version display
- Input validation
- Case-insensitive options
- Range checking
- Error messages

### `conftest.py`
Pytest fixtures for mocking hardware dependencies

## Coverage Report

Current coverage: **50%** (500 statements, 249 missing)

**Well-covered areas:**
- Musical system logic (90%+)
- Joystick quality mapping (100%)
- MIDI message handling (85%)
- Constants and configuration (100%)
- CLI argument parsing (95%)

**Areas with lower coverage:**
- Controller input handling (requires hardware)
- Main application loop (requires hardware)
- Display and feedback systems
- Test mode functions

## Continuous Integration

GitHub Actions runs tests automatically on:
- Push to main, develop, or claude/* branches
- Pull requests to main or develop

Tested on:
- Ubuntu, Windows, macOS
- Python 3.8, 3.9, 3.10, 3.11, 3.12

## Writing New Tests

Example test:
```python
from joychord import MusicalSystem, ChordQuality

def test_my_feature():
    system = MusicalSystem(key_index=0, octave=0)
    chord = system.build_chord(1, ChordQuality.MAJOR, 0)
    assert chord == [60, 64, 67]
```

Use fixtures from `conftest.py`:
```python
def test_with_mock(mock_midi_system):
    mock_midi_system.send_note_on(60)
    assert 60 in mock_midi_system.active_notes
```

## Coverage Goals

- Core musical logic: 90%+ ✅
- MIDI system: 85%+ ✅
- Input handling: 50%+ ⚠️ (hardware-dependent)
- Overall: 50%+ ✅

## Known Limitations

- Controller input tests require actual hardware
- MIDI tests are mocked (no real MIDI I/O)
- pygame initialization is mocked in most tests
- Display/UI tests are minimal

## CI Badge

Add to README:
```markdown
![CI](https://github.com/pco2699/joychord/workflows/CI/badge.svg)
```
