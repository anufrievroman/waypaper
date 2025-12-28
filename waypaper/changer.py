"""Module that runs the system processes to change the wallpaper"""

import subprocess
import time
from typing import Optional
from pathlib import Path

from waypaper.config import Config
from waypaper.options import get_monitor_names_with_hyprctl


def find_process_pid(command: str) -> Optional[int]:
    """Find the PID of the process matching the exact command"""
    try:
        result = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, text=True)
        processes = result.stdout.splitlines()
        for process in processes:
            if command in process:
                # Extract PID (second column after splitting):
                return int(process.split()[1])
        return None
    except Exception:
        return None


def seek_and_destroy(process: str, monitor: str = "All"):
    """Find if a backend is already running somewhere and kill it"""

    # Kill all process instances if we want to set for all monitors:
    if monitor == "All":
        try:
            subprocess.check_output(["pgrep", f"{process}"], encoding='utf-8')
            subprocess.Popen(["killall", f"{process}"])
            time.sleep(0.1)
            print(f"Killed all previous instances of {process}")
        except subprocess.CalledProcessError:
            pass

    # Kill swww-daemon or awww-daemon if both are running at the same time, only works on all monitors
    elif process == "swww-daemon":
        try:
            subprocess.Popen(["swww kill"])
        except subprocess.CalledProcessError:
            pass
    elif process == "awww-daemon":
        try:
            subprocess.Popen(["awww kill"])
        except subprocess.CalledProcessError:
            pass

    # Otherwise, find PID of the process for certain monitor and kill it:
    else:
        if process == "mpvpaper":
            pid = find_process_pid(f"mpvpaper -f socket-{monitor}")
        elif process == "swaybg":
            pid = find_process_pid(f"swaybg -o {monitor}")
        elif process == "gslapper":
            pid = find_process_pid(f"gslapper.*{monitor}")
        else:
            return
        try:
            subprocess.run(['kill', '-9', str(pid)], check=True)
            print(f"Detected {process} on {monitor} and killed it")
        except Exception as e:
            pass


def change_with_swaybg(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with swaybg backend"""

    # Check pid of current swaybg process:
    if monitor == "All":
        pid = find_process_pid(f"swaybg")
    else:
        pid = find_process_pid(f"swaybg -o {monitor}")

    # Launch a new swaybg process:
    fill = cf.fill_option.lower()
    command = ["swaybg"]
    if monitor != "All":
        command.extend(["-o", monitor])
    command.extend(["-i", str(image_path)])
    command.extend(["-m", fill, "-c", cf.color])
    subprocess.Popen(command)

    # Kill previous swaybg process once new wallpaper is set:
    if pid:
        time.sleep(0.2)
        subprocess.run(['kill', '-9', str(pid)], check=True)


def change_with_mpvpaper(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with mpvpaper backend"""

    fill_types = {
            "fill": "panscan=1.0",
            "fit": "panscan=0.0",
            "center": "",
            "stretch": "--keepaspect=no",
            "tile": "",
            }
    fill = fill_types[cf.fill_option.lower()]

    # If mpvpaper is already active on given monitor, try to call that process in that socket:
    try:
        subprocess.check_output(["pgrep", "-f", f"socket-{monitor}"], encoding='utf-8')
        time.sleep(0.2)
        print(f"Detected running mpvpaper on {monitor}, now trying to call mpvpaper socket")
        subprocess.Popen(f"echo 'loadfile \"{image_path}\"' | socat - /tmp/mpv-socket-{monitor}", shell=True)

    # If mpvpaper is not running, create a new process in a new socket:
    except subprocess.CalledProcessError:
        print("Detected no running mpvpaper, starting new mpvpaper process")
        command = ["mpvpaper", "--fork"]
        if cf.mpvpaper_sound:
            command.extend(["-o", f"input-ipc-server=/tmp/mpv-socket-{monitor} {cf.mpvpaper_options} loop {fill} --background-color='{cf.color}'"])
        else:
            command.extend(["-o", f"input-ipc-server=/tmp/mpv-socket-{monitor} {cf.mpvpaper_options} loop {fill} --mute=yes --background-color='{cf.color}'"])

        # Specify the monitor:
        if monitor == "All":
            command.extend('*')
        else:
            command.extend([monitor])

        command.extend([image_path])

        print(f"{command=}")
        subprocess.Popen(command)


def change_with_gslapper(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with gslapper backend"""

    # Map waypaper fill options to gSlapper options (using updated gSlapper capabilities):
    fill_options = {
        "fill": "panscan=1.0",      # Full screen coverage
        "fit": "panscan=1.0",       # As you specified for proper video fitting  
        "center": "original",       # Native resolution
        "stretch": "stretch",       # New gSlapper stretch support
        "tile": "panscan=1.0"       # Tiled behavior (using full coverage)
    }
    
    # Get the gSlapper option for current fill setting:
    gslapper_fill = fill_options.get(cf.fill_option.lower(), "panscan=1.0")
    print(f"gSlapper fill option: {cf.fill_option} -> {gslapper_fill}")

    # Kill any existing gSlapper process for this monitor:
    seek_and_destroy("gslapper", monitor)

    # Build gSlapper command with proper options:
    command = ["gslapper", "--fork"]
    
    # Build options list:
    options = []
    options.append("loop")  # Always loop videos
    options.append(gslapper_fill)  # Add the fill/scaling option
    
    if not cf.mpvpaper_sound:  # If sound is OFF in UI
        options.append("no-audio")
    
    # Add user's custom options if any:
    if cf.mpvpaper_options.strip():
        options.append(cf.mpvpaper_options.strip())
    
    # Build options string:
    if options:
        command.extend(["-o", " ".join(options)])
    
    # Specify the monitor:
    if monitor == "All":
        command.append('*')
    else:
        command.append(monitor)
    
    # Add the image/video path:
    command.append(str(image_path))
    
    print(f"gSlapper command: {command}")
    subprocess.Popen(command)


def change_with_swww(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with swww backend"""

    # Because swaybg and hyprpaper are known to conflict with swww, kill them:
    seek_and_destroy("swaybg")
    seek_and_destroy("hyprpaper")
    # if both swww and awww  are running they conflict
    seek_and_destroy("awww-daemon")

    fill_types = {
            "fill": "crop",
            "fit": "fit",
            "center": "no",
            "stretch": "crop",
            "tile": "no",
            }
    fill = fill_types[cf.fill_option.lower()]

    # Check if swww-daemon is already running. If not, launch it:
    try:
        subprocess.check_output(["pgrep", "swww-daemon"], encoding='utf-8')
    except subprocess.CalledProcessError:
        subprocess.Popen(["swww-daemon"])
        print("Launched swww-daemon")

    # Get rid of this in future when swww updates everywhere:
    version_p = subprocess.run(["swww", "-V"], capture_output=True, text=True)
    swww_version = [int(x) for x in version_p.stdout.strip().split("-")[0].split(" ")[1].split(".")]

    command = ["swww", "img", image_path]
    command.extend(["--resize", fill])
    if swww_version >= [0, 11, 0]:
        command.extend(["--fill-color", cf.color.lstrip("#")])
    else:
        command.extend(["--fill-color", cf.color])
    command.extend(["--transition-type", cf.swww_transition_type])
    command.extend(["--transition-step", str(cf.swww_transition_step)])
    command.extend(["--transition-angle", str(cf.swww_transition_angle)])
    command.extend(["--transition-duration", str(cf.swww_transition_duration)])
    command.extend(["--transition-fps", str(cf.swww_transition_fps)])
    if monitor != "All":
        command.extend(["--outputs", monitor])
    subprocess.run(command)

def change_with_awww(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with awww backend"""

    # Because swaybg and hyprpaper are known to conflict with swww, kill them:
    seek_and_destroy("swaybg")
    seek_and_destroy("hyprpaper")
    # if both swww and awww are running they conflict
    seek_and_destroy("swww-daemon")

    fill_types = {
            "fill": "crop",
            "fit": "fit",
            "center": "no",
            "stretch": "crop",
            "tile": "no",
            }
    fill = fill_types[cf.fill_option.lower()]

    # Check if swww-daemon is already running. If not, launch it:
    try:
        subprocess.check_output(["pgrep", "awww-daemon"], encoding='utf-8')
    except subprocess.CalledProcessError:
        subprocess.Popen(["awww-daemon"])
        print("Launched awww-daemon")

    # Get rid of this in future when swww updates everywhere:
    version_p = subprocess.run(["awww", "-V"], capture_output=True, text=True)
    awww_version = [int(x) for x in version_p.stdout.strip().split("-")[0].split(" ")[1].split(".")]

    command = ["awww", "img", image_path]
    command.extend(["--resize", fill])
    if awww_version >= [0, 11, 0]:
        command.extend(["--fill-color", cf.color.lstrip("#")])
    else:
        command.extend(["--fill-color", cf.color])
    command.extend(["--transition-type", cf.swww_transition_type])
    command.extend(["--transition-step", str(cf.swww_transition_step)])
    command.extend(["--transition-angle", str(cf.swww_transition_angle)])
    command.extend(["--transition-duration", str(cf.swww_transition_duration)])
    command.extend(["--transition-fps", str(cf.swww_transition_fps)])
    if monitor != "All":
        command.extend(["--outputs", monitor])
    subprocess.run(command)

def change_with_feh(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with feh backend"""

    fill_types = {
            "fill": "--bg-fill",
            "fit": "--bg-max",
            "center": "--bg-center",
            "stretch": "--bg-scale",
            "tile": "--bg-tile",
            }
    fill = fill_types[cf.fill_option.lower()]
    command = ["feh", fill, "--image-bg", cf.color]
    command.extend([str(image_path)])
    subprocess.Popen(command)

def change_with_xwallpaper(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with xwallpaper backend"""

    fill_types = {
            "fill": "--zoom",
            "fit": "--maximize",
            "center": "--center",
            "stretch": "--stretch",
            "tile": "--tile",
            }
    fill = fill_types[cf.fill_option.lower()]
    # Since xwallpaper doesn't accept 'All', but 'all'
    if monitor == "All":
        monitor = "all"
    command = ["xwallpaper", "--output", monitor, fill]
    command.extend([str(image_path)])
    subprocess.Popen(command)

def change_with_wallutils(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with wallutils backend"""
    fill_types = {
            "fill": "scale",
            "fit": "scale",
            "center": "center",
            "stretch": "stretch",
            "tile": "tile",
            }
    fill = fill_types[cf.fill_option.lower()]
    subprocess.Popen(["setwallpaper", "--mode", fill, image_path])


def change_with_finder(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper on macOS"""
    command = f"osascript -e 'tell application \"Finder\" to set desktop picture to POSIX file \"{image_path}\"'"
    subprocess.Popen(command, shell=True)


def change_with_hyprpaper(image_path: Path, cf: Config, monitor: str):
    """Change wallpaper with hyprpaper backend"""

    # Check if hyprpaper is already running, otherwise start it, and preload the wallpaper:
    try:
        subprocess.check_output(["pgrep", "hyprpaper"], encoding='utf-8')
    except subprocess.CalledProcessError:
        subprocess.Popen(["hyprpaper"])
        time.sleep(1)
    preload_command = ["hyprctl", "hyprpaper", "preload", image_path]

    # Decide which monitors are affected:
    if monitor == "All":
        # monitors = [m.name for m in screeninfo.get_monitors()]
        # monitor_info = subprocess.run(["hyprctl", "monitors", "-j"], capture_output=True, text=True, check=True)
        # monitors = [m["name"] for m in json.loads(monitor_info.stdout)]
        monitors = get_monitor_names_with_hyprctl()
    else:
        monitors: list = [monitor]

    # Change the wallpaper one by one for each affected monitor:
    for m in monitors:
        wallpaper_command = ["hyprctl", "hyprpaper", "wallpaper", f"{m},{image_path}"]
        unload_command = ["hyprctl", "hyprpaper", "unload", "all"]
        result: str = ""
        retry_counter: int = 0

        # Since sometimes hyprpaper fails to change the wallpaper, we try until success:
        while result != "ok" and retry_counter < 10:
            try:
                subprocess.check_output(unload_command, encoding="utf-8").strip()
                subprocess.check_output(preload_command, encoding="utf-8").strip()
            except Exception:
                pass
                # Preloading images with Hyprpaper is currently unavailable due to https://github.com/hyprwm/hyprpaper/pull/288
                # It has not yet been determined if this will be reimplemented - https://github.com/hyprwm/hyprpaper/issues/292
            try:
                result = subprocess.check_output(wallpaper_command, encoding="utf-8").strip()
                time.sleep(0.1)
            except Exception:
                retry_counter += 1


def change_wallpaper(image_path: Path, cf: Config, monitor: str):
    """Run system commands to change the wallpaper depending on the backend"""

    print(f"Selected file: {image_path}")

    try:
        if cf.backend == "swaybg":
            change_with_swaybg(image_path, cf, monitor)
        if cf.backend == "mpvpaper":
            change_with_mpvpaper(image_path, cf, monitor)
        if cf.backend == "swww":
            change_with_swww(image_path, cf, monitor)
        if cf.backend == "awww":
            change_with_awww(image_path, cf, monitor)
        if cf.backend == "feh":
            change_with_feh(image_path, cf, monitor)
        if cf.backend == "xwallpaper":
            change_with_xwallpaper(image_path, cf, monitor)
        if cf.backend == "wallutils":
            change_with_wallutils(image_path, cf, monitor)
        if cf.backend == "hyprpaper":
            change_with_hyprpaper(image_path, cf, monitor)
        if cf.backend == "gslapper":
            change_with_gslapper(image_path, cf, monitor)
        if cf.backend == "macos":
            change_with_finder(image_path, cf, monitor)
        if cf.backend != "none":
            filename = Path(image_path).resolve().name
            print(f"Sent {cf.backend} command to set {filename} on {monitor} display\n")

        # Run a post command:
        if cf.post_command and cf.use_post_command:
            modified_image_path = str(image_path).replace(" ", "\\ ")
            post_command = cf.post_command.replace("$wallpaper", modified_image_path)
            post_command = post_command.replace("$monitor", monitor)
            subprocess.Popen(post_command, shell=True)
            print(f'Executed "{post_command}" post-command\n')

    except Exception as e:
        print(f"Error occured while changing wallpaper: \n{e}")
