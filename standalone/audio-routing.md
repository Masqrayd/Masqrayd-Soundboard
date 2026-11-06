# Audio routing contract — Masqrayd Soundboard

## Default: BOTH

On each sound trigger, the intended default is:
- **Audience output ON**: OBS Studio 33.0.0 captures soundboard playback in stream and recording.
- **Headphone monitoring ON**: host hears the same sound locally.
- Both can be toggled independently in the future audio-routing UI; default remains both.

## Initial implementation strategy

The prototype currently plays through the Windows default output device. For an initial test, OBS Application Audio Capture (BETA) can capture the soundboard's process audio while the host listens to that same Windows output through headphones. This can satisfy BOTH without generating two separate audio streams, **provided** the Windows default output is the host's headphones and OBS captures the process audio correctly. Do not add OBS Monitor and Output for that same signal unless explicitly needed: that can create double playback or echo. Do not also capture the same signal through Desktop Audio.

## Acceptance tests (not yet performed)

1. Launch the soundboard with headphones selected as Windows output.
2. Add OBS 33.0.0 Application Audio Capture for the soundboard process.
3. Play a sound: verify it is audible in headphones.
4. Verify the OBS meter moves and a local OBS recording contains the sound exactly once.
5. Check a live/recorded test for doubled playback, clipping, and latency.
6. Confirm host microphone remains independently controllable.
7. Test the Broadcast Stack launch button and the teleprompter launcher together, including OBS restart.
8. Test after packaging as a Windows x64 EXE (capture the EXE process rather than Python).

## Limitations

The current prototype does **not** provide dedicated device routing, independently switchable headphone/audience buses, OBS-native monitoring, or an installable EXE. These are requirements for a later build, not implemented features. OBS Application Audio Capture behavior and Windows output configuration must be verified on the user's machine.
