"""Module that runs the system processes to change the wallpaper"""

import subprocess
import time

from waypaper.options import BACKEND_OPTIONS


def change_wallpaper(image_path, cf, monitor, txt):
    """Run system commands to change the wallpaper depending on the backend"""

    try:
        # swaybg backend:
        if cf.backend == "swaybg":
            fill = cf.fill_option.lower()
            try:
                subprocess.Popen(["killall", "swaybg"])
                time.sleep(0.005)
            except Exception as e:
                print(f"{txt.err_kill} {e}")
            command = ["swaybg"]
            # if monitor != "All":
                # command.extend(["-o", monitor])
            command.extend(["-i", image_path])
            command.extend(["-m", fill, "-c", cf.color])
            subprocess.Popen(command)
            print(f"{txt.msg_setwith} {cf.backend}")

        # swww backend:
        elif cf.backend == "swww":
            fill_types = {
                    "fill": "crop",
                    "fit": "fit",
                    "center": "no",
                    "stretch": "crop",
                    "tile": "no",
                    }
            fill = fill_types[cf.fill_option.lower()]
            if "swaybg" in cf.installed_backends:
                try:
                    subprocess.Popen(["killall", "swaybg"])
                    time.sleep(0.005)
                except Exception as e:
                    print(f"{txt.err_kill} {e}")
            subprocess.Popen(["swww-daemon"])
            command = ["swww", "img", image_path]
            command.extend(["--resize", fill])
            command.extend(["--fill-color", cf.color])
            command.extend(["--transition-type", cf.swww_transition_type])
            command.extend(["--transition-step", str(cf.swww_transition_step)])
            command.extend(["--transition-angle", str(cf.swww_transition_angle)])
            command.extend(["--transition-duration", str(cf.swww_transition_duration)])
            if monitor != "All":
                command.extend(["--outputs", monitor])
            subprocess.Popen(command)
            print(f"{txt.msg_setwith} {cf.backend}")

        # feh backend:
        elif cf.backend == "feh":
            fill_types = {
                    "fill": "--bg-fill",
                    "fit": "--bg-max",
                    "center": "--bg-center",
                    "stretch": "--bg-scale",
                    "tile": "--bg-tile",
                    }
            fill = fill_types[cf.fill_option.lower()]
            command = ["feh", fill, "--image-bg", cf.color]
            command.extend([image_path])
            subprocess.Popen(command)
            print(f"{txt.msg_setwith} {cf.backend}")

        # wallutils backend:
        elif cf.backend == "wallutils":
            fill_types = {
                    "fill": "scale",
                    "fit": "scale",
                    "center": "center",
                    "stretch": "stretch",
                    "tile": "tile",
                    }
            fill = fill_types[cf.fill_option.lower()]

            subprocess.Popen(["setwallpaper", "--mode", fill, image_path])
            print(f"{txt.msg_setwith} {cf.backend}")

        else:
            print(f"{txt.err_notsup} {cf.backend}")

        # Run a post command:
        if cf.post_command:
            modified_image_path = image_path.replace(" ", "\\ ")
            post_command = cf.post_command.replace("$wallpaper", modified_image_path)
            subprocess.Popen(post_command, shell=True)
            print(f'Post command {post_command} executed')

    except Exception as e:
        print(f"{txt.err_wall} {e}")
