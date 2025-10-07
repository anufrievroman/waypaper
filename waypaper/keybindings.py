import gi

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

class keys:
    def __init__(self):
        self.KEYS = {
            "clear_input_fields" : ["Escape", "Return", "KP_Enter"],
            "quit" : ["q", "Escape"],
            "reload_wallpaers" : "r",
            "random_wallpaper" : "R",
            "toggle_hidden_files" : "period",
            "search" : "slash",
            "toggle_include_subfolders" : "s",
            "navigation_left" : ["h", "Left"],
            "navigation_down" : ["j", "Down"],
            "navigation_up" : ["k", "Up"],
            "navigation_right" : ["l", "Right"],
            "choose_folder" : "f",
            "scroll_to_the_top" : "g",
            "zen_mode" : "z",
            "scroll_to_the_bottom" : "G",
            "help_page" : "question",
            "select_wallpaper" : ["Enter", "KP_Enter"]
        }
    
    def fill_out_keys(self, situation):
        result_keys = []
        for i in range(len(self.KEYS[situation])):
            result_keys.append(Gdk.keyval_from_name(self.KEYS[situation][i]))
        return result_keys
    
    def clear_input_fields(self):
        return fill_out_keys("clear_input_fields")

    def quit(self):
        return fill_out_keys("quit")
    
    def clear_cache(self):
        return fill_out_keys("clear_cache")
    
    def reload_wallpaers(self):
        return fill_out_keys("reload_wallpaers")

    def random_wallpaper(self):
        return fill_out_keys("random_wallpaper")

    def toggle_hidden_files(self):
        return fill_out_keys("toggle_hidden_files")

    def search(self):
        return fill_out_keys("search")

    def toggle_include_subfolders(self):
        return fill_out_keys("toggle_include_subfolders")

    def navigation_left(self):
        return fill_out_keys("navigation_left")

    def navigation_down(self):
        return fill_out_keys("navigation_down")

    def navigation_up(self):
        return fill_out_keys("navigation_up")
    
    def navigation_right(self):
        return fill_out_keys("navigation_right")
    
    def choose_folder(self):
        return fill_out_keys("choose_folder")
    
    def scroll_to_the_top(self):
        return fill_out_keys("scroll_to_the_top")
    
    def zen_mode(self):
        return fill_out_keys("zen_mode")
    
    def scroll_to_the_bottom(self):
        return fill_out_keys("scroll_to_the_bottom")
    
    def help_page(self):
        return fill_out_keys("help_page")
    
    def select_wallpaper(self):
        return fill_out_keys("select_wallpaper")

aboba = Keybindigs()
print(aboba.get_keys("main_quit"))