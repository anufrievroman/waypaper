"""Wallpaper override coordination file.

When waypaper launches a wallpaper backend (swww, linux-wallpaperengine, mpvpaper,
swaybg, gslapper, awww) for a given monitor, it records the backend name, the
owning PID, and a timestamp in this file. External compositors and shells (e.g.
DankMaterialShell) can poll the file to know which monitors are currently owned
by an external backend and skip rendering their own wallpaper on those monitors.
When the recorded PID dies, the entry is stale; readers fall back automatically.

File path: ``$XDG_STATE_HOME/lzt/wallpaper-override.json``
(default: ``~/.local/state/lzt/wallpaper-override.json``)

Schema (versioned):
    {
      "version": 1,
      "overrides": {
        "HDMI-A-1": {
          "backend": "linux-wallpaperengine",
          "pid": 403735,
          "since": 1735680000
        }
      }
    }

Writes are atomic (tempfile + os.replace + fsync) so concurrent readers never
see a half-written file. Missing or malformed files are treated as empty — the
file is a coordination hint, not a source of truth.
"""

import json
import os
import tempfile
import time
from pathlib import Path

SCHEMA_VERSION = 1


def _default_path() -> Path:
    """Resolve the default path each call so env-var overrides take effect at runtime."""
    return Path(
        os.environ.get(
            "LZT_WALLPAPER_OVERRIDE_PATH",
            str(Path.home() / ".local" / "state" / "lzt" / "wallpaper-override.json"),
        )
    )


def _empty() -> dict:
    """Return a fresh, empty override document."""
    return {"version": SCHEMA_VERSION, "overrides": {}}


def _read(path: Path) -> dict:
    """Read the override document, falling back to empty on any error."""
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return _empty()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return _empty()
    if not isinstance(data, dict):
        return _empty()
    overrides = data.get("overrides")
    if not isinstance(overrides, dict):
        overrides = {}
    return {"version": SCHEMA_VERSION, "overrides": overrides}


def _write_atomic(data: dict, path: Path) -> None:
    """Write `data` to `path` atomically.

    Uses mkstemp + fsync + os.replace so a concurrent reader never sees a
    truncated or partially-written file. Cleans up the temp file on failure.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=".wallpaper-override-",
        suffix=".json.tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def set_override(monitor: str, backend: str, pid: int, path: Path | None = None) -> None:
    """Record that `backend` (with `pid`) is now owning `monitor`.

    Overwrites any prior entry for the same monitor. The timestamp is set to
    "now" (epoch seconds) so readers can detect very stale entries.
    """
    if path is None:
        path = _default_path()
    data = _read(path)
    data["overrides"][monitor] = {
        "backend": str(backend),
        "pid": int(pid),
        "since": int(time.time()),
    }
    _write_atomic(data, path)


def clear_override(monitor: str, path: Path | None = None) -> None:
    """Remove the override entry for `monitor`. No-op if absent."""
    if path is None:
        path = _default_path()
    data = _read(path)
    if monitor in data["overrides"]:
        del data["overrides"][monitor]
        _write_atomic(data, path)


def clear_all_overrides(path: Path | None = None) -> None:
    """Remove every override entry. Used at waypaper exit."""
    if path is None:
        path = _default_path()
    data = _read(path)
    if data["overrides"]:
        data["overrides"] = {}
        _write_atomic(data, path)


def read_overrides(path: Path | None = None) -> dict:
    """Return the current overrides as ``{monitor: {backend, pid, since}}``.

    Stale entries (PID no longer alive) are NOT filtered here — the reader
    decides what to do with them, since it has more context (e.g. it might
    grace-period a recent crash).
    """
    if path is None:
        path = _default_path()
    return _read(path).get("overrides", {})
