"""Module with some of the common functions, like file operations"""

import os
import random
import shutil

from waypaper.options import IMAGE_EXTENSIONS, BACKEND_OPTIONS

def has_image_extension(file_path, backend):
    """Check if the file has image extension"""
    image_extensions = IMAGE_EXTENSIONS[backend]
    ext = os.path.splitext(file_path)[1].lower()
    return ext in image_extensions


def get_image_paths(backend, root_folder, include_subfolders=False, include_hidden=False, depth=None):
    """Get a list of file paths depending of weather we include subfolders and how deep we scan"""
    image_paths = []
    for root, directories, files in os.walk(root_folder):
        if not include_subfolders and root != root_folder:
            continue
        if depth is not None and root != root_folder:
            current_depth = root.count(os.path.sep) - str(root_folder).count(os.path.sep)
            if current_depth > depth:
                continue
        for filename in files:
            if not has_image_extension(filename, backend):
                continue
            if filename.startswith('.') and not include_hidden:
                continue
            image_paths.append(os.path.join(root, filename))
    return image_paths


def get_random_file(backend, folder, include_subfolders, include_hidden=False):
    """Pick a random file from the folder"""
    try:
        image_paths = get_image_paths(backend, folder, include_subfolders, include_hidden, depth=1)
        return random.choice(image_paths)
    except:
        return None


def check_installed_backends():
    """Check which backends are installed in the system"""
    installed_backends = []
    for backend in BACKEND_OPTIONS:
        if backend == "wallutils":
            binary_name = "setwallpaper"
        else:
            binary_name = backend
        is_installed = bool(shutil.which(binary_name))
        if is_installed:
            installed_backends.append(backend)
    return installed_backends
