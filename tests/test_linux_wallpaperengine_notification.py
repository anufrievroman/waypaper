import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from waypaper.changer import change_with_linux_wallpaperengine


class LinuxWallpaperengineNotificationTests(unittest.TestCase):
    def make_config(self) -> SimpleNamespace:
        return SimpleNamespace(
            fill_option="fill",
            linux_wallpaperengine_silent=True,
            linux_wallpaperengine_noautomute=True,
            linux_wallpaperengine_no_audio_processing=False,
            linux_wallpaperengine_no_fullscreen_pause=False,
            linux_wallpaperengine_fullscreen_pause_only_active=False,
            linux_wallpaperengine_disable_particles=True,
            linux_wallpaperengine_disable_mouse=False,
            linux_wallpaperengine_disable_parallax=False,
            linux_wallpaperengine_clamp="none",
            linux_wallpaperengine_volume=15,
            linux_wallpaperengine_fps=30,
        )

    def make_preview_path(self, tmp_dir: str) -> Path:
        wallpaper_dir = Path(tmp_dir) / "wallpaper"
        wallpaper_dir.mkdir()
        preview_path = wallpaper_dir / "preview.jpg"
        preview_path.write_text("preview", encoding="utf-8")
        return preview_path

    def test_running_process_does_not_notify(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            process = MagicMock()
            process.poll.return_value = None

            with patch("waypaper.changer.seek_and_destroy"), patch(
                "waypaper.changer.subprocess.Popen", return_value=process
            ) as popen_mock, patch("waypaper.changer.time.sleep"), patch(
                "waypaper.changer.notify_waypaper_issue"
            ) as notify_mock:
                change_with_linux_wallpaperengine(
                    self.make_preview_path(tmp_dir),
                    self.make_config(),
                    "DP-1",
                )

        command = popen_mock.call_args.args[0]
        self.assertNotIn("&", command)
        self.assertTrue(popen_mock.call_args.kwargs["start_new_session"])
        notify_mock.assert_not_called()

    def test_immediate_exit_notifies_user(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            process = MagicMock()
            process.poll.return_value = 7

            with patch("waypaper.changer.seek_and_destroy"), patch(
                "waypaper.changer.subprocess.Popen", return_value=process
            ), patch("waypaper.changer.time.sleep"), patch(
                "waypaper.changer.notify_waypaper_issue"
            ) as notify_mock:
                change_with_linux_wallpaperengine(
                    self.make_preview_path(tmp_dir),
                    self.make_config(),
                    "DP-1",
                )

        notify_mock.assert_called_once()
        summary, message = notify_mock.call_args.args
        self.assertEqual(summary, "Waypaper launch failed")
        self.assertIn("linux-wallpaperengine exited immediately with code 7", message)


if __name__ == "__main__":
    unittest.main()