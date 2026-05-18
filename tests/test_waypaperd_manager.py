import subprocess
import unittest
from unittest.mock import patch

from waypaper.waypaperd_manager import WaypaperdManager


class WaypaperdManagerTests(unittest.TestCase):
    def test_check_returns_true_when_service_is_active(self):
        with patch("waypaper.waypaperd_manager.subprocess.run") as run_mock:
            run_mock.return_value.returncode = 0

            self.assertTrue(WaypaperdManager().check())

            run_mock.assert_called_once_with(
                ["systemctl", "--user", "is-active", "--quiet", "waypaperd.service"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def test_check_returns_false_when_service_is_inactive(self):
        with patch("waypaper.waypaperd_manager.subprocess.run") as run_mock:
            run_mock.return_value.returncode = 3

            self.assertFalse(WaypaperdManager().check())

    def test_launch_starts_service(self):
        with patch("waypaper.waypaperd_manager.subprocess.run") as run_mock:
            run_mock.return_value.returncode = 0

            self.assertTrue(WaypaperdManager().launch())

            run_mock.assert_called_once_with(
                ["systemctl", "--user", "start", "waypaperd.service"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def test_stop_stops_service(self):
        with patch("waypaper.waypaperd_manager.subprocess.run") as run_mock:
            run_mock.return_value.returncode = 0

            self.assertTrue(WaypaperdManager().stop())

            run_mock.assert_called_once_with(
                ["systemctl", "--user", "stop", "waypaperd.service"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def test_restart_restarts_service(self):
        with patch("waypaper.waypaperd_manager.subprocess.run") as run_mock:
            run_mock.return_value.returncode = 0

            self.assertTrue(WaypaperdManager().restart())

            run_mock.assert_called_once_with(
                ["systemctl", "--user", "restart", "waypaperd.service"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def test_kill_uses_service_stop(self):
        with patch.object(WaypaperdManager, "stop", return_value=True) as stop_mock:
            self.assertTrue(WaypaperdManager().kill())
            stop_mock.assert_called_once_with()

    def test_commands_return_false_when_systemctl_is_missing(self):
        with patch("waypaper.waypaperd_manager.subprocess.run", side_effect=FileNotFoundError):
            manager = WaypaperdManager()

            self.assertFalse(manager.check())
            self.assertFalse(manager.launch())
            self.assertFalse(manager.stop())
            self.assertFalse(manager.restart())

    def test_is_supported_checks_systemctl_on_path(self):
        with patch("waypaper.waypaperd_manager.shutil.which", return_value="/usr/bin/systemctl"):
            self.assertTrue(WaypaperdManager().is_supported())

        with patch("waypaper.waypaperd_manager.shutil.which", return_value=None):
            self.assertFalse(WaypaperdManager().is_supported())


if __name__ == "__main__":
    unittest.main()
