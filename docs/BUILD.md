# Native plugin build notes (prototype)

This is an initial source prototype, **not a compiled or OBS-tested release**.

Target OBS Studio **33.0.0 (64-bit)** on Windows x64, as confirmed by the user's About screenshot. Requires a matching OBS Studio 33.0.0 SDK, Qt 6 Core/Widgets/Multimedia, CMake 3.28+, and a compatible C++17 compiler.

Configure using the OBS plugin template/toolchain appropriate to your installed OBS version. The CMake project expects `libobs`, `obs-frontend-api`, and `Qt6` package discovery. No packaged dependencies or installer are provided yet.

## Compatibility gate

- Build against OBS Studio 33.0.0 and matching Qt 6 components; do not reuse a prebuilt OBS 32.2.2 plugin binary.
- Verify that the compiled DLL loads in OBS 33.0.0 before packaging an installer.
- Do not overwrite, uninstall, or modify existing Broadcast Stack 1.4.0 components or teleprompter launcher configuration.
- Test OBS 33.0.0 startup, dock visibility, recording audio routing, headphone monitoring, and teleprompter launch independently before labeling a release compatible.

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
