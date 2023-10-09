"""Main module that runs the program and either runs GUI or just changer wallpaper"""

import time


from waypaper.config import cf
from waypaper.arguments import args
from waypaper.app import App
from waypaper.changer import change_wallpaper
from waypaper.common import get_random_file


__version__ = "2.0.2"


def run():
    """Read user arguments and either run GUI app or just reset the wallpaper"""

    cf.read_parameters_from_user_arguments(args)

    # Set the wallpaper and quit:
    if args.restore:
        for wallpaper, monitor in zip(cf.wallpaper, cf.monitors):

            if args.random:
                wallpaper = get_random_file(cf.image_folder, cf.include_subfolders)

            if wallpaper is None:
                continue
            change_wallpaper(wallpaper, cf.fill_option, cf.color, cf.backend, monitor)
            time.sleep(0.1)
        exit()

    # Print the version and quit:
    if args.version:
        print(f"waypaper v.{__version__}")
        exit()

    # Start GUI:
    app = App()
    app.run()


if __name__ == "__main__":
    run()
