"""Regression tests for seek_and_destroy missing-PID edge cases.

Ensures seek_and_destroy exits silently and skips the subprocess execution
when find_process_pid returns None or invalid identifiers, preventing noisy
'failed to parse argument' syntax errors from the system kill binary.
"""
import unittest
from unittest.mock import patch, MagicMock
from waypaper.changer import seek_and_destroy


class SeekAndDestroyMissingPidTests(unittest.TestCase):

    def test_no_crash_when_pid_is_none(self):
        """If find_process_pid returns None, seek_and_destroy must return silently."""
        with patch("waypaper.changer.find_process_pid", return_value=None), patch(
            "waypaper.changer.subprocess.run"
        ) as run_mock, patch("waypaper.changer.subprocess.Popen") as popen_mock:
            seek_and_destroy("linux-wallpaperengine", "HDMI-A-1")

        # The critical assertion: kill was NEVER called with "None"
        kill_calls = [
            c for c in run_mock.call_args_list
            if c.args and c.args[0] and c.args[0][0] == "kill"
        ]
        self.assertEqual(
            kill_calls, [],
            "should not call kill when PID is None (was crashing with 'None' arg)"
        )

    def test_no_crash_when_pid_is_none_mpvpaper(self):
        """Same fix covers mpvpaper / swaybg / gslapper branches."""
        with patch("waypaper.changer.find_process_pid", return_value=None), patch(
            "waypaper.changer.subprocess.run"
        ) as run_mock, patch("waypaper.changer.subprocess.Popen"):
            seek_and_destroy("mpvpaper", "DP-1")

        kill_calls = [
            c for c in run_mock.call_args_list
            if c.args and c.args[0] and c.args[0][0] == "kill"
        ]
        self.assertEqual(kill_calls, [])


if __name__ == "__main__":
    unittest.main()
