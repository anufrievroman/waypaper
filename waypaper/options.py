"""Module that contains lists of possible options used in the application"""
import json
import subprocess
import shutil

from typing import List, Dict

from waypaper.output import display_error, display_info

BACKEND_OPTIONS: List[str] = ["none", "swaybg", "swww", "feh", "xwallpaper", "wallutils", "hyprpaper", "mpvpaper", "gslapper", "macos", "awww",  "json"]
FILL_OPTIONS: List[str] = ["fill", "stretch", "fit", "center", "tile"]
SORT_OPTIONS: List[str] = ["name", "namerev", "date", "daterev", "random"]
SORT_DISPLAYS: Dict[str, str] = {"name": "Name ↓", "namerev": "Name ↑", "date": "Date ↓", "daterev": "Date ↑", "random": "Random"}

VIDEO_EXTENSIONS: List[str] = ['.webm', '.mkv', '.flv', '.vob', '.ogv', '.ogg', '.rrc', '.gifv', '.mng', '.movawww',
                               '.avi', '.qt', '.wmv', '.yuv', '.rm', '.asf', '.amv', '.mp4', '.m4p', '.m4v',
                               '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.m4v', '.svi', '.3gp', '.3g2', '.mxf',
                               '.roq', '.nsv', '.flv', '.f4v', '.f4p', '.f4a', '.f4b', '.mod' ]

IMAGE_EXTENSIONS: Dict[str, List[str]] = {
        BACKEND_OPTIONS[0]: ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[1]: ['.gif', '.jpg', '.jpeg', '.png'],
        BACKEND_OPTIONS[2]: ['.gif', '.jpg', '.jpeg', '.jxl', '.png', '.webp', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[3]: ['.gif', '.jpg', '.jpeg', '.png', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[4]: ['.jpeg', '.png'],
        BACKEND_OPTIONS[5]: ['.gif', '.jpg', '.jpeg', '.png'],
        BACKEND_OPTIONS[6]: ['.jpg', '.jpeg', '.png', '.webp', '.jxl'],
        BACKEND_OPTIONS[7]: ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.pnm', '.tiff', '.avif'] + VIDEO_EXTENSIONS,
        BACKEND_OPTIONS[8]: ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.pnm', '.tiff', '.avif'] + VIDEO_EXTENSIONS,
        BACKEND_OPTIONS[9]: ['.gif', '.jpg', '.jpeg', '.png'],
        BACKEND_OPTIONS[10]: ['.gif', '.jpg', '.jpeg', '.jxl', '.png', '.webp', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[11]: ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.pnm', '.tiff', '.avif'] + VIDEO_EXTENSIONS,
        }

SWWW_TRANSITION_TYPES: List[str] = ["any", "none", "simple", "fade", "wipe",  "left", "right", "top",
                                "bottom", "wave", "grow", "center", "outer", "random"]

TIMERS: Dict[str, int] = {"30 sec": 30, "1 min": 60, "2 min": 120, "5 min": 300, "10 min": 600, "30 min": 1800, "1 hour": 3600,
          "2 hours": 7200, "6 hours": 21600, "12 hours": 43200, "1 day": 86400, "1 week": 604800}

def get_installed_backends() -> List[str]:
    """Check which backends are installed in the system"""
    installed_backends = ["none"]
    for backend in BACKEND_OPTIONS:
        if backend == "none":
            continue
        elif backend == "wallutils":
            binary_name = "setwallpaper"
        elif backend == "macos":
            binary_name = "sw_vers"
        elif backend == "json":
            binary_name = "jq"
        else:
            binary_name = backend
        is_installed = bool(shutil.which(binary_name))
        if is_installed:
            installed_backends.append(backend)
    return installed_backends

def get_monitor_names_with_swww() -> List[str]:
    """Obtain the list of plugged monitors using swww daemon"""
    connected_monitors: List[str] = []
    try:
        # Check if swww-deamon is already running. If not, launch it:
        try:
            subprocess.check_output(["pgrep", "swww-daemon"], encoding='utf-8')
        except subprocess.CalledProcessError:
            subprocess.Popen(["swww-daemon"])
            display_info("The swww-daemon launched.")
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
        display_error(f"Exception: {e}")
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
            display_info("The awww-daemon launched.")
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
        display_error(f"Exception: {e}")
    return connected_monitors

def get_monitor_names_with_hyprctl() -> List[str]:
    """Obtain the list of plugged monitors using hyprctl"""
    monitors_info = subprocess.run(["hyprctl", "monitors", "-j"], capture_output=True, text=True, check=True)
    return [monitor["name"] for monitor in json.loads(monitors_info.stdout)]


def get_monitors(backend) -> List[str]:
    """Get a list of monitor names by various means depending on the backend.
    Returns a list of monitor names or an empty list if an error occurs."""
    try:

        available_backends = get_installed_backends()

        monitor_lookup_helpers = {
            "hyprctl": get_monitor_names_with_hyprctl,
            "awww": get_monitor_names_with_awww,
            "swww": get_monitor_names_with_swww,
        }

        if backend == "json":
            for identifier in monitor_lookup_helpers:
                if identifier in monitor_lookup_helpers and identifier in available_backends:
                    method = monitor_lookup_helpers[identifier]
                    return method()

        for identifier in monitor_lookup_helpers:
            if backend == identifier:
                method = monitor_lookup_helpers[backend]
                return method()


        from screeninfo import get_monitors as _get_monitors
        return [m.name for m in _get_monitors()]


    except Exception as e:
        display_error(f"Error fetching monitors: {e}. Falling back to 'All'.")
        return []


def get_monitor_options(backend) -> List[str]:
    """Get a list of available monitors for the CLI."""
    mons = get_monitors(backend)
    return ["All"] + mons if mons else ["All"]
