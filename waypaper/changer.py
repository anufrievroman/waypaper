"""Module that runs the system processes to change the wallpaper"""

import subprocess

def change_wallpaper(image_path, fill_option, backend="swaybg"):
    """Run a system command swaybg -i image_path -m fill_option &"""
    try:
        # swaybg backend:
        if backend == "swaybg":
            fill = fill_option.lower()
            subprocess.Popen(["swaybg", "-i", image_path, "-m", fill])
            print("Image set with swaybg")

        # ewww backend:
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
            subprocess.Popen(["swww", "img", image_path, "--resize", fill])
            print("Image set with swww")

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

            subprocess.Popen(["feh", fill, image_path])
            print("Image set with feh")

        # wbg backend (unstable):
        # elif backend == "wbg":
            # subprocess.Popen(["killall", "swaybg"])
            # subprocess.Popen(["killall", "swww"])
            # subprocess.Popen(["killall", "wbg"])
            # subprocess.Popen(["wbg", image_path])
            # print("Image set with wbg")

        else:
            print(f"The backend {backend} is not supported")

    except Exception as e:
        print("Error changing wallpaper:", e)
