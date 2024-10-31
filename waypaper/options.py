from typing import List, Dict

BACKEND_OPTIONS: List[str] = ["none", "swaybg", "swww", "feh", "wallutils", "hyprpaper", "mpvpaper"]
FILL_OPTIONS: List[str] = ["fill", "stretch", "fit", "center", "tile"]
SORT_OPTIONS: List[str] = ["name", "namerev", "date", "daterev"]
SORT_DISPLAYS: Dict[str, str] = {
                "name": "Name ↓",
                "namerev": "Name ↑",
                "date": "Date ↓",
                "daterev": "Date ↑"}

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
        BACKEND_OPTIONS[6]: ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.pnm', '.tiff'] + VIDEO_EXTENSIONS,
        }

SWWW_TRANSITION_TYPES: List[str] = ["any", "none", "simple", "fade", "wipe",  "left", "right", "top",
                                "bottom", "wave", "grow", "center", "outer", "random"]
