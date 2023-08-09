"""Module that runs the system processes to change the wallpaper"""

import subprocess

def change_wallpaper(image_path, fill_option):
    """Run a system command swaybg -i image_path -m fill_option &"""
    try:
        subprocess.Popen(["swaybg", "-i", image_path, "-m", fill_option.lower()])
        print("Wallpaper changed successfully.")
    except Exception as e:
        print("Error changing wallpaper:", e)
