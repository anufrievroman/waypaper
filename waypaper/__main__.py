"""Main module that runs the program and either runs GUI or just changer wallpaper"""

import time
import argparse
import gettext

from waypaper.config import Config
from waypaper.app import App
from waypaper.changer import change_wallpaper
from waypaper.common import get_random_file
from waypaper.aboutdata import AboutData
from waypaper.options import FILL_OPTIONS, BACKEND_OPTIONS





def run():
    """Read user arguments and either run GUI app or just reset the wallpaper"""

    aboutData = AboutData()

    gettext.install(aboutData.applicationName())

    cf = Config()

    parser = argparse.ArgumentParser(prog = aboutData.applicationName(), description =
                                     _("GUI wallpaper setter for Wayland and X11. It works as a frontend for {backends}".format(backends=BACKEND_OPTIONS)),
                                     epilog = _("For more information, visit: {homePage}").
                                     format(homePage=aboutData.homePage()))
    parser.add_argument("-v", "--version", help=_("print version of the program"),
                        action="store_true")
    parser.add_argument("--restore", help=_("restore last wallpaper"), action="store_true")
    parser.add_argument("--random", help=_("set a random wallpaper"), action="store_true")
    parser.add_argument("--fill", help=_("specify how to fill the screen with chosen image"),
                        action="store_true")
    parser.add_argument("--backend", help=_("specify which backend to use to set wallpaper"),
                        choices=BACKEND_OPTIONS)
    args = parser.parse_args()
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
        exit(0)

    # Print the version and quit:
    if args.version:
        print(f"{aboutData.applicationName()} v.{aboutData.applicationVersion()}")
        exit(0)

    # Start GUI:
    app = App()
    app.run()


if __name__ == "__main__":
    run()
