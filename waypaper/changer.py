"""Module that runs the system processes to change the wallpaper"""

import subprocess
import time

from waypaper.config import cf

if cf.lang == "de":
    from waypaper.translation_de import *
elif cf.lang == "fr":
    from waypaper.translation_fr import *
elif cf.lang == "ru":
    from waypaper.translation_ru import *
elif cf.lang == "pl":
    from waypaper.translation_pl import *
elif cf.lang == "zh":
    from waypaper.translation_zh import *
else:
    from waypaper.translation_en import *


def change_wallpaper(image_path, fill_option, color, backend, monitor):
    """Run a system command to change the wallpaper depending on the backend"""

    try:
        # swaybg backend:
        if backend == "swaybg":
            fill = fill_option.lower()
            try:
                subprocess.Popen(["killall", "swaybg"])
                time.sleep(0.005)
            except Exception as e:
                print(f"{ERR_KILL} {e}")
            command = ["swaybg"]
            # if monitor != "All":
                # command.extend(["-o", monitor])
            command.extend(["-i", image_path])
            command.extend(["-m", fill, "-c", color])
            subprocess.Popen(command)
            print(f"{MSG_SETWITH} {backend}")

        # swww backend:
        elif backend == "swww":
            fill_types = {
                    "fill": "crop",
                    "fit": "fit",
                    "center": "no",
                    "stretch": "crop",
                    "tile": "no",
                    }
            fill = fill_types[fill_option.lower()]
            try:
                subprocess.Popen(["killall", "swaybg"])
                time.sleep(0.005)
            except Exception as e:
                print(f"{ERR_KILL} {e}")
            subprocess.Popen(["swww", "init"])
            command = ["swww", "img", image_path]
            command.extend(["--resize", fill])
            command.extend(["--fill-color", color])
            command.extend(["--transition-step", str(10)])
            if monitor != "All":
                command.extend(["--outputs", monitor])
            subprocess.Popen(command)
            print(f"{MSG_SETWITH} {backend}")

        # feh backend:
        elif backend == "feh":
            fill_types = {
                    "fill": "--bg-fill",
                    "fit": "--bg-max",
                    "center": "--bg-center",
                    "stretch": "--bg-scale",
                    "tile": "--bg-tile",
                    }
            fill = fill_types[fill_option.lower()]
            command = ["feh", fill, "--image-bg", color]
            command.extend([image_path])
            subprocess.Popen(command)
            print(f"{MSG_SETWITH} {backend}")

        # wallutils backend:
        elif backend == "wallutils":
            fill_types = {
                    "fill": "scale",
                    "fit": "scale",
                    "center": "center",
                    "stretch": "stretch",
                    "tile": "tile",
                    }
            fill = fill_types[fill_option.lower()]

            subprocess.Popen(["setwallpaper", "--mode", fill, image_path])
            print(f"{MSG_SETWITH} {backend}")

        else:
            print(f"{ERR_NOTSUP} {backend}")

    except Exception as e:
        print(f"{ERR_WALL} {e}")
