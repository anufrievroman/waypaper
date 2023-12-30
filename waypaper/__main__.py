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
    from waypaper.translations import German as txt
elif cf.lang == "fr":
    from waypaper.translations import French as txt
elif cf.lang == "ru":
    from waypaper.translations import Russian as txt
elif cf.lang == "pl":
    from waypaper.translations import Polish as txt
elif cf.lang == "zh":
    from waypaper.translations import Chinese as txt
else:
    from waypaper.translations import English as txt


parser = argparse.ArgumentParser(prog = aboutData.applicationName(), description = txt.msg_desc,
                                 epilog = txt.msg_info)
parser.add_argument("-v", "--version", help=txt.msg_arg_help, action="store_true")
parser.add_argument("--restore", help=txt.msg_arg_rest, action="store_true")
parser.add_argument("--random", help=txt.msg_arg_rand, action="store_true")
parser.add_argument("--fill", help=txt.msg_arg_fill, action="store_true")
parser.add_argument("--backend", help=txt.msg_arg_back, choices=BACKEND_OPTIONS)
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
            change_wallpaper(wallpaper, cf.fill_option, cf.color, cf.backend, monitor, txt)
            time.sleep(0.1)
        exit(0)

    # Print the version and quit:
    if args.version:
        print(f"{aboutData.applicationName()} v.{aboutData.applicationVersion()}")
        exit(0)

    # Start GUI:
    app = App(txt)
    app.run()


if __name__ == "__main__":
    run()
