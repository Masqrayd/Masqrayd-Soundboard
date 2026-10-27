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

## Sound button, monitoring, and library requirements (mandatory)

- Each sound button has an independent user-selected color, persistent across restarts, regardless of bank/category.
- On press, immediately show visible feedback; while playing, brighten/highlight the button and display an active indicator. Return to idle on completion. Looping sounds remain active until stopped. Very short sounds must show a minimum perceptible confirmation interval.
- Support distinct audience/OBS output and headphone monitoring controls, independent monitor volume/mute, master volume, and per-sound gain. Avoid doubled audio/feedback; validate routing in actual OBS recordings.
- Offer a dedicated, user-configurable sound-library directory, defaulting to a `Masqrayd Soundboard` folder under the user's Music directory (not the OBS program directory).
- Support organized subfolders/banks (Reactions, Comedy, News, Crime, Intros, Custom), file import, custom button labels independent of filenames, and persistent mappings from button to audio file.
- Persist sound metadata (label, file path or relative library reference, color, gain, loop, hotkey, bank) in a library manifest, with portable relative paths for managed files where possible.
- Provide missing-file warnings and a `Relink Sounds from Folder` recovery workflow, with confirmation for ambiguous filename matches.
- Keep library configuration separate from the teleprompter launcher and all other Broadcast Stack modules.

## Library lifecycle and active-board curation (mandatory)

- No arbitrary small cap on the total number of imported sounds; keep the interface responsive by loading audio on demand and only rendering active sounds in the dock.
- Maintain separate Active, Archived, and Retired states. Active sounds appear on the playable dock; archived and retired sounds remain in the library with their files and all metadata intact.
- Allow reactivation without reimporting or losing custom labels, colors, gains, loops, hotkeys, and file mappings.
- Provide a compact searchable Manage Library view with sorting, multi-select, and bulk Activate / Archive / Retire actions.
- Allow drag-to-reorder active sound buttons and persist the arrangement.
- Permanent deletion must be a separate explicit action with confirmation; archiving or retiring must never delete audio files.
- Store lifecycle state and ordering in the sound-library manifest. Avoid eager loading every archived audio file into memory.

## Status

Project repository initialized. No compiled plugin is available yet.

## Related repositories

- [Broadcast Timer](https://github.com/Masqrayd/Masqrayd-Broadcast-Timer)
- [Scene Vault](https://github.com/Masqrayd/Scene-Vault)
- [Camera Pop-Out Native](https://github.com/Masqrayd/Camera-Pop-Out-Native)

Copyright (c) Masqrayd Media LLC. License selection pending. No third-party code has been copied into this repository.
