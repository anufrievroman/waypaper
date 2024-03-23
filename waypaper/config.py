"""Module responsible for reading and saving the configuration file"""

import configparser
import pathlib
import os
from sys import exit
from platformdirs import user_config_path, user_pictures_path, user_cache_path

from waypaper.aboutdata import AboutData
from waypaper.options import FILL_OPTIONS, SORT_OPTIONS, SWWW_TRANSITION_TYPES, BACKEND_OPTIONS
from waypaper.common import check_installed_backends


class Config:
    """User configuration loaded from the config.ini file"""
    def __init__(self):
        self.image_folder = user_pictures_path()
        self.installed_backends = check_installed_backends()
        self.selected_wallpaper = ""
        self.selected_monitor = "All"
        self.fill_option = FILL_OPTIONS[0]
        self.sort_option = SORT_OPTIONS[0]
        self.backend = self.installed_backends[0] if self.installed_backends else BACKEND_OPTIONS[0]
        self.color = "#ffffff"
        self.swww_transition_type = SWWW_TRANSITION_TYPES[0]
        self.swww_transition_step = 90
        self.swww_transition_angle = 0
        self.swww_transition_duration = 2
        self.lang = "en"
        self.monitors = [self.selected_monitor]
        self.wallpapers = []
        self.post_command = ""
        self.include_subfolders = False
        self.show_hidden = False
        self.about = AboutData()
        self.cache_dir = user_cache_path(self.about.applicationName())
        self.config_dir = user_config_path(self.about.applicationName())
        self.config_file = self.config_dir / "config.ini"

        # Create config and cache folders:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True,exist_ok=True)

        self.read()
        self.check_validity()


    def read(self):
        """Load data from the config.ini or use default if it does not exists"""
        config = configparser.ConfigParser()
        config.read(self.config_file, 'utf-8')

        # Read parameters:
        self.image_folder = config.get("Settings", "folder", fallback=self.image_folder)
        self.fill_option = config.get("Settings", "fill", fallback=self.fill_option)
        self.sort_option = config.get("Settings", "sort", fallback=self.sort_option)
        self.backend = config.get("Settings", "backend", fallback=self.backend)
        self.color = config.get("Settings", "color", fallback=self.color)
        self.post_command = config.get("Settings", "post_command", fallback=self.post_command)
        self.swww_transition_type = config.get("Settings", "swww_transition_type", fallback=self.swww_transition_type)
        self.swww_transition_step = config.get("Settings", "swww_transition_step", fallback=self.swww_transition_step)
        self.swww_transition_angle = config.get("Settings", "swww_transition_angle", fallback=self.swww_transition_angle)
        self.swww_transition_duration = config.get("Settings", "swww_transition_duration", fallback=self.swww_transition_duration)
        self.lang = config.get("Settings", "language", fallback=self.lang)
        self.include_subfolders = config.getboolean("Settings", "subfolders", fallback=self.include_subfolders)
        self.show_hidden = config.getboolean("Settings", "show_hidden", fallback=self.show_hidden)
        self.monitors_str = config.get("Settings", "monitors", fallback=self.selected_monitor, raw=True)
        self.wallpapers_str = config.get("Settings", "wallpaper", fallback="", raw=True)

        # Convert strings to lists:
        if self.monitors_str is not None:
            self.monitors = [str(monitor) for monitor in self.monitors_str.split(",")]
        if self.wallpapers_str is not None:
            self.wallpapers = [str(paper) for paper in self.wallpapers_str.split(",")]

    def check_validity(self):
        """Check if the config parameters are valid and correct them if needed"""
        if self.backend not in BACKEND_OPTIONS:
            self.backend = self.installed_backends[0] if self.installed_backends else BACKEND_OPTIONS[0]
        if self.sort_option not in SORT_OPTIONS:
            self.sort_option = SORT_OPTIONS[0]
        if self.fill_option not in FILL_OPTIONS:
            self.fill_option = FILL_OPTIONS[0]
        if self.swww_transition_type not in SWWW_TRANSITION_TYPES:
            self.swww_transition_type = "any"

        if 0 > int(self.swww_transition_angle) > 180:
            self.swww_transition_angle = 0
        if 0 > int(self.swww_transition_step) > 255:
            self.swww_transition_step = 90
        if 0 > int(self.swww_transition_duration):
            self.swww_transition_duration = 2

    def save(self):
        """Update the parameters and save them to the configuration file"""

        # If only certain monitor was affected, change only its wallpaper:
        if self.selected_monitor == "All":
            self.monitors = [self.selected_monitor]
            self.wallpapers = [self.selected_wallpaper]
        elif self.selected_monitor in self.monitors:
            index = self.monitors.index(self.selected_monitor)
            self.wallpapers[index] = self.selected_wallpaper
        else:
            self.monitors.append(self.selected_monitor)
            self.wallpapers.append(self.selected_wallpaper)

        # Write configuration to the file:
        config = configparser.ConfigParser()
        config.read(self.config_file)
        if not config.has_section("Settings"):
            config.add_section("Settings")
        config.set("Settings", "language", self.lang)
        config.set("Settings", "folder", self.image_folder)
        config.set("Settings", "wallpaper", ",".join(self.wallpapers))
        config.set("Settings", "backend", self.backend)
        config.set("Settings", "monitors", ",".join(self.monitors))
        config.set("Settings", "fill", self.fill_option)
        config.set("Settings", "sort", self.sort_option)
        config.set("Settings", "color", self.color)
        config.set("Settings", "subfolders", str(self.include_subfolders))
        config.set("Settings", "show_hidden", str(self.show_hidden))
        config.set("Settings", "post_command", self.post_command)
        config.set("Settings", "swww_transition_type", str(self.swww_transition_type))
        config.set("Settings", "swww_transition_step", str(self.swww_transition_step))
        config.set("Settings", "swww_transition_angle", str(self.swww_transition_angle))
        config.set("Settings", "swww_transition_duration", str(self.swww_transition_duration))
        with open(self.config_file, "w") as configfile:
            config.write(configfile)


    def read_parameters_from_user_arguments(self, args):
        """Read user arguments provided at the run. These values take priority over config.ini"""
        if args.backend:
            self.backend = args.backend
        if args.fill:
            self.fill_option = args.fill

