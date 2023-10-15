"""Main module that runs the program and either runs GUI or just changer wallpaper"""

import time
import argparse


from waypaper.config import Config
from waypaper.app import App
from waypaper.changer import change_wallpaper
from waypaper.common import get_random_file
from waypaper.aboutdata import AboutData
from waypaper.options import FILL_OPTIONS, BACKEND_OPTIONS

aboutData = AboutData()

cf = Config()
if cf.lang == "de":
    from waypaper.translation_de import *
elif cf.lang == "fr":
    from waypaper.translation_fr import *
elif cf.lang == "ru":
    from waypaper.translation_ru import *
elif cf.lang == "pl":
    from waypaper.translation_pl import *
else:
    from waypaper.translation_en import *


parser = argparse.ArgumentParser(prog = aboutData.applicationName(), description = MSG_DESC,
                                 epilog = MSG_INFO)
parser.add_argument("-v", "--version", help=MSG_ARG_HELP, action="store_true")
parser.add_argument("--restore", help=MSG_ARG_REST, action="store_true")
parser.add_argument("--random", help=MSG_ARG_RAND, action="store_true")
parser.add_argument("--fill", help=MSG_ARG_FILL, action="store_true")
parser.add_argument("--backend", help=MSG_ARG_BACK, choices=BACKEND_OPTIONS)
args = parser.parse_args()



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
