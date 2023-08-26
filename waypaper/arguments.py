"""Module that parses user arguments and returns them in args object"""

import argparse

from waypaper.options import FILL_OPTIONS, BACKEND_OPTIONS

parser = argparse.ArgumentParser(
                prog = 'waypaper',
                description = 'GUI wallpaper setter for Wayland and X11. It works as a frontend for feh, swaybg, wallutils, and swww.',
                epilog = 'For more information, visit: https://github.com/anufrievroman/waypaper')

parser.add_argument("-v", "--version", help="print version of the program", action="store_true")
parser.add_argument("--restore", help="restore last wallpaper.", action="store_true")
parser.add_argument("--fill", help="specify how to fill the screen with chosen image.", choices=FILL_OPTIONS)
parser.add_argument("--backend", help="specify which backend to use to set wallpaper.", choices=BACKEND_OPTIONS)

args = parser.parse_args()
