"""Module with some of the common functions, like file and image operations"""

import os
import gi
import random
import shutil
import imageio
from pathlib import Path
from typing import List
from PIL import Image

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib

from waypaper.options import IMAGE_EXTENSIONS, BACKEND_OPTIONS, VIDEO_EXTENSIONS


def has_image_extension(file_path: str, backend: str) -> bool:
    """Check if the file has image extension"""
    image_extensions = IMAGE_EXTENSIONS[backend]
    ext = os.path.splitext(file_path)[1].lower()
    return ext in image_extensions


def get_image_paths(backend: str,
                    folder_list: list[Path],
                    include_subfolders: bool = False,
                    include_all_subfolders: bool = False,
                    include_hidden: bool = False,
                    only_gifs: bool = False) -> list[str]:
    """Get a list of file paths depending on the filters that were requested."""

    image_path_list: list[str] = []
    for folder in folder_list:
        for root, directories, files in os.walk(folder, followlinks=True):

            # Remove hidden files from consideration:
            for directory in directories:
                if directory.startswith('.') and not include_hidden:
                    directories.remove(directory)

            # Remove subfolders from consideration:
            if not include_subfolders and str(root) != str(folder):
                continue

            # Remove deep folders from consideration:
            if not include_all_subfolders and str(root) != str(folder):
                current_depth = root.count(os.path.sep) - str(folder).count(os.path.sep)
                if current_depth > 1:
                    continue

            # Remove files that are not images from consideration:
            for image_name in files:
                if image_name.startswith('.') and not include_hidden:
                    continue
                if not has_image_extension(image_name, backend):
                    continue
                if not image_name.casefold().endswith('.gif') and only_gifs:
                    continue
                image_path_list.append(os.path.join(root, image_name))
    return image_path_list


def get_image_name(full_path: str, base_folder_list: list[Path], include_path: bool) ->  str:
    """Get image name that may or may not include parent folders"""
    full_path = Path(full_path).resolve()

    # If path is not required, just return file name:
    if not include_path:
        return full_path.name

    # Otherwise, find from which folder file comes from and append this folder:
    for base_folder in base_folder_list:
        base_folder = Path(base_folder).resolve()
        if not full_path.is_relative_to(base_folder):
            continue
        common_folder = base_folder.name
        return str(Path(common_folder, full_path.relative_to(base_folder)))


def get_random_file(backend: str,
                    folder_list: list[Path],
                    include_subfolders: bool,
                    include_all_subfolders: bool,
                    cache_dir: Path,
                    include_hidden: bool = False) -> str | None:
    """Pick a random file from the folder and update cache"""
    try:
        # Get all image paths from the folder:
        image_paths = get_image_paths(backend, folder_list, include_subfolders, include_all_subfolders,
                                      include_hidden, only_gifs=False)

        # Read cache file with already used images:
        cache_file = cache_dir / "used_wallpapers.txt"
        if cache_file.exists():
            with cache_file.open('r') as file:
                used_images = [line.strip() for line in file.readlines()]
        # Create it if the file does not exists:
        else:
            cache_file.touch()
            used_images = []

        # Pick a random image from unused images:
        remaining_images = list(filter(lambda img: img not in set(used_images), image_paths))
        if remaining_images:
            random_image = random.choice(remaining_images)
            used_images.append(random_image)
        else:
            random_image = random.choice(image_paths)
            used_images = [random_image]

        # Write the cache file:
        with cache_file.open('w') as file:
            for img in used_images:
                file.write(img + '\n')

        return random_image

    except Exception as e:
        print(f"Error getting random image: {e}")
        return None


def check_installed_backends() -> List[str]:
    """Check which backends are installed in the system"""
    installed_backends = ["none"]
    for backend in BACKEND_OPTIONS:
        if backend == "none":
            continue
        if backend == "wallutils":
            binary_name = "setwallpaper"
        else:
            binary_name = backend
        is_installed = bool(shutil.which(binary_name))
        if is_installed:
            installed_backends.append(backend)
    return installed_backends


def cache_image(image_path: str, cache_dir: Path) -> None:
    """Create small copies of images using various libraries depending on the file type"""
    ext = os.path.splitext(image_path)[1].lower()
    cache_file = cache_dir / Path(os.path.basename(image_path))
    width = 240
    try:
        # If it's a video, extract the first frame:
        if ext in VIDEO_EXTENSIONS:
            reader = imageio.get_reader(image_path)
            first_frame = reader.get_data(0)
            # Convert the numpy array to a PIL image:
            pil_image = Image.fromarray(first_frame)
            aspect_ratio = pil_image.height / pil_image.width
            new_height = int(width * aspect_ratio)
            resized_image = pil_image.resize((width, new_height))
            resized_image.save(str(cache_file), "JPEG")
            return

        # If it's an image, create preview depending on the filetype
        if ext == ".webp":
            img = Image.open(image_path)
            data = img.tobytes()
            img_width, img_height = img.size
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(data, GdkPixbuf.Colorspace.RGB, False, 8, img_width, img_height, img_width * 3)
        else:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(image_path))
        aspect_ratio = pixbuf.get_width() / pixbuf.get_height()
        height = int(width / aspect_ratio)
        scaled_pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
        scaled_pixbuf.savev(str(cache_file), "jpeg", [], [])

    # If image processing failed, create a black placeholder:
    except Exception as e:
        print(f"Could not generate preview for {os.path.basename(image_path)}")
        print(e)
        black_pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, width, width*9/16)
        black_pixbuf.fill(0x0)
        black_pixbuf.savev(str(cache_file), "jpeg", [], [])
