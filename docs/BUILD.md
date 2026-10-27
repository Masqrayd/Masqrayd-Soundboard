# Native plugin build notes (prototype)

This is an initial source prototype, **not a compiled or OBS-tested release**.

Requires Windows x64, a matching OBS Studio SDK, Qt 6 Core/Widgets/Multimedia, CMake 3.28+, and a compatible C++17 compiler.

Configure using the OBS plugin template/toolchain appropriate to your installed OBS version. The CMake project expects `libobs`, `obs-frontend-api`, and `Qt6` package discovery. No packaged dependencies or installer are provided yet.

## Important limitations

- Audio currently plays through Qt Multimedia's selected system-default output. It is **not yet routed as an OBS audio source**; recording/streaming and monitor-only separation are **not implemented**.
- Playback is one sound at a time; per-sound volume editing, loop, fade, hotkeys, drag reorder, bulk library management, relink, and banks are planned.
- The prototype uses a unique OBS dock ID and separate library folder. It does not edit Broadcast Stack or teleprompter files.
- Build and runtime validation on the target OBS version are required before installation.

## Manual smoke tests after building

1. Confirm OBS opens with the existing Broadcast Stack and teleprompter launcher unchanged.
2. Confirm the dock appears under OBS Docks and can be shown/hidden.
3. Import WAV and MP3; verify the button is added and playback is audible locally.
4. Verify independent button colors, pressed/playing border, stop, archive, retire, restore and restart persistence.
5. Confirm Soundboard closure does not affect teleprompter launch, running process, or saved settings.
6. Do **not** assume audio is in OBS recordings until OBS-native routing is implemented and verified.
