import sys

from waypaper.app import App
from waypaper.changer import change_wallpaper


__version__ = "1.1"


def run():
    """Read user arguments and either run GUI app or just reset the wallpaper"""

    app = App()
    app.load_data()

    if "--restore" in sys.argv:
        if app.current_wallpaper is not None:
            change_wallpaper(app.current_wallpaper, app.fill_option)
        exit()
    else:
        app.run()


if __name__ == "__main__":
    run()
