"""Module with some of the common functions, like file operations"""

import os
import random

from waypaper.options import IMAGE_EXTENSIONS

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
