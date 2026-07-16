# gSlapper IPC Integration Design

**Date:** 2026-07-17  
**Status:** Approved

## Context

Waypaper added gSlapper support before gSlapper exposed its current IPC protocol. The integration launches a new process for each wallpaper change, attempts per-output cleanup with a literal `gslapper.*<output>` substring, and uses `killall` for global stop operations. The substring cannot match a normal command line, while `killall` can terminate gSlapper sessions that Waypaper does not own.

Current gSlapper supports per-instance Unix sockets and commands for changing media, querying playback, pausing, resuming, and stopping. Waypaper can use that protocol without adding a dependency or expanding its settings UI.

## Goals

- Reuse a running gSlapper instance when it can change media through IPC.
- Manage gSlapper independently per output.
- Preserve gSlapper sessions started by users, systemd, or other applications.
- Support the existing Stop all, Pause, Sound, and Fill controls.
- Report launch and IPC failures to the user.
- Keep the implementation inside the existing backend and UI files.

## Non-goals

- Support gSlapper builds without the current IPC protocol.
- Add transition, cache, FPS, layer, or status controls.
- Add a settings dialog, configuration keys, dependency, or controller module.
- Refactor other wallpaper backends.

## Architecture

`waypaper/changer.py` will contain the IPC and lifecycle helpers. Each output receives a deterministic socket below `$XDG_RUNTIME_DIR/waypaper`. A short digest of the output name keeps the socket path bounded and avoids unsafe filename characters.

A module-level lock will serialize gSlapper lifecycle operations. Wallpaper changes are infrequent, so one lock provides the smallest safe design. A `ponytail:` comment will record the ceiling and name per-output locks as the upgrade path if contention becomes measurable.

The IPC helper will use Python's `socket` module, send one newline-terminated command, read one response line, and apply bounded read and write timeouts. It will reject paths containing newlines because the protocol cannot represent them safely.

## Wallpaper Change Flow

1. Acquire the gSlapper lifecycle lock.
2. Resolve the Waypaper-owned socket for the selected output.
3. Stop only overlapping Waypaper-managed instances. Selecting `All` stops managed per-output instances. Selecting one output stops a managed `All` instance. Other per-output instances keep running.
4. If the target socket answers `query`, send `change <path>`.
5. If gSlapper reports that it cannot update an active video, stop that target through IPC and launch it once with the new path.
6. If the socket is stale, remove that socket only. Launch gSlapper with `--ipc-socket`, then wait for `query` to succeed before reporting success.

The launch command will preserve Waypaper's sound and custom GStreamer options. It will map Waypaper scaling modes to current gSlapper tokens:

| Waypaper | gSlapper |
| --- | --- |
| Fill | `fill` |
| Stretch | `stretch` |
| Fit | `panscan=1.0` |
| Center | `original` |
| Tile | `fill` |

gSlapper has no tile mode, so Tile keeps the current fallback behavior.

## Playback and Stop Controls

Waypaper will show its existing Pause button for gSlapper. The handler will query the selected managed instance, then send `pause` or `resume`. The button will retain its static label and existing toggle behavior.

Stop all will enumerate sockets in Waypaper's runtime directory and send `stop` to each live managed instance. It will not inspect the process table or touch sockets outside that directory.

Changing Sound will restart only the selected managed instance because gSlapper does not expose a runtime audio command. Waypaper will keep the existing sound setting and UI control.

No new widgets or configuration fields are required. When gSlapper is selected, the Stop button can use Waypaper's translated Stop all label as its tooltip instead of the mpv-specific tooltip.

## Errors

The backend will raise errors for a missing `XDG_RUNTIME_DIR`, invalid paths, IPC timeouts, protocol errors, launch failures, and startup timeouts. `change_wallpaper()` will log the error and call Waypaper's existing desktop notification helper. A failed wallpaper change will not run the post-command or print a success message.

Waypaper targets the current gSlapper IPC contract. It will not probe for old versions or fall back to process matching and `killall`.

## Verification

`tests/test_gslapper.py` will use `unittest`, mocks, and temporary Unix sockets. Tests will cover socket naming, output overlap, IPC framing and responses, process reuse, the video restart fallback, pause and resume, owned-instance stopping, launch arguments, stale sockets, and startup failure.

Manual testing on Wayland will cover static images, video changes, rapid selections, two outputs, `All`, Pause, Sound, Stop all, restore and slideshow paths, and preservation of an externally started gSlapper session.

## Files

- Modify `waypaper/changer.py` for IPC, lifecycle, launch, and error reporting.
- Modify `waypaper/app.py` to expose and route the existing controls.
- Create `tests/test_gslapper.py` for the backend checks.
- Modify `README.md` to point to the current gSlapper repository.

