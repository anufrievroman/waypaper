import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from waypaper.changer import change_with_linux_wallpaperengine, describe_linux_wallpaperengine_pause_policy


class LinuxWallpaperengineLoggingTests(unittest.TestCase):
    def make_config(self, cache_dir: Path) -> SimpleNamespace:
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
            cache_dir=cache_dir,
        )

    def test_describe_pause_policy_variants(self):
        config = self.make_config(Path("/tmp"))
        self.assertEqual(describe_linux_wallpaperengine_pause_policy(config), "renderer default")

        config.linux_wallpaperengine_fullscreen_pause_only_active = True
        self.assertIn("fullscreen-pause-only-active", describe_linux_wallpaperengine_pause_policy(config))

        config.linux_wallpaperengine_no_fullscreen_pause = True
        self.assertEqual(
            describe_linux_wallpaperengine_pause_policy(config),
            "disabled via --no-fullscreen-pause",
        )

    def test_scene_log_records_running_process_health(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir)
            wallpaper_dir = cache_dir / "scene-wallpaper"
            wallpaper_dir.mkdir()
            image_path = wallpaper_dir / "project.json"
            image_path.write_text("{}", encoding="utf-8")
            log_path = cache_dir / "launcher.log"
            config = self.make_config(cache_dir)

            process = MagicMock(pid=4242)
            process.poll.return_value = None

            with patch("waypaper.changer.seek_and_destroy"), patch(
                "waypaper.changer.get_wallpaperengine_project",
                return_value={"title": "Test Scene", "type": "scene", "file": "scene.json"},
            ), patch(
                "waypaper.changer.resolve_linux_wallpaperengine_binary",
                return_value="/usr/bin/linux-wallpaperengine",
            ), patch(
                "waypaper.changer.resolve_linux_wallpaperengine_assets_dir",
                return_value=Path("/assets"),
            ), patch(
                "waypaper.changer.get_linux_wallpaperengine_log_path",
                return_value=log_path,
            ), patch(
                "waypaper.changer.subprocess.Popen",
                return_value=process,
            ) as popen_mock, patch(
                "waypaper.changer.time.sleep"
            ), patch(
                "waypaper.changer.notify_waypaper_issue"
            ) as notify_mock:
                change_with_linux_wallpaperengine(image_path, config, "DP-1")

            command = popen_mock.call_args.args[0]
            self.assertNotIn("--disable-particles", command)

            log_text = log_path.read_text(encoding="utf-8")
            self.assertIn("Launch PID: 4242", log_text)
            self.assertIn("Process status after initial check: still running after 0.5s.", log_text)
            self.assertIn("Fullscreen pause policy: renderer default", log_text)
            notify_mock.assert_not_called()

    def test_immediate_exit_is_recorded_in_log(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir)
            wallpaper_dir = cache_dir / "video-wallpaper"
            wallpaper_dir.mkdir()
            image_path = wallpaper_dir / "project.json"
            image_path.write_text("{}", encoding="utf-8")
            log_path = cache_dir / "launcher.log"
            config = self.make_config(cache_dir)

            process = MagicMock(pid=99)
            process.poll.return_value = 7

            with patch("waypaper.changer.seek_and_destroy"), patch(
                "waypaper.changer.get_wallpaperengine_project",
                return_value={"title": "Test Video", "type": "video", "file": "video.mp4"},
            ), patch(
                "waypaper.changer.resolve_linux_wallpaperengine_binary",
                return_value="/usr/bin/linux-wallpaperengine",
            ), patch(
                "waypaper.changer.resolve_linux_wallpaperengine_assets_dir",
                return_value=Path("/assets"),
            ), patch(
                "waypaper.changer.get_linux_wallpaperengine_log_path",
                return_value=log_path,
            ), patch(
                "waypaper.changer.subprocess.Popen",
                return_value=process,
            ), patch(
                "waypaper.changer.time.sleep"
            ), patch(
                "waypaper.changer.change_with_static_fallback",
                return_value="swaybg",
            ), patch(
                "waypaper.changer.notify_waypaper_issue"
            ) as notify_mock:
                change_with_linux_wallpaperengine(image_path, config, "DP-1")

            log_text = log_path.read_text(encoding="utf-8")
            self.assertIn("Process status after initial check: exited with code 7", log_text)
            notify_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()