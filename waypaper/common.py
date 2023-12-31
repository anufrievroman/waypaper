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


def get_image_paths(backend, root_folder, include_subfolders=False, depth=None):
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
            if has_image_extension(filename, backend):
                image_paths.append(os.path.join(root, filename))
    return image_paths


def get_random_file(folder, include_subfolders):
    """Pick a random file from the folder"""
    try:
        image_paths = get_image_paths(folder, include_subfolders, depth=1)
        return random.choice(image_paths)
    except:
        return None


def check_missing_backends():
    """Check which backends are installed in the system"""
    missing_backends = []
    for backend in BACKEND_OPTIONS:
        if backend == "wallutils":
            backend = "setwallpaper"
        is_backend_missing = not bool(shutil.which(backend))
        missing_backends.append(is_backend_missing)
    return missing_backends
