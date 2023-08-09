import sys

from waypaper.app import App
from waypaper.changer import change_wallpaper
from waypaper.config import cf


__version__ = "1.2.1"


def run():
    """Read user arguments and either run GUI app or just reset the wallpaper"""

    # Set the wallpaper and quit:
    if "--restore" in sys.argv:
        if cf.wallpaper is not None:
            change_wallpaper(cf.wallpaper, cf.fill_option)
        exit()

    # Print the version and quit:
    elif "--version" in sys.argv:
        print(f"waypaper v.{__version__}")
        exit()

    # Start GUI:
    else:
        app = App()
        app.run()


if __name__ == "__main__":
    run()
