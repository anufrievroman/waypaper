"""Module that contains lists of possible options used in the application"""

from typing import List, Dict
from screeninfo import get_monitors as _get_monitors

BACKEND_OPTIONS: List[str] = ["none", "swaybg", "swww", "feh", "wallutils", "hyprpaper", "mpvpaper"]
FILL_OPTIONS: List[str] = ["fill", "stretch", "fit", "center", "tile"]
SORT_OPTIONS: List[str] = ["name", "namerev", "date", "daterev"]
SORT_DISPLAYS: Dict[str, str] = {"name": "Name ↓", "namerev": "Name ↑", "date": "Date ↓", "daterev": "Date ↑"}

VIDEO_EXTENSIONS: List[str] = ['.webm', '.mkv', '.flv', '.vob', '.ogv', '.ogg', '.rrc', '.gifv', '.mng', '.mov',
                               '.avi', '.qt', '.wmv', '.yuv', '.rm', '.asf', '.amv', '.mp4', '.m4p', '.m4v',
                               '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.m4v', '.svi', '.3gp', '.3g2', '.mxf',
                               '.roq', '.nsv', '.flv', '.f4v', '.f4p', '.f4a', '.f4b', '.mod' ]

IMAGE_EXTENSIONS: Dict[str, List[str]] = {
        BACKEND_OPTIONS[0]: ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[1]: ['.gif', '.jpg', '.jpeg', '.png'],
        BACKEND_OPTIONS[2]: ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[3]: ['.gif', '.jpg', '.jpeg', '.png', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[4]: ['.gif', '.jpg', '.jpeg', '.png'],
        BACKEND_OPTIONS[5]: ['.jpg', '.jpeg', '.png', '.webp'],
        BACKEND_OPTIONS[6]: ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.pnm', '.tiff', '.avif'] + VIDEO_EXTENSIONS,
        }

SWWW_TRANSITION_TYPES: List[str] = ["any", "none", "simple", "fade", "wipe",  "left", "right", "top",
                                "bottom", "wave", "grow", "center", "outer", "random"]

TIMERS: Dict[str, int] = {"30 sec": 30, "1 min": 60, "2 min": 120, "5 min": 300, "10 min": 600, "30 min": 1800, "1 hour": 3600,
          "2 hours": 7200, "6 hours": 21600, "12 hours": 43200, "1 day": 86400, "1 week": 604800}

def get_monitors() -> List[str]:
    """Get a list of monitor names using screeninfo. Returns a list of monitor names or an empty list if an error occurs."""
    try:
        return [m.name for m in _get_monitors()]
    except Exception as e:
        print(f"Error fetching monitors with screeninfo: {e}. Falling back to 'All'.")
        return []

def get_monitor_options() -> List[str]:
    """Get a list of available monitors for the CLI."""
    mons = get_monitors()
    return ["All"] + mons if mons else ["All"]
