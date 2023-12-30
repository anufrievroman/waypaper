"""Module that runs the system processes to change the wallpaper"""

import subprocess
import time


def change_wallpaper(image_path, fill_option, color, backend, monitor, txt):
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
