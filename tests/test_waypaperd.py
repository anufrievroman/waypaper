import sys
import unittest
from unittest.mock import patch

from waypaper import waypaperd


class WaypaperdTests(unittest.TestCase):
    def test_parse_args_uses_default_interval(self):
        args = waypaperd.parse_args([])
        self.assertEqual(args.interval, waypaperd.DEFAULT_INTERVAL_SECONDS)

    def test_parse_args_accepts_custom_interval(self):
        args = waypaperd.parse_args(["600"])
        self.assertEqual(args.interval, 600)

    def test_positive_interval_rejects_non_positive_values(self):
        with self.assertRaises(Exception):
            waypaperd.positive_interval("0")

    def test_build_waypaper_command_uses_current_python(self):
        self.assertEqual(
            waypaperd.build_waypaper_command(),
            [sys.executable, "-m", "waypaper", "--random"],
        )

    def test_trigger_random_wallpaper_returns_subprocess_code(self):
        with patch("waypaper.waypaperd.subprocess.run") as run_mock:
            run_mock.return_value.returncode = 7
            self.assertEqual(waypaperd.trigger_random_wallpaper(["waypaper"]), 7)
            run_mock.assert_called_once_with(["waypaper"], check=False)

    def test_main_exits_cleanly_on_keyboard_interrupt(self):
        with patch("waypaper.waypaperd.trigger_random_wallpaper", return_value=0), patch(
            "waypaper.waypaperd.time.sleep", side_effect=KeyboardInterrupt
        ):
            self.assertEqual(waypaperd.main(["60"]), 0)


if __name__ == "__main__":
    unittest.main()