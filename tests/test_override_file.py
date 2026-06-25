"""Tests for waypaper.override_file.

Covers the coordination file that waypaper writes so external compositors
(DankMaterialShell, etc.) know which monitors are currently owned by an
external wallpaper backend and can fall back when the owning process dies.
"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import ANY, patch

from waypaper.override_file import (
    SCHEMA_VERSION,
    clear_all_overrides,
    clear_override,
    read_overrides,
    set_override,
)


class OverrideFileTests(unittest.TestCase):
    """End-to-end behavior using a real temp file (no mocking of the file I/O)."""

    def setUp(self):
        self.tmp = Path(self._tempdir())
        self.path = self.tmp / "wallpaper-override.json"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    @staticmethod
    def _tempdir() -> str:
        import tempfile
        return tempfile.mkdtemp(prefix="wp-override-")

    def test_empty_when_file_missing(self):
        """A missing file is treated as empty, not an error."""
        self.assertEqual(read_overrides(self.path), {})

    def test_set_and_read(self):
        set_override("HDMI-A-1", "linux-wallpaperengine", 403735, self.path)
        self.assertEqual(
            read_overrides(self.path),
            {"HDMI-A-1": {"backend": "linux-wallpaperengine", "pid": 403735, "since": ANY}},
        )

    def test_set_overwrites_previous_for_same_monitor(self):
        set_override("HDMI-A-1", "swww", 100, self.path)
        set_override("HDMI-A-1", "linux-wallpaperengine", 200, self.path)
        result = read_overrides(self.path)
        self.assertEqual(result["HDMI-A-1"]["backend"], "linux-wallpaperengine")
        self.assertEqual(result["HDMI-A-1"]["pid"], 200)

    def test_clear_specific_monitor(self):
        set_override("HDMI-A-1", "swww", 100, self.path)
        set_override("DP-1", "mpvpaper", 200, self.path)
        clear_override("HDMI-A-1", self.path)
        result = read_overrides(self.path)
        self.assertNotIn("HDMI-A-1", result)
        self.assertIn("DP-1", result)

    def test_clear_absent_monitor_is_noop(self):
        set_override("HDMI-A-1", "swww", 100, self.path)
        clear_override("DP-1", self.path)  # not present
        self.assertIn("HDMI-A-1", read_overrides(self.path))

    def test_clear_all(self):
        set_override("HDMI-A-1", "swww", 100, self.path)
        set_override("DP-1", "mpvpaper", 200, self.path)
        clear_all_overrides(self.path)
        self.assertEqual(read_overrides(self.path), {})

    def test_clear_all_when_empty_is_noop(self):
        """Calling clear_all on a missing file must not create the file."""
        clear_all_overrides(self.path)
        self.assertFalse(self.path.exists())

    def test_persisted_file_is_valid_json(self):
        """A reader (e.g. DMS) can json.load the file without our helper."""
        set_override("HDMI-A-1", "swww", 100, self.path)
        with self.path.open() as f:
            data = json.load(f)
        self.assertEqual(data["version"], SCHEMA_VERSION)
        self.assertIn("HDMI-A-1", data["overrides"])

    def test_corrupt_file_falls_back_to_empty(self):
        """A truncated file should not crash readers."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("{not valid json", encoding="utf-8")
        self.assertEqual(read_overrides(self.path), {})

    def test_atomic_write_does_not_leave_tmp_files(self):
        """After a successful set, only the real file remains (no .tmp)."""
        set_override("HDMI-A-1", "swww", 100, self.path)
        siblings = list(self.path.parent.iterdir())
        self.assertEqual(sorted(p.name for p in siblings), ["wallpaper-override.json"])

    def test_atomic_write_failure_preserves_prior_state(self):
        """If os.replace fails, the existing file must remain intact."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps({"version": SCHEMA_VERSION, "overrides": {"X": {"backend": "y", "pid": 1, "since": 0}}}),
            encoding="utf-8",
        )
        with patch("waypaper.override_file.os.replace", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                set_override("Z", "swww", 99, self.path)
        # Prior state preserved
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertIn("X", data["overrides"])
        self.assertNotIn("Z", data["overrides"])

    def test_set_override_uses_xdg_state_home_when_set(self):
        """If $LZT_WALLPAPER_OVERRIDE_PATH is set, it overrides the default."""
        import tempfile
        with tempfile.TemporaryDirectory() as custom:
            custom_path = Path(custom) / "custom.json"
            with patch.dict(os.environ, {"LZT_WALLPAPER_OVERRIDE_PATH": str(custom_path)}):
                set_override("HDMI-A-1", "swww", 1)
            self.assertTrue(custom_path.exists())


if __name__ == "__main__":
    unittest.main()
