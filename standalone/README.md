# Masqrayd Soundboard — standalone prototype

This branch is a **prototype**, not an OBS plugin or a tested installer. It requires Python 3 and pygame on Windows.

## Run

```powershell
py -m pip install -r standalone/requirements.txt
py standalone/soundboard.py
```

Import WAV, MP3, or OGG sounds. The library is saved in `%USERPROFILE%\\Music\\Masqrayd Soundboard\\library.json` and imported files under `Sounds`.

## OBS integration (manual validation required)

1. Start the standalone soundboard.
2. In OBS 33.0.0, add an **Application Audio Capture (BETA)** source and select the soundboard's running process (Python during development; packaged EXE later).
3. Record a short test, play a sound, and confirm the recording contains it.
4. Listen on headphones and ensure Desktop Audio is not capturing the same output a second time; mute/disable duplicate captures.
5. Verify OBS's monitoring settings and the existing teleprompter launcher independently.

## Not implemented yet

Standalone EXE/installer, Broadcast Stack launch button, dedicated output-device selection, independent monitoring bus, per-sound volume, loop controls, drag reorder, and automated Windows runtime verification.

This branch deliberately avoids modifying OBS plugin files or the Broadcast Stack/teleprompter.
