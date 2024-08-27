"""Module that runs GUI app"""

import threading
import os
import gi
import shutil
from pathlib import Path
from PIL import Image

from waypaper.aboutdata import AboutData
from waypaper.changer import change_wallpaper
from waypaper.config import Config
from waypaper.common import get_image_paths, get_random_file, get_monitor_names_hyprctl, get_monitor_names_swww
from waypaper.options import FILL_OPTIONS, SORT_OPTIONS, SORT_DISPLAYS
from waypaper.translations import Chinese, English, French, German, Polish, Russian, Belarusian, Spanish

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib


def read_webp_image(image_path: str) -> GdkPixbuf:
    """Read webp images using Pillow library and convert it to pixbuf format"""
    img = Image.open(image_path)
    data = img.tobytes()
    width, height = img.size
    pixbuf = GdkPixbuf.Pixbuf.new_from_data(data, GdkPixbuf.Colorspace.RGB, False, 8, width, height, width * 3)
    return pixbuf


def cache_image(image_path: str, cache_dir: Path) -> None:
    """Resize and cache images using gtk library"""
    ext = os.path.splitext(image_path)[1].lower()
    try:
        if ext == ".webp":
            pixbuf = read_webp_image(str(image_path))
        else:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(image_path))

    # If image processing failed, create a black placeholder:
    except GLib.Error:
        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 1280, 720)
        pixbuf.fill(0x0)

    aspect_ratio = pixbuf.get_width() / pixbuf.get_height()
    scaled_width = 240
    scaled_height = int(scaled_width / aspect_ratio)
    scaled_pixbuf = pixbuf.scale_simple(scaled_width, scaled_height, GdkPixbuf.InterpType.BILINEAR)
    output_file = cache_dir / Path(os.path.basename(image_path))
    scaled_pixbuf.savev(str(output_file), "jpeg", [], [])


class App(Gtk.Window):
    """Main application class that controls GUI"""

    def __init__(self, txt: Chinese|English|French|German|Polish|Russian|Belarusian|Spanish, cf: Config) -> None:
        super().__init__(title="Waypaper")
        self.cf = cf
        self.about = AboutData()
        self.txt = txt
        self.check_backends()
        self.set_default_size(820, 600)
        self.connect("delete-event", Gtk.main_quit)
        self.selected_index = 0
        self.highlighted_image_row = 0
        self.init_ui()

        # Start the image processing in a separate thread:
        threading.Thread(target=self.process_images).start()

    def init_ui(self) -> None:
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

        # Create a backend dropdown menu:
        self.backend_option_combo = Gtk.ComboBoxText()
        for backend in self.cf.installed_backends:
            self.backend_option_combo.append_text(backend)

        # Set as active line the backend from config, if it is installed:
        active_num = 0
        if self.cf.backend in self.cf.installed_backends:
            active_num = self.cf.installed_backends.index(self.cf.backend)
        self.backend_option_combo.set_active(active_num)
        self.backend_option_combo.connect("changed", self.on_backend_option_changed)
        self.backend_option_combo.set_tooltip_text(self.txt.tip_backend)

        # Create a fill option dropdown menu:
        self.fill_option_combo = Gtk.ComboBoxText()
        for option in FILL_OPTIONS:
            capitalized_option = option[0].upper() + option[1:]
            self.fill_option_combo.append_text(capitalized_option)
        if self.cf.fill_option in FILL_OPTIONS:
            active_fill_option_index = FILL_OPTIONS.index(self.cf.fill_option)
            self.fill_option_combo.set_active(active_fill_option_index)
        else:
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

        # Create the options menu button:
        self.options_button = Gtk.Button(label="Options")
        self.options_button.connect("clicked", self.on_options_button_clicked)

        # Create a horizontal box for display option and exit button:
        self.options_box = Gtk.HBox(spacing=10)
        self.options_box.pack_end(self.exit_button, False, False, 0)
        self.options_box.pack_end(self.options_button, False, False, 0)
        self.options_box.pack_end(self.refresh_button, False, False, 0)
        self.options_box.pack_end(self.random_button, False, False, 0)
        self.options_box.pack_end(self.sort_option_combo, False, False, 0)
        self.options_box.pack_start(self.backend_option_combo, False, False, 0)
        self.button_row_alignment.add(self.options_box)

        self.monitor_option_display()
        self.fill_option_display()
        self.color_picker_display()

        # Connect the "q" key press event to exit the application
        self.connect("key-press-event", self.on_key_pressed)
        self.show_all()


    def create_menu(self) -> None:
        """Create a GTK menu and items inside it"""
        self.menu = Gtk.Menu()

        # Create gifs toggle:
        self.filter_gifs_checkbox = Gtk.CheckMenuItem(label=self.txt.msg_gifs)
        self.filter_gifs_checkbox.set_active(self.cf.show_gifs_only)
        self.filter_gifs_checkbox.connect("toggled", self.on_filter_gifs_toggled)

        # Create subfolder toggle:
        self.include_subfolders_checkbox = Gtk.CheckMenuItem(label=self.txt.msg_subfolders)
        self.include_subfolders_checkbox.set_active(self.cf.include_subfolders)
        self.include_subfolders_checkbox.connect("toggled", self.on_include_subfolders_toggled)

        # Create hidden toggle:
        self.include_hidden_checkbox = Gtk.CheckMenuItem(label=self.txt.msg_hidden)
        self.include_hidden_checkbox.set_active(self.cf.show_hidden)
        self.include_hidden_checkbox.connect("toggled", self.on_hidden_files_toggled)

        self.menu.append(self.filter_gifs_checkbox)
        self.menu.append(self.include_subfolders_checkbox)
        self.menu.append(self.include_hidden_checkbox)
        self.menu.show_all()


    def on_options_button_clicked(self, widget) -> None:
        '''Position the menu at the button and show it'''
        self.create_menu()
        self.menu.popup_at_widget(widget, Gdk.Gravity.NORTH, Gdk.Gravity.SOUTH, None)


    def monitor_option_display(self) -> None:
        """Display monitor option if backend is swww or hyprpaper (with swww installed)"""
        self.options_box.remove(self.monitor_option_combo)
        # Check available monitors:
        monitor_names = ["All"]
        if self.cf.backend == "swww":
            connected_monitors = get_monitor_names_swww()
            monitor_names.extend(connected_monitors)
        elif self.cf.backend == "hyprpaper":
            connected_monitors = get_monitor_names_hyprctl()
            monitor_names.extend(connected_monitors)
        else:
            return

        # Create a monitor option dropdown menu:
        self.monitor_option_combo = Gtk.ComboBoxText()
        for monitor in monitor_names:
            self.monitor_option_combo.append_text(monitor)
            self.monitor_option_combo.set_active(0)
            self.monitor_option_combo.connect("changed", self.on_monitor_option_changed)
            self.monitor_option_combo.set_tooltip_text(self.txt.tip_display)

        # Add it to the row of buttons:
        self.options_box.pack_start(self.monitor_option_combo, False, False, 0)


    def fill_option_display(self):
        """Display fill option if backend is not hyprpaper"""
        self.options_box.remove(self.fill_option_combo)
        if self.cf.backend not in ['hyprpaper', 'none']:
            self.options_box.pack_end(self.fill_option_combo, False, False, 0)

    def color_picker_display(self):
        """Display color option if backend is not hyprpaper"""
        self.options_box.remove(self.color_picker_button)
        if self.cf.backend not in ['hyprpaper', 'none']:
            self.options_box.pack_end(self.color_picker_button, False, False, 0)

    def check_backends(self) -> None:
        """Before running the app, check which backends are installed or show the error"""
        if len(self.cf.installed_backends) == 1:
            self.show_message(self.txt.err_backend)
            exit()


    def show_message(self, message: str) -> None:
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


    def sort_images(self) -> None:
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


    def process_images(self) -> None:
        """Load images from the selected folder, resize them, and arrange into a grid"""

        self.image_paths = get_image_paths(self.cf.backend, str(self.cf.image_folder), self.cf.include_subfolders,
                                           self.cf.show_hidden, self.cf.show_gifs_only, depth=1)
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
            cached_image_path = self.cf.cache_dir / os.path.basename(image_path)
            if not cached_image_path.exists():
                cache_image(image_path, self.cf.cache_dir)

            # Load cached thumbnail:
            thumbnail = GdkPixbuf.Pixbuf.new_from_file(str(cached_image_path))
            self.thumbnails.append(thumbnail)
            self.image_names.append(os.path.basename(image_path))

        # When image processing is done, remove caching label and display the images:
        self.bottom_loading_box.remove(self.loading_label)
        GLib.idle_add(self.load_image_grid)


    def load_image_grid(self) -> None:
        """Reload the grid of images"""

        # Clear existing images:
        for child in self.grid.get_children():
            self.grid.remove(child)

        current_y = 0
        current_row_heights = [0]*self.cf.number_of_columns
        for index, [thumbnail, name, path] in enumerate(zip(self.thumbnails, self.image_names, self.image_paths)):

            row = index // self.cf.number_of_columns
            column = index % self.cf.number_of_columns

            # Calculate current y coordinate in the scroll window:
            aspect_ratio = thumbnail.get_width() / thumbnail.get_height()
            current_row_heights[column] = int(240 / aspect_ratio)
            if column == 0:
                current_y += max(current_row_heights) + 10
                current_row_heights = [0]*self.cf.number_of_columns

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


    def scroll_to_selected_image(self) -> None:
        """Scroll the window to see the highlighted image"""
        scrolled_window_height = self.scrolled_window.get_vadjustment().get_page_size()
        # current_y = self.highlighted_image_row * 180
        subscreen_num = self.highlighted_image_y // scrolled_window_height
        scroll = scrolled_window_height * subscreen_num
        self.scrolled_window.get_vadjustment().set_value(scroll)


    def choose_folder(self) -> None:
        """Choosing the folder of images, saving the path, and reloading images"""
        dialog = Gtk.FileChooserDialog(
            self.txt.msg_choosefolder, self, Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, self.txt.msg_select, Gtk.ResponseType.OK)
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.cf.image_folder = Path(dialog.get_filename())
            threading.Thread(target=self.process_images).start()
        dialog.destroy()


    def on_choose_folder_clicked(self, widget) -> None:
        """Choosing the folder of images, saving the path, and reloading images"""
        self.choose_folder()
        self.cf.save()


    def on_filter_gifs_toggled(self, toggle) -> None:
        """Toggle only gifs checkbox via menu"""
        self.cf.show_gifs_only = toggle.get_active()
        threading.Thread(target=self.process_images).start()


    def on_include_subfolders_toggled(self, toggle) -> None:
        """Toggle subfolders visibility via menu"""
        self.cf.include_subfolders = toggle.get_active()
        threading.Thread(target=self.process_images).start()


    def toggle_include_subfolders(self) -> None:
        """Toggle subfolders visibility via key"""
        self.cf.include_subfolders = not self.cf.include_subfolders
        threading.Thread(target=self.process_images).start()


    def on_hidden_files_toggled(self, toggle) -> None:
        """Toggle visibility of hidden files via menu"""
        self.cf.show_hidden = toggle.get_active()
        threading.Thread(target=self.process_images).start()


    def toggle_hidden_files(self) -> None:
        """Toggle visibility of hidden files via keys"""
        self.cf.show_hidden = not self.cf.show_hidden
        threading.Thread(target=self.process_images).start()


    def on_fill_option_changed(self, combo) -> None:
        """Save fill parameter when it was changed"""
        self.cf.fill_option = combo.get_active_text().lower()


    def on_monitor_option_changed(self, combo) -> None:
        """Save monitor parameter when it was changed"""
        self.cf.selected_monitor = combo.get_active_text()


    def on_sort_option_changed(self, combo) -> None:
        """Save sort parameter whet it is changed"""
        selected_option = combo.get_active_text()
        selected_option_num = list(SORT_DISPLAYS.values()).index(selected_option)
        self.cf.sort_option =  list(SORT_DISPLAYS.keys())[selected_option_num]
        threading.Thread(target=self.process_images).start()


    def on_backend_option_changed(self, combo) -> None:
        """Save backend parameter whet it is changed"""
        self.cf.backend = self.backend_option_combo.get_active_text()
        self.cf.selected_monitor = "All"
        self.monitor_option_display()
        self.fill_option_display()
        self.color_picker_display()
        self.show_all()


    def on_color_set(self, color_button):
        """Convert selected color to web format"""
        rgba_color = color_button.get_rgba()
        red = int(rgba_color.red * 255)
        green = int(rgba_color.green * 255)
        blue = int(rgba_color.blue * 255)
        self.cf.color = "#{:02X}{:02X}{:02X}".format(red, green, blue)


    def on_image_clicked(self, widget, path: str) -> None:
        """On clicking an image, set it as a wallpaper and save"""
        self.cf.backend = self.backend_option_combo.get_active_text()
        self.cf.select_wallpaper(path)
        self.selected_index = self.image_paths.index(path)
        self.load_image_grid()
        print(self.txt.msg_path, self.cf.selected_wallpaper)
        self.cf.fill_option = self.fill_option_combo.get_active_text().lower() or self.cf.fill_option
        if self.cf.selected_wallpaper:
            change_wallpaper(self.cf.selected_wallpaper, self.cf, self.cf.selected_monitor, self.txt)
        self.cf.save()


    def on_refresh_clicked(self, widget) -> None:
        """On clicking refresh button, clear cache"""
        self.clear_cache()


    def on_random_clicked(self, widget) -> None:
        """On clicking random button, set random wallpaper"""
        self.set_random_wallpaper()


    def on_exit_clicked(self, widget) -> None:
        """On clicking exit button, exit"""
        Gtk.main_quit()


    def set_random_wallpaper(self) -> None:
        """Choose a random image and set it as the wallpaper"""
        self.cf.backend = self.backend_option_combo.get_active_text()
        new_wallpaper =  get_random_file(self.cf.backend, str(self.cf.image_folder), self.cf.include_subfolders)
        if new_wallpaper:
            self.cf.select_wallpaper(new_wallpaper)
        else:
            return
        print(self.txt.msg_path, self.cf.selected_wallpaper)
        self.cf.fill_option = self.fill_option_combo.get_active_text().lower() or self.cf.fill_option
        if self.cf.selected_wallpaper:
            change_wallpaper(self.cf.selected_wallpaper, self.cf, self.cf.selected_monitor, self.txt)
        self.cf.save()


    def clear_cache(self) -> None:
        """Delete cache folder and reprocess the images"""
        try:
            shutil.rmtree(self.cf.cache_dir)
            os.makedirs(self.cf.cache_dir)
        except OSError as e:
            print(f"{self.txt.err_cache} '{self.cf.cache_dir}': {e}")
        threading.Thread(target=self.process_images).start()


    def on_key_pressed(self, widget, event) -> bool:
        """Process various key binding"""
        if (event.keyval == Gdk.KEY_q) or (event.keyval == Gdk.KEY_Escape):
            Gtk.main_quit()

        elif event.keyval == Gdk.KEY_r:
            self.clear_cache()

        elif event.keyval == Gdk.KEY_R:
            self.set_random_wallpaper()

        elif event.keyval in [Gdk.KEY_period]:
            self.toggle_hidden_files()

        elif event.keyval in [Gdk.KEY_s]:
            self.toggle_include_subfolders()

        elif event.keyval in [Gdk.KEY_h, Gdk.KEY_Left]:
            self.selected_index = max(self.selected_index - 1, 0)
            self.load_image_grid()
            self.scroll_to_selected_image()

        elif event.keyval in [Gdk.KEY_j, Gdk.KEY_Down]:
            self.selected_index = min(self.selected_index + self.cf.number_of_columns, len(self.image_paths) - 1)
            self.load_image_grid()
            self.scroll_to_selected_image()

        elif event.keyval in [Gdk.KEY_k, Gdk.KEY_Up]:
            self.selected_index = max(self.selected_index - self.cf.number_of_columns, 0)
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
            self.cf.select_wallpaper(wallpaper_path)
            print(self.txt.msg_path, self.cf.selected_wallpaper)
            self.cf.backend = self.backend_option_combo.get_active_text()
            self.cf.fill_option = self.fill_option_combo.get_active_text().lower() or self.cf.fill_option
            if self.cf.selected_wallpaper:
                change_wallpaper(self.cf.selected_wallpaper, self.cf, self.cf.selected_monitor, self.txt)
            self.cf.save()

        # Prevent other default key handling:
        return event.keyval in [Gdk.KEY_Up, Gdk.KEY_Down, Gdk.KEY_Left, Gdk.KEY_Right, Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_period]


    def run(self) -> None:
        """Run GUI application"""
        self.connect("destroy", self.on_exit_clicked)
        self.show_all()
        Gtk.main()
