"""Wallpaper Engine project helpers and linux-wallpaperengine launcher."""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Callable, Optional

import screeninfo

from waypaper.options import LINUX_WALLPAPERENGINE_CLAMP, LINUX_WALLPAPERENGINE_FILL_OPTIONS


StaticFallback = Callable[[Path, Any, str], Optional[str]]
StopExisting = Callable[[str, str], None]


def get_wallpaperengine_preview(wallpaperengine_folder: Path | str) -> list[str]:
    image_path_list = []
    for root, directories, files in os.walk(wallpaperengine_folder):
        for file in files:
            if Path(file).stem == "preview":
                image_path_list.append(os.path.join(root, file))
    return image_path_list


def get_wallpaperengine_project(full_path: Path | str) -> dict:
    full_path = Path(full_path)
    image_dir = full_path if full_path.is_dir() else full_path.parent
    with open(image_dir / "project.json", "r", encoding="utf-8") as project_file:
        project = json.load(project_file)
    wallpaper_type = str(project.get("type", "unknown")).strip().lower() or "unknown"
    project["type"] = wallpaper_type
    project["title"] = str(project.get("title") or image_dir.name)
    return project


def get_wallpaperengine_image_name(full_path: Path | str) -> str:
    return str(get_wallpaperengine_project(full_path)["title"])


def _find_process_pids(command: str | tuple[str, ...]) -> list[int]:
    try:
        required_fragments = (command,) if isinstance(command, str) else command
        result = subprocess.run(['ps', '-eo', 'pid=,args='], stdout=subprocess.PIPE, text=True, check=True)
        processes = result.stdout.splitlines()
        matching_pids: list[int] = []
        for process in processes:
            pid_text, _, command_line = process.strip().partition(' ')
            if command_line and all(fragment in command_line for fragment in required_fragments):
                matching_pids.append(int(pid_text))
        return matching_pids
    except Exception:
        return []


def find_replacement_linux_wallpaperengine_pid(monitor: str, current_pid: int) -> Optional[int]:
    """Find a newer linux-wallpaperengine PID after the current one was replaced."""
    command: str | tuple[str, ...]
    if monitor == "All":
        command = "linux-wallpaperengine"
    else:
        command = ("linux-wallpaperengine", f"--screen-root {monitor}")

    for pid in _find_process_pids(command):
        if pid > current_pid:
            return pid
    return None


def notify_waypaper_issue(summary: str, body: str) -> None:
    """Send a simple desktop notification when a wallpaper launch fails."""
    try:
        if shutil.which("notify-send"):
            subprocess.Popen(["notify-send", summary, body], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def resolve_linux_wallpaperengine_binary(cf: Any) -> str:
    configured_binary = getattr(cf, "linux_wallpaperengine_binary", "").strip()
    if configured_binary:
        expanded_binary = Path(configured_binary).expanduser()
        if expanded_binary.exists():
            return str(expanded_binary)
        resolved_binary = shutil.which(configured_binary)
        if resolved_binary:
            return resolved_binary
        raise FileNotFoundError(f"Configured linux-wallpaperengine executable was not found: {expanded_binary}")

    resolved_binary = shutil.which("linux-wallpaperengine")
    if resolved_binary:
        return resolved_binary
    raise FileNotFoundError("linux-wallpaperengine executable was not found in PATH")


def resolve_linux_wallpaperengine_assets_dir(cf: Any, binary_path: str) -> Optional[Path]:
    configured_assets = getattr(cf, "linux_wallpaperengine_assets_dir", "").strip()
    candidates: list[Path] = []

    if configured_assets:
        candidates.append(Path(configured_assets).expanduser())

    binary_dir = Path(binary_path).expanduser().resolve().parent
    candidates.append(binary_dir / "assets")

    workshop_dir = getattr(cf, "wallpaperengine_folder", None)
    if workshop_dir:
        workshop_path = Path(workshop_dir).expanduser()
        try:
            steamapps_dir = workshop_path.parents[2]
            candidates.append(steamapps_dir / "common" / "wallpaper_engine" / "assets")
        except IndexError:
            pass

    candidates.extend([
        Path("~/.steam/steam/steamapps/common/wallpaper_engine/assets").expanduser(),
        Path("~/.steam/root/steamapps/common/wallpaper_engine/assets").expanduser(),
        Path("~/.local/share/Steam/steamapps/common/wallpaper_engine/assets").expanduser(),
        Path("~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/wallpaper_engine/assets").expanduser(),
        Path("~/snap/steam/common/.local/share/Steam/steamapps/common/wallpaper_engine/assets").expanduser(),
    ])

    seen_paths: set[str] = set()
    for candidate in candidates:
        candidate_key = str(candidate)
        if candidate_key in seen_paths:
            continue
        seen_paths.add(candidate_key)
        if candidate.is_dir():
            return candidate
    return None


def get_linux_wallpaperengine_log_path(cf: Any, monitor: str) -> Path:
    log_dir = cf.cache_dir / "linux-wallpaperengine"
    log_dir.mkdir(parents=True, exist_ok=True)
    safe_monitor = monitor.replace("/", "_")
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    return log_dir / f"{timestamp}-{safe_monitor}.log"


def describe_linux_wallpaperengine_pause_policy(cf: Any) -> str:
    if cf.linux_wallpaperengine_no_fullscreen_pause:
        return "disabled via --no-fullscreen-pause"
    if cf.linux_wallpaperengine_fullscreen_pause_only_active:
        return "limited to the active fullscreen output via --fullscreen-pause-only-active"
    return "renderer default"


def change_with_linux_wallpaperengine(
        image_path: Path,
        cf: Any,
        monitor: str,
        stop_existing: StopExisting,
        static_fallback: StaticFallback) -> None:
    stop_existing("linux-wallpaperengine", monitor)

    if cf.fill_option.lower() in LINUX_WALLPAPERENGINE_FILL_OPTIONS:
        fill = cf.fill_option.lower()
    else:
        fill = LINUX_WALLPAPERENGINE_FILL_OPTIONS[3]

    background_path = image_path if image_path.is_dir() else image_path.parent
    if not background_path.exists():
        raise FileNotFoundError(f"Wallpaper directory does not exist: {background_path}")

    project_metadata = None
    compatibility_notes: list[str] = []
    if not image_path.is_dir():
        try:
            project_metadata = get_wallpaperengine_project(image_path)
        except Exception:
            project_metadata = None

    binary_path = resolve_linux_wallpaperengine_binary(cf)
    assets_dir = resolve_linux_wallpaperengine_assets_dir(cf, binary_path)
    log_path = get_linux_wallpaperengine_log_path(cf, monitor)
    command = [binary_path]

    if monitor == "All":
        for active_monitor in [m.name for m in screeninfo.get_monitors()]:
            if active_monitor is not None:
                command.extend(["--screen-root", active_monitor])
    else:
        command.extend(["--screen-root", monitor])

    if cf.linux_wallpaperengine_silent:
        command.append("--silent")
    if cf.linux_wallpaperengine_noautomute:
        command.append("--noautomute")
    if cf.linux_wallpaperengine_no_audio_processing:
        command.append("--no-audio-processing")
    if cf.linux_wallpaperengine_no_fullscreen_pause:
        command.append("--no-fullscreen-pause")
    if cf.linux_wallpaperengine_fullscreen_pause_only_active:
        command.append("--fullscreen-pause-only-active")
    wallpaper_type = project_metadata.get("type") if project_metadata is not None else None
    if cf.linux_wallpaperengine_disable_particles and wallpaper_type == "scene":
        compatibility_notes.append(
            "Compatibility override: skipped --disable-particles for a scene wallpaper because some animated scenes render nearly static with particles disabled."
        )
    elif cf.linux_wallpaperengine_disable_particles:
        command.append("--disable-particles")
    if cf.linux_wallpaperengine_disable_mouse:
        command.append("--disable-mouse")
    if cf.linux_wallpaperengine_disable_parallax:
        command.append("--disable-parallax")
    if cf.linux_wallpaperengine_clamp != LINUX_WALLPAPERENGINE_CLAMP[0]:
        command.extend(["--clamp", cf.linux_wallpaperengine_clamp])

    command.extend(["--volume", str(cf.linux_wallpaperengine_volume)])
    command.extend(["--fps", str(cf.linux_wallpaperengine_fps)])
    command.extend(["--scaling", fill])
    if assets_dir:
        command.extend(["--assets-dir", str(assets_dir)])

    command.append(str(background_path))
    print(f"linux-wallpaperengine command: {shlex.join(command)}")

    replacement_pid = None

    with log_path.open("w", encoding="utf-8") as log_handle:
        log_handle.write("Waypaper linux-wallpaperengine launch\n")
        log_handle.write(f"Monitor: {monitor}\n")
        log_handle.write(f"Background: {background_path}\n")
        if project_metadata is not None:
            log_handle.write(f"Wallpaper title: {project_metadata.get('title', background_path.name)}\n")
            log_handle.write(f"Wallpaper type: {project_metadata.get('type', 'unknown')}\n")
            if project_metadata.get("file"):
                log_handle.write(f"Wallpaper entry file: {project_metadata['file']}\n")
        for note in compatibility_notes:
            log_handle.write(f"Note: {note}\n")
        log_handle.write(f"Fullscreen pause policy: {describe_linux_wallpaperengine_pause_policy(cf)}\n")
        log_handle.write(f"Assets dir: {assets_dir if assets_dir else 'not resolved'}\n")
        log_handle.write(f"Command: {shlex.join(command)}\n\n")
        log_handle.flush()

        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=log_handle,
            start_new_session=True,
        )
        log_handle.write(f"Launch PID: {process.pid}\n")
        time.sleep(0.5)
        exit_code = process.poll()
        if exit_code is None:
            log_handle.write(
                "Process status after initial check: still running after 0.5s. "
                "If the wallpaper appears blank or static, the issue is likely in linux-wallpaperengine runtime behavior or wallpaper content rather than an immediate Waypaper launch failure.\n"
            )
        else:
            if exit_code == -9:
                replacement_pid = find_replacement_linux_wallpaperengine_pid(monitor, process.pid)
            if replacement_pid is not None:
                log_handle.write(
                    "Process status after initial check: exited with code "
                    f"{exit_code}, but a newer linux-wallpaperengine process "
                    f"(PID {replacement_pid}) is already running for {monitor}; "
                    "suppressing launch-failed notification.\n"
                )
            else:
                log_handle.write(f"Process status after initial check: exited with code {exit_code}\n")
        log_handle.flush()

    print(f"linux-wallpaperengine log file: {log_path}")
    if exit_code is not None:
        if replacement_pid is not None:
            print(
                "linux-wallpaperengine exited with code "
                f"{exit_code}, but a newer process for {monitor} is already running "
                f"(PID {replacement_pid}); suppressing failure notification"
            )
            return

        fallback_backend = None
        if not image_path.is_dir() and image_path.exists():
            fallback_backend = static_fallback(image_path, cf, monitor)

        message = f"linux-wallpaperengine exited immediately with code {exit_code}. See {log_path}"
        if fallback_backend:
            message += f" Fallback applied with {fallback_backend}."
        print(message)
        notify_waypaper_issue("Waypaper launch failed", message)