"""Main module that runs the program and either runs GUI or just changer wallpaper"""

import time
import argparse


from waypaper.config import Config
from waypaper.app import App
from waypaper.changer import change_wallpaper
from waypaper.common import get_random_file
from waypaper.aboutdata import AboutData
from waypaper.options import FILL_OPTIONS, BACKEND_OPTIONS
from waypaper.translations import English, German, French, Russian, Polish, Chinese

about = AboutData()
cf = Config()

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
else:
    txt = English()


parser = argparse.ArgumentParser(prog = about.applicationName(), description = txt.msg_desc,
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
            change_wallpaper(wallpaper, cf.fill_option, cf.color, cf.backend, monitor, cf.swww_transition, txt)
            time.sleep(0.1)
        exit(0)

    # Print the version and quit:
    if args.version:
        print(f"{about.applicationName()} v.{about.applicationVersion()}")
        exit(0)

    # Start GUI:
    app = App(txt)
    app.run()


if __name__ == "__main__":
    run()
