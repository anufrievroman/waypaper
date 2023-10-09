"""Module that parses user arguments and returns them in args object"""

import argparse

from waypaper.options import FILL_OPTIONS, BACKEND_OPTIONS
from waypaper.config import cf

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


parser = argparse.ArgumentParser(prog = "waypaper", description = MSG_DESC, epilog = MSG_INFO)
parser.add_argument("-v", "--version", help=MSG_ARG_HELP, action="store_true")
parser.add_argument("--restore", help=MSG_ARG_REST, action="store_true")
parser.add_argument("--random", help=MSG_ARG_RAND, action="store_true")
parser.add_argument("--fill", help=MSG_ARG_FILL, action="store_true")
parser.add_argument("--backend", help=MSG_ARG_BACK, choices=BACKEND_OPTIONS)
args = parser.parse_args()
