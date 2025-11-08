# JoyChord Quick Start Guide

## 🚀 Super Fast Setup with uv

### 1. Install uv (One-Time Setup)

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**macOS (Homebrew):**
```bash
brew install uv
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install JoyChord

```bash
# Clone the repository
git clone https://github.com/pco2699/joychord.git
cd joychord

# Install dependencies (creates .venv automatically)
uv sync

# That's it! 🎉
```

### 3. Connect Your Controller

**Bluetooth Controllers:**
- PlayStation DualShock 4 / DualSense
- Xbox One / Series X|S
- Nintendo Switch Pro Controller
- Generic Bluetooth gamepad

**Pair your controller:**
- **Windows:** Settings → Bluetooth & devices → Add device
- **macOS:** System Settings → Bluetooth
- **Linux:** `bluetoothctl` or your desktop's Bluetooth manager

### 4. Set Up MIDI

**Windows:**
1. Download [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)
2. Install and launch loopMIDI
3. Create a virtual MIDI port (e.g., "loopMIDI Port")

**Linux:**
```bash
# ALSA is usually already installed
# No additional setup needed
```

**macOS:**
```bash
# Core MIDI is built-in
# No additional setup needed
```

### 5. Run JoyChord

```bash
# Test that your controller is detected
uv run joychord --test-buttons

# Run JoyChord
uv run joychord

# Or start in a specific key
uv run joychord --key D
```

### 6. Connect to Your DAW

**Ableton Live:**
1. Preferences → Link/Tempo/MIDI
2. Enable "Track" and "Remote" for JoyChord's MIDI port
3. Create a MIDI track
4. Set input to JoyChord's port
5. Load an instrument (e.g., piano, synth)
6. Press buttons on your controller!

**Logic Pro:**
1. Preferences → MIDI
2. Enable JoyChord's virtual port
3. Create a Software Instrument track
4. Set MIDI input to JoyChord
5. Play!

**FL Studio:**
1. Options → MIDI Settings
2. Enable JoyChord's port
3. Create a channel with an instrument
4. Route MIDI to that channel

**Reaper:**
1. Options → Preferences → MIDI Devices
2. Enable JoyChord's port as input
3. Create a track with VSTi
4. Set track to record MIDI from JoyChord

## 🎮 Basic Controls

### Chord Buttons

```
    L2[ii]   L1[vi]          R1[Inv]  R2[IV]
   (minor)  (minor)                   (major)

            △[V]
          (major)
        □[iii]  ○[vii°]
       (minor)  (dim)
            ×[I]
          (major)
```

### Quick Reference

1. **Press any chord button** → Plays the chord
2. **Move LEFT stick while holding** → Changes chord quality
3. **Press R1 while holding chord** → Cycles through inversions
4. **D-Pad LEFT/RIGHT** → Change key
5. **D-Pad UP/DOWN** → Change octave
6. **Hold × then press □** → Plays slash chord (I/iii)
7. **Press START** → Shows full help
8. **Double-tap START** → All notes off (panic)

## 🎵 Try This First

1. Press **×** (bottom face button) → Plays **C major** chord
2. While holding ×, move **LEFT stick DOWN** → Changes to **C sus4**
3. While holding ×, move **LEFT stick RIGHT** → Changes to **C maj7**
4. Release × and press **D-Pad RIGHT** → Changes key to **C#**
5. Press **×** again → Now plays **C# major**
6. Press **△** (top face button) → Plays **G# major** (dominant V)
7. Hold **×** and press **R1** → Cycles through inversions

## 💡 Tips

- **Deadzone:** LEFT stick has a deadzone (center area) - major movement needed to change quality
- **Slash chords:** Great for bass lines - try holding V and pressing I
- **Inversions:** Smooth voice leading - try I (root) → IV (1st inv) → V (2nd inv) → I
- **Help overlay:** Press START anytime to see the full control reference

## 🧪 Troubleshooting

### Controller not detected
```bash
# Check if pygame sees your controller
uv run joychord --test-buttons

# If nothing appears, check Bluetooth pairing
```

### No MIDI output
```bash
# List available MIDI ports
uv run joychord --list-midi

# Windows: Ensure loopMIDI is running
# Linux: Check ALSA with `aconnect -l`
# macOS: Should work out of the box
```

### Wrong button mapping
```bash
# Test your specific controller
uv run joychord --test-buttons

# Press each button to see its index
# Different controllers may have different layouts
```

### Notes stuck on
```bash
# Double-tap START button for panic (all notes off)
# Or restart JoyChord
```

## 📚 Next Steps

- Read [README.md](README.md) for full documentation
- Check [IMPLEMENTATION.md](IMPLEMENTATION.md) for technical details
- Experiment with different keys and octaves
- Try slash chords for advanced harmony
- Use inversions for smooth voice leading

## 🎹 Musical Theory Quick Reference

**Nashville Number System:**
- **I** (Tonic) - Home chord, feels resolved
- **ii** (Supertonic) - Leads to V or I
- **iii** (Mediant) - Substitute for I
- **IV** (Subdominant) - Pre-dominant, leads to V
- **V** (Dominant) - Creates tension, wants to resolve to I
- **vi** (Submediant) - Relative minor, substitute for I
- **vii°** (Leading Tone) - Diminished, leads to I

**Common Progressions:**
- **I - V - vi - IV** (Pop progression)
- **I - IV - V - I** (Classic rock)
- **ii - V - I** (Jazz turnaround)
- **I - vi - IV - V** (50s progression)

## ⌨️ Command Reference

```bash
uv run joychord              # Run with defaults (C major)
uv run joychord --key D      # Start in D major
uv run joychord --octave 1   # Start one octave up
uv run joychord --bpm 140    # Set BPM to 140
uv run joychord --debug      # Enable debug output
uv run joychord --test-buttons  # Test controller mapping
uv run joychord --list-midi  # List MIDI ports
uv run joychord --help       # Show all options
```

---

**Ready to make music! 🎵**

For questions or issues: https://github.com/pco2699/joychord/issues
