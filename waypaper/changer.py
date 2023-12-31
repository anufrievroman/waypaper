"""Module that runs the system processes to change the wallpaper"""

import subprocess
import time

from waypaper.options import BACKEND_OPTIONS


def change_wallpaper(image_path, cf, monitor, txt, missing_backends):
    """Run a system command to change the wallpaper depending on the backend"""

    fill_option = cf.fill_option
    color = cf.color
    backend = cf.backend
    swww_transition = cf.swww_transition

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
            print(f"{txt.msg_setwith} {backend}")

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
            is_swaybg_installed = not missing_backends[BACKEND_OPTIONS.index("swaybg")]
            if is_swaybg_installed:
                try:
                    subprocess.Popen(["killall", "swaybg"])
                    time.sleep(0.005)
                except Exception as e:
                    print(f"{ERR_KILL} {e}")
            print(missing_backends)
            subprocess.Popen(["swww", "init"])
            command = ["swww", "img", image_path]
            command.extend(["--resize", fill])
            command.extend(["--fill-color", color])
            command.extend(["--transition-type", swww_transition])
            # command.extend(["--transition-step", str(30)])
            if monitor != "All":
                command.extend(["--outputs", monitor])
            subprocess.Popen(command)
            print(f"{txt.msg_setwith} {backend}")

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
            print(f"{txt.msg_setwith} {backend}")

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
            print(f"{txt.msg_setwith} {backend}")

        else:
            print(f"{txt.err_notsup} {backend}")

    except Exception as e:
        print(f"{txt.err_wall} {e}")
