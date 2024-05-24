"""Module with some of the common functions, like file operations"""

import os
import random
import shutil

from waypaper.options import IMAGE_EXTENSIONS, BACKEND_OPTIONS
from typing import List


def has_image_extension(file_path: str, backend: str) -> List[str]:
    """Check if the file has image extension"""
    image_extensions = IMAGE_EXTENSIONS[backend]
    ext = os.path.splitext(file_path)[1].lower()
    return ext in image_extensions


def get_image_paths(backend: str,
                    root_folder: str,
                    include_subfolders: bool = False,
                    include_hidden: bool = False,
                    only_gifs: bool = False,
                    depth: bool = False):
    """Get a list of file paths depending on the filters that were requested"""
    image_paths = []
    for root, directories, files in os.walk(root_folder):
        # Remove hidden files from consideration:
        for directory in directories:
            if directory.startswith('.') and not include_hidden:
                directories.remove(directory)

        # Remove subfolders from consideration:
        if not include_subfolders and str(root) != str(root_folder):
            continue

        # Remove deep w from consideration:
        if depth is not None and root != root_folder:
            current_depth = root.count(os.path.sep) - str(root_folder).count(
                os.path.sep)
            if current_depth > depth:
                continue

        # Remove files that are not images from consideration:
        for filename in files:
            if filename.startswith('.') and not include_hidden:
                continue
            if not has_image_extension(filename, backend):
                continue
            if not filename.endswith('.gif') and only_gifs:
                continue
            image_paths.append(os.path.join(root, filename))
        # print(root, directories, files)
    return image_paths


def get_random_file(backend: str,
                    folder: str,
                    include_subfolders: bool,
                    include_hidden: bool = False):
    """Pick a random file from the folder"""
    try:
        image_paths = get_image_paths(backend,
                                      folder,
                                      include_subfolders,
                                      include_hidden,
                                      only_gifs=False,
                                      depth=1)
        return random.choice(image_paths)
    except:
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
