"""Module that runs the system processes to change the wallpaper"""

import subprocess
import time

from waypaper.translation_en import *


def change_wallpaper(image_path, fill_option, color, backend, monitor):
    """Run a system command to change the wallpaper depending on the backend"""

    try:
        # swaybg backend:
        if backend == "swaybg":
            fill = fill_option.lower()
            subprocess.Popen(["killall", "swaybg"])
            time.sleep(0.005)
            command = ["swaybg", "-i", image_path, "-m", fill, "-c", color]
            if monitor not in ["All", ""]:
                command.extend(["--output", monitor])
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
            subprocess.Popen(["killall", "swaybg"])
            time.sleep(0.005)
            subprocess.Popen(["swww", "init"])
            command = ["swww", "img", image_path]
            command.extend(["--resize", fill])
            command.extend(["--fill-color", color])
            command.extend(["--transition-step", str(10)])
            if monitor not in ["All", ""]:
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

            subprocess.Popen(["feh", fill, "--image-bg", color, image_path])
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
