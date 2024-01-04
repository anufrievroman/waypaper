BACKEND_OPTIONS = ["swaybg", "swww", "feh", "wallutils"]
FILL_OPTIONS = ["fill", "stretch", "fit", "center", "tile"]
SORT_OPTIONS = ["name", "namerev", "date", "daterev"]
SORT_DISPLAYS = {
                "name": "Name ↓",
                "namerev": "Name ↑",
                "date": "Date ↓",
                "daterev": "Date ↑"}

IMAGE_EXTENSIONS = {
        BACKEND_OPTIONS[0]: ['.gif', '.jpg', '.jpeg', '.png'],
        BACKEND_OPTIONS[1]: ['.gif', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[2]: ['.gif', '.jpg', '.jpeg', '.png', '.bmp', '.pnm', '.tiff'],
        BACKEND_OPTIONS[3]: ['.gif', '.jpg', '.jpeg', '.png'],
        }

SWWW_TRANSITION_TYPES = ["any", "none", "simple", "fade", "wipe",  "left", "right", "top",
                                "bottom", "wave", "grow", "center", "outer", "random"]
