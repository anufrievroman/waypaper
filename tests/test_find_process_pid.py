"""Tests for find_process_pid behavior contract.

Covers the refactor from `ps aux | python parse` (slow, large output) to
`pgrep -f` (purpose-built, ~2x faster). The tests pin behavior so the
refactor is safe.
"""
import subprocess
import unittest
from unittest.mock import patch

from waypaper.changer import find_process_pid


def _completed(returncode=0, stdout="", stderr=""):
    """Build a CompletedProcess-like object."""
    cp = subprocess.CompletedProcess(args=[], returncode=returncode)
    cp.stdout = stdout
    cp.stderr = stderr
    return cp


class FindProcessPidTests(unittest.TestCase):

    def test_returns_pid_when_match_exists(self):
        """When pgrep finds the command, return its PID as int."""
        with patch("waypaper.changer.subprocess.run",
                   return_value=_completed(returncode=0, stdout="12345\n")) as run_mock:
            pid = find_process_pid("linux-wallpaperengine --screen-root HDMI-A-1")

        self.assertEqual(pid, 12345)
        # Verify pgrep -f was used (not ps aux)
        args = run_mock.call_args.args[0]
        self.assertEqual(args[0], "pgrep")
        self.assertEqual(args[1], "-f")

    def test_returns_none_when_no_match(self):
        """When pgrep finds nothing (exit code 1), return None."""
        with patch("waypaper.changer.subprocess.run",
                   return_value=_completed(returncode=1, stdout="")):
            pid = find_process_pid("nonexistent-process --screen-root HDMI-A-1")

        self.assertIsNone(pid)

    def test_returns_first_pid_when_multiple_match(self):
        """When pgrep returns multiple PIDs, return the first (lowest PID)."""
        # pgrep -f returns PIDs in ascending order; first line is the smallest PID
        with patch("waypaper.changer.subprocess.run",
                   return_value=_completed(returncode=0, stdout="111\n222\n333\n")):
            pid = find_process_pid("mpvpaper -f socket-HDMI-A-1")

        self.assertEqual(pid, 111)

    def test_handles_empty_stdout_with_zero_return(self):
        """When pgrep returns 0 but stdout is empty (edge case), return None."""
        with patch("waypaper.changer.subprocess.run",
                   return_value=_completed(returncode=0, stdout="")):
            pid = find_process_pid("anything")

        self.assertIsNone(pid)

    def test_returns_int_not_str(self):
        """The returned PID must be int (caller passes to kill -9)."""
        with patch("waypaper.changer.subprocess.run",
                   return_value=_completed(returncode=0, stdout="99999")):
            pid = find_process_pid("foo bar")

        self.assertIsInstance(pid, int)
        self.assertEqual(pid, 99999)

    def test_handles_subprocess_error_gracefully(self):
        """If subprocess.run raises (e.g., pgrep not found), return None."""
        with patch("waypaper.changer.subprocess.run",
                   side_effect=FileNotFoundError("pgrep not found")):
            pid = find_process_pid("anything")

        self.assertIsNone(pid)

    def test_handles_timeout_gracefully(self):
        """If subprocess.run times out, return None (don't hang the wallpaper change)."""
        with patch("waypaper.changer.subprocess.run",
                   side_effect=subprocess.TimeoutExpired(cmd="pgrep", timeout=5)):
            pid = find_process_pid("anything")

        self.assertIsNone(pid)

    def test_pgrep_call_has_timeout(self):
        """Defense in depth: subprocess.run must have a timeout to prevent hangs."""
        with patch("waypaper.changer.subprocess.run",
                   return_value=_completed(returncode=0, stdout="1\n")) as run_mock:
            find_process_pid("anything")

        # Verify timeout was passed
        self.assertIsNotNone(run_mock.call_args.kwargs.get("timeout"),
                             "subprocess.run must have a timeout to prevent pgrep hangs")

    def test_strips_whitespace_in_output(self):
        """pgrep output may have trailing newlines or whitespace; strip them."""
        with patch("waypaper.changer.subprocess.run",
                   return_value=_completed(returncode=0, stdout="  12345  \n")):
            pid = find_process_pid("foo")

        self.assertEqual(pid, 12345)


if __name__ == "__main__":
    unittest.main()