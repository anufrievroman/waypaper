import gi
import configparser
from waypaper.config import Config

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

class Keys:
    def __init__(self, cf: Config) -> None:
        self.cf = cf
        self.clear_input_fields = [Gdk.keyval_from_name("Escape"), Gdk.keyval_from_name("Return"), Gdk.keyval_from_name("KP_Enter")]
        self.quit = [Gdk.keyval_from_name("q"), Gdk.keyval_from_name("Escape")]
        self.clear_cache = [Gdk.keyval_from_name("r")]
        self.random_wallpaper = [Gdk.keyval_from_name("R")]
        self.hidden_files = [Gdk.keyval_from_name("period")]
        self.search = [Gdk.keyval_from_name("slash")]
        self.include_subfolders = [Gdk.keyval_from_name("s")]
        self.navigation_left = [Gdk.keyval_from_name("h"), Gdk.keyval_from_name("Left")]
        self.navigation_down = [Gdk.keyval_from_name("j"), Gdk.keyval_from_name("Down")]
        self.navigation_up = [Gdk.keyval_from_name("k"), Gdk.keyval_from_name("Up")]
        self.navigation_right = [Gdk.keyval_from_name("l"), Gdk.keyval_from_name("Right")]
        self.choose_folder = [Gdk.keyval_from_name("f")]
        self.scroll_to_top = [Gdk.keyval_from_name("g")]
        self.zen_mode = [Gdk.keyval_from_name("z")]
        self.scroll_to_bottom = [Gdk.keyval_from_name("G")]
        self.help_page = [Gdk.keyval_from_name("question")]
        self.select_wallpaper = [Gdk.keyval_from_name("Return"), Gdk.keyval_from_name("KP_Enter")]
    
    def fill_keys_from_file(self, path):
        keybindings = configparser.ConfigParser()
        keybindings.read(self.cf.keybindings_file, 'utf-8')
        
        self.clear_input_fields = self.fill_out_keys(keybindings.get("Keybindings", "clear_input_fields", fallback=self.clear_input_fields))
        self.quit = self.fill_out_keys(keybindings.get("Keybindings", "quit", fallback=self.quit))
        self.clear_cache = self.fill_out_keys(keybindings.get("Keybindings", "clear_cache", fallback=self.clear_cache))
        self.random_wallpaper = self.fill_out_keys(keybindings.get("Keybindings", "random_wallpaper", fallback=self.random_wallpaper))
        self.hidden_files = self.fill_out_keys(keybindings.get("Keybindings", "hidden_files", fallback=self.hidden_files))
        self.search = self.fill_out_keys(keybindings.get("Keybindings", "search", fallback=self.search))
        self.include_subfolders = self.fill_out_keys(keybindings.get("Keybindings", "include_subfolders", fallback=self.include_subfolders))
        self.navigation_left = self.fill_out_keys(keybindings.get("Keybindings", "navigation_left", fallback=self.navigation_left))
        self.navigation_down = self.fill_out_keys(keybindings.get("Keybindings", "navigation_down", fallback=self.navigation_down))
        self.navigation_up = self.fill_out_keys(keybindings.get("Keybindings", "navigation_up", fallback=self.navigation_up))
        self.navigation_right = self.fill_out_keys(keybindings.get("Keybindings", "navigation_right", fallback=self.navigation_right))
        self.choose_folder = self.fill_out_keys(keybindings.get("Keybindings", "choose_folder", fallback=self.choose_folder))
        self.scroll_to_top = self.fill_out_keys(keybindings.get("Keybindings", "scroll_to_top", fallback=self.scroll_to_top))
        self.zen_mode = self.fill_out_keys(keybindings.get("Keybindings", "zen_mode", fallback=self.zen_mode))
        self.scroll_to_bottom = self.fill_out_keys(keybindings.get("Keybindings", "scroll_to_bottom", fallback=self.scroll_to_bottom))
        self.help_page = self.fill_out_keys(keybindings.get("Keybindings", "help_page", fallback=self.help_page))
        self.select_wallpaper = self.fill_out_keys(keybindings.get("Keybindings", "select_wallpaper", fallback=self.select_wallpaper))
    
    def fill_out_keys(self, keys):
        if type(keys) is list:
            return keys
        else:
            result_keycodes = []
            for key in keys.split(', '):
                result_keycodes.append(Gdk.keyval_from_name(key))
            return result_keycodes