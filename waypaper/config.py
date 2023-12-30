"""Module responsible for taking care of configuration file"""

import configparser
import pathlib
import os
from sys import exit
from platformdirs import user_config_path, user_pictures_path, user_cache_path

from waypaper.aboutdata import AboutData
from waypaper.options import FILL_OPTIONS, SORT_OPTIONS

class Config:
    """User configuration loaded from the config.ini file"""
    def __init__(self):
        self.image_folder = user_pictures_path()
        self.selected_wallpaper = ""
        self.selected_monitor = "All"
        self.fill_option = "fill"
        self.sort_option = "name"
        self.backend = "swaybg"
        self.color = "#ffffff"
        self.lang = "en"
        self.monitors = [self.selected_monitor]
        self.wallpaper = []
        self.include_subfolders = False
        self.aboutData = AboutData()
        self.cachePath = user_cache_path(self.aboutData.applicationName())
        self.configPath = user_config_path(self.aboutData.applicationName())
        self.config_file = self.configPath / "config.ini"

        # Create config and cache folders:
        self.configPath.mkdir(parents=True, exist_ok=True)
        self.cachePath.mkdir(parents=True,exist_ok=True)

        self.read()


    def read(self):
        """Load data from the config.ini or use default if it does not exists"""
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
        self.color = config.get("Settings", "color", fallback=self.color)
        self.lang = config.get("Settings", "language", fallback=self.lang)
        self.include_subfolders = config.getboolean("Settings", "subfolders", fallback=self.include_subfolders)

        self.monitors_str = config.get("Settings", "monitors", fallback=self.selected_monitor, raw=True)
        if self.monitors_str is not None:
            self.monitors = [str(monitor) for monitor in self.monitors_str.split(",")]

        self.wallpaper_str = config.get("Settings", "wallpaper", fallback="", raw=True)
        if self.wallpaper_str is not None:
            self.wallpaper = [str(paper) for paper in self.wallpaper_str.split(",")]


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
        if not config.has_section("Settings"):
            config.add_section("Settings")
        config.set("Settings", "folder", self.image_folder)
        config.set("Settings", "fill", self.fill_option)
        config.set("Settings", "sort", self.sort_option)
        config.set("Settings", "backend", self.backend)
        config.set("Settings", "color", self.color)
        config.set("Settings", "language", self.lang)
        config.set("Settings", "subfolders", str(self.include_subfolders))
        config.set("Settings", "wallpaper", ",".join(self.wallpaper))
        config.set("Settings", "monitors", ",".join(self.monitors))
        with open(self.config_file, "w") as configfile:
            config.write(configfile)


    def read_parameters_from_user_arguments(self, args):
        """Read user arguments provided at the run. These values take priority over config.ini"""
        if args.backend:
            self.backend = args.backend
        if args.fill:
            self.fill_option = args.fill

