"""Module that runs GUI app"""

import subprocess
import threading
import os
import shutil
import gi
from pathlib import Path
from platformdirs import user_cache_path

from waypaper.aboutdata import AboutData
from waypaper.changer import change_wallpaper
from waypaper.config import Config
from waypaper.common import get_image_paths, get_random_file
from waypaper.options import FILL_OPTIONS, BACKEND_OPTIONS, SORT_OPTIONS, SORT_DISPLAYS

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib


def cache_image(image_path, cachedir):
    """Resize and cache images using gtk library"""
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(image_path))
    aspect_ratio = pixbuf.get_width() / pixbuf.get_height()
    scaled_width = 240
    scaled_height = int(scaled_width / aspect_ratio)
    scaled_pixbuf = pixbuf.scale_simple(scaled_width, scaled_height, GdkPixbuf.InterpType.BILINEAR)
    output_file = cachedir / Path(os.path.basename(image_path))
    scaled_pixbuf.savev(str(output_file), "jpeg", [], [])


class App(Gtk.Window):
    """Main application class that controls GUI"""

    def __init__(self, txt):
        super().__init__(title="Waypaper")
        self.txt = txt
        self.check_backends()
        self.set_default_size(780, 600)
        self.connect("delete-event", Gtk.main_quit)
        self.selected_index = 0
        self.highlighted_image_row = 0
        self.aboutData = AboutData()
        self.cachePath = user_cache_path(self.aboutData.applicationName())
        self.cf = Config()
        self.init_ui()

        # Start the image processing in a separate thread:
        threading.Thread(target=self.process_images).start()

    def init_ui(self):
        """Initialize the UI elements of the application"""

        # Create a vertical box for layout:
        self.main_box = Gtk.VBox(spacing=10)
        self.add(self.main_box)

        # Create a button to open folder dialog:
        self.choose_folder_button = Gtk.Button(label=self.txt.msg_changefolder)
        self.choose_folder_button.connect("clicked", self.on_choose_folder_clicked)
        self.main_box.pack_start(self.choose_folder_button, False, False, 0)

        # Create an alignment container to place the grid in the top-right corner:
        self.grid_alignment = Gtk.Alignment(xalign=1, yalign=0.0, xscale=0.5, yscale=1)
        self.main_box.pack_start(self.grid_alignment, True, True, 0)

        # Create a scrolled window for the grid of images:
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.grid_alignment.add(self.scrolled_window)

        # Create a grid layout for images:
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(0)
        self.grid.set_column_spacing(0)
        self.scrolled_window.add(self.grid)

        # Create subfolder toggle:
        self.include_subfolders_checkbox = Gtk.ToggleButton(label=self.txt.msg_subfolders)
        self.include_subfolders_checkbox.set_active(self.cf.include_subfolders)
        self.include_subfolders_checkbox.connect("toggled", self.on_include_subfolders_toggled)
        self.include_subfolders_checkbox.set_tooltip_text(self.txt.tip_subfolder)

        # Create a backend dropdown menu:
        self.backend_option_combo = Gtk.ComboBoxText()
        for backend, is_missing in zip(BACKEND_OPTIONS, self.missing_backends):
            if not is_missing:
                self.backend_option_combo.append_text(backend)

        # Set as active line the backend from config, if it is installed:
        try:
            installed_backends = [value for value, miss in zip(BACKEND_OPTIONS, self.missing_backends) if not miss]
            active_num = installed_backends.index(self.cf.backend)
        except:
            active_num = 0
        self.backend_option_combo.set_active(active_num)
        self.backend_option_combo.connect("changed", self.on_backend_option_changed)
        self.backend_option_combo.set_tooltip_text(self.txt.tip_backend)

        # Create a fill option dropdown menu:
        self.fill_option_combo = Gtk.ComboBoxText()
        for option in FILL_OPTIONS:
            capitalized_option = option[0].upper() + option[1:]
            self.fill_option_combo.append_text(capitalized_option)
        self.fill_option_combo.set_active(0)
        self.fill_option_combo.connect("changed", self.on_fill_option_changed)
        self.fill_option_combo.set_tooltip_text(self.txt.tip_fill)

        # Create a color picker:
        self.color_picker_button = Gtk.ColorButton()
        self.color_picker_button.set_use_alpha(True)
        rgba_color = Gdk.RGBA()
        rgba_color.parse(self.cf.color)
        self.color_picker_button.set_rgba(rgba_color)
        self.color_picker_button.connect("color-set", self.on_color_set)
        self.color_picker_button.set_tooltip_text(self.txt.tip_color)

        # Create a sort option dropdown menu:
        self.sort_option_combo = Gtk.ComboBoxText()
        for option in SORT_OPTIONS:
            self.sort_option_combo.append_text(SORT_DISPLAYS[option])
        active_num = SORT_OPTIONS.index(self.cf.sort_option)
        self.sort_option_combo.set_active(active_num)
        self.sort_option_combo.connect("changed", self.on_sort_option_changed)
        self.sort_option_combo.set_tooltip_text(self.txt.tip_sorting)


        # Create exit button:
        self.exit_button = Gtk.Button(label=self.txt.msg_exit)
        self.exit_button.connect("clicked", self.on_exit_clicked)
        self.exit_button.set_tooltip_text(self.txt.tip_exit)

        # Create refresh button:
        self.refresh_button = Gtk.Button(label=self.txt.msg_refresh)
        self.refresh_button.connect("clicked", self.on_refresh_clicked)
        self.refresh_button.set_tooltip_text(self.txt.tip_refresh)

        # Create random button:
        self.random_button = Gtk.Button(label=self.txt.msg_random)
        self.random_button.connect("clicked", self.on_random_clicked)
        self.random_button.set_tooltip_text(self.txt.tip_random)

        # Create a box to contain the bottom row of buttons with margin:
        self.bottom_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.bottom_button_box.set_margin_bottom(10)
        self.main_box.pack_end(self.bottom_button_box, False, False, 0)

        # Create a box to contain the loading label:
        self.bottom_loading_box = Gtk.HBox(spacing=0)
        self.bottom_loading_box.set_margin_bottom(0)
        self.main_box.pack_end(self.bottom_loading_box, False, False, 0)

        # Create alignment container:
        self.button_row_alignment = Gtk.Alignment(xalign=0.5, yalign=0.0, xscale=0.5, yscale=0.5)
        self.bottom_button_box.pack_start(self.button_row_alignment, True, False, 0)

        # Create a monitor option dropdown menu:
        self.monitor_option_combo = Gtk.ComboBoxText()

        # Create a horizontal box for display option and exit button:
        self.options_box = Gtk.HBox(spacing=10)
        self.options_box.pack_end(self.exit_button, False, False, 0)
        self.options_box.pack_end(self.refresh_button, False, False, 0)
        self.options_box.pack_end(self.random_button, False, False, 0)
        self.options_box.pack_end(self.include_subfolders_checkbox, False, False, 0)
        self.options_box.pack_end(self.sort_option_combo, False, False, 0)
        self.options_box.pack_end(self.color_picker_button, False, False, 0)
        self.options_box.pack_end(self.fill_option_combo, False, False, 0)
        self.options_box.pack_start(self.backend_option_combo, False, False, 0)
        self.button_row_alignment.add(self.options_box)

        self.monitor_option_display()

        # Connect the "q" key press event to exit the application
        self.connect("key-press-event", self.on_key_pressed)
        self.show_all()


    def monitor_option_display(self):
        """Display monitor option if backend is swww"""
        self.options_box.remove(self.monitor_option_combo)
        # if "swww" not in self.missing_backends and self.cf.backend not in ["wallutils", "feh"]:
        if self.cf.backend == "swww":

            # Check available monitors:
            monitor_names = ["All"]
            try:
                subprocess.Popen(["swww", "init"])
                query_output = str(subprocess.check_output(["swww", "query"], encoding='utf-8'))
                monitors = query_output.split("\n")
                for monitor in monitors[:-1]:
                    monitor_names.append(monitor.split(':')[0])
            except Exception as e:
                print(f"{self.txt.err_disp} {e}")

            # Create a monitor option dropdown menu:
            self.monitor_option_combo = Gtk.ComboBoxText()
            for monitor in monitor_names:
                self.monitor_option_combo.append_text(monitor)
                self.monitor_option_combo.set_active(0)
                self.monitor_option_combo.connect("changed", self.on_monitor_option_changed)
                self.monitor_option_combo.set_tooltip_text(self.txt.tip_display)

            # Add it to the row of buttons:
            self.options_box.pack_start(self.monitor_option_combo, False, False, 0)


    def check_backends(self):
        """Before running the app, check which backends are installed"""
        self.missing_backends = []
        for backend in BACKEND_OPTIONS:
            if backend == "wallutils":
                backend = "setwallpaper"
            is_backend_missing = not bool(shutil.which(backend))
            self.missing_backends.append(is_backend_missing)

        # Show error message if no backends are installed:
        if all(self.missing_backends):
            self.show_message(sefl.txt.err_backend)
            exit()


    def show_message(self, message):
        """If no backends are installed, show a message"""
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            message_format=message,
        )
        dialog.run()
        dialog.destroy()


    def sort_images(self):
        """Sort images depending on the sorting option"""
        if self.cf.sort_option == "name":
            self.image_paths.sort(key=lambda x: os.path.basename(x))
        elif self.cf.sort_option == "namerev":
            self.image_paths.sort(key=lambda x: os.path.basename(x), reverse=True)
        elif self.cf.sort_option == "date":
            self.image_paths.sort(key=lambda x: os.path.getmtime(x))
        elif self.cf.sort_option == "daterev":
            self.image_paths.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        else:
            pass


    def process_images(self):
        """Load images from the selected folder, resize them, and arrange into a grid"""

        self.image_paths = get_image_paths(self.cf.image_folder, self.cf.include_subfolders, depth=1)
        self.sort_images()

        # Show caching label:
        self.loading_label = Gtk.Label(label=self.txt.msg_caching)
        self.bottom_loading_box.add(self.loading_label)
        self.show_all()

        self.thumbnails = []
        self.image_names = []

        for image_path in self.image_paths:
            if os.path.getsize(image_path) == 0:
                # Skip zero byte files inside the image_path
                self.image_paths.remove(image_path)
                continue
            # If this image is not cached yet, resize and cache it:
            cached_image_path = self.cachePath/os.path.basename(image_path)
            if not cached_image_path.exists():
                cache_image(image_path, self.cachePath)

            # Load cached thumbnail:
            thumbnail = GdkPixbuf.Pixbuf.new_from_file(str(cached_image_path))
            self.thumbnails.append(thumbnail)
            self.image_names.append(os.path.basename(image_path))

        # When image processing is done, remove caching label and display the images:
        self.bottom_loading_box.remove(self.loading_label)
        GLib.idle_add(self.load_image_grid)


    def load_image_grid(self):
        """Reload the grid of images"""

        # Clear existing images:
        for child in self.grid.get_children():
            self.grid.remove(child)

        current_y = 0
        current_row_heights = [0, 0, 0]
        for index, [thumbnail, name, path] in enumerate(zip(self.thumbnails, self.image_names, self.image_paths)):

            row = index // 3
            column = index % 3

            # Calculate current y coordinate in the scroll window:
            aspect_ratio = thumbnail.get_width() / thumbnail.get_height()
            current_row_heights[column] = int(240 / aspect_ratio)
            if column == 0:
                current_y += max(current_row_heights) + 10
                current_row_heights = [0, 0, 0]

            # Create a button with an image and add tooltip:
            image = Gtk.Image.new_from_pixbuf(thumbnail)
            image.set_tooltip_text(name)
            button = Gtk.Button()
            if index == self.selected_index:
                button.set_relief(Gtk.ReliefStyle.NORMAL)
                self.highlighted_image_y = current_y
            else:
                button.set_relief(Gtk.ReliefStyle.NONE)
            button.add(image)

            # Add button to the grid and connect clicked event:
            self.grid.attach(button, column, row, 1, 1)
            button.connect("clicked", self.on_image_clicked, path)

        self.show_all()


    def scroll_to_selected_image(self):
        """Scroll the window to see the highlighed image"""
        scrolled_window_height = self.scrolled_window.get_vadjustment().get_page_size()
        # current_y = self.highlighted_image_row * 180
        subscreen_num = self.highlighted_image_y // scrolled_window_height
        scroll = scrolled_window_height * subscreen_num
        self.scrolled_window.get_vadjustment().set_value(scroll)


    def choose_folder(self):
        """Choosing the folder of images, saving the path, and reloading images"""

        dialog = Gtk.FileChooserDialog(
            self.txt.msg_choosefolder, self, Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, self.txt.msg_select, Gtk.ResponseType.OK)
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.cf.image_folder = dialog.get_filename()
            threading.Thread(target=self.process_images).start()
        dialog.destroy()


    def on_choose_folder_clicked(self, widget):
        """Choosing the folder of images, saving the path, and reloading images"""
        self.choose_folder()
        self.cf.save()


    def on_include_subfolders_toggled(self, toggle):
        """On chosing to include subfolders"""
        self.cf.include_subfolders = toggle.get_active()
        threading.Thread(target=self.process_images).start()


    def on_fill_option_changed(self, combo):
        """Save fill parameter when it was changed"""
        self.cf.fill_option = combo.get_active_text()


    def on_monitor_option_changed(self, combo):
        """Save monitor parameter when it was changed"""
        self.cf.selected_monitor = combo.get_active_text()


    def on_sort_option_changed(self, combo):
        """Save sort parameter whet it is changed"""
        selected_option = combo.get_active_text()
        selected_option_num = list(SORT_DISPLAYS.values()).index(selected_option)
        self.cf.sort_option =  list(SORT_DISPLAYS.keys())[selected_option_num]
        threading.Thread(target=self.process_images).start()


    def on_backend_option_changed(self, combo):
        """Save backend parameter whet it is changed"""
        self.cf.backend = combo.get_active_text()
        self.cf.selected_monitor = "All"
        self.monitor_option_display()
        self.show_all()


    def on_color_set(self, color_button):
        """Convert selected color to web format"""
        rgba_color = color_button.get_rgba()
        red = int(rgba_color.red * 255)
        green = int(rgba_color.green * 255)
        blue = int(rgba_color.blue * 255)
        self.cf.color = "#{:02X}{:02X}{:02X}".format(red, green, blue)


    def on_image_clicked(self, widget, path):
        """On clicking an image, set it as a wallpaper and save"""
        self.cf.selected_wallpaper = path
        self.selected_index = self.image_paths.index(path)
        self.load_image_grid()
        print(self.txt.msg_path, self.cf.selected_wallpaper)
        self.cf.fill_option = self.fill_option_combo.get_active_text() or self.cf.fill_option
        change_wallpaper(self.cf.selected_wallpaper, self.cf.fill_option, self.cf.color,
                         self.cf.backend, self.cf.selected_monitor, self.txt)
        self.cf.save()


    def on_refresh_clicked(self, widget):
        """On clicking refresh button, clear cache"""
        self.clear_cache()


    def on_random_clicked(self, widget):
        """On clicking random button, set random wallpaper"""
        self.set_random_wallpaper()


    def on_exit_clicked(self, widget):
        """On clicking exit button, exit"""
        Gtk.main_quit()


    def set_random_wallpaper(self):
        """Choose a random image and set it as the wallpaper"""
        self.cf.selected_wallpaper = get_random_file(self.cf.image_folder, self.cf.include_subfolders)
        if self.cf.selected_wallpaper is None:
            return
        print(self.txt.msg_path, self.cf.selected_wallpaper)
        self.cf.fill_option = self.fill_option_combo.get_active_text() or self.cf.fill_option
        change_wallpaper(self.cf.selected_wallpaper, self.cf.fill_option, self.cf.color,
                         self.cf.backend, self.cf.selected_monitor, self.txt)
        self.cf.save()


    def clear_cache(self):
        """Delete cache folder and reprocess the images"""
        try:
            shutil.rmtree(self.cachePath)
            os.makedirs(self.cachePath)
        except OSError as e:
            print(f"{self.txt.err_cache} '{self.cachePath}': {e}")
        threading.Thread(target=self.process_images).start()


    def on_key_pressed(self, widget, event):
        """Process various key bindigns"""
        if event.keyval == Gdk.KEY_q:
            Gtk.main_quit()

        elif event.keyval == Gdk.KEY_r:
            self.clear_cache()

        elif event.keyval == Gdk.KEY_R:
            self.set_random_wallpaper()

        elif event.keyval in [Gdk.KEY_h, Gdk.KEY_Left]:
            self.selected_index = max(self.selected_index - 1, 0)
            self.load_image_grid()
            self.scroll_to_selected_image()

        elif event.keyval in [Gdk.KEY_j, Gdk.KEY_Down]:
            self.selected_index = min(self.selected_index + 3, len(self.image_paths) - 1)
            self.load_image_grid()
            self.scroll_to_selected_image()

        elif event.keyval in [Gdk.KEY_k, Gdk.KEY_Up]:
            self.selected_index = max(self.selected_index - 3, 0)
            self.load_image_grid()
            self.scroll_to_selected_image()

        elif event.keyval in [Gdk.KEY_l, Gdk.KEY_Right]:
            self.selected_index = min(self.selected_index + 1, len(self.image_paths) - 1)
            self.load_image_grid()
            self.scroll_to_selected_image()

        elif event.keyval == Gdk.KEY_f:
            self.choose_folder()

        elif event.keyval == Gdk.KEY_g:
            self.selected_index = 0
            self.load_image_grid()
            self.scroll_to_selected_image()

        elif event.keyval == Gdk.KEY_G:
            self.selected_index = len(self.image_paths) - 1
            self.load_image_grid()
            self.scroll_to_selected_image()

        elif event.keyval == Gdk.KEY_question:
            message = self.txt.msg_help
            self.show_message(message)

        elif event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_KP_Enter:
            wallpaper_path = self.image_paths[self.selected_index]
            self.cf.selected_wallpaper = wallpaper_path
            print(self.txt.msg_path, self.cf.selected_wallpaper)
            self.cf.fill_option = self.fill_option_combo.get_active_text() or self.cf.fill_option
            change_wallpaper(self.cf.selected_wallpaper, self.cf.fill_option, self.cf.color,
                             self.cf.backend, self.cf.selected_monitor, self.txt)
            self.cf.save()

        # Prevent other default key handling:
        if event.keyval in [Gdk.KEY_Up, Gdk.KEY_Down, Gdk.KEY_Left, Gdk.KEY_Right, Gdk.KEY_Return, Gdk.KEY_KP_Enter]:
            return True


    def run(self):
        """Run GUI application"""
        self.connect("destroy", self.on_exit_clicked)
        self.show_all()
        Gtk.main()
