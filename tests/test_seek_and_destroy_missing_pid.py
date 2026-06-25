"""Regression test for Bug C: seek_and_destroy must NOT crash when find_process_pid returns None.

Reproduction: when the user clicks a wallpaper for the FIRST time after a fresh boot,
no linux-wallpaperengine/swww-daemon is running for that monitor, so find_process_pid
returns None. The old code did `str(None) = "None"` and ran `kill -9 None` which
prints the noisy error `kill: fallo al analizar el argumento: 'None'`.
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
