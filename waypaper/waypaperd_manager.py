"""Systemd user-service wrapper for waypaperd."""

import shutil
import subprocess


class WaypaperdManager:
    """Control waypaperd through the systemd user service."""

    def __init__(self, service_name: str = "waypaperd.service") -> None:
        self.service_name = service_name

    def is_supported(self) -> bool:
        return shutil.which("systemctl") is not None

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["systemctl", "--user", *args, self.service_name],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def check(self) -> bool:
        try:
            return self._run("is-active", "--quiet").returncode == 0
        except (FileNotFoundError, OSError):
            return False

    def launch(self) -> bool:
        try:
            return self._run("start").returncode == 0
        except (FileNotFoundError, OSError):
            return False

    def stop(self) -> bool:
        try:
            return self._run("stop").returncode == 0
        except (FileNotFoundError, OSError):
            return False

    def restart(self) -> bool:
        try:
            return self._run("restart").returncode == 0
        except (FileNotFoundError, OSError):
            return False

    def kill(self) -> bool:
        return self.stop()