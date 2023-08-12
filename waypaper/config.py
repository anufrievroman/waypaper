"""Module responsible for taking care of configuration file"""

import configparser
import pathlib
import getopt
import sys
import os

from waypaper.options import FILL_OPTIONS, BACKEND_OPTIONS
from waypaper.arguments import args


class Config:
    """User configuration loaded from the config.ini file"""
    def __init__(self):
        self.image_folder = str(pathlib.Path.home())
        if os.path.exists(str(pathlib.Path.home()) + "/Pictures"):
            self.image_folder = str(pathlib.Path.home()) + "/Pictures"
        self.wallpaper = None
        self.fill_option = "fill"
        self.backend = "swaybg"
        self.color = "#ffffff"
        self.include_subfolders = False
        self.config_folder  = str(pathlib.Path.home()) + "/.config/waypaper"
        self.config_file  = self.config_folder + "/config.ini"


    def create(self):
        """Create a default config.ini file if it does not exist"""
        config = configparser.ConfigParser()
        config["Settings"] = {
                "folder": str(self.image_folder),
                "fill": str(self.fill_option),
                "backend": str(self.backend),
                "color": str(self.color),
                "subfolders": str(self.include_subfolders),
                "wallpaper": str(self.wallpaper),
                }
        with open(cf.config_file, "w") as configfile:
            config.write(configfile)


    def read(self):
        """Load data from the config.ini or use default if it does not exists"""
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file, 'utf-8')
            self.image_folder = config.get("Settings", "folder", fallback=self.image_folder)
            self.wallpaper = config.get("Settings", "wallpaper", fallback=self.wallpaper)
            self.fill_option = config.get("Settings", "fill", fallback=self.fill_option)
            self.backend = config.get("Settings", "backend", fallback=self.backend)
            self.color  = config.get("Settings", "color", fallback=self.color)
            self.include_subfolders = config.getboolean("Settings", "subfolders", fallback=self.include_subfolders)
        except Exception as e:
            print(e)
            exit()


    def save(self):
        """Save the parameters to the configuration file"""
        config = configparser.ConfigParser()
        config.read(self.config_file)
        config.set("Settings", "folder", cf.image_folder)
        config.set("Settings", "wallpaper", cf.wallpaper)
        config.set("Settings", "fill", cf.fill_option)
        config.set("Settings", "backend", cf.backend)
        config.set("Settings", "color", cf.color)
        config.set("Settings", "subfolders", str(cf.include_subfolders))
        with open(cf.config_file, "w") as configfile:
            config.write(configfile)


    def read_parameters_from_user_arguments(self):
        """Read user arguments that were provided at the run. These values take priority over config.ini"""
        if args.backend:
            self.backend = args.backend
        if args.fill:
            self.fill_option = args.fill


cf = Config()

# Create config folder:
if not os.path.exists(cf.config_folder):
    os.makedirs(cf.config_folder)

# Create config file:
if not os.path.exists(cf.config_file):
    cf.create()

# Read config file:
cf.read()
cf.read_parameters_from_user_arguments()
