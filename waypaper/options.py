from typing import List, Dict
BACKEND_OPTIONS: List[str] = ["none", "swaybg", "swww", "feh", "wallutils", "hyprpaper"]
FILL_OPTIONS: List[str] = ["fill", "stretch", "fit", "center", "tile"]
SORT_OPTIONS: List[str] = ["name", "namerev", "date", "daterev"]
SORT_DISPLAYS: Dict[str, str] = {
                "name": "Name ↓",
                "namerev": "Name ↑",
                "date": "Date ↓",
                "daterev": "Date ↑"}

IMAGE_EXTENSIONS: Dict[BACKEND_OPTIONS, List[str]] = {
        BACKEND_OPTIONS[0]: ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[1]: ['.gif', '.jpg', '.jpeg', '.png'],
        BACKEND_OPTIONS[2]: ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[3]: ['.gif', '.jpg', '.jpeg', '.png', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[4]: ['.gif', '.jpg', '.jpeg', '.png'],
        BACKEND_OPTIONS[5]: ['.jpg', '.jpeg', '.png', '.webp'],
        }

SWWW_TRANSITION_TYPES: List[str] = ["any", "none", "simple", "fade", "wipe",  "left", "right", "top",
                                "bottom", "wave", "grow", "center", "outer", "random"]
