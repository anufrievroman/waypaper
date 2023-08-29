"""Module that parses user arguments and returns them in args object"""

import argparse

from waypaper.options import FILL_OPTIONS, BACKEND_OPTIONS
from waypaper.translation_en import *


parser = argparse.ArgumentParser(prog = "waypaper", description = MSG_DESC, epilog = MSG_INFO)
parser.add_argument("-v", "--version", help=MSG_ARG_HELP, action="store_true")
parser.add_argument("--restore", help=MSG_ARG_REST, action="store_true")
parser.add_argument("--fill", help=MSG_ARG_FILL, choices=FILL_OPTIONS)
parser.add_argument("--backend", help=MSG_ARG_BACK, choices=BACKEND_OPTIONS)
args = parser.parse_args()
