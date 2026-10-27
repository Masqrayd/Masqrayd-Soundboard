# Masqrayd Soundboard

Native OBS Studio soundboard project for the Masqrayd broadcasting workflow.

## Goal

Create a compact, customizable, dockable soundboard that plays audio into OBS and can later integrate with Masqrayd Broadcast Stack. Protect existing working plugins and scene collections during development.

## Planned features

- Resizable, detachable native Qt dock with responsive sound buttons
- Custom sound banks; drag-and-drop file import and reordering
- Rename, remove, recolor and organize sounds
- Play, restart, loop, fade out and Stop All
- Individual and master volume; OBS recording/stream audio routing and optional monitoring
- User-configurable hotkeys
- Persist sound banks, preferences and panel layout across OBS restarts
- Optional OBS startup and future Broadcast Stack integration
- Garnet, graphite and muted pink visual theme

## Development phases

1. Confirm installed OBS version, API compatibility and Windows x64 native build toolchain.
2. Register plugin and dock; implement and verify basic audio playback inside OBS.
3. Build sound-bank editing, drag-and-drop, hotkeys, volumes and settings persistence.
4. Test OBS recording/stream capture, monitoring, restarts and installs.
5. Integrate with existing Broadcast Stack panel attachment mechanism once its interface/source is available.

## Teleprompter non-interference requirements (mandatory)

The existing Broadcast Stack teleprompter launcher is protected functionality. The Soundboard must:

- Never modify, remove, replace, or intercept the teleprompter launch button, configured Python script path, batch/VBS launcher, settings JSON, or startup preferences.
- Use separate processes and lifecycle controls; Soundboard Stop All, shutdown, restart, and errors must not terminate or restart the teleprompter.
- Use separate configuration files/namespaces and avoid changing existing Broadcast Stack state.
- Avoid conflicting global hotkeys, dock IDs, source names, and process names; offer configurable hotkeys with conflict checks.
- Preserve OBS startup behavior and all existing Stack modules.
- Pass regression checks before release: teleprompter launch before/after Soundboard load; simultaneous operation; Soundboard close/restart while teleprompter runs; OBS restart with saved launcher settings; hotkey isolation.

Do not claim these checks passed until tested on the actual Windows OBS installation.

## Status

Project repository initialized. No compiled plugin is available yet.

## Related repositories

- [Broadcast Timer](https://github.com/Masqrayd/Masqrayd-Broadcast-Timer)
- [Scene Vault](https://github.com/Masqrayd/Scene-Vault)
- [Camera Pop-Out Native](https://github.com/Masqrayd/Camera-Pop-Out-Native)

Copyright (c) Masqrayd Media LLC. License selection pending. No third-party code has been copied into this repository.
