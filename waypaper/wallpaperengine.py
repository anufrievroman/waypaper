"""Wallpaper Engine project helpers.

This module is intentionally limited to Wallpaper Engine metadata
normalization: project directory resolution, project.json parsing with
type/title normalization, and entry-file resolution for video projects.

It is not used for backend-selection decisions. The user's chosen backend
in the picker is always honored.
"""

import json
from pathlib import Path


def get_wallpaperengine_project_dir(full_path: Path | str) -> Path:
    full_path = Path(full_path)
    return full_path if full_path.is_dir() else full_path.parent


def get_wallpaperengine_project(full_path: Path | str) -> dict:
    image_dir = get_wallpaperengine_project_dir(full_path)
    with open(image_dir / "project.json", "r") as file:
        project = json.load(file)
    wallpaper_type = str(project.get("type", "unknown")).strip().lower() or "unknown"
    project["type"] = wallpaper_type
    project["title"] = str(project.get("title") or image_dir.name)
    return project


def get_wallpaperengine_entry_path(full_path: Path | str) -> Path | None:
    image_dir = get_wallpaperengine_project_dir(full_path)
    project = get_wallpaperengine_project(image_dir)
    entry_name = project.get("file")
    if not entry_name:
        return None

    entry_path = image_dir / entry_name
    if entry_path.exists():
        return entry_path
    return None