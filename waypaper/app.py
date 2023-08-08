"""Module that runs GUI app"""

import gi
import os
import subprocess
import configparser

from waypaper.changer import change_wallpaper

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk


class App(Gtk.Window):
    """Main application class that controls GUI"""

    selected_image_path = None
    thumb_width = 240
    default_fill_option = "fill"

    config_dir = os.path.expanduser("~/.config/waypaper")
    config_file_path = os.path.join(config_dir, "config.ini")
    number_of_columns = 3
    padding = 0


    def __init__(self):
        super().__init__(title="Waypaper")
        self.set_default_size(780, 600)


        # Create the configuration directory if it doesn't exist:
        os.makedirs(self.config_dir, exist_ok=True)

        # Create a vertical box for layout:
        self.main_box = Gtk.VBox(spacing=10)
        self.add(self.main_box)

        # Create a button to open folder dialog:
        self.choose_folder_button = Gtk.Button(label="Choose wallpaper folder")
        self.choose_folder_button.connect("clicked", self.on_choose_folder_clicked)
        self.main_box.pack_start(self.choose_folder_button, False, False, 0)

        # Create an alignment container to place the grid in the top-right corner:
        self.grid_alignment = Gtk.Alignment(xalign=1, yalign=0.0, xscale=0.5, yscale=1)
        self.main_box.pack_start(self.grid_alignment, True, True, 0)

        # Create a scrolled window for the grid:
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.grid_alignment.add(self.scrolled_window)

        # Create a grid layout for images:
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(self.padding)
        self.grid.set_column_spacing(self.padding)
        self.scrolled_window.add(self.grid)

        # Set default image folder:
        self.default_image_folder = os.path.expanduser("~/Pictures")

        # Create a display option dropdown menu:
        self.fill_option_label = Gtk.Label(label="Fill option:")
        self.fill_option_combo = Gtk.ComboBoxText()
        self.fill_option_combo.append_text("stretch")
        self.fill_option_combo.append_text("fit")
        self.fill_option_combo.append_text("fill")
        self.fill_option_combo.append_text("center")
        self.fill_option_combo.append_text("tile")
        self.fill_option_combo.set_active(2)  # Default to "fill"

        # Create a box to contain the bottom row of buttons with margin
        self.bottom_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.bottom_button_box.set_margin_bottom(10)
        self.main_box.pack_end(self.bottom_button_box, False, False, 0)

        # Create an alignment container to center align the row of buttons
        self.button_row_alignment = Gtk.Alignment(xalign=0.5, yalign=0.0, xscale=0.5, yscale=0.5)
        self.bottom_button_box.pack_start(self.button_row_alignment, True, False, 0)

        # Create a horizontal box for display option and exit button
        self.option_exit_box = Gtk.HBox(spacing=10)
        self.option_exit_box.pack_start(self.fill_option_label, False, False, 0)
        self.option_exit_box.pack_start(self.fill_option_combo, False, False, 0)
        self.option_exit_box.pack_end(self.create_exit_button(), False, False, 0)
        self.button_row_alignment.add(self.option_exit_box)

        # Connect the "q" key press event to exit the application
        self.connect("key-press-event", self.on_key_pressed)


    def create_exit_button(self):
        exit_button = Gtk.Button(label="Exit")
        exit_button.connect("clicked", self.on_exit_clicked)
        return exit_button


    def load_data(self):
        """Load data from the config or use default if it does not exists"""
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file_path):
            config.read(self.config_file_path)
            self.image_folder = config.get("Settings", "folder", fallback=self.default_image_folder)
            self.fill_option = config.get("Settings", "fill", fallback=self.default_fill_option)
            self.current_wallpaper = config.get("Settings", "wallpaper", fallback=None)
        else:
            self.image_folder = self.default_image_folder


    def save_data(self):
        """Save the parameters to the configuration file"""
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file_path):
            config.read(self.config_file_path)

        if not config.has_section("Settings"):
            config.add_section("Settings")

        # Save folder:
        config.set("Settings", "folder", self.image_folder)

        # Save selected wallpaper:
        if self.selected_image_path is not None:
            config.set("Settings", "wallpaper", self.selected_image_path)

        # Save fill option:
        fill_option = self.fill_option_combo.get_active_text() or self.default_fill_option
        config.set("Settings", "fill", fill_option)

        with open(self.config_file_path, "w") as configfile:
            config.write(configfile)


    def load_images(self):
        """Load images from the selected folder, resize them, and arrange int grid"""

        if not os.path.exists(self.default_image_folder):
            self.default_image_folder = "/"

        if not os.path.exists(self.image_folder):
            self.image_folder = self.default_image_folder


        # Clear existing images:
        for child in self.grid.get_children():
            self.grid.remove(child)

        row = 0
        col = 0

        # Load images from the folder:
        for filename in os.listdir(self.image_folder):
            if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".gif"):
                image_path = os.path.join(self.image_folder, filename)

                # Load and scale the image:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)
                aspect_ratio = pixbuf.get_width() / pixbuf.get_height()
                scaled_width = self.thumb_width
                scaled_height = int(scaled_width / aspect_ratio)
                scaled_pixbuf = pixbuf.scale_simple(scaled_width, scaled_height, GdkPixbuf.InterpType.BILINEAR)

                # Create a button with an image inside:
                image = Gtk.Image.new_from_pixbuf(scaled_pixbuf)
                button = Gtk.Button()
                button.set_relief(Gtk.ReliefStyle.NONE)  # Remove border
                button.add(image)

                # Add button to the grid and connect clicked event:
                self.grid.attach(button, col, row, 1, 1)
                button.connect("clicked", self.on_image_clicked, image_path)

                col += 1
                if col >= self.number_of_columns:
                    col = 0
                    row += 1

        # Show all images:
        self.grid.show_all()


    def on_choose_folder_clicked(self, widget):
        """Choosing the folder of images, saving the path, and reloading images"""

        dialog = Gtk.FileChooserDialog(
            "Please choose a folder", self, Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK)
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.image_folder = dialog.get_filename()
            self.save_data()
            self.load_images()
        dialog.destroy()


    def on_image_clicked(self, widget, user_data):
        """On clicking an image, set it as a wallpaper and save"""
        self.selected_image_path = user_data
        print("Selected image path:", self.selected_image_path)
        fill_option = self.fill_option_combo.get_active_text() or self.default_fill_option
        change_wallpaper(self.selected_image_path, fill_option)
        self.save_data()


    def on_exit_clicked(self, widget):
        """On clicking exit button, save the data and quit"""
        self.save_data()
        Gtk.main_quit()


    def on_key_pressed(self, widget, event):
        """On clicking q, save the data and quit"""
        if event.keyval == Gdk.KEY_q:
            self.save_data()
            Gtk.main_quit()


    def run(self):
        """Run GUI application"""
        self.load_images()
        self.connect("destroy", self.on_exit_clicked)
        self.show_all()
        Gtk.main()
