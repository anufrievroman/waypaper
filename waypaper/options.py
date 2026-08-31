"""Module that contains lists of possible options used in the application"""
import json
import os
import subprocess
import sys

from pathlib import Path
from typing import List, Dict


BACKEND_OPTIONS: List[str] = ["none", "swaybg", "swww", "feh", "xwallpaper", "wallutils", "hyprpaper", "mpvpaper", "gslapper", "macos", "awww", "linux-wallpaperengine"]
FILL_OPTIONS: List[str] = ["fill", "stretch", "fit", "center", "tile"]
LINUX_WALLPAPERENGINE_FILL_OPTIONS: List[str] = ["fill", "stretch", "fit", "default"]
SORT_OPTIONS: List[str] = ["name", "namerev", "date", "daterev", "random"]
SORT_DISPLAYS: Dict[str, str] = {"name": "Name ↓", "namerev": "Name ↑", "date": "Date ↓", "daterev": "Date ↑", "random": "Random"}

VIDEO_EXTENSIONS: List[str] = ['.webm', '.mkv', '.flv', '.vob', '.ogv', '.ogg', '.rrc', '.gifv', '.mng', '.mov',
                               '.avi', '.qt', '.wmv', '.yuv', '.rm', '.asf', '.amv', '.mp4', '.m4p', '.m4v',
                               '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.m4v', '.svi', '.3gp', '.3g2', '.mxf',
                               '.roq', '.nsv', '.flv', '.f4v', '.f4p', '.f4a', '.f4b', '.mod' ]

IMAGE_EXTENSIONS: Dict[str, List[str]] = {
        BACKEND_OPTIONS[0]: ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[1]: ['.gif', '.jpg', '.jpeg', '.png'],
        BACKEND_OPTIONS[2]: ['.gif', '.jpg', '.jpeg', '.jxl', '.png', '.webp', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[3]: ['.gif', '.jpg', '.jpeg', '.png', '.bmp', '.pnm', '.tiff', '.webp'],
        BACKEND_OPTIONS[4]: ['.jpeg', '.png'],
        BACKEND_OPTIONS[5]: ['.gif', '.jpg', '.jpeg', '.png'],
        BACKEND_OPTIONS[6]: ['.jpg', '.jpeg', '.png', '.webp', '.jxl'],
        BACKEND_OPTIONS[7]: ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.pnm', '.tiff', '.avif'] + VIDEO_EXTENSIONS,
        BACKEND_OPTIONS[8]: ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.pnm', '.tiff', '.avif'] + VIDEO_EXTENSIONS,
        BACKEND_OPTIONS[9]: ['.gif', '.jpg', '.jpeg', '.png'],
        BACKEND_OPTIONS[10]: ['.gif', '.jpg', '.jpeg', '.png', '.jxl', '.webp', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[11]: []
        }

SWWW_TRANSITION_TYPES: List[str] = ["any", "none", "simple", "fade", "wipe",  "left", "right", "top",
                                "bottom", "wave", "grow", "center", "outer", "random"]
SWWW_FILTER_TYPES: List[str] = ["Nearest", "Bilinear", "CatmullRom", "Mitchell", "Lanczos3"]

TIMERS: Dict[str, int] = {"30 sec": 30, "1 min": 60, "2 min": 120, "5 min": 300, "10 min": 600, "30 min": 1800, "1 hour": 3600,
          "2 hours": 7200, "6 hours": 21600, "12 hours": 43200, "1 day": 86400, "1 week": 604800}

LINUX_WALLPAPERENGINE_CLAMP: List[str] = ["none", "clamp", "border", "repeat"]


def get_monitor_names_with_swww() -> List[str]:
    """Obtain the list of plugged monitors using swww daemon"""
    connected_monitors: List[str] = []
    try:
        # Check if swww-deamon is already running. If not, launch it:
        try:
            subprocess.check_output(["pgrep", "swww-daemon"], encoding='utf-8')
        except subprocess.CalledProcessError:
            subprocess.Popen(["swww-daemon"])
            print("The swww-daemon launched.")
        # Check available monitors:
        monitors_info = str(subprocess.check_output(["swww", "query"], encoding='utf-8'))
        monitors = monitors_info.split("\n")
        version_p = subprocess.run(["swww", "-V"], capture_output=True, text=True)
        swww_version = [int(x) for x in version_p.stdout.strip().split("-")[0].split(" ")[1].split(".")]
        for monitor in monitors[:-1]:
            if swww_version >= [0, 11, 0]:
                connected_monitors.append(monitor.split(':')[1].lstrip())
            else:
                connected_monitors.append(monitor.split(':')[0])

    except Exception as e:
        print(f"Exception: {e}")
    return connected_monitors

def get_monitor_names_with_awww() -> List[str]:
    """Obtain the list of plugged monitors using awww daemon"""
    connected_monitors: List[str] = []
    try:
        # Check if awww-deamon is already running. If not, launch it:
        try:
            subprocess.check_output(["pgrep", "awww-daemon"], encoding='utf-8')
        except subprocess.CalledProcessError:
            subprocess.Popen(["awww-daemon"])
            print("The awww-daemon launched.")
        # Check available monitors:
        monitors_info = str(subprocess.check_output(["awww", "query"], encoding='utf-8'))
        monitors = monitors_info.split("\n")
        version_p = subprocess.run(["awww", "-V"], capture_output=True, text=True)
        awww_version = [int(x) for x in version_p.stdout.strip().split("-")[0].split(" ")[1].split(".")]
        for monitor in monitors[:-1]:
            if awww_version >= [0, 11, 0]:
                connected_monitors.append(monitor.split(':')[1].lstrip())
            else:
                connected_monitors.append(monitor.split(':')[0])

    except Exception as e:
        print(f"Exception: {e}")
    return connected_monitors

def get_monitor_names_with_hyprctl() -> List[str]:
    """Obtain the list of plugged monitors using hyprctl"""
    monitors_info = subprocess.run(["hyprctl", "monitors", "-j"], capture_output=True, text=True, check=True)
    return [monitor["name"] for monitor in json.loads(monitors_info.stdout)]


def _monitors_from_drm() -> List[str]:
    """Read connected outputs from the kernel via /sys/class/drm (Wayland / DRM).

    Connector directories are named like 'card0-DP-1'; we strip the 'cardN-'
    prefix to obtain the output name ('DP-1') as reported by wlroots-based
    compositors."""
    names: List[str] = []
    drm = Path("/sys/class/drm")
    if not drm.is_dir():
        return names
    for card in sorted(drm.glob("card*-*")):
        try:
            if (card / "status").read_text().strip() == "connected":
                name = card.name.split("-", 1)[1]
                if name not in names:  # dedupe across multiple GPUs
                    names.append(name)
        except OSError:
            continue
    return names


def _monitors_from_xrandr() -> List[str]:
    """Read active outputs from xrandr (Xorg)."""
    out = subprocess.run(
        ["xrandr", "--listmonitors"], capture_output=True, text=True, check=True
    )
    # First line is "Monitors: N"; the last token of each row is the output name.
    names = [line.split()[-1] for line in out.stdout.splitlines()[1:] if line.strip()]
    # Under XWayland xrandr returns XWAYLAND0/1... — a sign we are really on
    # Wayland, so fall back to the DRM connector names instead.
    if any(name.startswith("XWAYLAND") for name in names):
        return _monitors_from_drm()
    return names


def _monitors_from_macos() -> List[str]:
    """List connected displays on macOS via system_profiler (no dependency)."""
    out = subprocess.run(
        ["system_profiler", "-json", "SPDisplaysDataType"],
        capture_output=True, text=True, check=True,
    )
    data = json.loads(out.stdout)
    names: List[str] = []
    for gpu in data.get("SPDisplaysDataType", []):
        for display in gpu.get("spdisplays_ndrvs", []):
            # Skip displays that are attached but not online, if reported.
            if display.get("spdisplays_online") == "spdisplays_no":
                continue
            name = display.get("_name")
            if name:
                names.append(name)
    return names


def _is_wayland() -> bool:
    """Best-effort detection of a Wayland session."""
    return bool(os.environ.get("WAYLAND_DISPLAY")) or \
        os.environ.get("XDG_SESSION_TYPE") == "wayland"


def get_plugged_monitors() -> List[str]:
    """Get plugged monitor names without third-party dependencies.

    Returns an empty list on any failure, in which case callers fall back to
    targeting 'All' outputs."""
    if sys.platform == "darwin":
        try:
            return _monitors_from_macos()
        except Exception:
            return []
    # Check WAYLAND_DISPLAY before DISPLAY: on Wayland, DISPLAY is also set for
    # XWayland, so relying on it would wrongly pick xrandr.
    if _is_wayland():
        return _monitors_from_drm()
    if os.environ.get("DISPLAY"):
        try:
            return _monitors_from_xrandr()
        except Exception:
            return _monitors_from_drm()
    return _monitors_from_drm()


def get_monitors(backend) -> List[str]:
    """Get a list of monitor names by various means depending on the backend.
    Returns a list of monitor names or an empty list if an error occurs."""
    try:
        if backend == "hyprpaper":
            return get_monitor_names_with_hyprctl()
        elif backend == "swww":
            return get_monitor_names_with_swww()
        elif backend == "awww":
            return get_monitor_names_with_awww()
        else:
            return get_plugged_monitors()
    except Exception as e:
        print(f"Error fetching monitors: {e}. Falling back to 'All'.")
        return []


def get_monitor_options(backend) -> List[str]:
    """Get a list of available monitors for the CLI."""
    mons = get_monitors(backend)
    return ["All"] + mons if mons else ["All"]
