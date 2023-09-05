"""Module responsible for taking care of configuration file"""

import configparser
import pathlib
import os

from waypaper.arguments import args
from waypaper.options import FILL_OPTIONS, SORT_OPTIONS


class Config:
    """User configuration loaded from the config.ini file"""
    def __init__(self):
        self.image_folder = str(pathlib.Path.home())
        if os.path.exists(str(pathlib.Path.home()) + "/Pictures"):
            self.image_folder = str(pathlib.Path.home()) + "/Pictures"
        self.selected_wallpaper = None
        self.selected_monitor = "All"
        self.fill_option = "fill"
        self.sort_option = "name"
        self.backend = "swaybg"
        self.color = "#ffffff"
        self.monitors = [self.selected_monitor]
        self.wallpaper = []
        self.include_subfolders = False
        self.config_folder = str(pathlib.Path.home()) + "/.config/waypaper"
        self.config_file = self.config_folder + "/config.ini"


    def create(self):
        """Create a default config.ini file if it does not exist"""
        config = configparser.ConfigParser()
        config["Settings"] = {
                "folder": str(self.image_folder),
                "fill": str(self.fill_option),
                "sort": str(self.sort_option),
                "backend": str(self.backend),
                "color": str(self.color),
                "subfolders": str(self.include_subfolders),
                "wallpaper": str(self.selected_wallpaper),
                "monitors": str(self.selected_monitor),
                }
        with open(cf.config_file, "w") as configfile:
            config.write(configfile)


    def read(self):
        """Load data from the config.ini or use default if it does not exists"""
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file, 'utf-8')
            self.image_folder = config.get("Settings", "folder", fallback=self.image_folder)
            self.fill_option = config.get("Settings", "fill", fallback=self.fill_option)
            if self.fill_option not in FILL_OPTIONS:
                self.sort_option = FILL_OPTIONS[0]
            self.sort_option = config.get("Settings", "sort", fallback=self.sort_option)
            if self.sort_option not in SORT_OPTIONS:
                self.sort_option = SORT_OPTIONS[0]
            self.backend = config.get("Settings", "backend", fallback=self.backend)
            self.color  = config.get("Settings", "color", fallback=self.color)
            self.include_subfolders = config.getboolean("Settings", "subfolders", fallback=self.include_subfolders)

            self.monitors_str = config.get("Settings", "monitors", fallback=self.selected_monitor, raw=True)
            if self.monitors_str is not None:
                self.monitors = [str(monitor) for monitor in self.monitors_str.split(",")]

            self.wallpaper_str = config.get("Settings", "wallpaper", fallback=self.wallpaper, raw=True)
            if self.wallpaper_str is not None:
                self.wallpaper = [str(paper) for paper in self.wallpaper_str.split(",")]
        except Exception as e:
            print(e)
            exit()


    def save(self):
        """Update the parameters and save them to the configuration file"""

        # If only certain monitor was affected, change only its wallpaper:
        if self.selected_monitor == "All":
            self.monitors = [self.selected_monitor]
            self.wallpaper = [self.selected_wallpaper]
        elif self.selected_monitor in self.monitors:
            index = self.monitors.index(self.selected_monitor)
            self.wallpaper[index] = self.selected_wallpaper
        else:
            self.monitors.append(self.selected_monitor)
            self.wallpaper.append(self.selected_wallpaper)

        # Write configuration to the file:
        config = configparser.ConfigParser()
        config.read(self.config_file)
        config.set("Settings", "folder", cf.image_folder)
        config.set("Settings", "fill", cf.fill_option)
        config.set("Settings", "sort", cf.sort_option)
        config.set("Settings", "backend", cf.backend)
        config.set("Settings", "color", cf.color)
        config.set("Settings", "subfolders", str(cf.include_subfolders))
        config.set("Settings", "wallpaper", ",".join(self.wallpaper))
        config.set("Settings", "monitors", ",".join(self.monitors))
        with open(cf.config_file, "w") as configfile:
            config.write(configfile)


    def read_parameters_from_user_arguments(self):
        """Read user arguments provided at the run. These values take priority over config.ini"""
        if args.backend:
            self.backend = args.backend
        if args.fill:
            self.fill_option = args.fill


cf = Config()

# Create config folder:
if not os.path.exists(cf.config_folder):
    os.makedirs(cf.config_folder)

# Create cache folder:
if not os.path.exists(f"{cf.config_folder}/.cache"):
    os.makedirs(f"{cf.config_folder}/.cache")

# Create config file:
if not os.path.exists(cf.config_file):
    cf.create()

# Read config file:
cf.read()
cf.read_parameters_from_user_arguments()
