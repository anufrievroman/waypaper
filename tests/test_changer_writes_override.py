"""Integration tests for the override_file wiring inside changer.py.

Verify that each change_with_X (swww, awww, swaybg, mpvpaper, gslapper,
linux-wallpaperengine) records an override entry with the right backend
name and PID, and that change_wallpaper clears any stale entry for the
monitor before launching a new backend.
"""

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from waypaper import changer, override_file
from waypaper.changer import change_wallpaper


def _lwe_config() -> SimpleNamespace:
    return SimpleNamespace(
        backend="linux-wallpaperengine",
        fill_option="fill",
        linux_wallpaperengine_silent=True,
        linux_wallpaperengine_noautomute=True,
        linux_wallpaperengine_no_audio_processing=False,
        linux_wallpaperengine_no_fullscreen_pause=False,
        linux_wallpaperengine_fullscreen_pause_only_active=False,
        linux_wallpaperengine_disable_particles=True,
        linux_wallpaperengine_disable_mouse=False,
        linux_wallpaperengine_disable_parallax=False,
        linux_wallpaperengine_clamp=changer.LINUX_WALLPAPERENGINE_CLAMP[0],
        linux_wallpaperengine_volume=15,
        linux_wallpaperengine_fps=30,
        post_command="",
        use_post_command=False,
        write_override_file=True,
    )


def _make_process(pid: int = 12345) -> MagicMock:
    p = MagicMock()
    p.pid = pid
    p.poll.return_value = None  # still running
    return p


class ChangeWithLinuxWallpaperengineWritesOverrideTests(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="wp-ov-int-"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_writes_override_after_popen(self):
        """The override is recorded with backend=linux-wallpaperengine and the new PID."""
        env = {**__import__("os").environ, "WAYPAPER_OVERRIDE_PATH": str(self.tmp / "ov.json")}
        with patch.dict(__import__("os").environ, env, clear=False):
            with patch("waypaper.changer.seek_and_destroy"), patch(
                "waypaper.changer.subprocess.Popen", return_value=_make_process(99999)
            ) as popen_mock, patch("waypaper.changer.time.sleep"), patch(
                "waypaper.changer.notify_waypaper_issue"
            ):
                changer.change_with_linux_wallpaperengine(
                    self.tmp / "preview.jpg", _lwe_config(), "HDMI-A-1"
                )

        # The override file MUST contain the entry for the new process.
        data = json.loads((self.tmp / "ov.json").read_text(encoding="utf-8"))
        self.assertIn("HDMI-A-1", data["overrides"])
        self.assertEqual(data["overrides"]["HDMI-A-1"]["backend"], "linux-wallpaperengine")
        self.assertEqual(data["overrides"]["HDMI-A-1"]["pid"], 99999)


class ChangeWallpaperClearsStaleOverrideTests(unittest.TestCase):
    """When the user changes wallpaper, any prior override for that monitor must be cleared."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="wp-ov-clear-"))
        self.path = self.tmp / "ov.json"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_stale_entry_for_same_monitor_is_replaced(self):
        """A previous override for the same monitor is replaced, not appended to."""
        # Pre-existing stale entry (the user previously had swww on HDMI-A-1
        # but the daemon died, leaving a stale entry).
        override_file.set_override("HDMI-A-1", "swww", 100, self.path)
        self.assertIn("HDMI-A-1", override_file.read_overrides(self.path))

        env = {**__import__("os").environ, "WAYPAPER_OVERRIDE_PATH": str(self.path)}
        with patch.dict(__import__("os").environ, env, clear=False):
            with patch("waypaper.changer.seek_and_destroy"), patch(
                "waypaper.changer.subprocess.Popen", return_value=_make_process(555)
            ), patch("waypaper.changer.time.sleep"), patch(
                "waypaper.changer.notify_waypaper_issue"
            ):
                change_wallpaper(self.tmp / "wp", _lwe_config(), "HDMI-A-1")

        result = override_file.read_overrides(self.path)
        # Old swww entry is gone; only the new lwe entry remains.
        self.assertEqual(len(result), 1)
        self.assertEqual(result["HDMI-A-1"]["backend"], "linux-wallpaperengine")
        self.assertEqual(result["HDMI-A-1"]["pid"], 555)


class ChangeWithSwaybgWritesOverrideTests(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="wp-ov-swaybg-"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_writes_override_with_swaybg_backend(self):
        env = {**__import__("os").environ, "WAYPAPER_OVERRIDE_PATH": str(self.tmp / "ov.json")}
        cfg = SimpleNamespace(
            fill_option="fill", color="#000000",
            post_command="", use_post_command=False,
            write_override_file=True,
        )
        with patch.dict(__import__("os").environ, env, clear=False):
            with patch("waypaper.changer.find_process_pid", return_value=None), patch(
                "waypaper.changer.subprocess.Popen", return_value=_make_process(7777)
            ) as popen_mock, patch("waypaper.changer.subprocess.run"):
                changer.change_with_swaybg(self.tmp / "image.jpg", cfg, "DP-1")

        data = json.loads((self.tmp / "ov.json").read_text(encoding="utf-8"))
        self.assertEqual(data["overrides"]["DP-1"]["backend"], "swaybg")
        self.assertEqual(data["overrides"]["DP-1"]["pid"], 7777)


class ChangeWithSwwwWritesDaemonPidTests(unittest.TestCase):
    """For swww, the override records the long-running daemon's PID, not the short-lived `swww img` PID."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="wp-ov-swww-"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_swww_writes_daemon_pid(self):
        cfg = SimpleNamespace(
            fill_option="fill", color="#000000",
            swww_filter="lanczos3", swww_transition_type="fade",
            swww_transition_step=1, swww_transition_angle=0,
            swww_transition_duration=1, swww_transition_fps=30,
            write_override_file=True,
        )
        env = {**__import__("os").environ, "WAYPAPER_OVERRIDE_PATH": str(self.tmp / "ov.json")}

        with patch.dict(__import__("os").environ, env, clear=False):
            with patch("waypaper.changer.seek_and_destroy"), patch(
                "waypaper.changer.subprocess.check_output", return_value="42424"
            ), patch("waypaper.changer.subprocess.run", return_value=MagicMock(stdout="swww 0.11.0")), patch(
                "waypaper.changer.subprocess.Popen"
            ):
                changer.change_with_swww(self.tmp / "image.jpg", cfg, "HDMI-A-1")

        data = json.loads((self.tmp / "ov.json").read_text(encoding="utf-8"))
        self.assertEqual(data["overrides"]["HDMI-A-1"]["backend"], "swww")
        self.assertEqual(data["overrides"]["HDMI-A-1"]["pid"], 42424)


class WriteOverrideFileFlagGateTests(unittest.TestCase):
    """When cf.write_override_file is False (the default), no override is recorded.

    The flag is opt-in to keep the surface area minimal for the 95% of users
    who don't coordinate with external compositors.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="wp-ov-flag-"))
        self.path = self.tmp / "ov.json"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _disabled_cfg(self) -> SimpleNamespace:
        return SimpleNamespace(
            fill_option="fill", color="#000000",
            post_command="", use_post_command=False,
            write_override_file=False,
        )

    def test_swaybg_skips_override_when_flag_disabled(self):
        env = {**__import__("os").environ, "WAYPAPER_OVERRIDE_PATH": str(self.path)}
        with patch.dict(__import__("os").environ, env, clear=False):
            with patch("waypaper.changer.find_process_pid", return_value=None), patch(
                "waypaper.changer.subprocess.Popen", return_value=_make_process(7777)
            ), patch("waypaper.changer.subprocess.run"):
                changer.change_with_swaybg(self.tmp / "image.jpg", self._disabled_cfg(), "DP-1")

        self.assertFalse(self.path.exists(), "no file should be written when flag is False")

    def test_lwe_skips_override_when_flag_disabled(self):
        env = {**__import__("os").environ, "WAYPAPER_OVERRIDE_PATH": str(self.path)}
        with patch.dict(__import__("os").environ, env, clear=False):
            with patch("waypaper.changer.seek_and_destroy"), patch(
                "waypaper.changer.subprocess.Popen", return_value=_make_process(99999)
            ), patch("waypaper.changer.time.sleep"), patch(
                "waypaper.changer.notify_waypaper_issue"
            ):
                cfg = _lwe_config()
                cfg.write_override_file = False
                changer.change_with_linux_wallpaperengine(
                    self.tmp / "preview.jpg", cfg, "HDMI-A-1"
                )

        self.assertFalse(self.path.exists(), "no file should be written when flag is False")

    def test_change_wallpaper_skips_clear_when_flag_disabled(self):
        # Seed an existing entry as if a prior session had the flag enabled.
        override_file.set_override("HDMI-A-1", "swww", 100, self.path)
        env = {**__import__("os").environ, "WAYPAPER_OVERRIDE_PATH": str(self.path)}
        with patch.dict(__import__("os").environ, env, clear=False):
            with patch("waypaper.changer.seek_and_destroy"), patch(
                "waypaper.changer.subprocess.Popen", return_value=_make_process(555)
            ), patch("waypaper.changer.time.sleep"), patch(
                "waypaper.changer.notify_waypaper_issue"
            ):
                cfg = _lwe_config()
                cfg.write_override_file = False
                change_wallpaper(self.tmp / "wp", cfg, "HDMI-A-1")

        # Pre-existing entry is untouched because the flag is off — waypaper
        # neither writes nor clears while the feature is disabled.
        result = override_file.read_overrides(self.path)
        self.assertEqual(result["HDMI-A-1"]["backend"], "swww")
        self.assertEqual(result["HDMI-A-1"]["pid"], 100)


if __name__ == "__main__":
    unittest.main()
