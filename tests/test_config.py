import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from waypaper.config import Config


class ConfigTests(unittest.TestCase):
    def test_read_uses_linux_wallpaperengine_noautomute_key(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            config_dir = root / "config"
            cache_dir = root / "cache"
            state_dir = root / "state"
            pictures_dir = root / "pictures"
            config_dir.mkdir()

            (config_dir / "config.ini").write_text(
                "[Settings]\n"
                "linux_wallpaperengine_silent = false\n"
                "linux_wallpaperengine_noautomute = true\n",
                encoding="utf-8",
            )

            with patch("waypaper.config.user_config_path", return_value=config_dir), patch(
                "waypaper.config.user_cache_path", return_value=cache_dir
            ), patch("waypaper.config.user_state_path", return_value=state_dir), patch(
                "waypaper.config.user_pictures_path", return_value=pictures_dir
            ), patch("waypaper.config.check_installed_backends", return_value=["none"]):
                config = Config()
                config.read()

            self.assertFalse(config.linux_wallpaperengine_silent)
            self.assertTrue(config.linux_wallpaperengine_noautomute)


if __name__ == "__main__":
    unittest.main()