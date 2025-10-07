import gi
from waypaper.config import Config

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

class Keys:
    def __init__(self, cf: Config) -> None:
        self.cf = cf
        self.KEYS = {
            "clear_input_fields" : ["Escape", "Return", "KP_Enter"],
            "quit" : ["q", "Escape"],
            "clear_cache" : ["r"],
            "random_wallpaper" : ["R"],
            "hidden_files" : ["period"],
            "search" : ["slash"],
            "include_subfolders" : ["s"],
            "navigation_left" : ["h", "Left"],
            "navigation_down" : ["j", "Down"],
            "navigation_up" : ["k", "Up"],
            "navigation_right" : ["l", "Right"],
            "choose_folder" : ["f"],
            "scroll_to_top" : ["g"],
            "zen_mode" : ["z"],
            "scroll_to_bottom" : ["G"],
            "help_page" : ["question"],
            "select_wallpaper" : ["Enter", "KP_Enter"]
        }
    
    def fill_keys_from_file(self, path):
        keybinds = ""
        result = {}
        try:
            with open(path, 'r') as keybindings:
                for line in keybindings:
                    if "[" not in line:
                        line = line.strip()
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().split(',')
                        for i in range(len(value)):
                            value[i] = value[i].strip(" ")
                        result[key] = value
            for situation in result:
                if situation in self.KEYS:
                    self.KEYS[situation] = result[situation]
        except OSError:
            pass
    
    def fill_out_keys(self, situation):
        result_keys = []
        for i in range(len(self.KEYS[situation])):
            result_keys.append(Gdk.keyval_from_name(self.KEYS[situation][i]))
        return result_keys
    
    def clear_input_fields(self):
        return self.fill_out_keys("clear_input_fields")

    def quit(self):
        return self.fill_out_keys("quit")
    
    def clear_cache(self):
        return self.fill_out_keys("clear_cache")
    
    def reload_wallpaers(self):
        return self.fill_out_keys("reload_wallpaers")

    def random_wallpaper(self):
        return self.fill_out_keys("random_wallpaper")

    def hidden_files(self):
        return self.fill_out_keys("hidden_files")

    def search(self):
        return self.fill_out_keys("search")

    def include_subfolders(self):
        return self.fill_out_keys("include_subfolders")

    def navigation_left(self):
        return self.fill_out_keys("navigation_left")

    def navigation_down(self):
        return self.fill_out_keys("navigation_down")

    def navigation_up(self):
        return self.fill_out_keys("navigation_up")
    
    def navigation_right(self):
        return self.fill_out_keys("navigation_right")
    
    def choose_folder(self):
        return self.fill_out_keys("choose_folder")
    
    def scroll_to_top(self):
        return self.fill_out_keys("scroll_to_top")
    
    def zen_mode(self):
        return self.fill_out_keys("zen_mode")
    
    def scroll_to_bottom(self):
        return self.fill_out_keys("scroll_to_bottom")
    
    def help_page(self):
        return self.fill_out_keys("help_page")
    
    def select_wallpaper(self):
        return self.fill_out_keys("select_wallpaper")