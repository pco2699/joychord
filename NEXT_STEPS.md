# Next Steps for 80% Test Coverage

## Remaining Work

### 1. Update Existing Test Imports ⏳
All test files need to use new import paths:

```python
# Old
from joychord import MusicalSystem, ChordQuality

# New
from joychord.musical_system import MusicalSystem
from joychord.enums import ChordQuality
```

Files to update:
- tests/test_musical_system.py
- tests/test_joystick_mapper.py
- tests/test_midi_system.py
- tests/test_constants.py
- tests/test_cli.py

### 2. Write Additional Tests ⏳

#### test_controller_input.py (NEW)
- Test button state tracking
- Test axis reading
- Test hat/D-Pad reading
- Test initialization error handling
- Est. 15 tests

#### test_joychord_app.py (NEW)
- Test chord button press/release handling
- Test slash chord detection
- Test quality updates
- Test inversion cycling
- Test D-Pad key/octave changes
- Test SELECT/START button handlers
- Test cleanup
- Est. 20 tests

#### test_chord_config.py (NEW)
- Validate all 7 buttons configured
- Test button properties
- Est. 5 tests

#### test_help_text.py (NEW)
- Test help text exists
- Test help text formatting
- Est. 2 tests

### 3. Run Updated Tests
```bash
uv run pytest tests/ -v --cov=joychord --cov-report=term-missing
```

Expected outcome: 80%+ coverage

### 4. Type Check with mypy
```bash
uv run mypy joychord/ --show-error-codes
```

Fix remaining type hint issues

### 5. Update GitHub Actions
Ensure CI passes with new structure

## Current Status

✅ Package refactored into 15 modules  
✅ Comprehensive type hints added  
✅ First set of model tests created  
✅ Documentation updated  
⏳ Test imports need updating  
⏳ Additional tests needed (target: +30 tests)  
⏳ Final verification needed  

## Timeline

- Update test imports: 15 minutes
- Write additional tests: 45 minutes
- Run and fix issues: 30 minutes
- **Total**: ~90 minutes to 80% coverage

## Commands Quick Reference

```bash
# Sync dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ --cov=joychord --cov-report=html

# Type check
uv run mypy joychord/

# Run CLI
uv run joychord --help
uv run joychord --test-buttons
```
