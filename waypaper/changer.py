"""Module that runs the system processes to change the wallpaper"""

import subprocess

def change_wallpaper(image_path, fill_option, color, backend):
    """Run a system command to change the wallpaper depending on the backend"""
    try:
        # swaybg backend:
        if backend == "swaybg":
            fill = fill_option.lower()
            subprocess.Popen(["swaybg", "-i", image_path, "-m", fill, "-c", color])
            print(f"Wallpaper was set with {backend}")

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
            subprocess.Popen(["swww", "init"])
            subprocess.Popen(["swww", "img", image_path, "--resize", fill, "--fill-color", color])
            print(f"Wallpaper was set with {backend}")

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
            print(f"Wallpaper was set with {backend}")

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
            print(f"Wallpaper was set with {backend}")

        # wbg backend (unstable):
        # elif backend == "wbg":
            # subprocess.Popen(["killall", "swaybg"])
            # subprocess.Popen(["killall", "swww"])
            # subprocess.Popen(["killall", "wbg"])
            # subprocess.Popen(["wbg", image_path])
            # print("Image set with wbg")

        # pcmanfm backend (unstable):
        # elif backend == "pcmanfm":
            # fill_types = {
                    # "fill": "--wallpaper-mode=screen",
                    # "fit": "--wallpaper-mode=fit",
                    # "center": "--wallpaper-mode=center",
                    # "stretch": "--wallpaper-mode=stretch",
                    # "tile": "--wallpaper-mode=tile",
                    # }
            # fill = fill_types[fill_option.lower()]

            # subprocess.Popen(["pcmanfm", "--desktop"])
            # subprocess.Popen(["pcmanfm", "-w", image_path, fill])
            # print("Image set with pcmanfm")

        else:
            print(f"The backend {backend} is not supported")

    except Exception as e:
        print("Error changing wallpaper:", e)
