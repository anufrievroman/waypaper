"""Module responsible for reading and saving the configuration and state files"""

import configparser
import pathlib
from argparse import Namespace
from typing import List
from platformdirs import user_config_path, user_pictures_path, user_cache_path, user_state_path

from waypaper.options import FILL_OPTIONS, SORT_OPTIONS, SWWW_TRANSITION_TYPES, BACKEND_OPTIONS
from waypaper.common import check_installed_backends


class Config:
    """User configuration loaded from the config.ini file"""
    def __init__(self):
        # All paths (folders or wallpapers) are Path objects
        self.name = "waypaper"
        self.home_path = pathlib.Path.home()
        self.image_folder_list: list[pathlib.Path] = []
        self.image_folder_fallback: str = str(user_pictures_path())
        self.installed_backends = check_installed_backends()
        self.selected_wallpaper = None
        self.selected_monitor = "All"
        self.fill_option = FILL_OPTIONS[0]
        self.sort_option = SORT_OPTIONS[0]
        self.backend = self.installed_backends[-1]
        self.color = "#ffffff"
        self.number_of_columns = 3
        self.swww_transition_type = SWWW_TRANSITION_TYPES[0]
        self.swww_transition_step = 90
        self.swww_transition_angle = 0
        self.swww_transition_duration = 2
        self.swww_transition_fps = 60
        self.mpvpaper_sound = False
        self.mpvpaper_options = ""
        self.lang = "en"
        self.monitors = [self.selected_monitor]
        self.wallpapers = []
        self.post_command = ""
        self.include_subfolders = False
        self.include_all_subfolders = False
        self.show_hidden = False
        self.show_gifs_only = False
        self.zen_mode = False
        self.cache_dir = user_cache_path(self.name)
        self.config_dir = user_config_path(self.name)
        self.config_file = self.config_dir / "config.ini"
        self.state_dir = user_state_path(self.name)
        self.state_file = self.state_dir / "state.ini"
        self.use_xdg_state = False
        self.use_post_command = True
        self.show_path_in_tooltip = True

        # Create config and cache folders:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)


    def select_wallpaper(self, path_str: str) -> None:
        self.selected_wallpaper = pathlib.Path(path_str)


    def shorten_path(self, path: pathlib.Path) -> str:
        """Replace home part of paths with tilde"""
        if path.is_relative_to(self.home_path):
            return str(path).replace(str(self.home_path), "~", 1)
        elif path:
            return str(path)
        else:
            return ''


    def get_image_folder_list(self, section: str, config) -> list[pathlib.Path]:
        image_folders_str: list[str] =  config.get(section, "folder", fallback = self.image_folder_fallback).split("\n")
        image_folder_list = [pathlib.Path(path_str).expanduser() for path_str in image_folders_str]
        return image_folder_list


    def read(self) -> None:
        """Load data from the config.ini or use default if it does not exists"""
        config = configparser.ConfigParser()
        config.read(self.config_file, 'utf-8')

        # Read basic parameters:
        self.fill_option = config.get("Settings", "fill", fallback=self.fill_option)
        self.sort_option = config.get("Settings", "sort", fallback=self.sort_option)
        self.backend = config.get("Settings", "backend", fallback=self.backend)
        self.color = config.get("Settings", "color", fallback=self.color)
        self.post_command = config.get("Settings", "post_command", fallback=self.post_command)
        self.swww_transition_type = config.get("Settings", "swww_transition_type", fallback=self.swww_transition_type)
        self.swww_transition_step = config.get("Settings", "swww_transition_step", fallback=self.swww_transition_step)
        self.swww_transition_angle = config.get("Settings", "swww_transition_angle", fallback=self.swww_transition_angle)
        self.swww_transition_duration = config.get("Settings", "swww_transition_duration", fallback=self.swww_transition_duration)
        self.swww_transition_fps = config.get("Settings", "swww_transition_fps", fallback=self.swww_transition_fps)
        self.mpvpaper_sound = config.getboolean("Settings", "mpvpaper_sound", fallback=self.mpvpaper_sound)
        self.mpvpaper_options = config.get("Settings", "mpvpaper_options", fallback=self.mpvpaper_options)
        self.number_of_columns = int(config.get("Settings", "number_of_columns", fallback=self.number_of_columns))
        self.lang = config.get("Settings", "language", fallback=self.lang)
        self.include_subfolders = config.getboolean("Settings", "subfolders", fallback=self.include_subfolders)
        self.include_all_subfolders = config.getboolean("Settings", "all_subfolders", fallback=self.include_all_subfolders)
        self.show_hidden = config.getboolean("Settings", "show_hidden", fallback=self.show_hidden)
        self.show_gifs_only = config.getboolean("Settings", "show_gifs_only", fallback=self.show_gifs_only)
        self.zen_mode = config.getboolean("Settings", "zen_mode", fallback=self.zen_mode)
        self.use_xdg_state = config.getboolean("Settings", "use_xdg_state", fallback=self.use_xdg_state)
        self.show_path_in_tooltip = config.getboolean("Settings", "show_path_in_tooltip", fallback=self.show_path_in_tooltip)

        # Read and convert strings representing lists and paths:
        monitors_str = config.get("Settings", "monitors", fallback=self.selected_monitor, raw=True)
        wallpapers_str = config.get("Settings", "wallpaper", fallback="", raw=True)
        self.image_folder_list = self.get_image_folder_list("Settings", config)
        if monitors_str:
            self.monitors = [str(monitor) for monitor in monitors_str.split(",")]
        if wallpapers_str:
            self.wallpapers = [pathlib.Path(paper).expanduser() for paper in wallpapers_str.split(",")]


    def read_state(self) -> None:
        """Load data from the state.ini file"""
        if not self.use_xdg_state:
            return

        state = configparser.ConfigParser()
        state.read(self.state_file, 'utf-8')

        # Read and convert strings representing lists and paths:
        monitors_str = state.get("State", "monitors", fallback=self.selected_monitor, raw=True)
        wallpapers_str = state.get("State", "wallpaper", fallback="", raw=True)
        self.image_folder_list = self.get_image_folder_list("State", state)
        if monitors_str:
            self.monitors = [str(monitor) for monitor in monitors_str.split(",")]
            self.selected_monitor = self.monitors[0]
        if wallpapers_str:
            self.wallpapers = [pathlib.Path(paper).expanduser() for paper in wallpapers_str.split(",")]


    def check_validity(self) -> None:
        """Check if the config parameters are valid and correct them if needed"""

        # Check validity of general options:
        if self.backend not in BACKEND_OPTIONS:
            self.backend = self.installed_backends[-1]
        if self.sort_option not in SORT_OPTIONS:
            self.sort_option = SORT_OPTIONS[0]
        if self.fill_option not in FILL_OPTIONS:
            self.fill_option = FILL_OPTIONS[0]
        if self.swww_transition_type not in SWWW_TRANSITION_TYPES:
            self.swww_transition_type = "any"
        if self.number_of_columns <= 0:
            self.number_of_columns = 1

        # Check validity of other swww options:
        if 0 > int(self.swww_transition_angle) > 180:
            self.swww_transition_angle = 0
        if 0 > int(self.swww_transition_step) > 255:
            self.swww_transition_step = 90
        if 0 > float(self.swww_transition_duration):
            self.swww_transition_duration = 2
        if 0 > int(self.swww_transition_fps):
            self.swww_transition_fps = 60


    def attribute_selected_wallpaper(self) -> None:
        """
        This function is used before saving config to attribute a wallpaper to a monitor.
        For example, if only certain monitor was affected,
        change only corresponding wallpaper in the wallpapers list.
        Otherwise, reset the list and set one wallpaper for all monitors.
        """
        if not self.selected_wallpaper:
            return
        if self.selected_monitor == "All":
            self.monitors = [self.selected_monitor]
            self.wallpapers = [self.selected_wallpaper]
        elif self.selected_monitor in self.monitors:
            index = self.monitors.index(self.selected_monitor)
            self.wallpapers[index] = self.selected_wallpaper
        else:
            self.monitors.append(self.selected_monitor)
            self.wallpapers.append(self.selected_wallpaper)


    def save_state_file(self) -> None:
        """Save some parameters to the state file"""
        state = configparser.ConfigParser()
        state.read(self.state_file)
        if not state.has_section("State"):
            state.add_section("State")
        self.write_folder_list_to_config("State", state)
        state.set("State", "monitors", ",".join(self.monitors))
        state.set("State", "wallpaper", ','.join(self.shorten_path(p) for p in self.wallpapers))
        try:
            with open(self.state_file, "w") as statefile:
                state.write(statefile)
        except PermissionError:
            print("Could not save state file due to permission error.")


    def write_folder_list_to_config(self, section: str, config):
        config_save_folder_str = ""
        for i, folder in enumerate(self.image_folder_list):
            if i == 0:
                config_save_folder_str += self.shorten_path(folder)
            else:
                config_save_folder_str += "\n     " + self.shorten_path(folder)
        config.set(section, "folder", config_save_folder_str)


    def save(self, only_state=False) -> None:
        """Save current parameters to the configuration file"""

        # Write configuration to the file:
        config = configparser.ConfigParser()
        config.read(self.config_file)
        if not config.has_section("Settings"):
            config.add_section("Settings")
        config.set("Settings", "language", self.lang)

        # If state file is used, some parameters are not save into config:
        if not self.use_xdg_state:
            self.write_folder_list_to_config("Settings", config)
            config.set("Settings", "monitors", ",".join(self.monitors))
            config.set("Settings", "wallpaper", ','.join(self.shorten_path(p) for p in self.wallpapers))

        # Save the parameters into config:
        config.set("Settings", "show_path_in_tooltip", str(self.show_path_in_tooltip))
        config.set("Settings", "backend", self.backend)
        config.set("Settings", "fill", self.fill_option)
        config.set("Settings", "sort", self.sort_option)
        config.set("Settings", "color", self.color)
        config.set("Settings", "subfolders", str(self.include_subfolders))
        config.set("Settings", "all_subfolders", str(self.include_all_subfolders))
        config.set("Settings", "show_hidden", str(self.show_hidden))
        config.set("Settings", "show_gifs_only", str(self.show_gifs_only))
        config.set("Settings", "zen_mode", str(self.zen_mode))
        config.set("Settings", "post_command", self.post_command)
        config.set("Settings", "number_of_columns", str(self.number_of_columns))
        config.set("Settings", "swww_transition_type", str(self.swww_transition_type))
        config.set("Settings", "swww_transition_step", str(self.swww_transition_step))
        config.set("Settings", "swww_transition_angle", str(self.swww_transition_angle))
        config.set("Settings", "swww_transition_duration", str(self.swww_transition_duration))
        config.set("Settings", "swww_transition_fps", str(self.swww_transition_fps))
        config.set("Settings", "mpvpaper_sound", str(self.mpvpaper_sound))
        config.set("Settings", "mpvpaper_options", str(self.mpvpaper_options))
        config.set("Settings", "use_xdg_state", str(self.use_xdg_state))

        try:
            with open(self.config_file, "w") as configfile:
                config.write(configfile)
        except PermissionError:
            print("Could not save config file due to permission error.")

        # If requested, save the state file:
        if self.use_xdg_state:
            self.save_state_file()


    def read_parameters_from_user_arguments(self, args: Namespace) -> None:
        """
        Read user arguments provided at the run. These values take priority over config.ini
        :param args Output of the argparse parser.parse_args() method. Should be only used in __main__.py.
        """
        if args.backend:
            self.backend = args.backend
        if args.fill:
            self.fill_option = args.fill
        if args.folder:
            self.image_folder_list = [pathlib.Path(path_str) for path_str in args.folder]
        if args.state_file:
            self.use_xdg_state = True # Use of a custom state file implies state is in a separate file, requires use_xdg_state
            self.state_file = pathlib.Path(args.state_file).expanduser()
        if args.no_post_command:
            self.use_post_command = False
