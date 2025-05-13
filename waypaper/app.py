"""Module that runs GUI app"""

import threading
import subprocess
import os
import gi
import shutil
import imageio
import screeninfo
from pathlib import Path

from waypaper.changer import change_wallpaper
from waypaper.config import Config
from waypaper.common import get_image_paths, get_image_name, get_random_file, cache_image
from waypaper.options import FILL_OPTIONS, SORT_OPTIONS, SORT_DISPLAYS, VIDEO_EXTENSIONS , SWWW_TRANSITION_TYPES
from waypaper.translations import Chinese, English, French, German, Polish, Russian, Belarusian, Spanish

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib


class App(Gtk.Window):
    """Main application class that controls GUI"""

    def __init__(self, txt: Chinese|English|French|German|Polish|Russian|Belarusian|Spanish, cf: Config) -> None:
        super().__init__(title="Waypaper")
        self.cf = cf
        self.txt = txt
        self.check_backends()
        self.set_default_size(820, 600)
        self.connect("delete-event", Gtk.main_quit)
        self.selected_index = 0
        self.highlighted_image_row = 0
        self.is_enering_text = False
        self.number_of_resize = 0
        self.init_ui()
        self.main_box.grab_focus()

        # Start the image processing in a separate thread:
        threading.Thread(target=self.process_images).start()


    def init_ui(self) -> None:
        """Initialize the UI elements of the application"""

        # Create a vertical box for general app layout:
        self.main_box = Gtk.VBox(spacing=10)
        self.add(self.main_box)

        # Load and apply CSS
        css_provider = Gtk.CssProvider()
        css = b"""
        .highlighted-button {
            border: 1px solid @theme_selected_bg_color;
        }
        """
        css_provider.load_from_data(css)

        # Apply CSS to the default screen
        screen = Gdk.Screen.get_default()
        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # TOP MENU

        # Create a box to contain the top row of items:
        self.top_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=60)
        self.top_button_box.set_margin_top(20)
        self.main_box.pack_start(self.top_button_box, False, False, 0)

        # Create alignment container for top menu:
        self.top_row_alignment = Gtk.Alignment(xalign=0.5, yalign=0.0, xscale=0.5, yscale=0.5)
        self.top_button_box.pack_start(self.top_row_alignment, True, False, 0)

        # Create a button to open folder dialog:
        self.choose_folder_button = Gtk.Button(label=self.txt.msg_changefolder)
        self.choose_folder_button.connect("clicked", self.on_choose_folder_clicked)

        # Create a search entry:
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text(self.txt.msg_search)
        self.search_entry.connect("changed", self.on_search_entry_changed)
        self.search_entry.connect("focus-in-event", self.on_focus_in)
        self.search_entry.connect("focus-out-event", self.on_focus_out)

        # Create a clear button:
        self.clear_button = Gtk.Button(label=self.txt.msg_clear)
        self.clear_button.connect("clicked", self.on_clear_button)

        # Create the options menu button:
        self.options_button = Gtk.Button(label=self.txt.msg_options)
        self.options_button.connect("clicked", self.on_options_button_clicked)

        # Create a sort option dropdown menu:
        self.sort_combo = Gtk.ComboBoxText()
        for option in SORT_OPTIONS:
            self.sort_combo.append_text(SORT_DISPLAYS[option])
        active_num = SORT_OPTIONS.index(self.cf.sort_option)
        self.sort_combo.set_active(active_num)
        self.sort_combo.connect("changed", self.on_sort_option_changed)
        self.sort_combo.set_tooltip_text(self.txt.tip_sorting)

        # Create refresh button:
        self.refresh_button = Gtk.Button(label=self.txt.msg_refresh)
        self.refresh_button.connect("clicked", self.on_refresh_clicked)
        self.refresh_button.set_tooltip_text(self.txt.tip_refresh)

        # Create random button:
        self.random_button = Gtk.Button(label=self.txt.msg_random)
        self.random_button.connect("clicked", self.on_random_clicked)
        self.random_button.set_tooltip_text(self.txt.tip_random)

        # Create exit button:
        self.exit_button = Gtk.Button(label=self.txt.msg_exit)
        self.exit_button.connect("clicked", self.on_exit_clicked)
        self.exit_button.set_tooltip_text(self.txt.tip_exit)

        # Add all top objects to the container:
        self.top_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.top_container.pack_start(self.choose_folder_button, False, False, 0)
        self.top_container.pack_start(self.search_entry, expand=False, fill=False, padding=0)
        self.top_container.pack_start(self.clear_button, expand=False, fill=False, padding=0)
        self.top_container.pack_start(self.sort_combo, expand=False, fill=False, padding=0)
        self.top_container.pack_start(self.refresh_button, expand=False, fill=False, padding=0)
        self.top_container.pack_start(self.random_button, expand=False, fill=False, padding=0)
        self.top_container.pack_start(self.options_button, expand=False, fill=False, padding=0)
        self.top_container.pack_start(self.exit_button, expand=False, fill=False, padding=0)
        self.top_row_alignment.add(self.top_container)

        # MIDDLE GRID

        # Create a scrolled window for the grid of images:
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        # Create a box to center the grid:
        self.center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.center_box.set_valign(Gtk.Align.CENTER)
        self.center_box.set_halign(Gtk.Align.CENTER)
        self.main_box.add(self.scrolled_window)

        # Create a grid layout for images:
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(0)
        self.grid.set_column_spacing(0)
        self.center_box.add(self.grid)
        self.scrolled_window.add(self.center_box)

        # BACKEND MENU

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

        # Create mpv stop button:
        self.mpv_stop_button = Gtk.Button(label=self.txt.msg_stop)
        self.mpv_stop_button.connect("clicked", self.on_mpv_stop_button_clicked)
        self.mpv_stop_button.set_tooltip_text(self.txt.tip_mpv_stop)

        # Create mpv pause button:
        self.mpv_pause_button = Gtk.Button(label=self.txt.msg_pause)
        self.mpv_pause_button.connect("clicked", self.on_mpv_pause_button_clicked)
        self.mpv_pause_button.set_tooltip_text(self.txt.tip_mpv_pause)

        # Create mpv sound toggle:
        self.mpv_sound_toggle = Gtk.ToggleButton(label=self.txt.msg_sound)
        self.mpv_sound_toggle.set_active(self.cf.mpvpaper_sound)
        self.mpv_sound_toggle.connect("toggled", self.on_mpv_sound_toggled)
        self.mpv_sound_toggle.set_tooltip_text(self.txt.tip_mpv_sound)

        # Create a box to contain the bottom row of buttons:
        self.bottom_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=60)
        self.bottom_button_box.set_margin_bottom(15)
        self.main_box.pack_end(self.bottom_button_box, False, False, 0)

        # Create a box to contain the loading label:
        self.bottom_loading_box = Gtk.HBox(spacing=0)
        self.bottom_loading_box.set_margin_bottom(0)
        self.main_box.pack_end(self.bottom_loading_box, False, False, 0)

        # Create alignment container for bottom menu:
        self.button_row_alignment = Gtk.Alignment(xalign=0.5, yalign=0.0, xscale=0.5, yscale=0.5)
        self.bottom_button_box.pack_start(self.button_row_alignment, True, False, 0)

        # Create a monitor option dropdown menu:
        self.monitor_option_combo = Gtk.ComboBoxText()

        # Create a horizontal box for display backend options:
        self.options_box = Gtk.HBox(spacing=10)
        self.options_box.pack_start(self.backend_option_combo, False, False, 0)
        self.button_row_alignment.add(self.options_box)

        # Create a transition type dropdown menu for swww
        self.swww_transitions_options = Gtk.ComboBoxText()

        #  Get angle for animation
        self.swww_angle_entry = Gtk.Entry()
        self.swww_angle_entry.set_width_chars(5)
        self.swww_angle_entry.set_placeholder_text("angle")
        self.swww_angle_entry.connect("focus-in-event", self.on_focus_in)
        self.swww_angle_entry.connect("focus-out-event", self.on_focus_out)

        #  Get steps for animation
        self.swww_steps_entry = Gtk.Entry()
        self.swww_steps_entry.set_width_chars(5)
        self.swww_steps_entry.set_placeholder_text("steps")
        self.swww_steps_entry.connect("focus-in-event", self.on_focus_in)
        self.swww_steps_entry.connect("focus-out-event", self.on_focus_out)

        #  Get duration for animation
        self.swww_duration_entry = Gtk.Entry()
        self.swww_duration_entry.set_width_chars(7)
        self.swww_duration_entry.set_placeholder_text("duration")
        self.swww_duration_entry.connect("focus-in-event", self.on_focus_in)
        self.swww_duration_entry.connect("focus-out-event", self.on_focus_out)

        #  Get fps for animation
        self.swww_fps_entry = Gtk.Entry()
        self.swww_fps_entry.set_width_chars(5)
        self.swww_fps_entry.set_placeholder_text("fps")
        self.swww_fps_entry.connect("focus-in-event", self.on_focus_in)
        self.swww_fps_entry.connect("focus-out-event", self.on_focus_out)

        # Add different buttons depending on backend:
        self.monitor_option_display()
        self.mpv_options_display()
        self.fill_option_display()
        self.color_picker_display()
        self.swww_options_display()

        # Connect the key press events to various actions:
        self.connect("key-press-event", self.on_key_pressed)

        self.connect("button-press-event", self.on_window_clicked)

        # Connect window resizing events to change the number of columns.
        # self.connect("size-allocate", self.on_window_resize)

        self.show_all()


    def create_options_menu(self) -> None:
        """Create a GTK menu with some options of the application"""
        self.menu = Gtk.Menu()

        # Create gifs toggle:
        self.filter_gifs_checkbox = Gtk.CheckMenuItem(label=self.txt.msg_gifs)
        self.filter_gifs_checkbox.set_active(self.cf.show_gifs_only)
        self.filter_gifs_checkbox.connect("toggled", self.on_filter_gifs_toggled)
        self.menu.append(self.filter_gifs_checkbox)

        # Create subfolder toggle:
        self.include_subfolders_checkbox = Gtk.CheckMenuItem(label=self.txt.msg_subfolders)
        self.include_subfolders_checkbox.set_active(self.cf.include_subfolders)
        self.include_subfolders_checkbox.connect("toggled", self.on_include_subfolders_toggled)
        self.menu.append(self.include_subfolders_checkbox)

        # Create all subfolder toggle:
        self.include_all_subfolders_checkbox = Gtk.CheckMenuItem(label=self.txt.msg_all_subfolders)
        self.include_all_subfolders_checkbox.set_active(self.cf.include_all_subfolders)
        self.include_all_subfolders_checkbox.connect("toggled", self.on_include_all_subfolders_toggled)
        self.menu.append(self.include_all_subfolders_checkbox)

        # Create hidden toggle:
        self.include_hidden_checkbox = Gtk.CheckMenuItem(label=self.txt.msg_hidden)
        self.include_hidden_checkbox.set_active(self.cf.show_hidden)
        self.include_hidden_checkbox.connect("toggled", self.on_hidden_files_toggled)
        self.menu.append(self.include_hidden_checkbox)

        # Create show folder path toggle:
        self.show_path_in_tooltip_checkbox = Gtk.CheckMenuItem(label=self.txt.msg_show_path_in_tooltip)
        self.show_path_in_tooltip_checkbox.set_active(self.cf.show_path_in_tooltip)
        self.show_path_in_tooltip_checkbox.connect("toggled", self.on_show_path_in_tooltip_toggled)
        self.menu.append(self.show_path_in_tooltip_checkbox)

        # Create zen mode toggle:
        self.zen_mode_checkbox = Gtk.CheckMenuItem(label=self.txt.msg_zen)
        self.zen_mode_checkbox.set_active(self.cf.zen_mode)
        self.zen_mode_checkbox.connect("toggled", self.on_zen_mode_toggled)
        self.menu.append(self.zen_mode_checkbox)

        self.menu.show_all()


    def on_options_button_clicked(self, widget) -> None:
        '''Position the menu at the button and show it'''
        self.create_options_menu()
        self.menu.popup_at_widget(widget, Gdk.Gravity.NORTH, Gdk.Gravity.SOUTH, None)

    def monitor_option_display(self) -> None:
        """Display monitor option if backend is not feh or wallutils"""
        self.options_box.remove(self.monitor_option_combo)
        # Check available monitors:
        monitor_names = ["All"]
        if self.cf.backend in ["feh", "wallutils", "none"]:
            return
        monitor_names.extend([m.name for m in screeninfo.get_monitors()])

        # Create a monitor option dropdown menu:
        self.monitor_option_combo = Gtk.ComboBoxText()
        for monitor in monitor_names:
            self.monitor_option_combo.append_text(monitor)
            self.monitor_option_combo.set_active(0)
            self.monitor_option_combo.connect("changed", self.on_monitor_option_changed)
            self.monitor_option_combo.set_tooltip_text(self.txt.tip_display)

        # Add it to the row of buttons:
        self.options_box.pack_start(self.monitor_option_combo, False, False, 0)

    def swww_options_display(self) -> None:
        """Show swww transition options if backend is swww"""
        self.options_box.remove(self.swww_transitions_options)
        self.options_box.remove(self.swww_angle_entry)
        self.options_box.remove(self.swww_steps_entry)
        self.options_box.remove(self.swww_fps_entry)
        self.options_box.remove(self.swww_duration_entry)

        if self.cf.backend != "swww":
            return

        self.swww_transitions_options = Gtk.ComboBoxText()
        for transitions in SWWW_TRANSITION_TYPES:
            self.swww_transitions_options.append_text(transitions)
        active_transition = 0
        if self.cf.swww_transition_type in SWWW_TRANSITION_TYPES:
            active_transition = SWWW_TRANSITION_TYPES.index(self.cf.swww_transition_type)
            self.swww_transitions_options.set_active(active_transition)
            self.swww_transitions_options.connect("changed", self.on_transition_option_changed)
            self.swww_transitions_options.set_tooltip_text(self.txt.tip_transition)

        self.options_box.pack_end(self.swww_steps_entry, False, False, 0)
        self.options_box.pack_end(self.swww_fps_entry, False, False, 0)
        self.options_box.pack_end(self.swww_angle_entry, False, False, 0)
        self.options_box.pack_end(self.swww_duration_entry, False, False, 0)
        self.options_box.pack_end(self.swww_transitions_options, False, False, 0)

    def swww_options_read(self) -> None:
        """Read swww transition options from the UI if they are valid"""
        if self.cf.backend != "swww":
            return
        angle = self.swww_angle_entry.get_text()
        steps = self.swww_steps_entry.get_text()
        fps = self.swww_fps_entry.get_text()
        duration = self.swww_duration_entry.get_text()
        if angle.isdigit():
            self.cf.swww_transition_angle = angle
        if steps.isdigit():
            self.cf.swww_transition_step = steps
        if fps.isdigit():
            self.cf.swww_transition_fps = fps
        if duration.isdigit():
            self.cf.swww_transition_duration = duration

    def mpv_options_display(self) -> None:
        """Show mpv options if backend is mpvpaper, and remove them for other backends"""
        self.options_box.remove(self.mpv_stop_button)
        self.options_box.remove(self.mpv_pause_button)
        self.options_box.remove(self.mpv_sound_toggle)
        if self.cf.backend == "mpvpaper":
            self.options_box.pack_end(self.mpv_stop_button, False, False, 0)
            self.options_box.pack_end(self.mpv_pause_button, False, False, 0)
            self.options_box.pack_end(self.mpv_sound_toggle, False, False, 0)

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
        """Show messages to user with ok button"""
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            message_format=message,
        )
        dialog.run()
        dialog.destroy()


    def process_images(self) -> None:
        """Load images from the selected folder, resize them, and arrange into a grid"""

        self.image_paths = get_image_paths(self.cf.backend, self.cf.image_folder_list, self.cf.include_subfolders,
                                      self.cf.include_all_subfolders, self.cf.show_hidden, self.cf.show_gifs_only)

        # Sort paths:
        if self.cf.sort_option in ["name", "namerev"]:
            self.image_paths.sort(reverse=(self.cf.sort_option == "namerev"))
        if self.cf.sort_option in ["date", "daterev"]:
            self.image_paths.sort(key=lambda x: os.path.getmtime(x), reverse=(self.cf.sort_option == "daterev"))

        # Show caching label:
        self.loading_label = Gtk.Label(label=self.txt.msg_caching)
        self.bottom_loading_box.add(self.loading_label)
        self.bottom_loading_box.show_all()

        self.thumbnails = []
        self.image_names = []

        for image_path in self.image_paths:

            # Skip zero byte files inside the image_path:
            if os.path.getsize(image_path) == 0:
                self.image_paths.remove(image_path)
                continue

            # If this image is not cached yet, resize and cache it:
            cached_image_path = self.cf.cache_dir / os.path.basename(image_path)
            if not cached_image_path.exists():
                cache_image(image_path, self.cf.cache_dir)

            # Load cached thumbnail:
            thumbnail = GdkPixbuf.Pixbuf.new_from_file(str(cached_image_path))
            self.thumbnails.append(thumbnail)

            # Get image name, which may or may not include parent folders:
            image_name = get_image_name(image_path, self.cf.image_folder_list, self.cf.show_path_in_tooltip)
            self.image_names.append(image_name)

        # When image processing is done, remove caching label and display the images:
        self.bottom_loading_box.remove(self.loading_label)
        GLib.idle_add(self.load_image_grid)


    def get_filtered_images(self) -> list:
        """Filter image paths, names, and thumbnails based on the search query, if any"""
        # Read what is written in the search bar, and if nothing, return all images:
        search_query = self.search_entry.get_text().lower()
        if not search_query:
            return self.thumbnails, self.image_names, self.image_paths

        # Otherwise, filter only images whos names match the search query:
        image_names = [name for name in self.image_names if search_query in name.lower()]
        thumbnails = [self.thumbnails[i] for i in range(len(self.image_names)) if search_query in self.image_names[i].lower()]
        image_paths = [self.image_paths[i] for i in range(len(self.image_names)) if search_query in self.image_names[i].lower()]

        return thumbnails, image_names, image_paths


    def load_image_grid(self) -> None:
        """Reload the grid of images"""

        thumbnails, image_names, image_paths = self.get_filtered_images()

        # Clear existing images:
        for child in self.grid.get_children():
            self.grid.remove(child)

        current_y = 0
        current_row_heights = [0] * self.cf.number_of_columns
        for index, [thumbnail, name, path] in enumerate(zip(thumbnails, image_names, image_paths)):

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
                button.get_style_context().add_class("highlighted-button")
                self.highlighted_image_y = current_y
            else:
                button.set_relief(Gtk.ReliefStyle.NONE)
            button.add(image)

            # Add button to the grid and connect clicked event:
            self.grid.attach(button, column, row, 1, 1)
            button.connect("clicked", self.on_image_clicked, path)

        self.grid.show_all()
        self.toggle_zen_mode()


    def toggle_zen_mode(self):
        """Hide or show UI elements when zen mode is enabled or disabled"""
        if self.cf.zen_mode:
            for widget in self.top_container:
                widget.hide()
            for widget in self.options_box:
                widget.hide()
        else:
            for widget in self.top_container:
                widget.show()
            for widget in self.options_box:
                widget.show()


    # def on_window_resize(self, widget, allocation) -> None:
        # """Recalculate the number of columns on window resize and repopulate the grid"""

        # As frequent resize freezed the interface, so we only do it each fifth resize:
        # self.number_of_resize += 1
        # if self.number_of_resize < 5:
            # return

        # Calculate new number of columns and reload the grid:
        # self.cf.number_of_columns = max(1, allocation.width // 250)
        # GLib.idle_add(self.load_image_grid)
        # self.number_of_resize = 0


    def scroll_to_selected_image(self) -> None:
        """Scroll the window to see the highlighted image"""
        scrolled_window_height = self.scrolled_window.get_vadjustment().get_page_size()
        # current_y = self.highlighted_image_row * 180
        subscreen_num = self.highlighted_image_y // scrolled_window_height
        scroll = scrolled_window_height * subscreen_num
        self.scrolled_window.get_vadjustment().set_value(scroll)


    def set_selected_wallpaper(self, path: str) -> None:
        """Set selected image as a wallpaper and save the state"""
        self.swww_options_read()
        self.cf.select_wallpaper(path)
        if self.cf.selected_wallpaper:
            threading.Thread(target=change_wallpaper, args=(self.cf.selected_wallpaper, self.cf, self.cf.selected_monitor)).start()
        self.cf.attribute_selected_wallpaper()
        self.cf.save()


    def choose_folder(self) -> None:
        """Choosing the folder of images, saving the path, and reloading images"""
        dialog = Gtk.FileChooserDialog(
            self.txt.msg_choosefolder, self, Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, self.txt.msg_select, Gtk.ResponseType.OK)
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.cf.image_folder_list = [Path(dialog.get_filename())]
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


    def on_zen_mode_toggled(self, toggle) -> None:
        """Toggle zen mode checkbox via menu"""
        self.show_message("You are entering Zen mode.\nPress z to return to normal mode.")
        self.cf.zen_mode = toggle.get_active()
        self.load_image_grid()


    def on_mpv_sound_toggled(self, toggle) -> None:
        """Toggle sound of mpv player"""
        self.cf.mpvpaper_sound = toggle.get_active()
        subprocess.Popen(f"echo 'cycle mute' | socat - /tmp/mpv-socket-{self.cf.selected_monitor}", shell=True)


    def on_include_subfolders_toggled(self, toggle) -> None:
        """Toggle subfolders visibility via menu"""
        self.cf.include_subfolders = toggle.get_active()
        if not self.cf.include_subfolders:
            self.cf.include_all_subfolders = False
        threading.Thread(target=self.process_images).start()


    def on_include_all_subfolders_toggled(self, toggle) -> None:
        """Toggle subfolders visibility via menu"""
        self.cf.include_all_subfolders = toggle.get_active()
        if self.cf.include_all_subfolders:
            self.cf.include_subfolders = True
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


    def on_show_path_in_tooltip_toggled(self, widget) -> None:
        """Toggle show image relative path in image tooltip"""
        self.cf.show_path_in_tooltip = not self.cf.show_path_in_tooltip
        threading.Thread(target=self.process_images).start()


    def on_fill_option_changed(self, combo) -> None:
        """Save fill parameter when it was changed"""
        self.cf.fill_option = combo.get_active_text().lower()


    def on_monitor_option_changed(self, combo) -> None:
        """Save monitor parameter when it was changed"""
        self.cf.selected_monitor = combo.get_active_text()


    def on_sort_option_changed(self, combo) -> None:
        """Save sort parameter when it is changed"""
        selected_option = combo.get_active_text()
        selected_option_num = list(SORT_DISPLAYS.values()).index(selected_option)
        self.cf.sort_option =  list(SORT_DISPLAYS.keys())[selected_option_num]
        threading.Thread(target=self.process_images).start()


    def on_backend_option_changed(self, combo) -> None:
        """Save backend parameter whet it is changed"""
        self.cf.backend = self.backend_option_combo.get_active_text()
        self.cf.selected_monitor = "All"
        self.monitor_option_display()
        self.mpv_options_display()
        self.fill_option_display()
        self.color_picker_display()
        self.swww_options_display()
        self.show_all()


    def on_transition_option_changed(self, combo) -> None:
        """Update the active transition type based on the selected option"""
        active_index = combo.get_active()
        self.cf.swww_transition_type = SWWW_TRANSITION_TYPES[active_index]
        print(f"Transition type changed to: {self.cf.swww_transition_type}")


    def on_color_set(self, color_button):
        """Convert selected color to web format"""
        rgba_color = color_button.get_rgba()
        red = int(rgba_color.red * 255)
        green = int(rgba_color.green * 255)
        blue = int(rgba_color.blue * 255)
        self.cf.color = "#{:02X}{:02X}{:02X}".format(red, green, blue)


    def on_image_clicked(self, widget, path: str) -> None:
        """On clicking an image, set it as a wallpaper and save"""
        self.selected_index = self.image_paths.index(path)
        self.load_image_grid()
        self.set_selected_wallpaper(path)

    def on_refresh_clicked(self, widget) -> None:
        """On clicking refresh button, clear cache"""
        self.clear_cache()

    def on_mpv_stop_button_clicked(self, widget) -> None:
        """On clicking mpv stop button, kill the mpvpaper"""
        subprocess.Popen(["killall", "mpvpaper"])

    def on_mpv_pause_button_clicked(self, widget) -> None:
        """On clicking mpv stop button, kill the mpvpaper"""
        subprocess.Popen(f"echo 'cycle pause' | socat - /tmp/mpv-socket-{self.cf.selected_monitor}", shell=True)

    def on_random_clicked(self, widget) -> None:
        """On clicking random button, set random wallpaper"""
        self.set_random_wallpaper()

    def on_exit_clicked(self, widget) -> None:
        """On clicking exit button, exit"""
        Gtk.main_quit()


    def set_random_wallpaper(self) -> None:
        """Choose a random image and set it as the wallpaper"""
        new_wallpaper =  get_random_file(self.cf.backend, self.cf.image_folder_list, self.cf.include_subfolders,
                                         self.cf.include_all_subfolders, self.cf.cache_dir)
        if new_wallpaper:
            self.cf.select_wallpaper(new_wallpaper)
        else:
            return
        if self.cf.selected_wallpaper:
            threading.Thread(target=change_wallpaper, args=(self.cf.selected_wallpaper, self.cf, self.cf.selected_monitor)).start()
        self.cf.attribute_selected_wallpaper()
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

        # Processing keys for losing focus on text fields:
        if self.is_enering_text:
            if event.keyval in [Gdk.KEY_Escape, Gdk.KEY_Return, Gdk.KEY_KP_Enter]:
                self.reset_input_fields()
            return

        # Processing rest of the keys:
        elif (event.keyval == Gdk.KEY_q) or (event.keyval == Gdk.KEY_Escape):
            Gtk.main_quit()

        elif event.keyval == Gdk.KEY_r:
            self.clear_cache()

        elif event.keyval == Gdk.KEY_R:
            self.set_random_wallpaper()

        elif event.keyval in [Gdk.KEY_period]:
            self.toggle_hidden_files()

        elif event.keyval in [Gdk.KEY_slash]:
            self.search_entry.grab_focus()
            return True

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

        elif event.keyval == Gdk.KEY_z:
            self.cf.zen_mode = not self.cf.zen_mode
            self.load_image_grid()

        elif event.keyval == Gdk.KEY_G:
            self.selected_index = len(self.image_paths) - 1
            self.load_image_grid()
            self.scroll_to_selected_image()

        elif event.keyval == Gdk.KEY_question:
            message = self.txt.msg_help
            self.show_message(message)

        elif event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_KP_Enter:
            wallpaper_path = self.image_paths[self.selected_index]
            self.set_selected_wallpaper(wallpaper_path)

        # Prevent other default key handling:
        return event.keyval in [Gdk.KEY_Up, Gdk.KEY_Down, Gdk.KEY_Left, Gdk.KEY_Right, Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_period]


    def on_search_entry_changed(self, entry, event=None):
        """This function is triggered when the user types in the search field"""
        self.load_image_grid()

    def on_clear_button(self, event):
        self.search_entry.set_text("")
        self.main_box.grab_focus()

    def on_focus_in(self, widget, event):
        self.is_enering_text = True

    def on_focus_out(self, widget, event):
        self.is_enering_text = False

    def reset_input_fields(self) -> None:
        """Reset all input fields and remove focus from them"""
        self.search_entry.set_visible(False)
        self.search_entry.set_visible(True)
        self.swww_angle_entry.set_visible(False)
        self.swww_angle_entry.set_visible(True)
        self.swww_steps_entry.set_visible(False)
        self.swww_steps_entry.set_visible(True)
        self.swww_duration_entry.set_visible(False)
        self.swww_duration_entry.set_visible(True)
        self.swww_fps_entry.set_visible(False)
        self.swww_fps_entry.set_visible(True)
        self.main_box.grab_focus()
        self.is_enering_text = False

    def on_window_clicked(self, widget, event) -> bool:
        """Handle clicks outside of input fields to unfocus them"""
        if self.is_enering_text:
            x, y = event.get_coords()

            focused_widget = self.get_focus()
            if focused_widget is not None:
                alloc = focused_widget.get_allocation()
                widget_x, widget_y = focused_widget.translate_coordinates(self, 0, 0) if focused_widget.translate_coordinates(self, 0, 0) else (0, 0)

                if (x < widget_x or x > widget_x + alloc.width or
                    y < widget_y or y > widget_y + alloc.height):
                    self.reset_input_fields()
                    return True

        return False

    def run(self) -> None:
        """Run GUI application"""
        self.connect("destroy", self.on_exit_clicked)
        self.show_all()
        Gtk.main()
