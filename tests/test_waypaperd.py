import argparse
import sys
import unittest
from unittest.mock import patch

from waypaper import waypaperd


class WaypaperdTests(unittest.TestCase):
    def test_parse_args_leaves_interval_unset_by_default(self):
        args = waypaperd.parse_args([])
        self.assertIsNone(args.interval)

    def test_parse_args_accepts_custom_interval(self):
        args = waypaperd.parse_args(["600"])
        self.assertEqual(args.interval, 600)

    def test_resolve_interval_uses_config_when_no_argument_is_given(self):
        with patch("waypaper.waypaperd.read_config_interval", return_value=900):
            self.assertEqual(waypaperd.resolve_interval(None), 900)

    def test_resolve_interval_prefers_explicit_argument(self):
        with patch("waypaper.waypaperd.read_config_interval") as read_config_interval:
            self.assertEqual(waypaperd.resolve_interval(600), 600)
            read_config_interval.assert_not_called()

    def test_read_config_interval_uses_waypaper_config(self):
        with patch("waypaper.waypaperd.Config") as config_class:
            config = config_class.return_value
            config.waypaperd_cycle_length = 1200

            self.assertEqual(waypaperd.read_config_interval(), 1200)
            config.read.assert_called_once_with()
            config.check_validity.assert_called_once_with()

    def test_positive_interval_rejects_non_positive_values(self):
        with self.assertRaises(argparse.ArgumentTypeError):
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
        with patch("waypaper.waypaperd.resolve_interval", return_value=60), patch(
            "waypaper.waypaperd.trigger_random_wallpaper", return_value=0
        ), patch(
            "waypaper.waypaperd.time.sleep", side_effect=KeyboardInterrupt
        ):
            self.assertEqual(waypaperd.main([]), 0)


if __name__ == "__main__":
    unittest.main()