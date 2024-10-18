"""Module with some of the common functions, like file operations"""

import os
import re
import random
import shutil
import subprocess
import json

from screeninfo import get_monitors
from pathlib import Path

from waypaper.options import IMAGE_EXTENSIONS, BACKEND_OPTIONS
from typing import List


def has_image_extension(file_path: str, backend: str) -> bool:
    """Check if the file has image extension"""
    image_extensions = IMAGE_EXTENSIONS[backend]
    ext = os.path.splitext(file_path)[1].lower()
    return ext in image_extensions


def get_image_paths(backend: str,
                    root_folder: str,
                    include_subfolders: bool = False,
                    include_hidden: bool = False,
                    only_gifs: bool = False,
                    depth: int = 1):
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
                    cache_dir: Path,
                    include_hidden: bool = False) -> str | None:
    """Pick a random file from the folder"""
    try:
        cache_file = cache_dir / "cache.json"
        # Create cache file if it doesn't exist:
        if not cache_file.exists():
            with open(cache_file, 'x') as f:
                f.write('''{}''')

        image_paths = get_image_paths(backend,
                                      folder,
                                      include_subfolders,
                                      include_hidden,
                                      only_gifs=False,
                                      depth=1)

        with open(cache_file, "r+") as cachefile:
            cache = json.load(cachefile)
            # Read used_image list from cache file:
            try:
                used_images = cache['used_images']
            except KeyError:
                used_images = []

            # Pick a random image from possible images:
            remaining_images = list(filter(lambda x: x not in set(used_images), image_paths))
            if len(remaining_images) == 0:
                used_images.clear()
                random_choice = random.choice(image_paths)
            else:
                random_choice = random.choice(remaining_images)

            # Write used_image list back into cache file after adding new selected image:
            used_images.append(random_choice)
            cache['used_images'] = used_images
            cachefile.seek(0)
            json.dump(cache, cachefile, indent=4)

        return random_choice
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


def get_monitor_names() -> List[str]:
    """Obtain the list of plugged monitors"""
    connected_monitors: List[str] = []
    for m in get_monitors():
        connected_monitors.append(m.name)
    return connected_monitors

