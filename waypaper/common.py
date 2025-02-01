"""Module with some of the common functions, like file operations"""

import os
import random
import shutil
from pathlib import Path
from typing import List

from waypaper.options import IMAGE_EXTENSIONS, BACKEND_OPTIONS


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
