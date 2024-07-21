"""Main module that runs the program and either runs GUI or just changer wallpaper"""

import argparse
import sys
import time
import json
import pathlib

from waypaper.aboutdata import AboutData
from waypaper.app import App
from waypaper.changer import change_wallpaper
from waypaper.common import get_random_file
from waypaper.config import Config
from waypaper.options import BACKEND_OPTIONS, FILL_OPTIONS
from waypaper.translations import Chinese, English, French, German, Polish, Russian, Spanish

# Get application metadata.
about = AboutData()
# Get application settings.
cf = Config()

# Define the text language of the application based on the configuration.
if cf.lang == "de":
    txt = German()
elif cf.lang == "fr":
    txt = French()
elif cf.lang == "ru":
    txt = Russian()
elif cf.lang == "pl":
    txt = Polish()
elif cf.lang == "zh":
    txt = Chinese()
elif cf.lang == "es":
    txt = Spanish()
else:
    txt = English()


# Define command line argument parser.
parser = argparse.ArgumentParser(
    prog=about.applicationName(), description=txt.msg_desc, epilog=txt.msg_info
)
parser.add_argument("-v", "--version", help=txt.msg_arg_help, action="store_true")
parser.add_argument("--restore", help=txt.msg_arg_rest, action="store_true")
parser.add_argument("--random", help=txt.msg_arg_rand, action="store_true")
parser.add_argument("--fill", help=txt.msg_arg_fill, choices=FILL_OPTIONS)
parser.add_argument("--wallpaper", help=txt.msg_arg_wall)
parser.add_argument("--backend", help=txt.msg_arg_back, choices=BACKEND_OPTIONS)
parser.add_argument("--list", help=txt.msg_arg_list, action='store_true')
args = parser.parse_args()


def run():
    """Read user arguments and either run GUI app or just reset the wallpaper"""

    cf.read_parameters_from_user_arguments(args)

    # Set the wallpaper and quit:
    if args.restore or args.random:
        for wallpaper, monitor in zip(cf.wallpapers, cf.monitors):

            if args.random:
                wallpaper = get_random_file(cf.backend, cf.image_folder, cf.include_subfolders, cf.show_hidden)
                cf.selected_wallpaper = str(wallpaper)
                cf.save()

            if wallpaper is None:
                continue

            change_wallpaper(wallpaper, cf, monitor, txt)
            time.sleep(0.1)
        sys.exit(0)
    
    # Set wallpaper from user arguments:
    if args.wallpaper:
        monitor = "All"
        wallpaper = pathlib.Path(args.wallpaper).expanduser()
        change_wallpaper(wallpaper, cf, monitor, txt)

        # Save this wallpaper in config and quit:
        cf.selected_wallpaper = wallpaper
        cf.selected_monitor = monitor
        cf.save()
        sys.exit(0)

    # Output wallpapers and monitors in json format:
    if args.list:
        wallpapers_and_monitors = list(map(lambda x: {"monitor": x[0], "wallpaper": x[1]}, zip(cf.monitors,cf.wallpapers_str.split(','))))
        print(json.dumps(wallpapers_and_monitors))
        sys.exit(0)

    # Print the version and quit:
    if args.version:
        print(f"{about.applicationName()} v.{about.applicationVersion()}")
        sys.exit(0)

    # Start GUI:
    app = App(txt)
    app.run()


if __name__ == "__main__":
    run()

