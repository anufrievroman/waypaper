"""Wallpaper Engine project helpers."""

import json
import os
from pathlib import Path
from typing import List


def get_wallpaperengine_preview(wallpaperengine_folder: Path | str) -> List[str]:
    image_path_list = []
    for root, directories, files in os.walk(wallpaperengine_folder):
        for file in files:
            if Path(file).stem == "preview":
                image_path_list.append(os.path.join(root, file))
    return image_path_list


def get_wallpaperengine_project_dir(full_path: Path | str) -> Path:
    full_path = Path(full_path)
    return full_path if full_path.is_dir() else full_path.parent


def get_wallpaperengine_project(full_path: Path | str) -> dict:
    image_dir = get_wallpaperengine_project_dir(full_path)
    with open(image_dir / "project.json", "r", encoding="utf-8") as file:
        project = json.load(file)
    wallpaper_type = str(project.get("type", "unknown")).strip().lower() or "unknown"
    project["type"] = wallpaper_type
    project["title"] = str(project.get("title") or image_dir.name)
    return project


def get_wallpaperengine_image_name(full_path: Path | str) -> str:
    try:
        project = get_wallpaperengine_project(full_path)
        wallpaper_type = project["type"]
        if wallpaper_type in {"scene", "video", "web"}:
            return f"{project['title']} [{wallpaper_type}]"
        return f"{project['title']} [{wallpaper_type} ?]"
    except Exception:
        return Path(full_path).parent.name