"""Module that runs the system processes to change the wallpaper"""

import subprocess

def change_wallpaper(image_path, fill_option, backend="swaybg"):
    """Run a system command swaybg -i image_path -m fill_option &"""
    try:
        # swaybg backend:
        if backend == "swaybg":
            subprocess.Popen(["swaybg", "-i", image_path, "-m", fill_option.lower()])
            print("Image set with swaybg")

        # ewww backend:
        elif backend == "swww":
            subprocess.Popen(["killall", "swaybg"])
            subprocess.Popen(["swww", "init"])
            subprocess.Popen(["swww", "img", image_path])
            print("Image set with swww")

        # wbg backend (nor stable):
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
