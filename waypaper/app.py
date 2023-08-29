"""Module that runs GUI app"""

import threading
import os
import shutil
import distutils.spawn
import gi

from waypaper.changer import change_wallpaper
from waypaper.config import cf
from waypaper.options import FILL_OPTIONS, BACKEND_OPTIONS, SORT_OPTIONS, SORT_DISPLAYS

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib

from waypaper.translation_en import *


def has_image_extension(file_path):
    """Check if the file has image extension"""
    image_extensions = ['.gif', '.jpg', '.jpeg', '.png']
    ext = os.path.splitext(file_path)[1].lower()
    return ext in image_extensions


def get_image_paths(root_folder, include_subfolders=False, depth=None):
    """Get a list of file paths depending of weather we include subfolders and how deep we scan"""
    image_paths = []
    for root, directories, files in os.walk(root_folder):
        if not include_subfolders and root != root_folder:
            continue
        if depth is not None and root != root_folder:
            current_depth = root.count(os.path.sep) - root_folder.count(os.path.sep)
            if current_depth > depth:
                continue
        for filename in files:
            if has_image_extension(filename):
                image_paths.append(os.path.join(root, filename))
    return image_paths


def cache_image(image_path):
    """Resize and cache images using gtk library"""
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)
    aspect_ratio = pixbuf.get_width() / pixbuf.get_height()
    scaled_width = 240
    scaled_height = int(scaled_width / aspect_ratio)
    scaled_pixbuf = pixbuf.scale_simple(scaled_width, scaled_height, GdkPixbuf.InterpType.BILINEAR)
    output_file = f"{cf.config_folder}/.cache/{os.path.basename(image_path)}"
    scaled_pixbuf.savev(output_file, "jpeg", [], [])


class App(Gtk.Window):
    """Main application class that controls GUI"""

    def __init__(self):
        super().__init__(title="Waypaper")
        self.check_backends()
        self.set_default_size(780, 600)
        self.init_ui()
        self.connect("delete-event", Gtk.main_quit)
        self.selected_index = 0
        self.highlighted_image_row = 0

        # Start the image processing in a separate thread:
        threading.Thread(target=self.process_images).start()


    def init_ui(self):
        """Initialize the UI elements of the application"""

        # Create a vertical box for layout:
        self.main_box = Gtk.VBox(spacing=10)
        self.add(self.main_box)

        # Create a button to open folder dialog:
        self.choose_folder_button = Gtk.Button(label=MSG_CHANGEFOLDER)
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
        self.include_subfolders_checkbox = Gtk.ToggleButton(label=MSG_SUBFOLDERS)
        self.include_subfolders_checkbox.set_active(cf.include_subfolders)
        self.include_subfolders_checkbox.connect("toggled", self.on_include_subfolders_toggled)

        # Create a backend dropdown menu:
        self.backend_option_combo = Gtk.ComboBoxText()
        for backend, is_missing in zip(BACKEND_OPTIONS, self.missing_backends):
            if not is_missing:
                self.backend_option_combo.append_text(backend)

        # Set as active line the backend from config, if it is installed:
        try:
            installed_backends = [value for value, miss in zip(BACKEND_OPTIONS, self.missing_backends) if not miss]
            active_num = installed_backends.index(cf.backend)
        except:
            active_num = 0
        self.backend_option_combo.set_active(active_num)
        self.backend_option_combo.connect("changed", self.on_backend_option_changed)

        # Create a fill option dropdown menu:
        self.fill_option_combo = Gtk.ComboBoxText()
        for option in FILL_OPTIONS:
            capitalized_option = option[0].upper() + option[1:]
            self.fill_option_combo.append_text(capitalized_option)
        self.fill_option_combo.set_active(0)
        self.fill_option_combo.connect("changed", self.on_fill_option_changed)

        # Create a color picker:
        self.color_picker_button = Gtk.ColorButton()
        self.color_picker_button.set_use_alpha(True)
        rgba_color = Gdk.RGBA()
        rgba_color.parse(cf.color)
        self.color_picker_button.set_rgba(rgba_color)
        self.color_picker_button.connect("color-set", self.on_color_set)

        # Create a sort option dropdown menu:
        self.sort_option_combo = Gtk.ComboBoxText()
        for option in SORT_OPTIONS:
            self.sort_option_combo.append_text(SORT_DISPLAYS[option])
        active_num = SORT_OPTIONS.index(cf.sort_option)
        self.sort_option_combo.set_active(active_num)
        self.sort_option_combo.connect("changed", self.on_sort_option_changed)

        # Create exit button:
        self.exit_button = Gtk.Button(label=MSG_EXIT)
        self.exit_button.connect("clicked", self.on_exit_clicked)

        # Create refresh button:
        self.refresh_button = Gtk.Button(label=MSG_REFRESH)
        self.refresh_button.connect("clicked", self.on_refresh_clicked)

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

        # Create a horizontal box for display option and exit button:
        self.options_box = Gtk.HBox(spacing=10)
        self.options_box.pack_end(self.exit_button, False, False, 0)
        self.options_box.pack_end(self.refresh_button, False, False, 0)
        self.options_box.pack_end(self.include_subfolders_checkbox, False, False, 0)
        self.options_box.pack_end(self.sort_option_combo, False, False, 0)
        self.options_box.pack_end(self.color_picker_button, False, False, 0)
        self.options_box.pack_end(self.fill_option_combo, False, False, 0)
        self.options_box.pack_end(self.backend_option_combo, False, False, 0)
        self.button_row_alignment.add(self.options_box)

        # Connect the "q" key press event to exit the application
        self.connect("key-press-event", self.on_key_pressed)
        self.show_all()


    def check_backends(self):
        """Before running the app, check which backends are installed"""
        self.missing_backends = []
        for backend in BACKEND_OPTIONS:
            if backend == "wallutils":
                backend = "setwallpaper"
            is_backend_missing = not bool(distutils.spawn.find_executable(backend))
            self.missing_backends.append(is_backend_missing)

        # Show error message if no backends are installed:
        if all(self.missing_backends):
            self.show_message(ERR_BACKEND)
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
        if cf.sort_option == "name":
            self.image_paths.sort(key=lambda x: os.path.basename(x))
        elif cf.sort_option == "namerev":
            self.image_paths.sort(key=lambda x: os.path.basename(x), reverse=True)
        elif cf.sort_option == "date":
            self.image_paths.sort(key=lambda x: os.path.getmtime(x))
        elif cf.sort_option == "daterev":
            self.image_paths.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        else:
            pass


    def process_images(self):
        """Load images from the selected folder, resize them, and arrange into a grid"""

        self.image_paths = get_image_paths(cf.image_folder, cf.include_subfolders, depth=1)
        self.sort_images()

        # Show caching label:
        self.loading_label = Gtk.Label(label=MSG_CACHING)
        self.bottom_loading_box.add(self.loading_label)
        self.show_all()

        self.thumbnails = []
        self.image_names = []

        for image_path in self.image_paths:

            # If this image is not cached yet, resize and cache it:
            if not os.path.exists(f"{cf.config_folder}/.cache/{os.path.basename(image_path)}"):
                cache_image(image_path)

            # Load cached thumbnail:
            cached_image_path = f"{cf.config_folder}/.cache/{os.path.basename(image_path)}"
            thumbnail = GdkPixbuf.Pixbuf.new_from_file(cached_image_path)
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

        row = 0
        col = 0

        for index, [thumbnail, name, path] in enumerate(zip(self.thumbnails, self.image_names, self.image_paths)):

            # Create a button with an image and add tooltip:
            image = Gtk.Image.new_from_pixbuf(thumbnail)
            image.set_tooltip_text(name)
            button = Gtk.Button()
            if index == self.selected_index:
                button.set_relief(Gtk.ReliefStyle.NORMAL)
                self.highlighted_image_row = row
            else:
                button.set_relief(Gtk.ReliefStyle.NONE)
            button.add(image)

            # Add button to the grid and connect clicked event:
            self.grid.attach(button, col, row, 1, 1)
            button.connect("clicked", self.on_image_clicked, path)

            col += 1
            if col >= 3:
                col = 0
                row += 1

        self.show_all()
        self.scroll_to_selected_image()


    def scroll_to_selected_image(self):
        """Scroll the window to see the highlighed image"""
        scrolled_window_height = self.scrolled_window.get_vadjustment().get_page_size()
        current_y = self.highlighted_image_row * 180
        subscreen_num = current_y // scrolled_window_height
        scroll = scrolled_window_height * subscreen_num
        self.scrolled_window.get_vadjustment().set_value(scroll)


    def choose_folder(self):
        """Choosing the folder of images, saving the path, and reloading images"""

        dialog = Gtk.FileChooserDialog(
            "Please choose a folder", self, Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, MSG_SELECT, Gtk.ResponseType.OK)
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            cf.image_folder = dialog.get_filename()
            cf.save()
            threading.Thread(target=self.process_images).start()
        dialog.destroy()


    def on_choose_folder_clicked(self, widget):
        """Choosing the folder of images, saving the path, and reloading images"""
        self.choose_folder()


    def on_include_subfolders_toggled(self, toggle):
        """On chosing to include subfolders"""
        cf.include_subfolders = toggle.get_active()
        threading.Thread(target=self.process_images).start()


    def on_fill_option_changed(self, combo):
        """Save fill parameter whet it is changed"""
        cf.fill_option = combo.get_active_text()


    def on_sort_option_changed(self, combo):
        """Save sort parameter whet it is changed"""
        selected_option = combo.get_active_text()
        selected_option_num = list(SORT_DISPLAYS.values()).index(selected_option)
        cf.sort_option =  list(SORT_DISPLAYS.keys())[selected_option_num]
        threading.Thread(target=self.process_images).start()


    def on_backend_option_changed(self, combo):
        """Save backend parameter whet it is changed"""
        cf.backend = combo.get_active_text()


    def on_color_set(self, color_button):
        """Convert selected color to web format"""
        rgba_color = color_button.get_rgba()
        red = int(rgba_color.red * 255)
        green = int(rgba_color.green * 255)
        blue = int(rgba_color.blue * 255)
        cf.color = "#{:02X}{:02X}{:02X}".format(red, green, blue)


    def on_image_clicked(self, widget, path):
        """On clicking an image, set it as a wallpaper and save"""
        cf.wallpaper = path
        self.selected_index = self.image_paths.index(path)
        self.load_image_grid()
        print(MSG_PATH, cf.wallpaper)
        cf.fill_option = self.fill_option_combo.get_active_text() or cf.fill_option
        change_wallpaper(cf.wallpaper, cf.fill_option, cf.color, cf.backend)
        cf.save()


    def on_refresh_clicked(self, widget):
        """On clicking refresh button, clear cache"""
        self.clear_cache()


    def on_exit_clicked(self, widget):
        """On clicking exit button, exit"""
        self.exit_app()


    def exit_app(self):
        """Save the data and quit"""
        cf.save()
        Gtk.main_quit()


    def clear_cache(self):
        """Delete cache folder and reprocess the images"""
        cache_folder = f"{cf.config_folder}/.cache"
        try:
            shutil.rmtree(cache_folder)
            os.makedirs(cache_folder)
        except OSError as e:
            print(f"{ERR_CACHE} '{cache_folder}': {e}")
        threading.Thread(target=self.process_images).start()


    def on_key_pressed(self, widget, event):
        """Process various key bindigns"""
        if event.keyval == Gdk.KEY_q:
            self.exit_app()

        elif event.keyval == Gdk.KEY_r:
            self.clear_cache()

        elif event.keyval in [Gdk.KEY_h, Gdk.KEY_Left]:
            self.selected_index = max(self.selected_index - 1, 0)
            self.load_image_grid()

        elif event.keyval in [Gdk.KEY_j, Gdk.KEY_Down]:
            self.selected_index = min(self.selected_index + 3, len(self.image_paths) - 1)
            self.load_image_grid()

        elif event.keyval in [Gdk.KEY_k, Gdk.KEY_Up]:
            self.selected_index = max(self.selected_index - 3, 0)
            self.load_image_grid()

        elif event.keyval in [Gdk.KEY_l, Gdk.KEY_Right]:
            self.selected_index = min(self.selected_index + 1, len(self.image_paths) - 1)
            self.load_image_grid()

        elif event.keyval == Gdk.KEY_f:
            self.choose_folder()

        elif event.keyval == Gdk.KEY_g:
            self.selected_index = 0
            self.load_image_grid()

        elif event.keyval == Gdk.KEY_G:
            self.selected_index = len(self.image_paths) - 1
            self.load_image_grid()

        elif event.keyval == Gdk.KEY_question:
            message = MSG_HELP
            self.show_message(message)

        elif event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_KP_Enter:
            wallpaper_path = self.image_paths[self.selected_index]
            cf.wallpaper = wallpaper_path
            print(MSG_PATH, cf.wallpaper)
            cf.fill_option = self.fill_option_combo.get_active_text() or cf.fill_option
            change_wallpaper(cf.wallpaper, cf.fill_option, cf.color, cf.backend)
            cf.save()

        # Prevent other default key handling:
        if event.keyval in [Gdk.KEY_Up, Gdk.KEY_Down, Gdk.KEY_Left, Gdk.KEY_Right, Gdk.KEY_Return, Gdk.KEY_KP_Enter]:
            return True


    def run(self):
        """Run GUI application"""
        self.connect("destroy", self.on_exit_clicked)
        self.show_all()
        Gtk.main()
