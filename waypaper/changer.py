"""Module that runs the system processes to change the wallpaper"""

import subprocess
import time

from waypaper.translation_en import *


def change_wallpaper(image_path, fill_option, color, backend):
    """Run a system command to change the wallpaper depending on the backend"""
    try:
        # swaybg backend:
        if backend == "swaybg":
            fill = fill_option.lower()
            subprocess.Popen(["killall", "swaybg"])
            time.sleep(0.005)
            subprocess.Popen(["swaybg", "-i", image_path, "-m", fill, "-c", color])
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
            subprocess.Popen(["swww", "img", image_path, "--resize", fill, "--fill-color", color])
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
        print(ERR_WALL, e)
