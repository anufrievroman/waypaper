"""Regression tests for the swww/awww background-cleanup path.

When waypaper switches to linux-wallpaperengine (or any dynamic renderer), the
swww-daemon and awww-daemon background layers must be cleared for the affected
monitor. Otherwise the previous static wallpaper stays visible in the Wayland
background layer behind the new dynamic scene (two stacked wallpapers on the
same monitor — the bug reported on 2026-06-25 with HDMI-A-1 showing the
ultrakill preview.gif behind the new spiderman scene).
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from waypaper.changer import change_with_linux_wallpaperengine, seek_and_destroy


class SwwwBackgroundCleanupTests(unittest.TestCase):
    """Verify change_with_linux_wallpaperengine clears swww/awww backgrounds."""

    def make_config(self) -> MagicMock:
        cf = MagicMock()
        cf.fill_option = "fill"
        cf.linux_wallpaperengine_silent = True
        cf.linux_wallpaperengine_noautomute = True
        cf.linux_wallpaperengine_no_audio_processing = False
        cf.linux_wallpaperengine_no_fullscreen_pause = False
        cf.linux_wallpaperengine_fullscreen_pause_only_active = False
        cf.linux_wallpaperengine_disable_particles = True
        cf.linux_wallpaperengine_disable_mouse = False
        cf.linux_wallpaperengine_disable_parallax = False
        cf.linux_wallpaperengine_clamp = "none"
        cf.linux_wallpaperengine_volume = 15
        cf.linux_wallpaperengine_fps = 30
        return cf

    def make_preview_path(self, tmp_dir: str) -> Path:
        wallpaper_dir = Path(tmp_dir) / "wallpaper"
        wallpaper_dir.mkdir()
        preview_path = wallpaper_dir / "preview.jpg"
        preview_path.write_text("preview", encoding="utf-8")
        return preview_path

    def test_clears_swww_and_awww_before_killing_old_linux_wallpaperengine(self):
        """The fix must call seek_and_destroy for swww-daemon, awww-daemon, then linux-wallpaperengine, all with the same monitor."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            process = MagicMock()
            process.poll.return_value = None

            with patch("waypaper.changer.seek_and_destroy") as seek_mock, patch(
                "waypaper.changer.subprocess.Popen", return_value=process
            ), patch("waypaper.changer.time.sleep"), patch(
                "waypaper.changer.notify_waypaper_issue"
            ):
                change_with_linux_wallpaperengine(
                    self.make_preview_path(tmp_dir),
                    self.make_config(),
                    "HDMI-A-1",
                )

        seek_calls = [c.args for c in seek_mock.call_args_list]
        seek_args = [(args[0], args[1]) for args in seek_calls]

        # Must clear both static backends and the dynamic backend on this monitor.
        self.assertIn(("swww-daemon", "HDMI-A-1"), seek_args)
        self.assertIn(("awww-daemon", "HDMI-A-1"), seek_args)
        self.assertIn(("linux-wallpaperengine", "HDMI-A-1"), seek_args)

        # Order: static backends cleared BEFORE killing the old linux-wallpaperengine,
        # otherwise the old scene stays visible while swww is still clearing.
        swww_idx = seek_args.index(("swww-daemon", "HDMI-A-1"))
        awww_idx = seek_args.index(("awww-daemon", "HDMI-A-1"))
        lwe_idx = seek_args.index(("linux-wallpaperengine", "HDMI-A-1"))
        self.assertLess(swww_idx, lwe_idx)
        self.assertLess(awww_idx, lwe_idx)


class SeekAndDestroySwwwPerMonitorTests(unittest.TestCase):
    """Verify seek_and_destroy clears swww background per-monitor, not the whole daemon."""

    def test_swww_daemon_per_monitor_clear(self):
        """When swww-daemon is running and monitor != 'All', run `swww clear --output <monitor>` (not `swww kill`)."""
        # pgrep returns 0 (swww-daemon running), then we expect swww clear with --output
        with patch("waypaper.changer.subprocess.run") as run_mock, patch(
            "waypaper.changer.subprocess.Popen"
        ) as popen_mock:
            # pgrep succeeds (returncode 0)
            run_mock.return_value = MagicMock(returncode=0, stdout=b"", stderr=b"")

            seek_and_destroy("swww-daemon", "HDMI-A-1")

        # The clear command must be per-monitor and must NOT be `swww kill`.
        popen_calls = popen_mock.call_args_list
        clear_calls = [
            c for c in popen_calls if c.args and c.args[0] and c.args[0][0] == "swww"
        ]
        self.assertEqual(len(clear_calls), 1, "expected exactly one swww clear call")
        cmd = clear_calls[0].args[0]
        self.assertEqual(cmd, ["swww", "clear", "--outputs", "HDMI-A-1"])
        # Verify stdin/stdout/stderr are devnull'd so the user never sees swww chatter
        self.assertEqual(clear_calls[0].kwargs.get("stdin"), __import__("subprocess").DEVNULL)

    def test_swww_daemon_noop_when_not_running(self):
        """When swww-daemon is not running, do not call swww clear."""
        with patch("waypaper.changer.subprocess.run") as run_mock, patch(
            "waypaper.changer.subprocess.Popen"
        ) as popen_mock:
            # pgrep fails (returncode 1, swww-daemon NOT running)
            run_mock.side_effect = __import__("subprocess").CalledProcessError(1, "pgrep")

            seek_and_destroy("swww-daemon", "HDMI-A-1")

        popen_calls = popen_mock.call_args_list
        swww_calls = [c for c in popen_calls if c.args and c.args[0] and "swww" in str(c.args[0])]
        self.assertEqual(swww_calls, [], "should not call swww clear when daemon is not running")

    def test_swww_daemon_all_mode_kills_daemon(self):
        """When monitor == 'All', behavior is preserved (swww kill)."""
        with patch("waypaper.changer.subprocess.run") as run_mock, patch(
            "waypaper.changer.subprocess.Popen"
        ) as popen_mock:
            run_mock.return_value = MagicMock(returncode=0, stdout=b"", stderr=b"")

            seek_and_destroy("swww-daemon", "All")

        # Should hit the "if monitor == 'All'" branch which uses killall, not Popen swww
        killall_calls = [
            c for c in popen_mock.call_args_list
            if c.args and c.args[0] and c.args[0][0] == "killall"
        ]
        self.assertTrue(killall_calls, "All-mode should use killall")


if __name__ == "__main__":
    unittest.main()