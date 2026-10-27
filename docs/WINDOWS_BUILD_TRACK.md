# Windows build track — OBS Studio 33.0.0 (x64)

This branch adds an initial experimental GitHub Actions build, not a production installer. It must NOT modify existing Broadcast Stack or teleprompter files.

Build prerequisites are derived from OBS plugin template / Scene Vault patterns. A matching OBS 33 toolchain and Qt 6 Multimedia libraries must be available.

**Do not install artifacts in OBS before reviewing compilation, dependency packaging, and runtime testing.**

Acceptance tests: visible dock, working imports, sound playback, archive/restore, per-button color, OBS recording/stream audio, headphone monitoring, no duplicate audio, and teleprompter launch preservation. Audio capture and independent monitoring are NOT implemented in the initial Qt Multimedia prototype.

The experimental workflow runs on pushes to this branch and PRs. If CMake dependency bootstrapping fails, diagnose the action logs before distribution.

## First CI finding (2026-10-27)

An early Windows run reached CMake configuration but failed because the runner did not have `libobsConfig.cmake` / an OBS SDK on `CMAKE_PREFIX_PATH`. The current build scaffolding is experimental and does not yet provision OBS 33 dependencies. Follow-up must pin and install OBS 33 developer dependencies and Qt Multimedia before compilation is possible; do not distribute artifacts from these attempts.
